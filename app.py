import sys
from datetime import datetime
from pathlib import Path
import tempfile

import streamlit as st

from xml_builder import TaskConfig, build_xml
import scheduler_cli as sc
from preview import preview_next_runs


st.set_page_config(page_title="Task Scheduler Frontend")


def parse_tasks_list(text: str):
    tasks = []
    current = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            if current:
                tasks.append(current)
                current = {}
            continue
        if ':' in line:
            key, val = line.split(':', 1)
            current[key.strip()] = val.strip()
    if current:
        tasks.append(current)
    return tasks


menu = st.sidebar.selectbox("Menu", ["Tasks", "Create Task"])

if menu == "Tasks":
    st.header("Scheduled Tasks")
    result = sc.query_all_tasks()
    if result.returncode != 0:
        st.error(f"Failed to query tasks: {result.stderr}")
    else:
        tasks = parse_tasks_list(result.stdout)
        for task in tasks:
            name = task.get("TaskName", "")
            short_name = name.split("\\")[-1]
            with st.expander(name):
                st.write(f"Status: {task.get('Status')}")
                st.write(f"Last Run Time: {task.get('Last Run Time')}")
                st.write(f"Next Run Time: {task.get('Next Run Time')}")
                st.write(f"Last Result: {task.get('Last Result')}")
                col1, col2, col3 = st.columns(3)
                if col1.button("Run", key=f"run_{name}"):
                    res = sc.run_task(short_name)
                    if res.returncode == 0:
                        st.success("Started")
                    else:
                        st.error(res.stderr)
                enabled = task.get('Scheduled Task State', '') != 'Disabled'
                toggle_text = "Disable" if enabled else "Enable"
                if col2.button(toggle_text, key=f"toggle_{name}"):
                    res = sc.change_enable(short_name, not enabled)
                    if res.returncode == 0:
                        st.success("Updated")
                    else:
                        st.error(res.stderr)
                if col3.button("Delete", key=f"del_{name}"):
                    res = sc.delete_task(short_name)
                    if res.returncode == 0:
                        st.success("Deleted")
                    else:
                        st.error(res.stderr)

elif menu == "Create Task":
    st.header("Create Task")
    with st.form("create_task"):
        name = st.text_input("Task Name")
        python_path = st.text_input("Python Path", value=sys.executable)
        script_path = st.text_input("Script Path")
        args = st.text_input("Arguments")
        workdir = st.text_input("Working Directory", value=str(Path.cwd()))
        interval = st.number_input("Every N minutes", min_value=1, value=60)
        multiple_policy = st.selectbox(
            "Multiple Instance Policy",
            ["Parallel", "Queue", "IgnoreNew", "StopExisting"],
        )
        start_when_available = st.checkbox("Start When Available", value=True)
        retry_count = st.number_input("Retry Count", min_value=0, value=3)
        retry_interval = st.number_input("Retry Interval (minutes)", min_value=1, value=5)
        submit = st.form_submit_button("Create")

    if submit:
        trigger_xml = f"""
<TimeTrigger>
  <Repetition>
    <Interval>PT{int(interval)}M</Interval>
    <StopAtDurationEnd>false</StopAtDurationEnd>
  </Repetition>
  <StartBoundary>{datetime.now().replace(second=0, microsecond=0).isoformat()}</StartBoundary>
</TimeTrigger>
"""
        config = TaskConfig(
            name=name,
            python_path=python_path,
            script_path=script_path,
            args=args,
            workdir=workdir,
            multiple_instances_policy=multiple_policy,
            start_when_available=str(start_when_available).lower(),
            retry_interval=f"PT{int(retry_interval)}M",
            retry_count=int(retry_count),
            trigger_xml=trigger_xml,
        )
        xml_content = build_xml(config)
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".xml") as f:
            f.write(xml_content)
            temp_path = Path(f.name)
        res = sc.create_task(temp_path, name)
        if res.returncode == 0:
            st.success("Task created")
        else:
            st.error(res.stderr)
        st.subheader("Next Runs Preview")
        cron_expr = f"*/{int(interval)} * * * *"
        for t in preview_next_runs(cron_expr):
            st.write(t)

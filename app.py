import sys
from datetime import datetime
from pathlib import Path
import tempfile

import streamlit as st

from xml_builder import (
    TaskConfig,
    build_xml,
    minutes_trigger,
    daily_trigger,
    weekly_trigger,
    monthly_days_trigger,
    monthly_last_day_trigger,
    monthly_nth_dow_trigger,
)
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
        if "找不到指定的文件" in result.stderr or "cannot find" in result.stderr.lower():
            tasks = []
        else:
            st.error(f"Failed to query tasks: {result.stderr}")
            tasks = []
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

    if "trigger_type" not in st.session_state:
        st.session_state.trigger_type = "Every N minutes"

    st.selectbox(
        "Trigger Type",
        [
            "Every N minutes",
            "Every N hours",
            "Daily",
            "Weekly",
            "Monthly",
        ],
        key="trigger_type",
    )

    with st.form("create_task"):
        name = st.text_input("Task Name")
        python_path = st.text_input("Python Path", value=sys.executable)
        script_path = st.text_input("Script Path")
        args = st.text_input("Arguments")
        workdir = st.text_input("Working Directory", value=str(Path.cwd()))

        if st.session_state.trigger_type in ("Every N minutes", "Every N hours"):
            interval = st.number_input("Interval", min_value=1, value=1, key="interval")
        if st.session_state.trigger_type == "Daily":
            daily_time = st.time_input("Time", value=datetime.now().time(), key="daily_time")
            day_interval = st.number_input("Every N days", min_value=1, value=1, key="day_interval")
        if st.session_state.trigger_type == "Weekly":
            weekdays = st.multiselect(
                "Weekdays",
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                key="weekdays",
            )
            week_time = st.time_input("Time", value=datetime.now().time(), key="week_time")
        if st.session_state.trigger_type == "Monthly":
            month_mode = st.selectbox("Mode", ["Specific Days", "Last Day", "Nth Weekday"], key="month_mode")
            month_time = st.time_input("Time", value=datetime.now().time(), key="month_time")
            if month_mode == "Specific Days":
                month_days = st.text_input("Days of Month (e.g. 1,15,31)", key="month_days")
            elif month_mode == "Nth Weekday":
                week_no = st.selectbox("Week", ["First", "Second", "Third", "Fourth", "Last"], key="week_no")
                week_day = st.selectbox(
                    "Day",
                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    key="week_day",
                )
        multiple_policy = st.selectbox(
            "Multiple Instance Policy",
            ["Parallel", "Queue", "IgnoreNew", "StopExisting"],
            key="multi_policy",
        )
        start_when_available = st.checkbox("Start When Available", value=True, key="start_when_available")
        retry_count = st.number_input("Retry Count", min_value=0, value=3, key="retry_count")
        retry_interval = st.number_input("Retry Interval (minutes)", min_value=1, value=5, key="retry_interval")
        submit = st.form_submit_button("Create")

    if submit:
        trigger_type = st.session_state.trigger_type
        now = datetime.now().replace(second=0, microsecond=0)
        cron_expr = None
        if trigger_type in ("Every N minutes", "Every N hours"):
            unit = "hours" if trigger_type.endswith("hours") else "minutes"
            trigger_xml = minutes_trigger(now, int(interval), unit)
            if unit == "hours":
                cron_expr = f"0 */{int(interval)} * * *"
            else:
                cron_expr = f"*/{int(interval)} * * * *"
        elif trigger_type == "Daily":
            trigger_xml = daily_trigger(datetime.combine(now.date(), daily_time), int(day_interval))
            cron_expr = f"{daily_time.minute} {daily_time.hour} */{int(day_interval)} * *"
        elif trigger_type == "Weekly":
            trigger_xml = weekly_trigger(datetime.combine(now.date(), week_time), weekdays)
            if weekdays:
                days = ','.join(day[:3].upper() for day in weekdays)
                cron_expr = f"{week_time.minute} {week_time.hour} * * {days}"
        elif trigger_type == "Monthly":
            start = datetime.combine(now.date(), month_time)
            if month_mode == "Specific Days":
                days = [int(d.strip()) for d in month_days.split(',') if d.strip().isdigit()]
                trigger_xml = monthly_days_trigger(start, days)
                if days:
                    cron_expr = f"{month_time.minute} {month_time.hour} {','.join(str(d) for d in days)} * *"
            elif month_mode == "Last Day":
                trigger_xml = monthly_last_day_trigger(start)
            else:
                trigger_xml = monthly_nth_dow_trigger(start, week_no, week_day)
        else:
            trigger_xml = ""
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
        # Windows `schtasks` requires the XML file to be UTF-16 encoded
        with tempfile.NamedTemporaryFile("w", encoding="utf-16", delete=False, suffix=".xml") as f:
            f.write(xml_content)
            temp_path = Path(f.name)
        res = sc.create_task(temp_path, name)
        if res.returncode == 0:
            st.success("Task created")
        else:
            st.error(res.stderr)
        st.subheader("Next Runs Preview")
        if cron_expr:
            for t in preview_next_runs(cron_expr):
                st.write(t)
        else:
            st.write("Preview not available for this trigger")

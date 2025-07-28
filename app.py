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
            if current and ('TaskName' in current or '任务名' in current):
                tasks.append(current)
                current = {}
            continue
        if ':' in line:
            # 找到最后一个有意义的冒号（排除值部分的冒号）
            # 对于"重复: 每: 0 小时， 2 分钟"这种格式
            if line.count(':') >= 2 and ('重复:' in line or 'Repeat:' in line):
                # 特殊处理重复相关字段
                parts = line.split(':', 2)  # 最多分割成3部分
                if len(parts) >= 3:
                    # "重复: 每: 0 小时， 2 分钟" -> key="重复: 每", value="0 小时， 2 分钟"
                    key = f"{parts[0].strip()}: {parts[1].strip()}"
                    val = parts[2].strip()
                    current[key] = val
                else:
                    # 正常处理
                    key, val = line.split(':', 1)
                    current[key.strip()] = val.strip()
            else:
                # 正常的单冒号字段
                key, val = line.split(':', 1)
                current[key.strip()] = val.strip()
    # 处理最后一个任务
    if current and ('TaskName' in current or '任务名' in current):
        tasks.append(current)
    return tasks


menu = st.sidebar.selectbox("Menu", ["Tasks", "Create Task"])

if menu == "Tasks":
    st.header("Scheduled Tasks")
    
    # 添加调试按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 刷新任务列表"):
            st.rerun()
    with col2:
        if st.button("🔍 调试信息"):
            st.subheader("调试信息")
            
            # 查看所有任务
            all_tasks = sc.list_all_tasks()
            if all_tasks.returncode == 0:
                pytasks_count = all_tasks.stdout.count("\\PyTasks\\")
                st.write(f"系统中包含 'PyTasks' 的任务数量: {pytasks_count}")
                
                if pytasks_count > 0:
                    st.text("找到的 PyTasks 任务:")
                    lines = all_tasks.stdout.split('\n')
                    for line in lines:
                        if '\\PyTasks\\' in line:
                            st.text(line.strip())
                else:
                    st.info("系统中暂无 PyTasks 相关任务")
            else:
                st.error(f"查询所有任务失败: {all_tasks.stderr}")
            
            # 检查 PyTasks 文件夹
            folder_result = sc.query_task_folder()
            if folder_result.returncode == 0:
                st.success("✅ PyTasks 文件夹存在且可访问")
            else:
                # 检查是否真的有任务存在
                if pytasks_count > 0:
                    st.warning("⚠️ PyTasks 任务存在但文件夹检测异常（可能是系统版本差异）")
                else:
                    st.info("ℹ️ PyTasks 文件夹不存在（正常情况，首次使用时会自动创建）")
                    
            st.write(f"**技术详情**:")
            st.write(f"- 文件夹检测返回码: {folder_result.returncode}")
            if folder_result.stderr and folder_result.stderr.strip():
                st.text(f"- 详细信息: {folder_result.stderr.strip()}")
    
    result = sc.query_all_tasks()
    if result.returncode != 0:
        if "找不到指定的文件" in result.stderr or "cannot find" in result.stderr.lower():
            tasks = []
            st.info("暂无任务或任务文件夹不存在")
        else:
            st.error(f"Failed to query tasks: {result.stderr}")
            tasks = []
    else:
        tasks = parse_tasks_list(result.stdout)
        if not tasks:
            st.info("PyTasks 文件夹下暂无任务")

    for idx, task in enumerate(tasks):
        name = task.get("TaskName", "") or task.get("任务名", "")
        short_name = name.split("\\")[-1] if name else f"task_{idx}"
        
        # 创建唯一的基础key，使用索引确保唯一性
        base_key = f"{idx}_{short_name}" if short_name else f"task_{idx}"
        
        # 检查任务状态 - 支持中英文字段名
        status = task.get('Status', '') or task.get('模式', '')
        enabled = status != 'Disabled' and status != '已禁用'
        
        # 根据状态设置标题颜色
        display_name = name if name else f"未知任务_{idx}"
        if enabled:
            title = f"✅ {display_name}"
        else:
            title = f"⚠️ {display_name} (已禁用)"
            
        with st.expander(title):
            # 任务信息 - 每行显示两个字段
            col1, col2 = st.columns(2)
            
            # 第一行：状态和计划状态
            with col1:
                st.write(f"**状态**: {status}")
            with col2:
                task_status = task.get('Scheduled Task State', '') or task.get('计划任务状态', 'N/A')
                st.write(f"**计划状态**: {task_status}")
            
            # 第二行：上次运行和下次运行
            col1, col2 = st.columns(2)
            with col1:
                last_run = task.get('Last Run Time', '') or task.get('上次运行时间', 'N/A')
                st.write(f"**上次运行**: {last_run}")
            with col2:
                next_run = task.get('Next Run Time', '') or task.get('下次运行时间', 'N/A')
                st.write(f"**下次运行**: {next_run}")
            
            # 第三行：上次结果和计划类型
            col1, col2 = st.columns(2)
            with col1:
                last_result = task.get('Last Result', '') or task.get('上次结果', 'N/A')
                st.write(f"**上次结果**: {last_result}")
            with col2:
                schedule_type = task.get('Schedule Type', '') or task.get('计划类型', 'N/A')
                st.write(f"**计划类型**: {schedule_type}")
            
            # 第四行：开始时间和开始日期
            col1, col2 = st.columns(2)
            with col1:
                start_time = task.get('Start Time', '') or task.get('开始时间', 'N/A')
                st.write(f"**开始时间**: {start_time}")
            with col2:
                start_date = task.get('Start Date', '') or task.get('开始日期', 'N/A')
                st.write(f"**开始日期**: {start_date}")
            
            # 第五行：重复间隔和执行命令
            col1, col2 = st.columns(2)
            with col1:
                repeat_every = task.get('Repeat: Every', '') or task.get('重复: 每', 'N/A')
                st.write(f"**重复间隔**: {repeat_every}")
            with col2:
                task_to_run = task.get('Task To Run', '') or task.get('要运行的任务', 'N/A')
                st.write(f"**执行命令**: {task_to_run}")
            
            # 第六行：工作目录和运行用户
            col1, col2 = st.columns(2)
            with col1:
                start_in = task.get('Start In', '') or task.get('起始于', 'N/A')
                st.write(f"**工作目录**: {start_in}")
            with col2:
                run_as_user = task.get('Run As User', '') or task.get('作为用户运行', 'N/A')
                st.write(f"**运行用户**: {run_as_user}")
            
            # 第七行：创建者
            col1, col2 = st.columns(2)
            with col1:
                author = task.get('Author', '') or task.get('创建者', 'N/A')
                st.write(f"**创建者**: {author}")
            with col2:
                st.write("")  # 空白占位
            
            # 操作按钮
            col1, col2, col3 = st.columns(3)
            
            # Run 按钮 - 如果任务被禁用则显示提示
            if enabled:
                if col1.button("▶️ 运行", key=f"run_{base_key}"):
                    res = sc.run_task(short_name)
                    if res.returncode == 0:
                        st.success("✅ 任务已启动")
                    else:
                        st.error(f"❌ 启动失败: {res.stderr}")
            else:
                if col1.button("▶️ 运行 (需先启用)", key=f"run_{base_key}", disabled=True):
                    st.warning("⚠️ 无法运行已禁用的任务，请先启用该任务")
            
            # Enable/Disable 按钮
            toggle_text = "⏸️ 禁用" if enabled else "▶️ 启用"
            if col2.button(toggle_text, key=f"toggle_{base_key}"):
                res = sc.change_enable(short_name, not enabled)
                if res.returncode == 0:
                    action = "禁用" if enabled else "启用"
                    st.success(f"✅ 任务已{action}")
                    st.rerun()  # 刷新界面以显示新状态
                else:
                    st.error(f"❌ 操作失败: {res.stderr}")
            
            # Delete 按钮
            if col3.button("🗑️ 删除", key=f"del_{base_key}"):
                res = sc.delete_task(short_name)
                if res.returncode == 0:
                    st.success("✅ 任务已删除")
                    st.rerun()  # 刷新界面
                else:
                    st.error(f"❌ 删除失败: {res.stderr}")

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
        # 检查任务名是否为空
        if not name.strip():
            st.error("❌ 任务名不能为空")
        # 检查任务是否已存在
        elif sc.task_exists(name.strip()):
            st.error(f"❌ 任务 '{name.strip()}' 已存在")
            st.info("请使用不同的任务名称，或者先到任务列表中删除现有任务")
        else:
            # 创建新任务
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
                    cron_expr = f"{month_time.minute} {month_time.hour} L * *"
                else:
                    trigger_xml = monthly_nth_dow_trigger(start, week_no, week_day)
                    cron_expr = f"{month_time.minute} {month_time.hour} * * {week_day}#{week_no}"
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
            
            res = sc.create_task(temp_path, name, False)
            
            # 清理临时文件
            try:
                temp_path.unlink()
            except:
                pass
                
            if res.returncode == 0:
                st.success(f"任务 '{name}' 创建成功！")
                st.info("请点击上方的 '刷新任务列表' 按钮查看新创建的任务。")
                
                # 预览功能 - 只在成功时显示
                st.subheader("Next Runs Preview")
                if cron_expr:
                    for t in preview_next_runs(cron_expr):
                        st.write(t)
                else:
                    st.write("Preview not available for this trigger")
            else:
                st.error(f"任务创建失败: {res.stderr}")

from dataclasses import dataclass
from datetime import datetime, time
from pathlib import Path
from typing import Optional, List

from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).parent / 'templates'


env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

MONTHS_XML = """<Months><January/><February/><March/><April/><May/><June/><July/><August/><September/><October/><November/><December/></Months>"""


@dataclass
class TaskConfig:
    name: str
    python_path: str
    script_path: str
    args: str = ''
    workdir: str = ''
    multiple_instances_policy: str = 'Parallel'
    start_when_available: str = 'true'
    retry_interval: str = 'PT5M'
    retry_count: int = 3
    trigger_xml: str = ''
    author: str = 'TaskScheduler'


def build_xml(config: TaskConfig) -> str:
    """Render the task XML using the template."""
    template = env.get_template('task_template.xml')
    xml = template.render(
        registration_date=datetime.now().isoformat(),
        author=config.author,
        triggers=config.trigger_xml,
        python_path=config.python_path,
        script_path=config.script_path,
        args=config.args,
        workdir=config.workdir,
        multiple_instances_policy=config.multiple_instances_policy,
        start_when_available=config.start_when_available,
        retry_interval=config.retry_interval,
        retry_count=config.retry_count,
    )
    return xml


def minutes_trigger(start: datetime, every: int, unit: str) -> str:
    interval = f"PT{every}{'H' if unit == 'hours' else 'M'}"
    return f"""<TimeTrigger>
  <StartBoundary>{start.isoformat()}</StartBoundary>
  <Enabled>true</Enabled>
  <Repetition>
    <Interval>{interval}</Interval>
  </Repetition>
</TimeTrigger>"""


def daily_trigger(start: datetime, days: int) -> str:
    return f"""<CalendarTrigger>
  <StartBoundary>{start.isoformat()}</StartBoundary>
  <ScheduleByDay>
    <DaysInterval>{days}</DaysInterval>
  </ScheduleByDay>
</CalendarTrigger>"""


def weekly_trigger(start: datetime, weekdays: List[str]) -> str:
    days_xml = ''.join(f'<{day}/>' for day in weekdays)
    return f"""<CalendarTrigger>
  <StartBoundary>{start.isoformat()}</StartBoundary>
  <ScheduleByWeek>
    <DaysOfWeek>{days_xml}</DaysOfWeek>
    <WeeksInterval>1</WeeksInterval>
  </ScheduleByWeek>
</CalendarTrigger>"""


def monthly_days_trigger(start: datetime, days: List[int]) -> str:
    days_xml = ''.join(f'<Day>{d}</Day>' for d in days)
    return f"""<CalendarTrigger>
  <StartBoundary>{start.isoformat()}</StartBoundary>
  <ScheduleByMonth>
    <DaysOfMonth>{days_xml}</DaysOfMonth>
    {MONTHS_XML}
  </ScheduleByMonth>
</CalendarTrigger>"""


def monthly_last_day_trigger(start: datetime) -> str:
    return f"""<CalendarTrigger>
  <StartBoundary>{start.isoformat()}</StartBoundary>
  <ScheduleByMonth>
    <DaysOfMonth><LastDay/></DaysOfMonth>
    {MONTHS_XML}
  </ScheduleByMonth>
</CalendarTrigger>"""


def monthly_nth_dow_trigger(start: datetime, week: str, day: str) -> str:
    return f"""<CalendarTrigger>
  <StartBoundary>{start.isoformat()}</StartBoundary>
  <ScheduleByMonthDayOfWeek>
    <DaysOfWeek><{day}/></DaysOfWeek>
    <Weeks><{week}/></Weeks>
    {MONTHS_XML}
  </ScheduleByMonthDayOfWeek>
</CalendarTrigger>"""

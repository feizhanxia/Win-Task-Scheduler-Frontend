from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).parent / 'templates'


env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


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

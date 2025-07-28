import subprocess
from pathlib import Path
from typing import List, Optional


SCHTASKS = 'schtasks'


def run_command(args: List[str]) -> subprocess.CompletedProcess:
    """Run a schtasks command and return the process result."""
    return subprocess.run(args, capture_output=True, text=True, shell=True)


def create_task(xml_path: Path, task_name: str) -> subprocess.CompletedProcess:
    return run_command([SCHTASKS, '/Create', '/XML', str(xml_path), '/TN', f"\\PyTasks\\{task_name}", '/F'])


def delete_task(task_name: str) -> subprocess.CompletedProcess:
    return run_command([SCHTASKS, '/Delete', '/TN', f"\\PyTasks\\{task_name}", '/F'])


def run_task(task_name: str) -> subprocess.CompletedProcess:
    return run_command([SCHTASKS, '/Run', '/TN', f"\\PyTasks\\{task_name}"])


def query_task(task_name: str) -> subprocess.CompletedProcess:
    return run_command([SCHTASKS, '/Query', '/TN', f"\\PyTasks\\{task_name}", '/V', '/FO', 'LIST'])


def query_task_xml(task_name: str) -> subprocess.CompletedProcess:
    return run_command([SCHTASKS, '/Query', '/TN', f"\\PyTasks\\{task_name}", '/XML'])


def query_all_tasks() -> subprocess.CompletedProcess:
    return run_command([SCHTASKS, '/Query', '/TN', '\\PyTasks\\*', '/FO', 'LIST'])


def change_enable(task_name: str, enable: bool) -> subprocess.CompletedProcess:
    flag = '/ENABLE' if enable else '/DISABLE'
    return run_command([SCHTASKS, flag, '/TN', f"\\PyTasks\\{task_name}"])

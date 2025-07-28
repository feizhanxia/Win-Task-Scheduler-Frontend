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
    # 先尝试查询 PyTasks 文件夹下的任务
    result = run_command([SCHTASKS, '/Query', '/TN', '\\PyTasks\\*', '/FO', 'LIST'])
    
    # 如果没有找到任务或出错，尝试查询所有任务然后过滤
    if result.returncode != 0 or not result.stdout.strip():
        # 查询所有任务并过滤出 PyTasks 相关的
        all_result = run_command([SCHTASKS, '/Query', '/FO', 'LIST'])
        if all_result.returncode == 0:
            # 过滤出包含 PyTasks 的任务
            lines = all_result.stdout.splitlines()
            filtered_lines = []
            include_block = False
            current_block = []
            
            for line in lines:
                if line.strip().startswith('TaskName:'):
                    if current_block and include_block:
                        filtered_lines.extend(current_block)
                        filtered_lines.append('')  # 添加空行分隔
                    current_block = [line]
                    include_block = '\\PyTasks\\' in line
                elif current_block:
                    current_block.append(line)
                elif not line.strip():  # 空行
                    if current_block and include_block:
                        filtered_lines.extend(current_block)
                        filtered_lines.append('')
                    current_block = []
                    include_block = False
            
            # 处理最后一个块
            if current_block and include_block:
                filtered_lines.extend(current_block)
            
            # 创建新的结果对象
            if filtered_lines:
                result = subprocess.CompletedProcess(
                    args=all_result.args,
                    returncode=0,
                    stdout='\n'.join(filtered_lines),
                    stderr=''
                )
    
    return result


def change_enable(task_name: str, enable: bool) -> subprocess.CompletedProcess:
    flag = '/ENABLE' if enable else '/DISABLE'
    return run_command([SCHTASKS, flag, '/TN', f"\\PyTasks\\{task_name}"])


def list_all_tasks() -> subprocess.CompletedProcess:
    """列出所有任务，用于调试"""
    return run_command([SCHTASKS, '/Query', '/FO', 'LIST'])


def query_task_folder() -> subprocess.CompletedProcess:
    """查询 PyTasks 文件夹是否存在"""
    return run_command([SCHTASKS, '/Query', '/TN', '\\PyTasks', '/FO', 'LIST'])

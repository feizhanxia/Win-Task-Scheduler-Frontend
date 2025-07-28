import subprocess
from pathlib import Path
from typing import List, Optional


SCHTASKS = 'schtasks'


def run_command(args: List[str]) -> subprocess.CompletedProcess:
    """Run a schtasks command and return the process result."""
    return subprocess.run(args, capture_output=True, text=True, shell=True)


def create_task(xml_path: Path, task_name: str, force_overwrite: bool = False) -> subprocess.CompletedProcess:
    """创建任务，可选择是否强制覆盖同名任务"""
    if force_overwrite:
        return run_command([SCHTASKS, '/Create', '/XML', str(xml_path), '/TN', f"\\PyTasks\\{task_name}", '/F'])
    else:
        # 不使用 /F 参数，如果任务存在会报错
        return run_command([SCHTASKS, '/Create', '/XML', str(xml_path), '/TN', f"\\PyTasks\\{task_name}"])


def task_exists(task_name: str) -> bool:
    """检查任务是否存在"""
    result = run_command([SCHTASKS, '/Query', '/TN', f"\\PyTasks\\{task_name}", '/FO', 'LIST'])
    return result.returncode == 0


def delete_task(task_name: str) -> subprocess.CompletedProcess:
    return run_command([SCHTASKS, '/Delete', '/TN', f"\\PyTasks\\{task_name}", '/F'])


def run_task(task_name: str) -> subprocess.CompletedProcess:
    return run_command([SCHTASKS, '/Run', '/TN', f"\\PyTasks\\{task_name}"])


def query_task(task_name: str) -> subprocess.CompletedProcess:
    return run_command([SCHTASKS, '/Query', '/TN', f"\\PyTasks\\{task_name}", '/V', '/FO', 'LIST'])


def query_task_xml(task_name: str) -> subprocess.CompletedProcess:
    return run_command([SCHTASKS, '/Query', '/TN', f"\\PyTasks\\{task_name}", '/XML'])


def query_all_tasks() -> subprocess.CompletedProcess:
    # 先简单查询所有任务，过滤出 PyTasks 相关的，然后再逐个获取详细信息
    all_result = run_command([SCHTASKS, '/Query', '/FO', 'LIST'])
    if all_result.returncode == 0 and all_result.stdout:
        # 找出所有PyTasks任务名
        lines = all_result.stdout.splitlines()
        pytask_names = []
        
        for line in lines:
            if line.strip().startswith('TaskName:') or line.strip().startswith('任务名:'):
                if '\\PyTasks\\' in line:
                    # 提取任务名
                    task_name = line.split(':', 1)[1].strip()
                    short_name = task_name.split('\\')[-1]
                    pytask_names.append(short_name)
        
        # 如果没有找到PyTasks任务，返回空结果
        if not pytask_names:
            result = subprocess.CompletedProcess(
                args=all_result.args,
                returncode=0,
                stdout='',
                stderr=''
            )
            return result
        
        # 逐个查询每个PyTasks任务的详细信息
        all_detailed_output = []
        for task_name in pytask_names:
            detailed_result = run_command([SCHTASKS, '/Query', '/TN', f"\\PyTasks\\{task_name}", '/V', '/FO', 'LIST'])
            if detailed_result.returncode == 0 and detailed_result.stdout:
                all_detailed_output.append(detailed_result.stdout.strip())
        
        # 合并所有详细输出
        if all_detailed_output:
            combined_output = '\n\n'.join(all_detailed_output)
            result = subprocess.CompletedProcess(
                args=all_result.args,
                returncode=0,
                stdout=combined_output,
                stderr=''
            )
        else:
            result = subprocess.CompletedProcess(
                args=all_result.args,
                returncode=0,
                stdout='',
                stderr=''
            )
    else:
        # 如果连查询所有任务都失败了，返回原始错误
        result = all_result
    
    return result


def change_enable(task_name: str, enable: bool) -> subprocess.CompletedProcess:
    flag = '/ENABLE' if enable else '/DISABLE'
    return run_command([SCHTASKS, '/Change', '/TN', f"\\PyTasks\\{task_name}", flag])


def list_all_tasks() -> subprocess.CompletedProcess:
    """列出所有任务，用于调试"""
    return run_command([SCHTASKS, '/Query', '/FO', 'LIST'])


def query_task_folder() -> subprocess.CompletedProcess:
    """查询 PyTasks 文件夹是否存在"""
    # 通过查询所有任务来检查是否有 PyTasks 文件夹
    all_result = run_command([SCHTASKS, '/Query', '/FO', 'LIST'])
    if all_result.returncode == 0 and all_result.stdout:
        # 检查输出中是否包含 PyTasks 文件夹标识
        output_lines = all_result.stdout.splitlines()
        has_pytasks_folder = False
        
        for line in output_lines:
            # 检查是否有 "文件夹: \PyTasks" 这样的行
            if ('文件夹:' in line and '\\PyTasks' in line) or ('Folder:' in line and '\\PyTasks' in line):
                has_pytasks_folder = True
                break
            # 或者检查是否有 PyTasks 任务（间接证明文件夹存在）
            if '\\PyTasks\\' in line:
                has_pytasks_folder = True
                break
        
        if has_pytasks_folder:
            # 创建成功的结果
            result = subprocess.CompletedProcess(
                args=all_result.args,
                returncode=0,
                stdout='PyTasks folder exists',
                stderr=''
            )
        else:
            # 创建失败的结果（文件夹不存在）
            result = subprocess.CompletedProcess(
                args=all_result.args,
                returncode=1,
                stdout='',
                stderr='PyTasks folder does not exist'
            )
    else:
        # 如果查询全部任务都失败了，返回原始错误
        result = all_result
    
    return result

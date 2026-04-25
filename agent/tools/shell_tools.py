"""
NexAgent - Shell 工具
打开应用程序、执行系统命令等
"""
import subprocess
import os
from pathlib import Path
from langchain_core.tools import tool


@tool
def open_vscode(directory: str = ".") -> str:
    """
    打开 VS Code

    Args:
        directory: 要打开的目录路径（默认当前目录）

    Returns:
        操作结果
    """
    try:
        path = Path(directory).resolve()
        if not path.exists():
            return f"目录不存在: {directory}"

        # 尝试使用 code 命令
        subprocess.Popen(["code", str(path)], shell=True, detached=True)
        return f"正在打开 VS Code: {path}"
    except Exception as e:
        return f"打开 VS Code 失败: {str(e)}"


@tool
def open_pycharm(directory: str = ".") -> str:
    """
    打开 PyCharm

    Args:
        directory: 要打开的目录路径（默认当前目录）

    Returns:
        操作结果
    """
    try:
        path = Path(directory).resolve()
        if not path.exists():
            return f"目录不存在: {directory}"

        # 常见 PyCharm 安装路径
        pycharm_paths = [
            r"C:\\Program Files\\JetBrains\\PyCharm\\bin\\pycharm64.exe",
            r"C:\\Program Files (x86)\\JetBrains\\PyCharm\\bin\\pycharm64.exe",
            os.path.expanduser(r"~\\AppData\\Local\\JetBrains\\Toolbox\\apps\\PyCharm\\*\\bin\\pycharm64.exe"),
        ]

        for pycharm_path in pycharm_paths:
            if "*" in pycharm_path:
                import glob
                matches = glob.glob(pycharm_path)
                if matches:
                    pycharm_path = matches[-1]
                    subprocess.Popen([pycharm_path, str(path)], shell=True, detached=True)
                    return f"正在打开 PyCharm: {path}"
            elif Path(pycharm_path).exists():
                subprocess.Popen([pycharm_path, str(path)], shell=True, detached=True)
                return f"正在打开 PyCharm: {path}"

        return "未找到 PyCharm，请确认已安装 PyCharm"
    except Exception as e:
        return f"打开 PyCharm 失败: {str(e)}"


@tool
def open_application(app_path: str) -> str:
    """
    打开任意应用程序

    Args:
        app_path: 应用程序的路径（.exe 文件路径）

    Returns:
        操作结果
    """
    try:
        path = Path(app_path).resolve()
        if not path.exists():
            return f"应用程序不存在: {app_path}"

        subprocess.Popen([str(path)], shell=True, detached=True)
        return f"正在打开: {app_path}"
    except Exception as e:
        return f"打开应用程序失败: {str(e)}"


@tool
def open_in_explorer(path: str = ".") -> str:
    """
    在文件资源管理器中打开目录

    Args:
        path: 目录路径（默认当前目录）

    Returns:
        操作结果
    """
    try:
        full_path = Path(path).resolve()
        if not full_path.exists():
            return f"路径不存在: {path}"

        subprocess.Popen(f"explorer {full_path}", shell=True)
        return f"已在文件资源管理器中打开: {full_path}"
    except Exception as e:
        return f"打开资源管理器失败: {str(e)}"


@tool
def get_system_info() -> str:
    """
    获取系统基本信息

    Returns:
        系统信息
    """
    import platform
    import os

    info = [
        f"系统: {platform.system()}",
        f"版本: {platform.version()}",
        f"架构: {platform.machine()}",
        f"处理器: {platform.processor()}",
        f"Python 版本: {platform.python_version()}",
        f"当前目录: {os.getcwd()}",
        f"用户目录: {os.path.expanduser('~')}",
    ]

    return "\n".join(info)


def get_shell_tools() -> list:
    """获取所有 Shell 工具"""
    return [
        open_vscode,
        open_pycharm,
        open_application,
        open_in_explorer,
        get_system_info,
    ]

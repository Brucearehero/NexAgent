"""
NexAgent - 代码执行工具
"""
import subprocess
import sys
import io
from contextlib import redirect_stdout, redirect_stderr
from langchain_core.tools import tool


@tool
def execute_python(code: str) -> str:
    """
    执行 Python 代码

    Args:
        code: Python 代码（必须是完整的、可执行的代码块）

    Returns:
        代码执行结果或错误信息
    """
    output = io.StringIO()
    errors = io.StringIO()

    try:
        with redirect_stdout(output), redirect_stderr(errors):
            exec(code, {"__name__": "__main__"})

        result = output.getvalue()
        error = errors.getvalue()

        if error:
            return f"执行结果:\n{result}\n\n警告/错误:\n{error}"
        return f"执行结果:\n{result}" if result else "代码执行完成，无输出"
    except SyntaxError as e:
        return f"语法错误: {str(e)}"
    except Exception as e:
        return f"执行错误: {type(e).__name__}: {str(e)}"


@tool
def execute_shell(command: str) -> str:
    """
    执行 Shell / PowerShell 命令

    Args:
        command: 要执行的命令

    Returns:
        命令执行结果
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        output = []
        if result.stdout:
            output.append(f"标准输出:\n{result.stdout}")
        if result.stderr:
            output.append(f"标准错误:\n{result.stderr}")
        if result.returncode != 0:
            output.append(f"退出码: {result.returncode}")

        if not output:
            return "命令执行完成，无输出"

        return "\n".join(output)
    except Exception as e:
        return f"命令执行失败: {str(e)}"


@tool
def check_python_version() -> str:
    """
    检查当前 Python 环境版本

    Returns:
        Python 版本信息
    """
    version = sys.version
    executable = sys.executable
    return f"Python 版本: {version}\n可执行文件: {executable}"


def get_code_tools() -> list:
    """获取所有代码执行工具"""
    return [
        execute_python,
        execute_shell,
        check_python_version,
    ]

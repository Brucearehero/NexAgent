"""
NexAgent - 代码执行工具
"""
import subprocess
import sys
import io
import time
from contextlib import redirect_stdout, redirect_stderr
from langchain_core.tools import tool
from agent.core import check_tool_stop, AgentStoppedException


@tool
def execute_python(code: str) -> str:
    """
    执行 Python 代码

    Args:
        code: Python 代码（必须是完整的、可执行的代码块）

    Returns:
        代码执行结果或错误信息
    """
    check_tool_stop()
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
    except AgentStoppedException:
        return "[已停止] 用户请求中断了执行。"
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
    check_tool_stop()
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        # 轮询检查停止标志
        while process.poll() is None:
            check_tool_stop()
            time.sleep(0.2)

        stdout, stderr = process.communicate()

        output = []
        if stdout:
            output.append(f"标准输出:\n{stdout}")
        if stderr:
            output.append(f"标准错误:\n{stderr}")
        if process.returncode != 0:
            output.append(f"退出码: {process.returncode}")

        if not output:
            return "命令执行完成，无输出"

        return "\n".join(output)
    except AgentStoppedException:
        try:
            process.kill()
        except Exception:
            pass
        return "[已停止] 用户请求中断了执行。"
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

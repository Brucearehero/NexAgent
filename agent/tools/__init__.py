"""
NexAgent - 工具集
"""
from .file_tools import get_file_tools
from .code_tools import get_code_tools
from .shell_tools import get_shell_tools
from .browser_tools import get_browser_tools
from .http_tools import get_http_tools


def get_all_tools() -> list:
    """获取所有工具"""
    tools = []
    tools.extend(get_file_tools())
    tools.extend(get_code_tools())
    tools.extend(get_shell_tools())
    tools.extend(get_browser_tools())
    tools.extend(get_http_tools())
    return tools

"""
NexAgent - 文件读写工具
"""
import os
import json
from pathlib import Path
from typing import Optional, List
from langchain_core.tools import tool


@tool
def read_file(file_path: str) -> str:
    """
    读取文件内容

    Args:
        file_path: 文件路径（绝对路径或相对于当前目录的路径）

    Returns:
        文件内容字符串
    """
    path = Path(file_path).resolve()

    if not path.exists():
        return f"文件不存在: {file_path}"

    if path.is_dir():
        return f"这是一个目录，不是文件: {file_path}"

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return f"文件内容 ({file_path}):\n{'-' * 40}\n{content}\n{'-' * 40}"
    except Exception as e:
        return f"读取文件失败: {str(e)}"


@tool
def write_file(file_path: str, content: str, append: bool = False) -> str:
    """
    写入内容到文件

    Args:
        file_path: 文件路径
        content: 要写入的内容
        append: 是否追加模式（默认覆盖）

    Returns:
        操作结果
    """
    path = Path(file_path).resolve()

    try:
        # 确保父目录存在
        path.parent.mkdir(parents=True, exist_ok=True)

        mode = "a" if append else "w"
        with open(path, mode, encoding="utf-8") as f:
            f.write(content)

        action = "追加到" if append else "写入到"
        return f"成功 {action}文件: {file_path}"
    except Exception as e:
        return f"写入文件失败: {str(e)}"


@tool
def list_directory(directory_path: str = ".") -> str:
    """
    列出目录内容

    Args:
        directory_path: 目录路径（默认当前目录）

    Returns:
        目录内容列表
    """
    path = Path(directory_path).resolve()

    if not path.exists():
        return f"目录不存在: {directory_path}"

    if not path.is_dir():
        return f"这不是一个目录: {directory_path}"

    try:
        items = []
        for item in sorted(path.iterdir()):
            item_type = "📁 目录" if item.is_dir() else "📄 文件"
            size = ""
            if item.is_file():
                size = f" ({item.stat().st_size} bytes)"
            items.append(f"  {item_type}: {item.name}{size}")

        result = f"目录内容 ({directory_path}):\n" + "\n".join(items)
        return result if items else f"目录为空: {directory_path}"
    except Exception as e:
        return f"列出目录失败: {str(e)}"


@tool
def delete_file(file_path: str) -> str:
    """
    删除文件或目录

    Args:
        file_path: 文件或目录路径

    Returns:
        操作结果
    """
    path = Path(file_path).resolve()

    if not path.exists():
        return f"路径不存在: {file_path}"

    try:
        if path.is_dir():
            import shutil
            shutil.rmtree(path)
            return f"已删除目录: {file_path}"
        else:
            path.unlink()
            return f"已删除文件: {file_path}"
    except Exception as e:
        return f"删除失败: {str(e)}"


@tool
def create_directory(directory_path: str) -> str:
    """
    创建目录

    Args:
        directory_path: 目录路径

    Returns:
        操作结果
    """
    path = Path(directory_path).resolve()

    try:
        path.mkdir(parents=True, exist_ok=True)
        return f"已创建目录: {directory_path}"
    except Exception as e:
        return f"创建目录失败: {str(e)}"


@tool
def read_json(file_path: str) -> str:
    """
    读取 JSON 文件

    Args:
        file_path: JSON 文件路径

    Returns:
        格式化后的 JSON 内容
    """
    path = Path(file_path).resolve()

    if not path.exists():
        return f"文件不存在: {file_path}"

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"读取 JSON 失败: {str(e)}"


@tool
def write_json(file_path: str, data: str, indent: int = 2) -> str:
    """
    写入 JSON 数据到文件

    Args:
        file_path: 文件路径
        data: JSON 字符串（必须是有效的 JSON）
        indent: 缩进空格数

    Returns:
        操作结果
    """
    path = Path(file_path).resolve()

    try:
        json_data = json.loads(data)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=indent)
        return f"成功写入 JSON 到: {file_path}"
    except json.JSONDecodeError as e:
        return f"无效的 JSON 格式: {str(e)}"
    except Exception as e:
        return f"写入 JSON 失败: {str(e)}"


def get_file_tools() -> list:
    """获取所有文件工具"""
    return [
        read_file,
        write_file,
        list_directory,
        delete_file,
        create_directory,
        read_json,
        write_json,
    ]

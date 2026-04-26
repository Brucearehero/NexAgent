"""
NexAgent - HTTP 请求工具
调用外部 API
"""
import httpx
import json
from typing import Optional
from langchain_core.tools import tool
from agent.core import check_tool_stop, AgentStoppedException


@tool
def http_get(url: str, headers: Optional[str] = None, params: Optional[str] = None) -> str:
    """
    发送 GET 请求

    Args:
        url: 请求 URL
        headers: 请求头（JSON 格式字符串，可选）
        params: 查询参数（JSON 格式字符串，可选）

    Returns:
        响应内容
    """
    check_tool_stop()
    try:
        kwargs = {"timeout": 30.0}

        if headers:
            kwargs["headers"] = json.loads(headers)
        if params:
            kwargs["params"] = json.loads(params)

        response = httpx.get(url, **kwargs)
        response.raise_for_status()

        # 尝试解析 JSON
        try:
            data = response.json()
            return json.dumps(data, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            return f"响应状态: {response.status_code}\n\n{response.text[:2000]}"

    except AgentStoppedException:
        return "[已停止] 用户请求中断了执行。"
    except httpx.TimeoutException:
        return "请求超时"
    except httpx.HTTPStatusError as e:
        return f"HTTP 错误 {e.response.status_code}: {str(e)}"
    except Exception as e:
        return f"请求失败: {str(e)}"


@tool
def http_post(
    url: str,
    body: str,
    headers: Optional[str] = None
) -> str:
    """
    发送 POST 请求

    Args:
        url: 请求 URL
        body: 请求体（JSON 格式字符串）
        headers: 请求头（JSON 格式字符串，可选）

    Returns:
        响应内容
    """
    check_tool_stop()
    try:
        kwargs = {
            "timeout": 30.0,
            "content": body,
            "headers": {"Content-Type": "application/json"},
        }

        if headers:
            extra_headers = json.loads(headers)
            kwargs["headers"].update(extra_headers)

        response = httpx.post(url, **kwargs)
        response.raise_for_status()

        try:
            data = response.json()
            return json.dumps(data, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            return f"响应状态: {response.status_code}\n\n{response.text[:2000]}"

    except AgentStoppedException:
        return "[已停止] 用户请求中断了执行。"
    except httpx.TimeoutException:
        return "请求超时"
    except httpx.HTTPStatusError as e:
        return f"HTTP 错误 {e.response.status_code}: {str(e)}"
    except Exception as e:
        return f"请求失败: {str(e)}"


@tool
def http_delete(url: str, headers: Optional[str] = None) -> str:
    """
    发送 DELETE 请求

    Args:
        url: 请求 URL
        headers: 请求头（JSON 格式字符串，可选）

    Returns:
        响应内容
    """
    check_tool_stop()
    try:
        kwargs = {"timeout": 30.0}

        if headers:
            kwargs["headers"] = json.loads(headers)

        response = httpx.delete(url, **kwargs)
        response.raise_for_status()

        try:
            data = response.json()
            return json.dumps(data, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            return f"响应状态: {response.status_code}\n\n{response.text[:2000]}"

    except AgentStoppedException:
        return "[已停止] 用户请求中断了执行。"
    except httpx.TimeoutException:
        return "请求超时"
    except httpx.HTTPStatusError as e:
        return f"HTTP 错误 {e.response.status_code}: {str(e)}"
    except Exception as e:
        return f"请求失败: {str(e)}"


@tool
def web_search(query: str, num_results: int = 5) -> str:
    """
    网页搜索（使用 DuckDuckGo）

    Args:
        query: 搜索关键词
        num_results: 返回结果数量（默认 5）

    Returns:
        搜索结果
    """
    check_tool_stop()
    try:
        from duckduckgo_search import DDGS

        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=num_results):
                check_tool_stop()
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")[:200],
                })

        if not results:
            return f"未找到与 '{query}' 相关的搜索结果"

        output = [f"搜索结果 ({query}):\n"]
        for i, r in enumerate(results, 1):
            output.append(f"{i}. {r['title']}")
            output.append(f"   URL: {r['url']}")
            output.append(f"   {r['snippet']}")
            output.append("")

        return "\n".join(output)

    except AgentStoppedException:
        return "[已停止] 用户请求中断了执行。"
    except ImportError:
        return "duckduckgo-search 未安装，请运行: pip install duckduckgo-search"
    except Exception as e:
        return f"搜索失败: {str(e)}"


def get_http_tools() -> list:
    """获取所有 HTTP 工具"""
    return [
        http_get,
        http_post,
        http_delete,
        web_search,
    ]

"""
NexAgent - 浏览器操作工具
使用 Playwright 控制浏览器（同步版本，浏览器实例复用）
浏览器打开后保持常驻，支持在同一个页面持续操作
"""
import json
import yaml
import time
from pathlib import Path
from langchain_core.tools import tool
from agent.core import check_tool_stop, AgentStoppedException

CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"

# 全局浏览器实例（进程内单例，浏览器打开后保持常驻）
_playwright_instance = None
_browser = None
_page = None


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_browser_config() -> dict:
    return load_config().get("browser", {})


def _ensure_browser():
    """
    确保浏览器已启动，返回 (playwright, browser, page) 元组。
    如果浏览器已启动则复用。
    """
    global _playwright_instance, _browser, _page

    if _browser is None or not _browser.is_connected():
        # 重新初始化
        _playwright_instance = None
        _browser = None
        _page = None

        try:
            from playwright.sync_api import sync_playwright
            _playwright_instance = sync_playwright().start()
        except ImportError:
            raise RuntimeError(
                "Playwright 未安装，请运行: pip install playwright && playwright install chromium"
            )

        cfg = get_browser_config()
        headless = cfg.get("headless", False)
        slow_mo = cfg.get("slow_mo", 100)

        _browser = _playwright_instance.chromium.launch(headless=headless, slow_mo=slow_mo)

    if _page is None:
        context = _browser.new_context()
        _page = context.new_page()

    return _playwright_instance, _browser, _page


def _close_browser():
    """关闭浏览器实例（手动调用时使用）"""
    global _playwright_instance, _browser, _page
    if _browser:
        try:
            _browser.close()
        except Exception:
            pass
    if _playwright_instance:
        try:
            _playwright_instance.stop()
        except Exception:
            pass
    _playwright_instance = None
    _browser = None
    _page = None


@tool
def browser_navigate(url: str) -> str:
    """
    打开或切换到指定 URL。如果浏览器已打开，则在当前页面导航。
    支持自动补全常见网站：b站/bilibili → https://www.bilibili.com，百度 → https://www.baidu.com 等。
    如果用户没有指定具体网址，先询问用户要打开哪个网站。

    Args:
        url: 目标网址或网站简称

    Returns:
        操作结果
    """
    # 兼容处理：LLM 有时会传 JSON 字符串 {"url": "..."}
    if isinstance(url, str):
        try:
            parsed = json.loads(url)
            if isinstance(parsed, dict) and "url" in parsed:
                url = parsed["url"]
        except (json.JSONDecodeError, TypeError):
            pass

    # 自动补全常见网站
    site_map = {
        "b站": "https://www.bilibili.com",
        "bilibili": "https://www.bilibili.com",
        "百度": "https://www.baidu.com",
        "baidu": "https://www.baidu.com",
        "知乎": "https://www.zhihu.com",
        "zhihu": "https://www.zhihu.com",
        "微博": "https://weibo.com",
        "github": "https://github.com",
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
    }
    url_stripped = url.strip()
    for key, full_url in site_map.items():
        if key in url_stripped.lower():
            url = full_url
            break
    else:
        # 不是常见网站，尝试补全协议头
        if not url_stripped.startswith(("http://", "https://")):
            if "." in url_stripped and " " not in url_stripped:
                url = "https://" + url_stripped
            else:
                return f"无法识别网址: {url}。请提供完整的网址（以 http:// 或 https:// 开头）"

    try:
        pw, browser, page = _ensure_browser()
        check_tool_stop()
        page.goto(url, timeout=30000)
        check_tool_stop()
        page.wait_for_load_state("networkidle")
        check_tool_stop()
        page.wait_for_timeout(1500)
        title = page.title()
        return f"已导航到: {url}\n页面标题: {title}\n浏览器将保持打开状态以便后续操作"
    except AgentStoppedException:
        return "[已停止] 用户请求中断了执行。"
    except RuntimeError as e:
        return f"浏览器启动失败: {e}"
    except Exception as e:
        _close_browser()
        return f"导航失败: {type(e).__name__}: {e}"


@tool
def browser_screenshot(file_name: str = "screenshot.png") -> str:
    """
    对当前页面截图

    Args:
        file_name: 保存的文件名

    Returns:
        截图保存结果
    """
    try:
        pw, browser, page = _ensure_browser()
        screenshot_path = Path(file_name).resolve()
        page.screenshot(path=str(screenshot_path), full_page=False)
        return f"截图已保存到: {screenshot_path}"
    except RuntimeError as e:
        return str(e)
    except Exception as e:
        _close_browser()
        return f"截图失败: {type(e).__name__}: {e}"


@tool
def browser_fill(selector: str, text: str) -> str:
    """
    填写表单输入框

    Args:
        selector: 元素的 CSS 选择器
        text: 要填写的文本

    Returns:
        操作结果
    """
    # 兼容处理：LLM 有时会传 JSON 字符串
    if isinstance(selector, str):
        try:
            parsed = json.loads(selector)
            if isinstance(parsed, dict):
                selector = parsed.get("selector", selector)
                text = parsed.get("text", text)
        except (json.JSONDecodeError, TypeError):
            pass

    try:
        pw, browser, page = _ensure_browser()
        page.fill(selector, text)
        return f"已在 {selector} 填写: {text}"
    except RuntimeError as e:
        return str(e)
    except Exception as e:
        _close_browser()
        return f"填写失败: {type(e).__name__}: {e}"


@tool
def browser_click(selector: str) -> str:
    """
    点击页面元素

    Args:
        selector: 元素的 CSS 选择器

    Returns:
        操作结果
    """
    try:
        pw, browser, page = _ensure_browser()
        check_tool_stop()
        page.click(selector)
        check_tool_stop()
        page.wait_for_load_state("networkidle")
        check_tool_stop()
        page.wait_for_timeout(500)
        return f"已点击: {selector}"
    except AgentStoppedException:
        return "[已停止] 用户请求中断了执行。"
    except RuntimeError as e:
        return str(e)
    except Exception as e:
        _close_browser()
        return f"点击失败: {type(e).__name__}: {e}"


@tool
def browser_search(query: str) -> str:
    """
    在浏览器中搜索（使用 DuckDuckGo）

    Args:
        query: 搜索关键词

    Returns:
        搜索结果摘要
    """
    try:
        pw, browser, page = _ensure_browser()
        check_tool_stop()
        page.goto(f"https://duckduckgo.com/?q={query}")
        check_tool_stop()
        page.wait_for_load_state("networkidle")
        check_tool_stop()
        page.wait_for_timeout(2000)

        titles = page.query_selector_all("h2")
        results = []
        for title in titles[:5]:
            text = title.inner_text()
            if text and len(text) > 5:
                results.append(text)

        if results:
            return f"搜索结果 ({query}):\n" + "\n".join(f"- {r}" for r in results)
        else:
            return f"未找到搜索结果: {query}"
    except AgentStoppedException:
        return "[已停止] 用户请求中断了执行。"
    except RuntimeError as e:
        return str(e)
    except Exception as e:
        _close_browser()
        return f"搜索失败: {type(e).__name__}: {e}"


@tool
def browser_close() -> str:
    """
    关闭当前浏览器窗口

    Returns:
        操作结果
    """
    _close_browser()
    return "浏览器已关闭"


def get_browser_tools() -> list:
    """获取所有浏览器工具"""
    return [
        browser_navigate,
        browser_screenshot,
        browser_fill,
        browser_click,
        browser_search,
        browser_close,
    ]

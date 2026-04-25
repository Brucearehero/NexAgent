"""
NexAgent - 浏览器操作工具
使用 Playwright 控制浏览器
"""
import asyncio
import yaml
from pathlib import Path
from typing import Optional
from langchain_core.tools import tool

CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_browser_config() -> dict:
    config = load_config()
    return config.get("browser", {})


async def _get_playwright():
    """动态获取 Playwright"""
    try:
        from playwright.async_api import async_playwright
        return async_playwright()
    except ImportError:
        return None


@tool
def browser_navigate(url: str) -> str:
    """
    打开浏览器并导航到指定 URL

    Args:
        url: 目标网址

    Returns:
        操作结果
    """
    async def _navigate():
        pw = await _get_playwright()
        if pw is None:
            return "Playwright 未安装，请运行: pip install playwright && playwright install chromium"

        cfg = get_browser_config()
        headless = cfg.get("headless", False)
        slow_mo = cfg.get("slow_mo", 100)

        browser = await pw.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url)
        await page.wait_for_load_state("networkidle")

        # 等待一小段时间让页面稳定
        await page.wait_for_timeout(1000)

        title = await page.title()
        await browser.close()

        return f"已打开: {url}\n页面标题: {title}"

    return asyncio.run(_navigate())


@tool
def browser_screenshot(file_name: str = "screenshot.png") -> str:
    """
    对当前页面截图

    Args:
        file_name: 保存的文件名

    Returns:
        截图保存结果
    """
    async def _screenshot():
        pw = await _get_playwright()
        if pw is None:
            return "Playwright 未安装，请运行: pip install playwright && playwright install chromium"

        browser = await pw.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # 检查是否有打开的页面
        screenshot_path = Path(file_name).resolve()
        await page.screenshot(path=str(screenshot_path))

        await browser.close()
        return f"截图已保存到: {screenshot_path}"

    return asyncio.run(_screenshot())


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
    async def _fill():
        pw = await _get_playwright()
        if pw is None:
            return "Playwright 未安装"

        browser = await pw.chromium.launch()
        page = await browser.new_page()

        await page.fill(selector, text)
        await browser.close()

        return f"已在 {selector} 填写: {text}"

    return asyncio.run(_fill())


@tool
def browser_click(selector: str) -> str:
    """
    点击页面元素

    Args:
        selector: 元素的 CSS 选择器

    Returns:
        操作结果
    """
    async def _click():
        pw = await _get_playwright()
        if pw is None:
            return "Playwright 未安装"

        browser = await pw.chromium.launch()
        page = await browser.new_page()

        await page.click(selector)
        await browser.close()

        return f"已点击: {selector}"

    return asyncio.run(_click())


@tool
def browser_search(query: str) -> str:
    """
    在浏览器中搜索（使用 DuckDuckGo）

    Args:
        query: 搜索关键词

    Returns:
        搜索结果摘要
    """
    async def _search():
        pw = await _get_playwright()
        if pw is None:
            return "Playwright 未安装"

        cfg = get_browser_config()
        headless = cfg.get("headless", False)

        browser = await pw.chromium.launch(headless=headless)
        page = await browser.new_page()

        # 使用 DuckDuckGo 搜索
        await page.goto(f"https://duckduckgo.com/?q={query}")
        await page.wait_for_load_state("networkidle")

        # 等待搜索结果加载
        await page.wait_for_timeout(2000)

        # 提取前几个搜索结果标题
        titles = await page.query_selector_all("h2")
        results = []
        for title in titles[:5]:
            text = await title.inner_text()
            if text and len(text) > 5:
                results.append(text)

        await browser.close()

        if results:
            return f"搜索结果 ({query}):\n" + "\n".join(f"- {r}" for r in results)
        else:
            return f"未找到搜索结果: {query}"

    return asyncio.run(_search())


def get_browser_tools() -> list:
    """获取所有浏览器工具"""
    return [
        browser_navigate,
        browser_screenshot,
        browser_fill,
        browser_click,
        browser_search,
    ]

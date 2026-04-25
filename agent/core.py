"""
NexAgent - Agent 核心
使用 LangChain 的 ReAct 模式构建 Agent
"""
import yaml
from pathlib import Path
from typing import List, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool

from .models.providers import get_chat_model, get_available_providers

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_agent(tools: List, provider: Optional[str] = None) -> AgentExecutor:
    """
    构建 LangChain Agent

    Args:
        tools: 工具列表
        provider: 模型提供商

    Returns:
        AgentExecutor 实例
    """
    config = load_config()
    agent_config = config.get("agent", {})

    # 获取 LLM
    llm = get_chat_model(provider)

    # 系统提示词
    system_prompt = agent_config.get(
        "system_prompt",
        "你是一个通用的 Windows AI Agent，可以帮助用户完成各种任务。"
    )

    # 创建 ReAct Agent
    agent = create_react_agent(llm, tools)

    # 创建执行器
    max_iterations = agent_config.get("max_iterations", 20)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=max_iterations,
        verbose=True,
        handle_parsing_errors=True,
    )

    return executor


def run_agent(user_input: str, tools: List, provider: Optional[str] = None) -> str:
    """
    运行 Agent 处理用户输入

    Args:
        user_input: 用户输入
        tools: 工具列表
        provider: 模型提供商

    Returns:
        Agent 的响应
    """
    executor = build_agent(tools, provider)

    config = load_config()
    system_prompt = config.get("agent", {}).get("system_prompt", "")

    response = executor.invoke({
        "input": user_input,
        "system_prompt": system_prompt,
    })

    return response.get("output", "Agent 执行完成，无输出")

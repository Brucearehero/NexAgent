"""
NexAgent - 模型提供者
支持多模型切换：OpenRouter / DeepSeek / Gemini / Groq / 硅基流动 / 智谱 GLM
"""
import os
import yaml
from pathlib import Path
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"


def load_config() -> dict:
    """加载配置文件"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_chat_model(provider: Optional[str] = None) -> any:
    """
    根据配置获取聊天模型

    Args:
        provider: 模型提供商，不传则使用配置中的默认 provider

    Returns:
        LangChain 兼容的聊天模型实例
    """
    config = load_config()
    model_config = config.get("model", {})

    # 确定使用哪个 provider
    if provider is None:
        provider = model_config.get("provider", "zhipu")

    model_names = model_config.get("model_name", {})

    if provider == "zhipu":
        api_key = os.getenv("ZHIPU_API_KEY")
        model_name = model_names.get("zhipu", "glm-4-flash")
        if not api_key:
            raise ValueError("智谱 GLM API 密钥未设置，请设置环境变量 ZHIPU_API_KEY")
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url="https://open.bigmodel.cn/api/paas/v4",
            temperature=0.7,
        )

    elif provider == "moonshot":
        api_key = os.getenv("MOONSHOT_API_KEY")
        model_name = model_names.get("moonshot", "moonshot-v1-8k")
        if not api_key:
            raise ValueError("Moonshot API 密钥未设置，请设置环境变量 MOONSHOT_API_KEY")
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1",
            temperature=0.7,
        )

    else:
        raise ValueError(f"不支持的模型 provider: {provider}")


def get_available_providers() -> list:
    """获取所有可用的模型 provider 列表"""
    return [
        {"id": "zhipu", "name": "智谱 GLM", "desc": "国产 GLM-4 系列"},
        {"id": "moonshot", "name": "Kimi (Moonshot)", "desc": "国产长文本模型，免费额度充足"},
    ]

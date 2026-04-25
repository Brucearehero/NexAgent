"""
NexAgent - 模型提供者
支持多模型切换：OpenRouter / DeepSeek / Gemini / Groq / 硅基流动 / 智谱 GLM
"""
import os
import yaml
from pathlib import Path
from typing import Optional
from langchain.chat_models import ChatOpenAI
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
        provider = model_config.get("provider", "openrouter")

    api_keys = model_config.get("api_keys", {})
    model_names = model_config.get("model_name", {})

    if provider == "openrouter":
        api_key = api_keys.get("openrouter") or os.getenv("OPENROUTER_API_KEY")
        model_name = model_names.get("openrouter", "anthropic/claude-3.5-haiku")
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7,
        )

    elif provider == "deepseek":
        api_key = api_keys.get("deepseek") or os.getenv("DEEPSEEK_API_KEY")
        model_name = model_names.get("deepseek", "deepseek-chat")
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            temperature=0.7,
        )

    elif provider == "gemini":
        api_key = api_keys.get("gemini") or os.getenv("GEMINI_API_KEY")
        model_name = model_names.get("gemini", "gemini-2.0-flash")
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.7,
        )

    elif provider == "groq":
        api_key = api_keys.get("groq") or os.getenv("GROQ_API_KEY")
        model_name = model_names.get("groq", "llama-3.3-70b-versatile")
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            temperature=0.7,
        )

    elif provider == "sili":
        api_key = api_keys.get("sili") or os.getenv("SILIN_API_KEY")
        model_name = model_names.get("sili", "Qwen/Qwen2.5-7B-Instruct")
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url="https://api.siliconflow.cn/v1",
            temperature=0.7,
        )

    elif provider == "zhipu":
        api_key = api_keys.get("zhipu") or os.getenv("ZHIPU_API_KEY")
        model_name = model_names.get("zhipu", "glm-4-flash")
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url="https://open.bigmodel.cn/api/paas/v4",
            temperature=0.7,
        )

    else:
        raise ValueError(f"不支持的模型 provider: {provider}")


def get_available_providers() -> list:
    """获取所有可用的模型 provider 列表"""
    return [
        {"id": "openrouter", "name": "OpenRouter", "desc": "聚合多模型，支持 Claude/GPT 等"},
        {"id": "deepseek", "name": "DeepSeek", "desc": "国产大模型，性价比高"},
        {"id": "gemini", "name": "Google Gemini", "desc": "Google Gemini 2.0 Flash"},
        {"id": "groq", "name": "Groq", "desc": "超快推理速度"},
        {"id": "sili", "name": "硅基流动", "desc": "国内可用，免费额度多"},
        {"id": "zhipu", "name": "智谱 GLM", "desc": "国产 GLM-4 系列"},
    ]

"""
NexAgent - FastAPI 主入口
"""
import asyncio
import uuid
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import yaml

from agent import run_agent, get_all_tools, get_available_providers
from agent.models.providers import get_chat_model

# ============ 配置 ============
CONFIG_PATH = Path(__file__).parent / "config.yaml"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

FRONTEND_HOST = CONFIG.get("frontend", {}).get("host", "127.0.0.1")
FRONTEND_PORT = CONFIG.get("frontend", {}).get("port", 8000)

# ============ FastAPI 应用 ============
app = FastAPI(
    title="NexAgent",
    description="Windows 通用 AI Agent 框架",
    version="1.0.0",
)

# 静态文件和模板
BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend" / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "frontend" / "templates")

# 存储对话历史
conversations = {}


# ============ 数据模型 ============
class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")
    provider: Optional[str] = Field(None, description="模型提供商")
    conversation_id: Optional[str] = Field(None, description="对话 ID")


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    tools_used: List[str] = []


class ConfigUpdateRequest(BaseModel):
    provider: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None


# ============ 路由 ============
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """主页"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/providers")
async def list_providers():
    """获取可用的模型提供商列表"""
    providers = get_available_providers()
    return {"providers": providers}


@app.get("/api/config")
async def get_config():
    """获取当前配置"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    # 隐藏 API Key
    if "api_keys" in config.get("model", {}):
        for k in config["model"]["api_keys"]:
            if config["model"]["api_keys"][k]:
                config["model"]["api_keys"][k] = "***"
    return config


@app.post("/api/config")
async def update_config(request: ConfigUpdateRequest):
    """更新配置"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if request.provider:
        config["model"]["provider"] = request.provider
    if request.api_key:
        api_keys = config.setdefault("model", {}).setdefault("api_keys", {})
        api_keys[request.provider or config["model"]["provider"]] = request.api_key
    if request.model_name:
        model_names = config.setdefault("model", {}).setdefault("model_name", {})
        model_names[request.provider or config["model"]["provider"]] = request.model_name

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

    return {"status": "ok", "message": "配置已更新"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """处理聊天消息"""
    # 获取或创建对话 ID
    conv_id = request.conversation_id or str(uuid.uuid4())

    # 初始化对话历史
    if conv_id not in conversations:
        conversations[conv_id] = []

    # 添加用户消息
    conversations[conv_id].append({"role": "user", "content": request.message})

    try:
        # 获取所有工具
        tools = get_all_tools()

        # 运行 Agent
        response = await asyncio.to_thread(
            run_agent,
            request.message,
            tools,
            request.provider
        )

        # 添加助手回复
        conversations[conv_id].append({"role": "assistant", "content": response})

        return ChatResponse(
            response=response,
            conversation_id=conv_id,
            tools_used=[],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """获取对话历史"""
    if conversation_id not in conversations:
        return {"messages": []}
    return {"messages": conversations[conversation_id]}


@app.delete("/api/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """删除对话"""
    if conversation_id in conversations:
        del conversations[conversation_id]
    return {"status": "ok"}


@app.get("/api/tools")
async def list_tools():
    """获取所有可用工具"""
    tools = get_all_tools()
    return {
        "tools": [
            {
                "name": t.name,
                "description": t.description,
            }
            for t in tools
        ]
    }


# ============ 健康检查 ============
@app.get("/api/health")
async def health():
    """健康检查"""
    return {"status": "ok"}


# ============ 启动 ============
if __name__ == "__main__":
    import uvicorn

    print(f"""
╔══════════════════════════════════════════════╗
║             NexAgent v1.0.0                  ║
║     Windows 通用 AI Agent 框架                ║
╠══════════════════════════════════════════════╣
║  本地 Web UI: http://{FRONTEND_HOST}:{FRONTEND_PORT}       ║
║  API 文档:    http://{FRONTEND_HOST}:{FRONTEND_PORT}/docs  ║
╠══════════════════════════════════════════════╣
║  按 Ctrl+C 停止服务器                        ║
╚══════════════════════════════════════════════╝
    """)

    uvicorn.run(
        "main:app",
        host=FRONTEND_HOST,
        port=FRONTEND_PORT,
        reload=True,
    )

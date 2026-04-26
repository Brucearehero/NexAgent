"""
NexAgent - FastAPI 主入口
"""
import asyncio
import uuid
import socket
import os
import queue
import threading
from pathlib import Path
from typing import Optional, List, AsyncGenerator
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import yaml

from agent import run_agent, get_all_tools, get_available_providers
from agent.core import set_stop_flag, clear_stop_flag, AgentStoppedException  # 导入停止标志管理和异常类
from agent.models.providers import get_chat_model


# ============ 单实例检查 ============
def check_single_instance(port: int) -> bool:
    """检查是否已有实例在运行"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.bind(('127.0.0.1', port))
        sock.close()
        return False  # 端口可用，说明没有实例在运行
    except OSError:
        return True   # 端口已被占用，说明已有实例在运行

# ============ 配置 ============
CONFIG_PATH = Path(__file__).parent / "config.yaml"

# 检查配置文件是否存在
if not CONFIG_PATH.exists():
    # 如果配置文件不存在，检查是否有示例配置文件
    EXAMPLE_CONFIG_PATH = Path(__file__).parent / "config.yaml.example"
    if EXAMPLE_CONFIG_PATH.exists():
        # 复制示例配置文件
        import shutil
        shutil.copy(EXAMPLE_CONFIG_PATH, CONFIG_PATH)
        print(f"\n[配置] 配置文件不存在，已从 config.yaml.example 创建默认配置文件\n")
    else:
        # 如果示例配置文件也不存在，创建默认配置
        default_config = {
            "agent": {
                "max_iterations": 20,
                "system_prompt": '你是一个通用的 AI Agent，运行在 Windows 平台上。\n\n    重要原则：\n\n    【搜索】搜索信息必须使用 web_search 工具（DuckDuckGo），禁止跳转到百度/bing.com 等搜索引擎网站。\n\n    【打开网站】只有用户明确要求"打开网站"、"打开b站"等时才使用 browser_navigate。\n\n    【本地应用】打开文件夹/文件管理器用 open_in_explorer，打开 VS Code 用 open_vscode，打开任意程序用 open_application。\n\n    【文件操作】读取/编辑/创建文件用 file_read / file_write / file_edit。\n\n    【代码执行】执行代码用 python_execute，运行命令用 shell_run。\n\n    【浏览器操作】用 Playwright 控制浏览器，仅在用户明确要求时使用。\n\n    【HTTP请求】调用外部 API 用 http_get / http_post。\n\n    每次只使用一个工具，等待结果后再决定下一步。\n\n    '
            },
            "browser": {
                "headless": False,
                "slow_mo": 100
            },
            "frontend": {
                "host": "127.0.0.1",
                "port": 8000
            },
            "model": {
                "api_keys": {
                    "moonshot": "your-moonshot-api-key",
                    "zhipu": "your-zhipu-api-key"
                },
                "model_name": {
                    "moonshot": "moonshot-v1-8k",
                    "zhipu": "glm-4-flash"
                },
                "provider": "zhipu"
            }
        }
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(default_config, f, allow_unicode=True, default_flow_style=False)
        print(f"\n[配置] 配置文件不存在，已创建默认配置文件\n")

# 加载配置
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
    steps: List[dict] = []  # 思考过程步骤


class ConfigUpdateRequest(BaseModel):
    provider: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None


# ============ 路由 ============
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """主页"""
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/providers")
async def list_providers():
    """获取可用的模型提供商列表"""
    providers = get_available_providers()
    return {"providers": providers}


@app.get("/api/models")
async def list_models():
    """获取已配置的模型列表"""
    models = []
    model_names = CONFIG.get("model", {}).get("model_name", {})
    
    # 检查环境变量中是否有API密钥
    for provider in model_names:
        if provider == "zhipu" and os.getenv("ZHIPU_API_KEY"):
            models.append({
                "provider": provider,
                "model": model_names.get(provider, "unknown"),
            })
        elif provider == "moonshot" and os.getenv("MOONSHOT_API_KEY"):
            models.append({
                "provider": provider,
                "model": model_names.get(provider, "unknown"),
            })
    
    return {"models": models, "default_provider": CONFIG.get("model", {}).get("provider")}


@app.get("/api/config")
async def get_config():
    """获取当前配置"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


@app.post("/api/config")
async def update_config(request: ConfigUpdateRequest):
    """更新配置"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if request.provider:
        config["model"]["provider"] = request.provider
    if request.model_name:
        model_names = config.setdefault("model", {}).setdefault("model_name", {})
        model_names[request.provider or config["model"]["provider"]] = request.model_name

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

    return {"status": "ok", "message": "配置已更新"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """处理聊天消息，返回最终答案 + 思考步骤"""
    conv_id = request.conversation_id or str(uuid.uuid4())
    clear_stop_flag(conv_id)

    if conv_id not in conversations:
        conversations[conv_id] = []

    conversations[conv_id].append({"role": "user", "content": request.message})

    try:
        tools = get_all_tools()
        # run_agent 返回字典 {"output": ..., "steps": [...]}
        result = await asyncio.to_thread(
            run_agent,
            request.message,
            tools,
            request.provider,
            conv_id,
            None
        )

        # 解析结果
        if isinstance(result, dict):
            final_output = result.get("output", str(result))
            steps = result.get("steps", [])
        else:
            final_output = str(result)
            steps = []

        # 添加助手回复
        conversations[conv_id].append({"role": "assistant", "content": final_output})

        return ChatResponse(
            response=final_output,
            conversation_id=conv_id,
            tools_used=[],
            steps=steps,
        )

    except AgentStoppedException:
        clear_stop_flag(conv_id)
        return ChatResponse(
            response="[已停止] 用户请求中断了执行。",
            conversation_id=conv_id,
            tools_used=[],
        )
    except Exception as e:
        clear_stop_flag(conv_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """处理聊天消息（SSE 流式返回思考过程）"""
    conv_id = request.conversation_id or str(uuid.uuid4())
    
    # 清除之前的停止标志
    clear_stop_flag(conv_id)

    # 初始化对话历史
    if conv_id not in conversations:
        conversations[conv_id] = []

    # 添加用户消息
    conversations[conv_id].append({"role": "user", "content": request.message})

    # 创建 SSE 队列
    sse_queue = queue.Queue(maxsize=100)

    async def event_generator() -> AsyncGenerator[str, None]:
        """SSE 事件生成器"""
        final_response = None
        agent_thread = None
        
        def run_agent_thread():
            """在线程中运行 Agent"""
            nonlocal final_response
            try:
                tools = get_all_tools()
                result = run_agent(
                    request.message,
                    tools,
                    request.provider,
                    conv_id,
                    sse_queue
                )
                # run_agent 返回字典 {"output": ..., "steps": [...]}
                if isinstance(result, dict):
                    final_response = result.get("output", str(result))
                else:
                    final_response = str(result)
            except AgentStoppedException:
                final_response = "[已停止] 用户请求中断了执行。"
            except Exception as e:
                final_response = f"[错误] {str(e)}"
        
        # 启动 Agent 线程
        agent_thread = threading.Thread(target=run_agent_thread)
        agent_thread.start()
        
        # 等待并推送事件
        while agent_thread.is_alive() or not sse_queue.empty():
            try:
                # 非阻塞获取事件
                event = sse_queue.get(timeout=0.5)
                event_type = event.get("event", "info")
                content = event.get("content", "")
                # SSE 格式：event: xxx\ndata: xxx\n\n
                yield f"event: {event_type}\ndata: {content}\n\n"
            except queue.Empty:
                # 没有事件时发送心跳
                yield f"event: heartbeat\ndata: \n\n"
        
        # Agent 完成，发送最终答案
        yield f"event: complete\ndata: {final_response}\n\n"
        
        # 添加助手回复到历史
        conversations[conv_id].append({"role": "assistant", "content": final_response})
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Conversation-ID": conv_id
        }
    )


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


@app.post("/api/stop/{conversation_id}")
async def stop_conversation(conversation_id: str):
    """停止指定对话的执行"""
    set_stop_flag(conversation_id)
    return {"status": "ok", "message": "停止请求已发送"}


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

    # 检查单实例
    if check_single_instance(FRONTEND_PORT):
        print(f"""
╔══════════════════════════════════════════════╗
║              [!] 警告                          ║
╠══════════════════════════════════════════════╣
║  NexAgent 已在运行中！                        ║
║                                              ║
║  请访问: http://{FRONTEND_HOST}:{FRONTEND_PORT}       ║
║                                              ║
║  如需重启，请先关闭现有窗口                   ║
╚══════════════════════════════════════════════╝
        """)
        input("按 Enter 键退出...")
        exit(1)

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

# NexAgent

> Windows 通用 AI Agent 框架 - 开箱即用的本地 AI 助手

## 功能特性

- 🔧 **多工具支持**：文件读写、代码执行、Shell 命令、浏览器控制、HTTP 请求、网页搜索
- 🤖 **多模型支持**：OpenRouter / DeepSeek / Google Gemini / Groq / 硅基流动 / 智谱 GLM
- 💻 **本地 Web UI**：简洁美观的对话界面，开箱即用
- 🛠️ **可扩展工具集**：基于 LangChain 构建，方便添加自定义工具
- 📦 **配置简单**：YAML 配置文件，无需硬编码

## 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/yourname/NexAgent.git
cd NexAgent

# 创建虚拟环境（推荐）
python -m venv venv
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 安装 Playwright（可选，用于浏览器操作）

```bash
playwright install chromium
```

### 3. 配置 API Key

编辑 `config.yaml`，填入你的模型 API Key：

```yaml
model:
  provider: "deepseek"  # 选择默认模型

  api_keys:
    deepseek: "your-api-key-here"  # 填入你的 DeepSeek API Key
```

### 4. 启动服务

```bash
python main.py
```

打开浏览器访问: http://127.0.0.1:8000

## 支持的模型

| 提供商 | 说明 | 免费额度 |
|--------|------|----------|
| OpenRouter | 聚合多模型（Claude/GPT 等） | 部分模型免费 |
| DeepSeek | 国产大模型，性价比高 | 有免费额度 |
| Google Gemini | Google Gemini 2.0 | 每天大量免费 |
| Groq | 超快推理速度 | 部分模型免费 |
| 硅基流动 | 国内可用，免费额度多 | 有免费额度 |
| 智谱 GLM | 国产 GLM-4 系列 | 有免费额度 |

## 工具集

### 文件操作
- `read_file` - 读取文件内容
- `write_file` - 写入文件（支持追加）
- `list_directory` - 列出目录内容
- `delete_file` - 删除文件/目录
- `create_directory` - 创建目录
- `read_json` / `write_json` - JSON 文件操作

### 代码执行
- `execute_python` - 执行 Python 代码
- `execute_shell` - 执行 Shell/PowerShell 命令
- `check_python_version` - 检查 Python 环境

### 系统操作
- `open_vscode` - 打开 VS Code
- `open_pycharm` - 打开 PyCharm
- `open_application` - 打开任意应用
- `open_in_explorer` - 在资源管理器中打开
- `get_system_info` - 获取系统信息

### 浏览器操作
- `browser_navigate` - 打开网页
- `browser_screenshot` - 页面截图
- `browser_fill` - 填写表单
- `browser_click` - 点击元素
- `browser_search` - 搜索

### HTTP / 搜索
- `http_get` - GET 请求
- `http_post` - POST 请求
- `http_delete` - DELETE 请求
- `web_search` - 网页搜索

## 项目结构

```
NexAgent/
├── main.py                 # FastAPI 入口
├── config.yaml             # 配置文件
├── requirements.txt        # 依赖列表
├── agent/
│   ├── core.py            # Agent 核心逻辑
│   ├── models/
│   │   └── providers.py   # 多模型支持
│   └── tools/
│       ├── file_tools.py   # 文件操作
│       ├── code_tools.py   # 代码执行
│       ├── shell_tools.py  # Shell/应用
│       ├── browser_tools.py# 浏览器操作
│       └── http_tools.py   # HTTP 请求
├── frontend/
│   ├── templates/
│   │   └── index.html     # Web UI
│   └── static/
│       └── .gitkeep
└── README.md
```

## 自定义扩展

### 添加新工具

在 `agent/tools/` 目录下创建新的工具文件，例如 `custom_tools.py`：

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(param: str) -> str:
    """工具描述"""
    # 你的工具逻辑
    return result

def get_custom_tools() -> list:
    return [my_custom_tool]
```

然后在 `agent/tools/__init__.py` 中导入：

```python
from .custom_tools import get_custom_tools

def get_all_tools() -> list:
    tools = []
    # ... 其他工具
    tools.extend(get_custom_tools())
    return tools
```

### 切换模型

在 Web UI 侧边栏选择模型，或通过 API：

```bash
curl -X POST http://127.0.0.1:8000/api/config \
  -H "Content-Type: application/json" \
  -d '{"provider": "gemini", "api_key": "your-key"}'
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | Web UI 主页 |
| `/api/chat` | POST | 发送消息 |
| `/api/providers` | GET | 获取可用模型列表 |
| `/api/tools` | GET | 获取工具列表 |
| `/api/config` | GET/POST | 获取/更新配置 |
| `/docs` | GET | API 文档 |

## 开发说明

- 前端使用原生 HTML/CSS/JavaScript，无额外框架依赖
- 后端基于 FastAPI + LangChain
- Agent 模式：ReAct（思考 → 行动 → 观察）

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

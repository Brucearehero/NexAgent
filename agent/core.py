"""
NexAgent - Agent 核心
使用 LangChain 的 ReAct 模式构建 Agent
"""
import yaml
import time
import threading
import logging
from pathlib import Path
from typing import List, Optional, Any, Dict, Iterator
from langchain_core.callbacks import BaseCallbackHandler
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import render_text_description
from langchain_core.agents import AgentAction, AgentFinish, AgentStep
from langchain_core.language_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatResult, LLMResult
from langchain_core.messages import BaseMessage

from .models.providers import get_chat_model, get_available_providers

# 配置 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
for logger_name in ['langchain', 'langchain_classic', 'langchain_core']:
    logging.getLogger(logger_name).setLevel(logging.INFO)

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

# ============ 停止标志管理（由 main.py 共享）============
_stop_flags = {}
_stop_flags_lock = threading.Lock()

# 线程局部变量，用于在工具中获取当前对话 ID
_local = threading.local()


def set_stop_flag(conv_id: str):
    with _stop_flags_lock:
        _stop_flags[conv_id] = True


def get_stop_flag(conv_id: str) -> bool:
    with _stop_flags_lock:
        return _stop_flags.get(conv_id, False)


def clear_stop_flag(conv_id: str):
    with _stop_flags_lock:
        if conv_id in _stop_flags:
            del _stop_flags[conv_id]


def get_current_conv_id() -> Optional[str]:
    """获取当前线程的对话 ID（供工具使用）"""
    return getattr(_local, 'conv_id', None)


def set_current_conv_id(conv_id: Optional[str]):
    """设置当前线程的对话 ID"""
    _local.conv_id = conv_id


def check_tool_stop():
    """
    供工具调用的停止检查函数。
    如果当前对话被标记停止，抛出 AgentStoppedException。
    """
    conv_id = get_current_conv_id()
    if conv_id and get_stop_flag(conv_id):
        clear_stop_flag(conv_id)
        print(f"[Agent] [STOPPED] 工具检测到停止信号")
        raise AgentStoppedException("用户请求停止")


def check_stop_flag(conv_id: str) -> bool:
    """
    检查停止标志，返回是否需要停止
    """
    if conv_id and get_stop_flag(conv_id):
        clear_stop_flag(conv_id)
        print(f"[Agent] [STOPPED] 检测到停止信号")
        return True
    return False


class AgentStoppedException(Exception):
    """Agent 被用户主动停止时抛出的异常"""
    pass


class StoppableLLMWrapper(BaseChatModel):
    """
    可中断的 LLM 包装器。
    
    在 LLM 生成过程中定期检查停止标志，如果检测到停止则抛出 AgentStoppedException。
    这是解决"停止按钮不生效"的核心：在 LLM 生成 token 的过程中也能被中断。
    """
    
    _wrapped_llm: BaseChatModel
    _conv_id: str
    
    @property
    def _llm_type(self) -> str:
        return "stoppable_wrapper"
    
    def __init__(self, wrapped_llm: BaseChatModel, conv_id: str):
        super().__init__()
        object.__setattr__(self, '_wrapped_llm', wrapped_llm)
        object.__setattr__(self, '_conv_id', conv_id)
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """
        重写 _generate 方法，在生成过程中检查停止标志。
        使用流式生成，每收到一个 token 就检查一次停止标志。
        """
        # 先检查一次停止标志
        if check_stop_flag(self._conv_id):
            raise AgentStoppedException("用户请求停止")
        
        # 使用流式生成
        full_content = ""
        try:
            # 检查是否支持流式生成
            if hasattr(self._wrapped_llm, 'stream'):
                # 使用流式生成
                for chunk in self._wrapped_llm.stream(messages, stop=stop, **kwargs):
                    # 每次收到一个 chunk 就检查停止标志
                    if check_stop_flag(self._conv_id):
                        raise AgentStoppedException("用户请求停止")
                    
                    if hasattr(chunk, 'content') and chunk.content:
                        full_content += chunk.content
            else:
                # 不支持流式生成，使用原始的_generate方法
                result = self._wrapped_llm._generate(messages, stop=stop, **kwargs)
                # 检查是否在生成过程中收到了停止信号
                if check_stop_flag(self._conv_id):
                    raise AgentStoppedException("用户请求停止")
                return result
            
            # 构建结果
            from langchain_core.outputs import ChatGeneration, ChatResult
            from langchain_core.messages import AIMessage
            
            generation = ChatGeneration(
                message=AIMessage(content=full_content),
                text=full_content,
            )
            return ChatResult(generations=[generation])
            
        except AgentStoppedException:
            raise
        except Exception as e:
            # 其他异常正常抛出
            raise
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """异步版本"""
        # 先检查一次停止标志
        if check_stop_flag(self._conv_id):
            raise AgentStoppedException("用户请求停止")
        
        # 使用异步流式生成
        full_content = ""
        try:
            # 检查是否支持异步流式生成
            if hasattr(self._wrapped_llm, 'astream'):
                # 使用异步流式生成
                async for chunk in self._wrapped_llm.astream(messages, stop=stop, **kwargs):
                    # 每次收到一个 chunk 就检查停止标志
                    if check_stop_flag(self._conv_id):
                        raise AgentStoppedException("用户请求停止")
                    
                    if hasattr(chunk, 'content') and chunk.content:
                        full_content += chunk.content
            else:
                # 不支持异步流式生成，使用原始的_agenerate方法
                result = await self._wrapped_llm._agenerate(messages, stop=stop, **kwargs)
                # 检查是否在生成过程中收到了停止信号
                if check_stop_flag(self._conv_id):
                    raise AgentStoppedException("用户请求停止")
                return result
            
            # 构建结果
            from langchain_core.outputs import ChatGeneration, ChatResult
            from langchain_core.messages import AIMessage
            
            generation = ChatGeneration(
                message=AIMessage(content=full_content),
                text=full_content,
            )
            return ChatResult(generations=[generation])
            
        except AgentStoppedException:
            raise
        except Exception as e:
            raise
    
    def _call(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> str:
        """兼容旧接口"""
        result = self._generate(messages, stop=stop, **kwargs)
        return result.generations[0][0].text
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return self._wrapped_llm._identifying_params if hasattr(self._wrapped_llm, '_identifying_params') else {}


def _make_executor_with_stop(tools, llm, agent, conv_id, sse_queue, max_iterations):
    """
    创建支持停止的 AgentExecutor。
    
    由于 AgentExecutor 是 pydantic BaseModel，不支持直接添加自定义字段，
    这里用闭包方式在 _should_continue 中检查停止标志。
    
    返回一个普通 AgentExecutor，但重写了 _should_continue 方法。
    """
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=max_iterations,
        verbose=False,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )
    
    # 用闭包保存 conv_id，重写 _should_continue
    original_should_continue = executor._should_continue
    
    def _patched_should_continue(iterations, time_elapsed):
        # 每次迭代前检查停止标志
        if check_stop_flag(conv_id):
            print(f"[Agent] [STOPPED] 检测到停止信号，终止执行 (迭代 {iterations})")
            return False
        return original_should_continue(iterations, time_elapsed)
    
    executor._should_continue = _patched_should_continue
    return executor


class StopCallbackHandler(BaseCallbackHandler):
    """
    LangChain 回调处理器，负责日志输出、SSE 事件推送和停止检查。
    """
    
    def __init__(self, conv_id: str, sse_queue: Optional[Any] = None):
        self.conv_id = conv_id
        self.sse_queue = sse_queue
    
    def _push_event(self, event_type: str, content: str):
        if self.sse_queue is not None:
            try:
                self.sse_queue.put_nowait({
                    "event": event_type,
                    "content": content
                })
            except Exception:
                pass
    
    def _check_stop(self):
        """检查停止标志，如需停止则抛出异常"""
        if check_stop_flag(self.conv_id):
            raise AgentStoppedException("用户请求停止")
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, *,
                      run_id, parent_run_id=None,
                      tags=None, metadata=None,
                      inputs=None, **kwargs) -> None:
        self._check_stop()
        tool_name = serialized.get('name', 'unknown') if isinstance(serialized, dict) else 'unknown'
        print(f"[Agent] [执行] 正在执行工具: {tool_name}")
        self._push_event("tool_start", f"正在执行工具: {tool_name}")
    
    def on_tool_end(self, output: str, *, run_id,
                    parent_run_id=None, **kwargs) -> None:
        self._check_stop()
        self._push_event("observation", output[:500] if len(output) > 500 else output)
    
    def on_tool_error(self, error, *, run_id,
                      parent_run_id=None, **kwargs) -> None:
        print(f"[Agent] [ERROR] 工具执行出错: {error}")
        self._push_event("error", str(error))
    
    def on_chain_start(self, serialized, inputs=None, **kwargs) -> None:
        self._check_stop()
        print(f"[Agent] [START] Agent 开始执行...")
        self._push_event("start", "开始思考...")
    
    def on_chain_end(self, outputs, **kwargs) -> None:
        print(f"[Agent] [DONE] Agent 执行完成")
    
    def on_chain_error(self, error, **kwargs) -> None:
        print(f"[Agent] [WARN] Agent 执行出错: {error}")
        self._push_event("error", str(error))
    
    def on_llm_start(self, serialized, prompts, **kwargs) -> None:
        self._check_stop()
        print(f"[Agent] [THINKING] 模型正在思考...")
        self._push_event("thinking", "模型正在思考...")
    
    def on_llm_end(self, response, **kwargs) -> None:
        self._check_stop()
        print(f"[Agent] [RESPONSE] 模型响应完成")
    
    def on_text(self, text: str, *, run_id, parent_run_id=None, **kwargs) -> None:
        self._check_stop()
        if "Thought:" in text:
            thought_content = text.split("Thought:")[-1].strip()[:200]
            print(f"[Agent] [THOUGHT] {thought_content}")
            self._push_event("thought", thought_content)
        if "Final Answer:" in text:
            final_answer = text.split("Final Answer:")[-1].strip()[:200]
            print(f"[Agent] [ANSWER] {final_answer}")
            self._push_event("answer", final_answer)


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_agent(tools: List, provider: Optional[str] = None,
                conv_id: str = "", sse_queue: Optional[Any] = None) -> AgentExecutor:
    """
    构建支持停止的 LangChain Agent
    
    Args:
        tools: 工具列表
        provider: 模型提供商
        conv_id: 对话 ID（用于停止标志）
        sse_queue: SSE 推送队列
    
    Returns:
        AgentExecutor 实例（已注入停止逻辑）
    """
    config = load_config()
    agent_config = config.get("agent", {})
    
    llm = get_chat_model(provider)
    
    # 用 StoppableLLMWrapper 包装 LLM，使其在生成过程中可被中断
    if conv_id:
        llm = StoppableLLMWrapper(llm, conv_id)
        print(f"[Agent] [STOP] LLM 已包装为可中断模式，对话ID: {conv_id}")
    
    system_prompt = agent_config.get(
        "system_prompt",
        "你是一个通用的 Windows AI Agent，可以帮助用户完成各种任务。\n\n"  
        "重要指令：\n"  
        "1. 当用户输入非常简短（如单个字母、数字或不完整的词语）时，不要使用任何工具，直接回答用户，询问具体需求。\n"  
        "2. 对于模糊或不明确的输入，先尝试理解用户的意图，不要使用工具，必要时直接提问。\n"  
        "3. 只有当输入包含足够的信息，并且确实需要外部信息时，才使用搜索工具。\n"  
        "4. 对于明显的拼写错误或缩写，尝试理解用户的真实意图，不要使用工具。\n"  
        "5. 如果不确定用户的需求，应该直接向用户提问以获取更多信息，不要使用任何工具。\n"  
        "6. 不要将英文输入自动视为需要打开浏览器的指令。只有当用户明确要求打开某个网站或需要浏览网页时，才使用浏览器工具。\n"  
        "7. 对于看起来像是拼写错误或无意义的英文输入（如 'dakaikuake'），不要使用任何工具，直接回答用户，询问具体需求。\n"  
        "8. 绝对不要尝试使用 'None' 作为工具。如果不需要使用工具，直接回答用户。"
    )
    
    tools_rendered = render_text_description(tools)
    tool_names_str = ", ".join([t.name for t in tools])
    
    react_prompt = PromptTemplate.from_template(
        """You are a helpful AI assistant. You MUST respond in Chinese (Simplified Chinese) for the Final Answer content, but ALL format labels must be in English.

{system_prompt}

You have access to the following tools:
{tool_names}

{tools}

IMPORTANT: You MUST follow this EXACT format with English labels only:

TO USE A TOOL:
Thought: I need to use the <tool_name> tool...
Action: <tool_name>
Action Input: {{"arg": "value"}}
Observation: <tool result>

TO ANSWER (NO tool needed):
Thought: I now know the answer.
Final Answer: <你的回答（用中文）>

NOTE: When you output "Final Answer:", do NOT output anything else (no Action, no Action Input). Just the final answer.

重要决策规则：
1. 对于以下情况，绝对不要使用任何工具，直接回答用户：
   - 输入非常简短（如单个字母、数字或不完整的词语）
   - 输入模糊或不明确
   - 输入看起来像是拼写错误或无意义的英文（如 'dakaikuake'）
   - 不确定用户需求时

2. 只有当输入包含足够的信息，并且确实需要外部信息时，才使用搜索工具。

3. 只有当用户明确要求打开某个网站或需要浏览网页时，才使用浏览器工具。

4. 绝对不要尝试使用 'None' 作为工具。如果不需要使用工具，直接使用 Final Answer 格式回答用户。

Begin!

Question: {input}
{agent_scratchpad}"""
    )
    react_prompt = react_prompt.partial(
        tools=tools_rendered,
        tool_names=tool_names_str,
        system_prompt=system_prompt,
        agent_scratchpad="",
    )
    
    agent = create_react_agent(llm, tools, react_prompt)
    max_iterations = agent_config.get("max_iterations", 20)
    
    # 创建支持停止的 executor
    executor = _make_executor_with_stop(
        tools, llm, agent, conv_id, sse_queue, max_iterations
    )
    
    return executor


def run_agent(user_input: str, tools: List, provider: Optional[str] = None,
              conversation_id: Optional[str] = None, sse_queue: Optional[Any] = None) -> dict:
    """
    运行 Agent 处理用户输入
    返回包含 output 和 steps 的字典
    """
    conv_id = conversation_id or ""
    
    # 设置线程局部变量，供工具层使用
    set_current_conv_id(conversation_id)
    
    executor = build_agent(tools, provider, conv_id, sse_queue)
    
    config = load_config()
    system_prompt = config.get("agent", {}).get("system_prompt", "")
    
    callbacks = []
    if conversation_id:
        callbacks = [StopCallbackHandler(conversation_id, sse_queue)]
        print(f"[Agent] [STOP] 停止监控已启动，对话ID: {conversation_id}")
    
    try:
        result = executor.invoke(
            {
                "input": user_input,
                "system_prompt": system_prompt,
            },
            {"callbacks": callbacks}
        )
        output = result.get("output", "Agent 执行完成，无输出")
        steps = []
        for action, observation in result.get("intermediate_steps", []):
            steps.append({
                "action": str(action.tool),
                "input": str(action.tool_input),
                "observation": str(observation)[:500],
            })
        
        # 检查是否是因为停止而结束
        if conv_id and get_stop_flag(conv_id):
            clear_stop_flag(conv_id)
            print(f"[Agent] [STOPPED] 已响应停止请求")
            if sse_queue:
                sse_queue.put_nowait({"event": "stopped", "content": "已停止"})
            return {"output": "[已停止] 用户请求中断了执行。", "steps": steps}
        
        return {"output": output, "steps": steps}
        
    except AgentStoppedException:
        print(f"[Agent] [STOPPED] 已响应停止请求 (AgentStoppedException)")
        if sse_queue:
            sse_queue.put_nowait({"event": "stopped", "content": "已停止"})
        return {"output": "[已停止] 用户请求中断了执行。", "steps": []}
    except Exception as e:
        # 检查是否因为停止导致异常
        if conv_id and get_stop_flag(conv_id):
            clear_stop_flag(conv_id)
            print(f"[Agent] [STOPPED] 已响应停止请求 (异常路径)")
            if sse_queue:
                sse_queue.put_nowait({"event": "stopped", "content": "已停止"})
            return {"output": "[已停止] 用户请求中断了执行。", "steps": []}
        raise
    finally:
        # 清理线程局部变量
        set_current_conv_id(None)

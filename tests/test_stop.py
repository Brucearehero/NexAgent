"""
NexAgent - 停止功能自测脚本
测试停止标志能否正确中断 Agent 执行
"""
import sys
import time
import threading
import queue
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agent.core import (
    set_stop_flag,
    get_stop_flag,
    clear_stop_flag,
    set_current_conv_id,
    get_current_conv_id,
    check_tool_stop,
    AgentStoppedException,
    _stop_flags,
    _stop_flags_lock,
)


def test_basic_stop_flag():
    """测试 1: 基本停止标志设置和获取"""
    print("=" * 60)
    print("测试 1: 基本停止标志设置和获取")
    print("=" * 60)

    conv_id = "test_conv_1"
    clear_stop_flag(conv_id)

    assert get_stop_flag(conv_id) is False, "初始状态应为 False"
    print("  [PASS] 初始状态为 False")

    set_stop_flag(conv_id)
    assert get_stop_flag(conv_id) is True, "设置后应为 True"
    print("  [PASS] 设置后为 True")

    clear_stop_flag(conv_id)
    assert get_stop_flag(conv_id) is False, "清除后应为 False"
    print("  [PASS] 清除后为 False")

    print("  [PASS] 测试 1 通过\n")
    return True


def test_check_tool_stop():
    """测试 2: check_tool_stop 函数"""
    print("=" * 60)
    print("测试 2: check_tool_stop 函数")
    print("=" * 60)

    conv_id = "test_conv_2"
    clear_stop_flag(conv_id)
    set_current_conv_id(conv_id)

    try:
        check_tool_stop()
        print("  [PASS] 未设置停止标志时不抛出异常")
    except AgentStoppedException:
        print("  [FAIL] 不应抛出异常")
        return False

    set_stop_flag(conv_id)
    try:
        check_tool_stop()
        print("  [FAIL] 应抛出 AgentStoppedException")
        return False
    except AgentStoppedException:
        print("  [PASS] 正确抛出 AgentStoppedException")

    assert get_stop_flag(conv_id) is False, "抛出异常后应自动清除标志"
    print("  [PASS] 抛出异常后自动清除标志")

    set_current_conv_id(None)
    print("  [PASS] 测试 2 通过\n")
    return True


def test_thread_local_conv_id():
    """测试 3: 线程局部变量"""
    print("=" * 60)
    print("测试 3: 线程局部变量")
    print("=" * 60)

    set_current_conv_id("main_thread_id")
    assert get_current_conv_id() == "main_thread_id"
    print("  [PASS] 主线程设置成功")

    result = {"conv_id": None}
    event = threading.Event()

    def worker():
        result["conv_id"] = get_current_conv_id()
        event.set()

    t = threading.Thread(target=worker)
    t.start()
    event.wait(timeout=2)

    assert result["conv_id"] is None, "子线程不应继承主线程的 conv_id"
    print("  [PASS] 子线程不继承主线程 conv_id")

    set_current_conv_id(None)
    print("  [PASS] 测试 3 通过\n")
    return True


def test_stop_during_long_operation():
    """测试 4: 模拟长时间操作中停止"""
    print("=" * 60)
    print("测试 4: 模拟长时间操作中停止")
    print("=" * 60)

    conv_id = "test_conv_4"
    clear_stop_flag(conv_id)

    stopped = {"value": False}
    event = threading.Event()

    def long_operation():
        # 在 worker 线程中设置 conv_id（模拟 run_agent 的行为）
        set_current_conv_id(conv_id)
        try:
            for i in range(10):
                check_tool_stop()
                time.sleep(0.2)
            stopped["value"] = False
        except AgentStoppedException:
            stopped["value"] = True
        finally:
            set_current_conv_id(None)
            event.set()

    t = threading.Thread(target=long_operation)
    t.start()

    time.sleep(0.5)
    set_stop_flag(conv_id)

    event.wait(timeout=3)

    assert stopped["value"] is True, "应在操作中被停止"
    print("  [PASS] 长时间操作中被正确停止")

    print("  [PASS] 测试 4 通过\n")
    return True


def test_stop_flag_thread_safety():
    """测试 5: 停止标志线程安全"""
    print("=" * 60)
    print("测试 5: 停止标志线程安全")
    print("=" * 60)

    conv_id = "test_conv_5"
    clear_stop_flag(conv_id)

    errors = []

    def setter():
        try:
            for _ in range(100):
                set_stop_flag(conv_id)
                clear_stop_flag(conv_id)
        except Exception as e:
            errors.append(str(e))

    threads = [threading.Thread(target=setter) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)

    assert len(errors) == 0, f"线程安全测试失败: {errors}"
    print("  [PASS] 多线程并发设置/清除无错误")
    print("  [PASS] 测试 5 通过\n")
    return True


def test_tool_imports():
    """测试 6: 工具模块导入检查"""
    print("=" * 60)
    print("测试 6: 工具模块导入检查")
    print("=" * 60)

    try:
        from agent.tools.browser_tools import get_browser_tools
        print("  [PASS] browser_tools 导入成功")
    except Exception as e:
        print(f"  [FAIL] browser_tools 导入失败: {e}")
        return False

    try:
        from agent.tools.code_tools import get_code_tools
        print("  [PASS] code_tools 导入成功")
    except Exception as e:
        print(f"  [FAIL] code_tools 导入失败: {e}")
        return False

    try:
        from agent.tools.http_tools import get_http_tools
        print("  [PASS] http_tools 导入成功")
    except Exception as e:
        print(f"  [FAIL] http_tools 导入失败: {e}")
        return False

    try:
        from agent.tools.file_tools import get_file_tools
        print("  [PASS] file_tools 导入成功")
    except Exception as e:
        print(f"  [FAIL] file_tools 导入失败: {e}")
        return False

    try:
        from agent.tools.shell_tools import get_shell_tools
        print("  [PASS] shell_tools 导入成功")
    except Exception as e:
        print(f"  [FAIL] shell_tools 导入失败: {e}")
        return False

    print("  [PASS] 测试 6 通过\n")
    return True


def test_tool_has_stop_check():
    """测试 7: 检查工具源文件是否包含停止检查"""
    print("=" * 60)
    print("测试 7: 检查工具源文件是否包含停止检查")
    print("=" * 60)

    tools_dir = Path(__file__).parent / "agent" / "tools"
    
    files_to_check = {
        "browser_tools.py": ["browser_navigate", "browser_click", "browser_search"],
        "code_tools.py": ["execute_shell", "execute_python"],
        "http_tools.py": ["http_get", "web_search"],
    }

    all_pass = True
    for filename, func_names in files_to_check.items():
        filepath = tools_dir / filename
        if not filepath.exists():
            print(f"  [FAIL] {filename} 文件不存在")
            all_pass = False
            continue
        
        source = filepath.read_text(encoding="utf-8")
        
        for func_name in func_names:
            if f"def {func_name}" in source:
                func_start = source.index(f"def {func_name}")
                # 查找下一个函数定义或文件结尾
                next_def = source.find(f"\ndef ", func_start + 1)
                if next_def == -1:
                    func_block = source[func_start:]
                else:
                    func_block = source[func_start:next_def]
                
                if "check_tool_stop" in func_block:
                    print(f"  [PASS] {filename}::{func_name} 包含 check_tool_stop")
                else:
                    print(f"  [FAIL] {filename}::{func_name} 缺少 check_tool_stop")
                    all_pass = False
            else:
                print(f"  [WARN] {filename} 中未找到 {func_name}")

    if all_pass:
        print("  [PASS] 测试 7 通过\n")
    else:
        print("  [FAIL] 测试 7 未通过\n")
    return all_pass


def test_callback_handler_has_stop_check():
    """测试 8: 检查 StopCallbackHandler 回调是否包含停止检查"""
    print("=" * 60)
    print("测试 8: 检查 StopCallbackHandler 回调")
    print("=" * 60)

    import inspect
    from agent.core import StopCallbackHandler

    methods_to_check = [
        "on_tool_start",
        "on_tool_end",
        "on_chain_start",
        "on_llm_start",
        "on_llm_end",
        "on_text",
    ]

    all_pass = True
    for method_name in methods_to_check:
        method = getattr(StopCallbackHandler, method_name, None)
        if method is None:
            print(f"  [FAIL] {method_name} 方法不存在")
            all_pass = False
            continue

        source = inspect.getsource(method)
        if "_check_stop" in source:
            print(f"  [PASS] {method_name} 包含 _check_stop")
        else:
            print(f"  [FAIL] {method_name} 缺少 _check_stop")
            all_pass = False

    if all_pass:
        print("  [PASS] 测试 8 通过\n")
    else:
        print("  [FAIL] 测试 8 未通过\n")
    return all_pass


def test_main_imports():
    """测试 9: 检查 main.py 是否正确导入 AgentStoppedException"""
    print("=" * 60)
    print("测试 9: 检查 main.py 导入")
    print("=" * 60)

    main_path = Path(__file__).parent / "main.py"
    source = main_path.read_text(encoding="utf-8")

    if "AgentStoppedException" in source:
        print("  [PASS] main.py 包含 AgentStoppedException 导入")
        print("  [PASS] 测试 9 通过\n")
        return True
    else:
        print("  [FAIL] main.py 缺少 AgentStoppedException 导入")
        print("  [FAIL] 测试 9 未通过\n")
        return False


def test_stoppable_llm_wrapper():
    """测试 10: 检查 StoppableLLMWrapper 是否存在"""
    print("=" * 60)
    print("测试 10: 检查 StoppableLLMWrapper")
    print("=" * 60)

    import inspect
    from agent.core import StoppableLLMWrapper

    # 检查类是否存在
    print("  [PASS] StoppableLLMWrapper 类存在")

    # 检查关键方法
    methods = ["_generate", "_agenerate", "_call"]
    for method in methods:
        if hasattr(StoppableLLMWrapper, method):
            print(f"  [PASS] StoppableLLMWrapper.{method} 存在")
        else:
            print(f"  [FAIL] StoppableLLMWrapper.{method} 不存在")
            return False

    # 检查 _generate 方法是否包含停止检查
    source = inspect.getsource(StoppableLLMWrapper._generate)
    if "get_stop_flag" in source and "AgentStoppedException" in source:
        print("  [PASS] _generate 包含停止检查逻辑")
    else:
        print("  [FAIL] _generate 缺少停止检查逻辑")
        return False

    # 检查 build_agent 是否使用了 StoppableLLMWrapper
    from agent.core import build_agent
    build_source = inspect.getsource(build_agent)
    if "StoppableLLMWrapper" in build_source:
        print("  [PASS] build_agent 使用了 StoppableLLMWrapper")
    else:
        print("  [FAIL] build_agent 未使用 StoppableLLMWrapper")
        return False

    print("  [PASS] 测试 10 通过\n")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  NexAgent 停止功能自测")
    print("=" * 60 + "\n")

    results = []

    results.append(("测试 1: 基本停止标志", test_basic_stop_flag()))
    results.append(("测试 2: check_tool_stop", test_check_tool_stop()))
    results.append(("测试 3: 线程局部变量", test_thread_local_conv_id()))
    results.append(("测试 4: 长时间操作停止", test_stop_during_long_operation()))
    results.append(("测试 5: 线程安全", test_stop_flag_thread_safety()))
    results.append(("测试 6: 工具模块导入", test_tool_imports()))
    results.append(("测试 7: 工具停止检查", test_tool_has_stop_check()))
    results.append(("测试 8: 回调停止检查", test_callback_handler_has_stop_check()))
    results.append(("测试 9: main.py 导入", test_main_imports()))
    results.append(("测试 10: StoppableLLMWrapper", test_stoppable_llm_wrapper()))

    print("\n" + "=" * 60)
    print("  测试结果汇总")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        icon = "[OK]" if result else "[!!]"
        print(f"  {icon} {name}: {status}")

    print(f"\n  总计: {passed}/{total} 通过")

    if passed == total:
        print("\n  所有测试通过！停止功能已正确实现。")
    else:
        print("\n  部分测试失败，请检查上述标记为 FAIL 的项目。")

    print("=" * 60 + "\n")

    sys.exit(0 if passed == total else 1)

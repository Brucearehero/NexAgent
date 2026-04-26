"""
NexAgent Agent 核心功能测试
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.core import AgentState, set_stop_flag, clear_stop_flag


class TestAgentState:
    """Agent 状态测试"""
    
    def test_agent_state_creation(self):
        """测试 AgentState 创建"""
        state = AgentState()
        assert state is not None
        assert hasattr(state, 'messages')
    
    def test_stop_flag_management(self):
        """测试停止标志管理"""
        test_id = "test-stop-flag-123"
        
        # 清除标志
        clear_stop_flag(test_id)
        
        # 设置标志
        set_stop_flag(test_id)
        
        # 验证清理
        clear_stop_flag(test_id)


class TestTools:
    """工具可用性测试"""
    
    def test_get_all_tools(self):
        """测试获取所有工具"""
        from agent import get_all_tools
        
        tools = get_all_tools()
        assert isinstance(tools, list)
        # 至少应该有基础工具
        
    def test_get_available_providers(self):
        """测试获取可用提供商"""
        from agent import get_available_providers
        
        providers = get_available_providers()
        assert isinstance(providers, dict)

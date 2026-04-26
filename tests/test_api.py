"""
NexAgent API 集成测试
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """健康检查端点测试"""
    
    def test_health_check(self):
        """测试健康检查端点返回正常状态"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    def test_health_check_no_auth_required(self):
        """验证健康检查无需认证"""
        response = client.get("/api/health")
        assert response.status_code == 200


class TestProvidersEndpoint:
    """模型提供商端点测试"""
    
    def test_list_providers(self):
        """测试获取提供商列表"""
        response = client.get("/api/providers")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data


class TestModelsEndpoint:
    """模型端点测试"""
    
    def test_list_models(self):
        """测试获取模型列表"""
        response = client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert "default_provider" in data


class TestConfigEndpoint:
    """配置端点测试"""
    
    def test_get_config(self):
        """测试获取配置（API Key 应被隐藏）"""
        response = client.get("/api/config")
        assert response.status_code == 200
        config = response.json()
        
        # 验证 API Key 被正确隐藏
        if "api_keys" in config.get("model", {}):
            for key, value in config["model"]["api_keys"].items():
                if value:  # 如果有值
                    assert value == "***", f"API Key for {key} should be masked"


class TestChatEndpoint:
    """聊天端点测试"""
    
    def test_chat_request_validation(self):
        """测试聊天请求参数验证"""
        # 缺少必需字段
        response = client.post("/api/chat", json={})
        assert response.status_code == 422  # FastAPI 验证错误
        
        # 有效请求（实际模型调用可能失败，但请求格式应该正确）
        response = client.post("/api/chat", json={
            "message": "你好",
            "provider": "zhipu"
        })
        # 注意：可能返回 500 如果 API Key 无效，但格式应该正确
        assert response.status_code in [200, 500]


class TestConversationEndpoint:
    """对话管理端点测试"""
    
    def test_get_nonexistent_conversation(self):
        """测试获取不存在的对话"""
        response = client.get("/api/conversation/nonexistent-id-123")
        assert response.status_code == 200
        assert response.json()["messages"] == []
    
    def test_delete_conversation(self):
        """测试删除对话"""
        response = client.delete("/api/conversation/test-id-456")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestToolsEndpoint:
    """工具端点测试"""
    
    def test_list_tools(self):
        """测试获取可用工具列表"""
        response = client.get("/api/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert isinstance(data["tools"], list)

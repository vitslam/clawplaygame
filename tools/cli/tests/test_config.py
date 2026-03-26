"""
配置管理测试
"""
import pytest
import json
from pathlib import Path
from ..config import Config


class TestConfig:
    """配置管理测试类"""
    
    @pytest.fixture
    def config(self, tmp_path):
        """创建测试配置"""
        # 临时目录
        import os
        old_home = os.environ.get('HOME')
        os.environ['HOME'] = str(tmp_path)
        
        cfg = Config()
        yield cfg
        
        # 清理
        if old_home:
            os.environ['HOME'] = old_home
        else:
            os.environ.pop('HOME', None)
    
    def test_init(self, config):
        """测试初始化"""
        assert config.config_dir.exists() or not config.config_file.exists()
    
    def test_get_set(self, config):
        """测试设置和获取"""
        config.set("test_key", "test_value")
        assert config.get("test_key") == "test_value"
        assert config.get("nonexistent", "default") == "default"
    
    def test_delete(self, config):
        """测试删除"""
        config.set("test_key", "value")
        config.delete("test_key")
        assert config.get("test_key") is None
    
    def test_api_url(self, config):
        """测试 API URL"""
        assert config.api_url == "http://localhost:8000"
        config.api_url = "http://example.com"
        assert config.api_url == "http://example.com"
    
    def test_current_user(self, config):
        """测试当前用户"""
        user = {"id": "user123", "nickname": "Test"}
        config.current_user = user
        assert config.current_user == user
        assert config.current_user["id"] == "user123"
    
    def test_current_room(self, config):
        """测试当前房间"""
        room = {"id": "room123", "room_name": "Test Room"}
        config.current_room = room
        assert config.current_room == room
    
    def test_clear_session(self, config):
        """测试清除会话"""
        config.current_user = {"id": "user123"}
        config.current_room = {"id": "room123"}
        config.clear_session()
        assert config.current_user is None
        assert config.current_room is None
    
    def test_save_load(self, config, tmp_path):
        """测试保存和加载"""
        config.set("key1", "value1")
        config.set("key2", 123)
        
        # 重新加载
        config2 = Config()
        assert config2.get("key1") == "value1"
        assert config2.get("key2") == 123

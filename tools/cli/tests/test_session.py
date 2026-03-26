"""
会话管理测试
"""
import pytest
from ..session import Session


class TestSession:
    """会话管理测试类"""
    
    @pytest.fixture
    def session(self, monkeypatch, tmp_path):
        """创建测试会话"""
        # Mock config
        import os
        os.environ['HOME'] = str(tmp_path)
        
        sess = Session()
        yield sess
    
    def test_init(self, session):
        """测试初始化"""
        assert session.user is None
        assert session.room is None
        assert not session.is_logged_in
        assert not session.in_room
    
    def test_user_setter(self, session):
        """测试用户设置"""
        user = {"id": "user123", "nickname": "Test"}
        session.user = user
        assert session.user == user
        assert session.user_id == "user123"
        assert session.user_name == "Test"
    
    def test_is_logged_in(self, session):
        """测试登录状态"""
        assert not session.is_logged_in
        session.user = {"id": "user123"}
        assert session.is_logged_in
    
    def test_room_setter(self, session):
        """测试房间设置"""
        room = {"id": "room123", "room_name": "Test"}
        session.room = room
        assert session.room == room
        assert session.room_id == "room123"
        assert session.in_room
    
    def test_is_host(self, session):
        """测试房主检查"""
        session.user = {"id": "user123"}
        session.room = {"host_id": "user123"}
        assert session.is_host()
        
        session.room = {"host_id": "other_user"}
        assert not session.is_host()
    
    def test_clear(self, session):
        """测试清除会话"""
        session.user = {"id": "user123"}
        session.room = {"id": "room123"}
        session.clear()
        assert not session.is_logged_in
        assert not session.in_room

"""
会话管理 - 管理用户登录状态和房间状态
"""
from typing import Optional, Dict
from .config import config


class Session:
    """会话管理类"""
    
    def __init__(self):
        self._user: Optional[Dict] = None
        self._room: Optional[Dict] = None
        self.load()
    
    def load(self) -> None:
        """从配置加载会话"""
        self._user = config.current_user
        self._room = config.current_room
    
    def save(self) -> None:
        """保存会话到配置"""
        if self._user:
            config.current_user = self._user
        if self._room:
            config.current_room = self._room
    
    def clear(self) -> None:
        """清除会话"""
        self._user = None
        self._room = None
        config.clear_session()
    
    @property
    def user(self) -> Optional[Dict]:
        """获取当前用户"""
        return self._user
    
    @user.setter
    def user(self, user: Dict) -> None:
        self._user = user
        self.save()
    
    @property
    def user_id(self) -> Optional[str]:
        """获取当前用户 ID"""
        return self._user.get("id") if self._user else None
    
    @property
    def user_name(self) -> Optional[str]:
        """获取当前用户昵称"""
        return self._user.get("nickname") if self._user else None
    
    @property
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self._user is not None
    
    @property
    def room(self) -> Optional[Dict]:
        """获取当前房间"""
        return self._room
    
    @room.setter
    def room(self, room: Dict) -> None:
        self._room = room
        self.save()
    
    @property
    def room_id(self) -> Optional[str]:
        """获取当前房间 ID"""
        return self._room.get("id") if self._room else None
    
    @property
    def in_room(self) -> bool:
        """检查是否在房间中"""
        return self._room is not None
    
    def is_host(self) -> bool:
        """检查是否是房主"""
        if not self._room or not self._user:
            return False
        return self._room.get("host_id") == self._user.get("id")


# 全局会话实例
session = Session()

"""
配置管理 - 管理 CLI 配置文件
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict


class Config:
    """配置管理类"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".clawplaygame"
        self.config_file = self.config_dir / "config.json"
        self._config: Dict = {}
        self.load()
    
    def load(self) -> None:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  读取配置文件失败：{e}")
                self._config = {}
        else:
            self._config = {}
    
    def save(self) -> None:
        """保存配置"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default=None):
        """获取配置值"""
        return self._config.get(key, default)
    
    def set(self, key: str, value) -> None:
        """设置配置值"""
        self._config[key] = value
        self.save()
    
    def delete(self, key: str) -> None:
        """删除配置值"""
        if key in self._config:
            del self._config[key]
            self.save()
    
    @property
    def api_url(self) -> str:
        """获取 API 地址"""
        return self.get("api_url", "http://localhost:8000")
    
    @api_url.setter
    def api_url(self, value: str) -> None:
        self.set("api_url", value)
    
    @property
    def current_user(self) -> Optional[Dict]:
        """获取当前用户信息"""
        return self.get("current_user")
    
    @current_user.setter
    def current_user(self, user: Dict) -> None:
        self.set("current_user", user)
    
    @property
    def current_room(self) -> Optional[Dict]:
        """获取当前房间信息"""
        return self.get("current_room")
    
    @current_room.setter
    def current_room(self, room: Dict) -> None:
        self.set("current_room", room)
    
    def clear_session(self) -> None:
        """清除会话数据"""
        if "current_user" in self._config:
            del self._config["current_user"]
        if "current_room" in self._config:
            del self._config["current_room"]
        self.save()


# 全局配置实例
config = Config()

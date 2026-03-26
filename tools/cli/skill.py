"""
OpenClaw Skill 集成 - 自然语言命令
"""
import re
from typing import Optional, Dict, Any
from rich.console import Console

from .config import config
from .session import session
from .client import api_client

console = Console()


class ClawPlaySkill:
    """ClawPlayGame OpenClaw Skill"""
    
    def __init__(self):
        self.name = "clawplaygame"
        self.description = "ClawPlayGame 游戏平台控制技能"
    
    def handle(self, message: str) -> str:
        """处理自然语言消息"""
        message = message.lower().strip()
        
        # 游戏相关
        if any(kw in message for kw in ["游戏列表", "有什么游戏", "游戏有哪些"]):
            return self.list_games()
        
        if "选择游戏" in message or "玩" in message:
            game_match = re.search(r'(werewolf|avalon|botc|spyfall)', message)
            if game_match:
                return self.select_game(game_match.group(1))
        
        # 房间相关
        if "创建房间" in message or "开个房间" in message:
            room_match = re.search(r'创建房间 [ 名字名称]?[:：]?\s*(.+)', message)
            if room_match:
                return self.create_room(room_match.group(1))
        
        if "加入房间" in message or "进房间" in message:
            room_match = re.search(r'([a-z0-9]+)', message)
            if room_match:
                return self.join_room(room_match.group(1))
        
        if "房间信息" in message or "看看房间" in message:
            return self.room_info()
        
        # 准备相关
        if "准备" in message:
            return self.player_ready()
        
        # 聊天相关
        if message.startswith("发送 ") or message.startswith("说 "):
            msg = message[2:].strip() if message.startswith("发送 ") else message[1:].strip()
            return self.send_message(msg)
        
        # 房主相关
        if "开始游戏" in message and session.is_host():
            return self.host_start()
        
        if "解散房间" in message and session.is_host():
            return self.host_dismiss()
        
        # 状态查询
        if "状态" in message or "我在哪" in message:
            return self.status()
        
        # 帮助
        if "帮助" in message or "怎么用" in message:
            return self.help()
        
        return "我不太明白你的意思。可以说'游戏列表'、'创建房间 名字'、'准备'、'发送 消息'等。"
    
    def list_games(self) -> str:
        """列出游戏"""
        try:
            games = api_client.list_games()
            text = "🎮 可用游戏：\n"
            for game in games:
                status = "✓" if game["status"] == "active" else "🚧"
                text += f"  {status} {game['name']} ({game['min_players']}-{game['max_players']}人)\n"
            return text
        except Exception as e:
            return f"获取游戏列表失败：{e}"
    
    def select_game(self, game_id: str) -> str:
        """选择游戏"""
        try:
            game = api_client.get_game(game_id)
            config.set("current_game", game)
            return f"✓ 已选择游戏：{game['name']}。可以说'房间列表'查看房间。"
        except Exception as e:
            return f"选择游戏失败：{e}"
    
    def create_room(self, name: str) -> str:
        """创建房间"""
        if not session.is_logged_in:
            return "⚠️ 请先登录。可以说'游客登录'。"
        
        current_game = config.get("current_game")
        if not current_game:
            return "⚠️ 请先选择游戏。可以说'选择游戏 werewolf'。"
        
        try:
            room = api_client.create_room(
                game_id=current_game["id"],
                player_name=session.user_name,
                room_name=name,
                player_id=session.user_id
            )
            session.room = room
            return f"✓ 房间创建成功：{name}（ID: {room['id']}）。可以说'准备'。"
        except Exception as e:
            return f"创建房间失败：{e}"
    
    def join_room(self, room_id: str) -> str:
        """加入房间"""
        if not session.is_logged_in:
            return "⚠️ 请先登录。可以说'游客登录'。"
        
        try:
            result = api_client.join_room(
                room_id=room_id,
                player_name=session.user_name,
                player_id=session.user_id
            )
            session.room = result["room"]
            room = result["room"]
            return f"✓ 已加入房间：{room['room_name']}。当前人数：{len(room['players'])}/{room['max_players']}"
        except Exception as e:
            return f"加入房间失败：{e}"
    
    def room_info(self) -> str:
        """房间信息"""
        if not session.in_room:
            return "⚠️ 当前不在房间中。"
        
        room = session.room
        text = f"🏠 房间：{room['room_name']}\n"
        text += f"  人数：{len(room['players'])}/{room['max_players']}\n"
        text += f"  状态：{room['status']}\n"
        text += "  玩家：\n"
        for i, p in enumerate(room.get("players", []), 1):
            ready = "✓" if p.get("is_ready", 0) == 1 else " "
            host = "👑" if p.get("role") == "host" else " "
            me = " (我)" if p.get("player_id") == session.user_id else ""
            text += f"    {i}. {ready} {host} {p['player_name']}{me}\n"
        return text
    
    def player_ready(self) -> str:
        """准备"""
        if not session.in_room:
            return "⚠️ 当前不在房间中。"
        
        try:
            result = api_client.toggle_ready(
                room_id=session.room_id,
                player_id=session.user_id
            )
            session.room = api_client.get_room(session.room_id)
            status = "已准备" if result["is_ready"] else "已取消准备"
            return f"✓ {status}。"
        except Exception as e:
            return f"操作失败：{e}"
    
    def send_message(self, msg: str) -> str:
        """发送消息"""
        if not session.in_room:
            return "⚠️ 当前不在房间中。"
        
        try:
            api_client.send_message(
                room_id=session.room_id,
                player_id=session.user_id,
                content=msg
            )
            return f"✓ 消息已发送：{msg}"
        except Exception as e:
            return f"发送失败：{e}"
    
    def host_start(self) -> str:
        """开始游戏"""
        if not session.is_host():
            return "⚠️ 只有房主可以开始游戏。"
        
        try:
            api_client.start_game(session.room_id)
            return "✓ 游戏已开始！"
        except Exception as e:
            return f"开始游戏失败：{e}"
    
    def host_dismiss(self) -> str:
        """解散房间"""
        if not session.is_host():
            return "⚠️ 只有房主可以解散房间。"
        
        try:
            api_client.delete_room(
                room_id=session.room_id,
                host_id=session.user_id
            )
            session.room = None
            return "✓ 房间已解散。"
        except Exception as e:
            return f"解散失败：{e}"
    
    def status(self) -> str:
        """状态"""
        if not session.is_logged_in:
            return "⚠️ 未登录。可以说'游客登录'。"
        
        text = f"👤 用户：{session.user_name}\n"
        if session.in_room:
            text += f"🏠 房间：{session.room.get('room_name')}\n"
            text += f"  状态：{session.room.get('status')}\n"
        else:
            text += "  房间：无\n"
        return text
    
    def help(self) -> str:
        """帮助"""
        return """📖 ClawPlayGame 技能帮助：

游戏相关：
  - "游戏列表" - 查看所有游戏
  - "选择游戏 werewolf" - 选择狼人杀
  - "房间列表" - 查看房间

房间相关：
  - "创建房间 名字" - 创建房间
  - "加入房间 abc123" - 加入房间
  - "房间信息" - 查看房间

游戏操作：
  - "准备" - 准备/取消准备
  - "发送 大家好" - 发送消息
  - "开始游戏" - 开始游戏（房主）
  - "解散房间" - 解散房间（房主）

其他：
  - "状态" - 查看当前状态
  - "帮助" - 显示帮助"""


# 全局 Skill 实例
skill = ClawPlaySkill()

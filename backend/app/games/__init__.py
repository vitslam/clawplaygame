"""
游戏管理器 - 管理所有游戏实例
"""
from typing import Dict, Optional
from app.games.avalon import AvalonGame

class GameManager:
    """游戏管理器"""
    
    def __init__(self):
        # room_id -> game instance
        self.games: Dict[str, AvalonGame] = {}
    
    def create_game(self, room_id: str, game_type: str) -> Optional[AvalonGame]:
        """创建新游戏"""
        if game_type != "avalon":
            return None
        
        game = AvalonGame(room_id=room_id)
        self.games[room_id] = game
        return game
    
    def get_game(self, room_id: str) -> Optional[AvalonGame]:
        """获取游戏实例"""
        return self.games.get(room_id)
    
    def delete_game(self, room_id: str) -> bool:
        """删除游戏"""
        if room_id in self.games:
            del self.games[room_id]
            return True
        return False
    
    def get_all_games(self) -> Dict[str, AvalonGame]:
        """获取所有游戏"""
        return self.games


# 全局游戏管理器
game_manager = GameManager()

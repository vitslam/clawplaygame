"""
游戏管理器 - 管理所有游戏实例
"""
from typing import Dict, Optional, Any

class GameManager:
    """游戏管理器"""
    
    def __init__(self):
        # room_id -> game instance
        self.games: Dict[str, Any] = {}
    
    def create_game(self, room_id: str, game_type: str, event_callback=None) -> Optional[Any]:
        """创建新游戏"""
        if game_type == "avalon":
            from app.games.avalon import AvalonGame
            game = AvalonGame(room_id=room_id)
        elif game_type == "doudizhu":
            from app.games.doudizhu import DouDizhuGame
            game = DouDizhuGame(room_id=room_id, event_callback=event_callback)
        elif game_type == "werewolf":
            # TODO: 狼人杀游戏实现
            return None
        else:
            return None
        
        self.games[room_id] = game
        return game
    
    def get_game(self, room_id: str) -> Optional[Any]:
        """获取游戏实例"""
        return self.games.get(room_id)
    
    def delete_game(self, room_id: str) -> bool:
        """删除游戏"""
        if room_id in self.games:
            del self.games[room_id]
            return True
        return False
    
    def get_all_games(self) -> Dict[str, Any]:
        """获取所有游戏"""
        return self.games


# 全局游戏管理器
game_manager = GameManager()

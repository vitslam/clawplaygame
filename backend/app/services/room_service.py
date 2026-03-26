"""
房间管理服务 - 业务逻辑层
"""
from app import db
from typing import Optional, List, Dict


class RoomService:
    """房间服务"""
    
    @staticmethod
    def create_room(room_id: str, game_id: str, room_name: str, host_id: str, 
                   host_name: str, max_players: int = 10, is_public: bool = True) -> bool:
        """创建房间"""
        return db.create_room(room_id, game_id, room_name, host_id, host_name, 
                            max_players, is_public)
    
    @staticmethod
    def get_room(room_id: str) -> Optional[Dict]:
        """获取房间信息"""
        return db.get_room_with_session(room_id)
    
    @staticmethod
    def get_rooms_by_game(game_id: str) -> List[Dict]:
        """获取游戏的所有房间"""
        rooms = db.get_rooms_by_game(game_id)
        result = []
        for room in rooms:
            players = db.get_room_players(room["id"])
            room_data = {
                **room,
                "players": players,
                "is_public": bool(room["is_public"])
            }
            result.append(room_data)
        return result
    
    @staticmethod
    def join_room(room_id: str, player_id: str, player_name: str) -> Optional[Dict]:
        """加入房间"""
        room = db.get_room_with_session(room_id)
        if not room:
            return None
        
        players = db.get_room_players(room_id)
        if len(players) >= room["max_players"]:
            raise ValueError("房间已满")
        
        if room["status"] != "waiting":
            raise ValueError("游戏已开始")
        
        # 检查是否已经在房间里
        existing_player = next((p for p in players if p["player_id"] == player_id), None)
        if existing_player:
            return {"room": room, "players": players, "already_joined": True}
        
        # 添加到房间
        db.add_player_to_room(room_id, player_id, player_name)
        
        # 添加系统消息
        db.add_message(room_id, f"{player_name} 加入了房间", "system")
        
        # 返回更新后的房间
        players = db.get_room_players(room_id)
        room = db.get_room_with_session(room_id)
        
        return {
            "room": room,
            "players": players,
            "already_joined": False
        }
    
    @staticmethod
    def kick_player(room_id: str, host_id: str, player_id: str) -> bool:
        """踢出玩家"""
        room = db.get_room(room_id)
        if not room:
            raise ValueError("房间不存在")
        
        if room["status"] != "waiting":
            raise ValueError("游戏已开始，无法踢人")
        
        if host_id != room["host_id"]:
            raise ValueError("只有房主有此权限")
        
        if player_id == room["host_id"]:
            raise ValueError("不能踢出房主自己")
        
        # 获取玩家名称
        players = db.get_room_players(room_id)
        player = next((p for p in players if p["player_id"] == player_id), None)
        player_name = player["player_name"] if player else player_id
        
        db.kick_player(room_id, player_id)
        db.add_message(room_id, f"玩家 {player_name} 被房主移出房间", "system")
        
        return True
    
    @staticmethod
    def transfer_host(room_id: str, host_id: str, new_host_id: str) -> bool:
        """移交房主"""
        room = db.get_room(room_id)
        if not room:
            raise ValueError("房间不存在")
        
        if room["status"] != "waiting":
            raise ValueError("游戏已开始，无法移交房主")
        
        if host_id != room["host_id"]:
            raise ValueError("只有房主有此权限")
        
        players = db.get_room_players(room_id)
        new_host = next((p for p in players if p["player_id"] == new_host_id), None)
        if not new_host:
            raise ValueError("玩家不在房间中")
        
        db.transfer_host(room_id, new_host_id, new_host["player_name"])
        db.add_message(room_id, f"房主将权限移交给 {new_host['player_name']}", "system")
        
        return True
    
    @staticmethod
    def update_room(room_id: str, host_id: str, room_name: str = None, 
                   is_public: bool = None) -> Dict:
        """修改房间信息"""
        room = db.get_room(room_id)
        if not room:
            raise ValueError("房间不存在")
        
        if room["status"] != "waiting":
            raise ValueError("游戏已开始，无法修改房间信息")
        
        if host_id != room["host_id"]:
            raise ValueError("只有房主有此权限")
        
        # 获取房主名称
        players = db.get_room_players(room_id)
        host_player = next((p for p in players if p["player_id"] == host_id), None)
        host_name = host_player["player_name"] if host_player else "房主"
        
        # 记录修改内容
        if room_name and room_name != room["room_name"]:
            db.add_message(room_id, f"{host_name} 将房间名称修改为：{room_name}", "action", host_id, host_name)
        
        if is_public is not None and is_public != room["is_public"]:
            status_text = "公开" if is_public else "私有"
            db.add_message(room_id, f"{host_name} 将房间设置为{status_text}", "action", host_id, host_name)
        
        db.update_room_info(room_id, room_name, is_public)
        
        updated_room = db.get_room(room_id)
        players = db.get_room_players(room_id)
        
        return {
            **updated_room,
            "players": players,
            "is_public": bool(updated_room["is_public"])
        }
    
    @staticmethod
    def delete_room(room_id: str, host_id: str) -> bool:
        """解散房间"""
        room = db.get_room(room_id)
        if not room:
            raise ValueError("房间不存在")
        
        if room["status"] != "waiting":
            raise ValueError("游戏已开始，无法解散房间")
        
        if host_id != room["host_id"]:
            raise ValueError("只有房主有此权限")
        
        db.delete_room(room_id)
        return True
    
    @staticmethod
    def toggle_ready(room_id: str, player_id: str) -> bool:
        """切换准备状态"""
        room = db.get_room(room_id)
        if not room:
            raise ValueError("房间不存在")
        
        if room["status"] != "waiting":
            raise ValueError("游戏已开始，无法切换准备状态")
        
        # 获取玩家名称
        players = db.get_room_players(room_id)
        player = next((p for p in players if p["player_id"] == player_id), None)
        if not player:
            raise ValueError("玩家不在房间中")
        
        # 切换准备状态
        is_ready = db.toggle_player_ready(room_id, player_id)
        
        # 发送动作消息
        action_text = "已准备" if is_ready else "取消了准备"
        db.add_message(room_id, f"{player['player_name']} {action_text}", "action", 
                      player_id, player['player_name'])
        
        return is_ready

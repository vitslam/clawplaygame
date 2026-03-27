from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional, Set
import asyncio
import json
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """事件类型枚举"""
    CHAT = "chat"
    PLAYER_JOIN = "player_join"
    PLAYER_LEAVE = "player_leave"
    PLAYER_READY = "player_ready"
    PLAYER_NOT_READY = "player_not_ready"
    ROOM_UPDATE = "room_update"
    GAME_STATE = "game_state"
    SYSTEM = "system"
    KICKED = "kicked"


class ConnectionInfo:
    """连接信息"""
    def __init__(self, websocket: WebSocket, player_id: str, player_name: str = ""):
        self.websocket = websocket
        self.player_id = player_id
        self.player_name = player_name
        self.connected_at = datetime.now()
        self.last_heartbeat = datetime.now()


class WebSocketManager:
    """WebSocket 连接管理器 - 支持发布/订阅模式"""
    
    def __init__(self):
        self.rooms: Dict[str, Dict[str, ConnectionInfo]] = {}
        self.connection_room: Dict[WebSocket, str] = {}
        self.reconnect_cache: Dict[str, dict] = {}
    
    async def connect(
        self, 
        websocket: WebSocket, 
        room_id: str, 
        player_id: str,
        player_name: str = "",
        reconnect_token: Optional[str] = None
    ) -> bool:
        """连接 WebSocket (假设已经 accept 过了)"""
        # 检查是否是重连
        if reconnect_token and player_id in self.reconnect_cache:
            cached = self.reconnect_cache[player_id]
            if cached.get("room_id") == room_id and cached.get("token") == reconnect_token:
                del self.reconnect_cache[player_id]
        
        # 初始化房间
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        
        # 如果玩家已存在，先断开旧连接
        if player_id in self.rooms[room_id]:
            old_conn = self.rooms[room_id][player_id]
            try:
                await old_conn.websocket.close()
            except:
                pass
            if old_conn.websocket in self.connection_room:
                del self.connection_room[old_conn.websocket]
        
        # 创建新连接
        conn_info = ConnectionInfo(websocket, player_id, player_name)
        self.rooms[room_id][player_id] = conn_info
        self.connection_room[websocket] = room_id
        
        return True
    
    async def disconnect(self, websocket: WebSocket, save_for_reconnect: bool = True):
        """断开 WebSocket 连接"""
        room_id = self.connection_room.get(websocket)
        if not room_id:
            return
        
        conn_info = self.rooms[room_id].get(
            next((pid for pid, c in self.rooms[room_id].items() if c.websocket == websocket), None)
        )
        
        if conn_info:
            player_id = conn_info.player_id
            player_name = conn_info.player_name
            
            if player_id in self.reconnect_cache:
                del self.reconnect_cache[player_id]
            
            del self.rooms[room_id][player_id]
            del self.connection_room[websocket]
            
            if not self.rooms[room_id]:
                del self.rooms[room_id]
            
            if not save_for_reconnect:
                await self.broadcast_event(
                    room_id,
                    EventType.PLAYER_LEAVE,
                    {"player_id": player_id, "player_name": player_name}
                )
    
    async def broadcast_event(self, room_id: str, event_type: EventType, data: dict):
        """广播事件给房间内所有玩家"""
        message = {
            "type": event_type.value,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "room_id": room_id
        }
        print(f"[WS 广播] 房间：{room_id}, 消息：{message}", flush=True)
        await self.broadcast(room_id, message)
    
    async def broadcast(self, room_id: str, message: dict, exclude_player_id: Optional[str] = None):
        """广播消息给房间内所有玩家"""
        print(f"[WS broadcast] 房间:{room_id} 连接数:{len(self.rooms.get(room_id, {}))} 玩家:{list(self.rooms.get(room_id, {}).keys())}", flush=True)
        if room_id not in self.rooms:
            print(f"[WS broadcast] 房间不存在", flush=True)
            return
        
        connections = list(self.rooms[room_id].values())
        print(f"[WS broadcast] 准备发送给 {len(connections)} 个连接", flush=True)
        tasks = []
        
        for conn in connections:
            if exclude_player_id and conn.player_id == exclude_player_id:
                continue
            tasks.append(self._safe_send(conn.websocket, message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_to_player(self, room_id: str, player_id: str, message: dict) -> bool:
        """发送消息给指定玩家"""
        if room_id not in self.rooms:
            return False
        
        conn = self.rooms[room_id].get(player_id)
        if not conn:
            return False
        
        return await self._safe_send(conn.websocket, message)
    
    async def _safe_send(self, websocket: WebSocket, message: dict) -> bool:
        """安全发送消息"""
        try:
            await websocket.send_json(message)
            return True
        except Exception as e:
            print(f"[WS] 发送失败：{e}")
            return False
    
    async def handle_message(self, room_id: str, player_id: str, message: dict):
        """处理客户端消息并广播"""
        event_type = message.get("type", "chat")
        data = message.get("data", message)
        data["sender_id"] = player_id
        
        type_mapping = {
            "chat": EventType.CHAT,
            "ready": EventType.PLAYER_READY,
            "not_ready": EventType.PLAYER_NOT_READY,
        }
        
        ws_type = type_mapping.get(event_type, EventType.SYSTEM)
        await self.broadcast_event(room_id, ws_type, data)
    
    def get_room_players(self, room_id: str) -> List[dict]:
        """获取房间在线玩家列表"""
        if room_id not in self.rooms:
            return []
        
        return [
            {
                "player_id": conn.player_id,
                "player_name": conn.player_name,
                "connected_at": conn.connected_at.isoformat()
            }
            for conn in self.rooms[room_id].values()
        ]
    
    def get_player_count(self, room_id: str) -> int:
        """获取房间在线玩家数"""
        return len(self.rooms.get(room_id, {}))
    
    def is_player_connected(self, room_id: str, player_id: str) -> bool:
        """检查玩家是否在线"""
        return room_id in self.rooms and player_id in self.rooms[room_id]
    
    def generate_reconnect_token(self, player_id: str, room_id: str) -> str:
        """生成重连令牌"""
        import secrets
        token = secrets.token_urlsafe(16)
        self.reconnect_cache[player_id] = {
            "room_id": room_id,
            "token": token,
            "created_at": datetime.now().isoformat()
        }
        return token
    
    async def cleanup_stale_connections(self, timeout_seconds: int = 300):
        """清理超时未心跳的连接"""
        now = datetime.now()
        stale_players = []
        
        for room_id, players in list(self.rooms.items()):
            for player_id, conn in list(players.items()):
                if (now - conn.last_heartbeat).total_seconds() > timeout_seconds:
                    stale_players.append((room_id, player_id, conn.websocket))
        
        for room_id, player_id, websocket in stale_players:
            print(f"[WS] 清理超时连接：{player_id}")
            await self.disconnect(websocket, save_for_reconnect=False)
    
    def update_heartbeat(self, room_id: str, player_id: str):
        """更新玩家心跳"""
        if room_id in self.rooms and player_id in self.rooms[room_id]:
            self.rooms[room_id][player_id].last_heartbeat = datetime.now()

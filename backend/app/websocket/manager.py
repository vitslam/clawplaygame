from fastapi import WebSocket
from typing import Dict, List
import asyncio


class WebSocketManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        # room_id -> [WebSocket connections]
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # WebSocket -> player_id
        self.player_mapping: Dict[WebSocket, str] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str):
        """连接 WebSocket"""
        await websocket.accept()
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        
        self.active_connections[room_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, room_id: str):
        """断开 WebSocket 连接"""
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
        
        if websocket in self.player_mapping:
            del self.player_mapping[websocket]
    
    async def broadcast(self, room_id: str, message: dict):
        """广播消息给房间内所有玩家"""
        if room_id in self.active_connections:
            # 异步发送给所有连接
            await asyncio.gather(
                *[self.send_json(connection, message) 
                  for connection in self.active_connections[room_id]],
                return_exceptions=True
            )
    
    async def send_json(self, websocket: WebSocket, message: dict):
        """发送 JSON 消息"""
        import json
        await websocket.send_json(message)
    
    def get_player_id(self, websocket: WebSocket) -> str:
        """获取玩家 ID"""
        return self.player_mapping.get(websocket, "unknown")
    
    def set_player_id(self, websocket: WebSocket, player_id: str):
        """设置玩家 ID 映射"""
        self.player_mapping[websocket] = player_id
    
    def get_room_players(self, room_id: str) -> int:
        """获取房间在线玩家数"""
        return len(self.active_connections.get(room_id, []))

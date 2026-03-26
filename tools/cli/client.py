"""
API 客户端 - 封装 ClawPlayGame 后端 API
"""
import httpx
import asyncio
import websockets
from typing import Optional, Dict, List, Callable, Any
from .config import config


class APIClient:
    """API 客户端类"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or config.api_url
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._message_handlers: List[Callable] = []
    
    async def close(self) -> None:
        """关闭客户端"""
        await self._client.aclose()
        if self._ws:
            await self._ws.close()
    
    # ========== 用户认证 API ==========
    
    async def register(self, username: str, password: str, nickname: str) -> Dict:
        """注册用户"""
        response = await self._client.post(
            "/api/users/register",
            json={
                "username": username,
                "password": password,
                "nickname": nickname
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def login(self, username: str, password: str) -> Dict:
        """用户登录"""
        response = await self._client.post(
            "/api/users/login",
            json={
                "username": username,
                "password": password
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def get_user(self, user_id: str) -> Dict:
        """获取用户信息"""
        response = await self._client.get(f"/api/users/{user_id}")
        response.raise_for_status()
        return response.json()
    
    async def update_heartbeat(self, user_id: str) -> None:
        """更新用户活跃时间"""
        await self._client.post(f"/api/users/{user_id}/heartbeat")
    
    # ========== 游戏 API ==========
    
    async def list_games(self) -> List[Dict]:
        """获取所有游戏列表"""
        response = await self._client.get("/api/games")
        response.raise_for_status()
        return response.json()
    
    async def get_game(self, game_id: str) -> Dict:
        """获取游戏详情"""
        response = await self._client.get(f"/api/games/{game_id}")
        response.raise_for_status()
        return response.json()
    
    async def list_rooms(self, game_id: str) -> List[Dict]:
        """获取游戏的所有房间"""
        response = await self._client.get(f"/api/rooms/{game_id}/rooms")
        response.raise_for_status()
        return response.json()
    
    # ========== 房间 API ==========
    
    async def create_room(
        self,
        game_id: str,
        player_name: str,
        room_name: str,
        max_players: int = 10,
        is_public: bool = True,
        player_id: Optional[str] = None
    ) -> Dict:
        """创建房间"""
        params = {}
        if player_id:
            params["player_id"] = player_id
        
        response = await self._client.post(
            f"/api/rooms/{game_id}/rooms",
            params=params,
            json={
                "player_name": player_name,
                "room_name": room_name,
                "max_players": max_players,
                "is_public": is_public
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def get_room(self, room_id: str) -> Dict:
        """获取房间信息"""
        response = await self._client.get(f"/api/rooms/{room_id}")
        response.raise_for_status()
        return response.json()
    
    async def join_room(self, room_id: str, player_name: str, player_id: Optional[str] = None) -> Dict:
        """加入房间"""
        response = await self._client.post(
            f"/api/rooms/{room_id}/join",
            json={
                "player_name": player_name,
                "player_id": player_id
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def leave_room(self, room_id: str) -> None:
        """离开房间（前端逻辑，后端无直接接口）"""
        pass
    
    async def kick_player(self, room_id: str, player_id: str, host_id: str) -> Dict:
        """踢出玩家"""
        response = await self._client.post(
            f"/api/rooms/{room_id}/kick",
            params={"host_id": host_id},
            json={"player_id": player_id}
        )
        response.raise_for_status()
        return response.json()
    
    async def transfer_host(self, room_id: str, new_host_id: str, host_id: str) -> Dict:
        """移交房主"""
        response = await self._client.post(
            f"/api/rooms/{room_id}/transfer-host",
            params={"host_id": host_id},
            json={"new_host_id": new_host_id}
        )
        response.raise_for_status()
        return response.json()
    
    async def update_room(
        self,
        room_id: str,
        host_id: str,
        room_name: Optional[str] = None,
        is_public: Optional[bool] = None
    ) -> Dict:
        """修改房间信息"""
        json_data = {}
        if room_name is not None:
            json_data["room_name"] = room_name
        if is_public is not None:
            json_data["is_public"] = is_public
        
        response = await self._client.put(
            f"/api/rooms/{room_id}",
            params={"host_id": host_id},
            json=json_data
        )
        response.raise_for_status()
        return response.json()
    
    async def delete_room(self, room_id: str, host_id: str) -> Dict:
        """解散房间"""
        response = await self._client.delete(
            f"/api/rooms/{room_id}",
            params={"host_id": host_id}
        )
        response.raise_for_status()
        return response.json()
    
    async def toggle_ready(self, room_id: str, player_id: str) -> Dict:
        """切换准备状态"""
        response = await self._client.post(
            f"/api/rooms/{room_id}/toggle-ready",
            json={"player_id": player_id}
        )
        response.raise_for_status()
        return response.json()
    
    async def start_game(self, room_id: str) -> Dict:
        """开始游戏"""
        response = await self._client.post(f"/api/rooms/{room_id}/start")
        response.raise_for_status()
        return response.json()
    
    # ========== 消息 API ==========
    
    async def send_message(
        self,
        room_id: str,
        player_id: str,
        content: str,
        message_type: str = "chat"
    ) -> Dict:
        """发送消息"""
        response = await self._client.post(
            f"/api/rooms/{room_id}/messages",
            json={
                "player_id": player_id,
                "content": content,
                "message_type": message_type
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def get_messages(self, room_id: str, limit: int = 50) -> List[Dict]:
        """获取消息历史"""
        response = await self._client.get(
            f"/api/rooms/{room_id}/messages",
            params={"limit": limit}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("messages", [])
    
    # ========== WebSocket ==========
    
    async def connect_ws(self, room_id: str) -> None:
        """连接 WebSocket"""
        ws_url = f"ws://{self.base_url.replace('http://', '')}/ws/rooms/{room_id}"
        self._ws = await websockets.connect(ws_url)
    
    async def disconnect_ws(self) -> None:
        """断开 WebSocket"""
        if self._ws:
            await self._ws.close()
            self._ws = None
    
    async def ws_send(self, message: Dict) -> None:
        """通过 WebSocket 发送消息"""
        if self._ws:
            await self._ws.send(httpx.Headers.serialize(message))
    
    async def ws_listen(self, callback: Callable[[Dict], None]) -> None:
        """监听 WebSocket 消息"""
        if not self._ws:
            raise RuntimeError("WebSocket not connected")
        
        async for message in self._ws:
            try:
                data = httpx.Headers.parse(message)
                callback(data)
            except Exception as e:
                print(f"⚠️  解析 WebSocket 消息失败：{e}")
    
    def add_message_handler(self, handler: Callable[[Dict], None]) -> None:
        """添加消息处理器"""
        self._message_handlers.append(handler)


# 全局 API 客户端实例
api_client = APIClient()

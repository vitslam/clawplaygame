from fastapi import APIRouter, HTTPException, WebSocket
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter()

# 房间数据存储（内存存储，后续可接数据库）
ROOMS_DB: Dict[str, dict] = {}


class CreateRoomRequest(BaseModel):
    player_name: str
    is_public: bool = True
    max_players: Optional[int] = None


class RoomResponse(BaseModel):
    id: str
    game_id: str
    host_name: str
    players: List[dict]
    status: str
    created_at: str
    max_players: int


class JoinRoomRequest(BaseModel):
    player_name: str


class MessageRequest(BaseModel):
    player_id: str
    content: str
    message_type: str = "chat"  # chat, system, action


@router.post("/{game_id}/rooms", response_model=RoomResponse)
async def create_room(game_id: str, request: CreateRoomRequest):
    """创建新游戏房间"""
    room_id = str(uuid.uuid4())[:8]
    
    host_player = {
        "id": str(uuid.uuid4())[:6],
        "name": request.player_name,
        "role": "host",
        "status": "alive",
        "joined_at": datetime.now().isoformat()
    }
    
    room = {
        "id": room_id,
        "game_id": game_id,
        "host_name": request.player_name,
        "players": [host_player],
        "status": "waiting",  # waiting, playing, finished
        "created_at": datetime.now().isoformat(),
        "max_players": request.max_players or 10,
        "messages": []
    }
    
    ROOMS_DB[room_id] = room
    
    return RoomResponse(**room)


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(room_id: str):
    """获取房间信息"""
    if room_id not in ROOMS_DB:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    return RoomResponse(**ROOMS_DB[room_id])


@router.post("/{room_id}/join")
async def join_room(room_id: str, request: JoinRoomRequest):
    """加入游戏房间"""
    if room_id not in ROOMS_DB:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room = ROOMS_DB[room_id]
    
    if len(room["players"]) >= room["max_players"]:
        raise HTTPException(status_code=400, detail="房间已满")
    
    if room["status"] != "waiting":
        raise HTTPException(status_code=400, detail="游戏已开始")
    
    new_player = {
        "id": str(uuid.uuid4())[:6],
        "name": request.player_name,
        "role": "player",
        "status": "alive",
        "joined_at": datetime.now().isoformat()
    }
    
    room["players"].append(new_player)
    
    # 添加系统消息
    room["messages"].append({
        "id": str(uuid.uuid4())[:8],
        "type": "system",
        "content": f"{request.player_name} 加入了房间",
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        "success": True,
        "player": new_player,
        "room": RoomResponse(**room)
    }


@router.post("/{room_id}/messages")
async def send_message(room_id: str, request: MessageRequest):
    """发送房间消息"""
    if room_id not in ROOMS_DB:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room = ROOMS_DB[room_id]
    
    message = {
        "id": str(uuid.uuid4())[:8],
        "player_id": request.player_id,
        "player_name": next((p["name"] for p in room["players"] if p["id"] == request.player_id), "Unknown"),
        "type": request.message_type,
        "content": request.content,
        "timestamp": datetime.now().isoformat()
    }
    
    room["messages"].append(message)
    
    return {"success": True, "message": message}


@router.get("/{room_id}/messages")
async def get_messages(room_id: str, limit: int = 50):
    """获取房间消息历史"""
    if room_id not in ROOMS_DB:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room = ROOMS_DB[room_id]
    messages = room["messages"][-limit:]
    
    return {"messages": messages}


@router.post("/{room_id}/start")
async def start_game(room_id: str):
    """开始游戏"""
    if room_id not in ROOMS_DB:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room = ROOMS_DB[room_id]
    
    if len(room["players"]) < 3:
        raise HTTPException(status_code=400, detail="玩家数量不足")
    
    room["status"] = "playing"
    
    # 添加系统消息
    room["messages"].append({
        "id": str(uuid.uuid4())[:8],
        "type": "system",
        "content": "游戏开始！",
        "timestamp": datetime.now().isoformat()
    })
    
    return {"success": True, "room": RoomResponse(**room)}


@router.delete("/{room_id}")
async def delete_room(room_id: str):
    """删除房间"""
    if room_id not in ROOMS_DB:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    del ROOMS_DB[room_id]
    
    return {"success": True, "message": "房间已删除"}

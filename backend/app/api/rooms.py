"""
房间管理 API - 接口声明层
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.services.room_service import RoomService
from app import db
import uuid

router = APIRouter()

# 预制房间数据
MOCK_ROOMS = [
    {
        "game_id": "werewolf",
        "name": "新手教学局",
        "host": "Lobster_01",
        "players": 6,
        "max": 9,
        "status": "playing",
        "session": {
            "phase": "night",
            "night_count": 1,
            "alive_roles": '["werewolf", "werewolf", "seer", "witch", "villager", "villager"]',
            "last_killed": None,
            "game_log": ["游戏开始", "天黑请闭眼", "狼人请睁眼"]
        }
    },
    {
        "game_id": "werewolf",
        "name": "高手进阶局",
        "host": "Crab_King",
        "players": 8,
        "max": 9,
        "status": "playing",
        "session": {
            "phase": "day",
            "night_count": 3,
            "alive_roles": '["werewolf", "seer", "witch", "villager", "hunter", "villager"]',
            "last_killed": "player_3",
            "game_log": ["游戏开始", "第 1 夜：玩家 4 死亡", "第 2 夜：玩家 2 死亡", "第 3 夜：玩家 3 死亡", "天亮了，开始讨论"]
        }
    },
    {
        "game_id": "werewolf",
        "name": "决赛圈",
        "host": "Shrimp_Boy",
        "players": 4,
        "max": 9,
        "status": "playing",
        "session": {
            "phase": "voting",
            "night_count": 5,
            "alive_roles": '["werewolf", "seer", "villager", "hunter"]',
            "last_killed": "player_5",
            "game_log": ["游戏开始", "第 1-4 夜多人死亡", "第 5 夜：玩家 5 死亡", "决赛圈！4 人存活", "请投票"]
        }
    },
]


def init_mock_rooms():
    """初始化预制房间到数据库"""
    existing = db.get_rooms_by_game("werewolf")
    if existing:
        print(f"✅ 数据库已有房间，跳过预制房间初始化")
        return
    
    for i, mock in enumerate(MOCK_ROOMS):
        room_id = f"mock_{i:03d}"
        host_id = f"host_{i}"
        session_id = f"session_{i:03d}"
        
        db.create_user(host_id, mock["host"])
        
        db.create_room(
            room_id=room_id,
            game_id=mock["game_id"],
            room_name=mock["name"],
            host_id=host_id,
            host_name=mock["host"],
            max_players=mock["max"],
            is_public=True,
            status=mock["status"]
        )
        
        for j in range(mock["players"]):
            player_id = f"p_{i}_{j}"
            player_name = f"玩家{j+1}"
            db.create_user(player_id, player_name)
            db.add_player_to_room(room_id, player_id, player_name)
        
        if mock.get("session"):
            db.create_game_session(session_id, room_id, mock["game_id"], mock["session"])
            db.update_room_session(room_id, session_id)
            
            for log_entry in mock["session"].get("game_log", []):
                db.add_message(room_id, log_entry, "system")
    
    print(f"✅ 已初始化 {len(MOCK_ROOMS)} 个预制房间到数据库")


class CreateRoomRequest(BaseModel):
    player_name: str
    room_name: str
    max_players: int = 10
    is_public: bool = True


class RoomResponse(BaseModel):
    id: str
    game_id: str
    room_name: str
    host_id: str
    host_name: str
    players: List[dict]
    status: str
    created_at: str
    max_players: int
    is_public: bool = True
    current_session_id: Optional[str] = None


class JoinRoomRequest(BaseModel):
    player_name: str
    player_id: Optional[str] = None


class MessageRequest(BaseModel):
    player_id: str
    content: str
    message_type: str = "chat"


class ToggleReadyRequest(BaseModel):
    player_id: str


class KickPlayerRequest(BaseModel):
    player_id: str


class TransferHostRequest(BaseModel):
    new_host_id: str


class UpdateRoomRequest(BaseModel):
    room_name: Optional[str] = None
    is_public: Optional[bool] = None


@router.post("/{game_id}/rooms", response_model=RoomResponse)
async def create_room(game_id: str, request: CreateRoomRequest, player_id: str = None):
    """创建新游戏房间"""
    room_id = str(uuid.uuid4())[:8]
    host_id = player_id or str(uuid.uuid4())[:12]
    
    # 创建/更新用户
    from app import db
    db.create_or_update_user(host_id, request.player_name)
    
    # 创建房间
    RoomService.create_room(
        room_id=room_id,
        game_id=game_id,
        room_name=request.room_name,
        host_id=host_id,
        host_name=request.player_name,
        max_players=request.max_players,
        is_public=request.is_public
    )
    
    # 获取房间数据
    room_data = RoomService.get_room(room_id)
    if not room_data:
        raise HTTPException(status_code=500, detail="创建房间失败")
    
    return RoomResponse(**room_data)


@router.get("/{game_id}/rooms", response_model=List[RoomResponse])
async def list_rooms(game_id: str):
    """获取指定游戏的所有房间"""
    rooms = RoomService.get_rooms_by_game(game_id)
    return [RoomResponse(**room) for room in rooms]


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(room_id: str):
    """获取房间信息"""
    room = RoomService.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    # 获取玩家列表
    players = db.get_room_players(room_id)
    room["players"] = players
    
    return RoomResponse(**room)


@router.post("/{room_id}/join")
async def join_room(room_id: str, request: JoinRoomRequest):
    """加入游戏房间"""
    from app import db
    
    player_id = request.player_id or str(uuid.uuid4())[:12]
    db.create_or_update_user(player_id, request.player_name)
    
    result = RoomService.join_room(room_id, player_id, request.player_name)
    if not result:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    try:
        if result.get("already_joined"):
            raise ValueError("房间已满")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    room_data = RoomService.get_room(room_id)
    room_data["players"] = db.get_room_players(room_id)
    if not room_data:
        raise HTTPException(status_code=500, detail="获取房间失败")
    
    return {
        "success": True,
        "player": {"id": player_id, "name": request.player_name},
        "room": RoomResponse(**room_data),
        "already_joined": result.get("already_joined", False)
    }


@router.post("/{room_id}/messages")
async def send_message(room_id: str, request: MessageRequest):
    """发送房间消息"""
    from app import db
    
    room = db.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    players = db.get_room_players(room_id)
    player_name = next((p["player_name"] for p in players if p["player_id"] == request.player_id), "Unknown")
    
    db.add_message(room_id, request.content, request.message_type, request.player_id, player_name)
    
    return {"success": True}


@router.get("/{room_id}/messages")
async def get_messages(room_id: str, limit: int = 50):
    """获取房间消息历史"""
    from app import db
    
    room = db.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    messages = db.get_room_messages(room_id, limit)
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            "id": msg["id"],
            "player_id": msg["player_id"],
            "player_name": msg["player_name"],
            "type": msg["message_type"],
            "content": msg["content"],
            "timestamp": msg["created_at"]
        })
    formatted_messages.reverse()
    
    return {"messages": formatted_messages}


@router.post("/{room_id}/toggle-ready")
async def toggle_ready(room_id: str, request: ToggleReadyRequest):
    """切换玩家准备状态"""
    try:
        is_ready = RoomService.toggle_ready(room_id, request.player_id)
        
        # 获取更新后的玩家信息
        from app import db
        players = db.get_room_players(room_id)
        player = next((p for p in players if p["player_id"] == request.player_id), None)
        
        return {
            "success": True,
            "is_ready": is_ready,
            "player": player
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{room_id}/kick")
async def kick_player(room_id: str, request: KickPlayerRequest, host_id: str = None):
    """房主踢出玩家"""
    try:
        RoomService.kick_player(room_id, host_id, request.player_id)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=400 if "房主" not in str(e) else 403, detail=str(e))


@router.post("/{room_id}/transfer-host")
async def transfer_host(room_id: str, request: TransferHostRequest, host_id: str = None):
    """移交房主权限"""
    try:
        RoomService.transfer_host(room_id, host_id, request.new_host_id)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=400 if "房主" not in str(e) else 403, detail=str(e))


@router.put("/{room_id}")
async def update_room(room_id: str, request: UpdateRoomRequest, host_id: str = None):
    """修改房间信息"""
    try:
        room = RoomService.update_room(room_id, host_id, request.room_name, request.is_public)
        return room
    except ValueError as e:
        raise HTTPException(status_code=400 if "房主" not in str(e) else 403, detail=str(e))


@router.delete("/{room_id}")
async def delete_room(room_id: str, host_id: str = None):
    """解散房间"""
    try:
        RoomService.delete_room(room_id, host_id)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=400 if "房主" not in str(e) else 403, detail=str(e))

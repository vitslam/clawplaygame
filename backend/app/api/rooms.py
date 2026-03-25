from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from app import db
import uuid

router = APIRouter()

# 预制假房间数据（测试用，启动时写入数据库）
# 只保留 3 个狼人杀房间，每个都有不同的对局状态
MOCK_ROOMS = [
    # 房间 1：刚开局，第 1 夜
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
    # 房间 2：第 3 夜，已经死了 2 人
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
    # 房间 3：决赛圈，剩 4 人
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
    # 检查是否已存在预制房间
    existing = db.get_rooms_by_game("werewolf")
    if existing:
        print(f"✅ 数据库已有房间，跳过预制房间初始化")
        return
    
    for i, mock in enumerate(MOCK_ROOMS):
        room_id = f"mock_{i:03d}"
        host_id = f"host_{i}"
        session_id = f"session_{i:03d}"
        
        # 创建用户
        db.create_user(host_id, mock["host"])
        
        # 创建房间
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
        
        # 添加假玩家
        for j in range(mock["players"]):
            player_id = f"p_{i}_{j}"
            player_name = f"玩家{j+1}"
            db.create_user(player_id, player_name)
            db.add_player_to_room(room_id, player_id, player_name)
        
        # 创建游戏对局
        if mock.get("session"):
            db.create_game_session(session_id, room_id, mock["game_id"], mock["session"])
            db.update_room_session(room_id, session_id)
            
            # 添加游戏日志作为消息
            for log_entry in mock["session"].get("game_log", []):
                db.add_message(room_id, log_entry, "system")
    
    print(f"✅ 已初始化 {len(MOCK_ROOMS)} 个预制房间到数据库")


class CreateRoomRequest(BaseModel):
    player_name: str
    room_name: str  # 房间名称
    max_players: int = 10  # 人数
    is_public: bool = True  # 是否公开


class RoomResponse(BaseModel):
    id: str
    game_id: str
    room_name: str  # 房间名称
    host_name: str
    players: List[dict]
    status: str
    created_at: str
    max_players: int
    is_public: bool = True  # 是否公开
    current_session_id: str = None  # 当前对局 ID


class JoinRoomRequest(BaseModel):
    player_name: str


class MessageRequest(BaseModel):
    player_id: str
    content: str
    message_type: str = "chat"  # chat, system, action


@router.get("/{game_id}/rooms", response_model=List[RoomResponse])
async def list_rooms(game_id: str):
    """获取指定游戏的所有房间"""
    rooms = db.get_rooms_by_game(game_id)
    
    # 获取每个房间的玩家
    result = []
    for room in rooms:
        players = db.get_room_players(room["id"])
        room_data = {
            **room,
            "players": players,
            "is_public": bool(room["is_public"])
        }
        result.append(RoomResponse(**room_data))
    
    return result


@router.post("/{game_id}/rooms", response_model=RoomResponse)
async def create_room(game_id: str, request: CreateRoomRequest):
    """创建新游戏房间"""
    room_id = str(uuid.uuid4())[:8]
    host_id = str(uuid.uuid4())[:6]
    
    # 创建用户
    db.create_user(host_id, request.player_name)
    
    # 创建房间
    db.create_room(
        room_id=room_id,
        game_id=game_id,
        room_name=request.room_name,
        host_id=host_id,
        host_name=request.player_name,
        max_players=request.max_players,
        is_public=request.is_public
    )
    
    # 获取房间数据
    room = db.get_room(room_id)
    players = db.get_room_players(room_id)
    
    room_data = {
        **room,
        "players": players,
        "is_public": bool(room["is_public"])
    }
    
    return RoomResponse(**room_data)


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(room_id: str):
    """获取房间信息"""
    room = db.get_room_with_session(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    players = db.get_room_players(room_id)
    room_data = {
        **room,
        "players": players,
        "is_public": bool(room["is_public"])
    }
    
    return RoomResponse(**room_data)


@router.post("/{room_id}/join")
async def join_room(room_id: str, request: JoinRoomRequest):
    """加入游戏房间"""
    room = db.get_room_with_session(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    players = db.get_room_players(room_id)
    if len(players) >= room["max_players"]:
        raise HTTPException(status_code=400, detail="房间已满")
    
    if room["status"] != "waiting":
        raise HTTPException(status_code=400, detail="游戏已开始")
    
    player_id = str(uuid.uuid4())[:6]
    
    # 创建用户并添加到房间
    db.create_user(player_id, request.player_name)
    db.add_player_to_room(room_id, player_id, request.player_name)
    
    # 添加系统消息
    db.add_message(room_id, f"{request.player_name} 加入了房间", "system")
    
    # 返回更新后的房间
    players = db.get_room_players(room_id)
    room_data = {
        **room,
        "players": players,
        "is_public": bool(room["is_public"])
    }
    
    return {"success": True, "player": {"id": player_id, "name": request.player_name}, "room": RoomResponse(**room_data)}


@router.post("/{room_id}/messages")
async def send_message(room_id: str, request: MessageRequest):
    """发送房间消息"""
    room = db.get_room_with_session(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    players = db.get_room_players(room_id)
    player_name = next((p["player_name"] for p in players if p["player_id"] == request.player_id), "Unknown")
    
    db.add_message(room_id, request.content, request.message_type, request.player_id, player_name)
    
    return {"success": True}


@router.get("/{room_id}/messages")
async def get_messages(room_id: str, limit: int = 50):
    """获取房间消息历史"""
    room = db.get_room_with_session(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    messages = db.get_room_messages(room_id, limit)
    # 反转顺序（最新的在最后）
    messages.reverse()
    
    return {"messages": messages}

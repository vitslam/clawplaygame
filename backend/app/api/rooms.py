from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from app import db
import uuid

router = APIRouter()

# 预制假房间数据（测试用，启动时写入数据库）
MOCK_ROOMS = [
    # 狼人杀房间 - 混合状态
    {"game_id": "werewolf", "name": "新手欢迎", "host": "Lobster_01", "players": 3, "max": 12, "status": "waiting"},
    {"game_id": "werewolf", "name": "仅限高手", "host": "Crab_King", "players": 12, "max": 12, "status": "playing"},
    {"game_id": "werewolf", "name": "休闲局", "host": "Shrimp_Boy", "players": 2, "max": 8, "status": "waiting"},
    {"game_id": "werewolf", "name": "仅限语音", "host": "Whale_Song", "players": 10, "max": 10, "status": "playing"},
    {"game_id": "werewolf", "name": "深夜修仙", "host": "Squid_Ward", "players": 1, "max": 6, "status": "waiting"},
    {"game_id": "werewolf", "name": "快速场", "host": "Fish_Master", "players": 4, "max": 9, "status": "waiting"},
    {"game_id": "werewolf", "name": "娱乐局", "host": "Dolphin_Girl", "players": 9, "max": 12, "status": "playing"},
    # 阿瓦隆房间 - 混合状态
    {"game_id": "avalon", "name": "梅林之路", "host": "Merlin_Pro", "players": 3, "max": 10, "status": "waiting"},
    {"game_id": "avalon", "name": "刺客战场", "host": "Assassin_X", "players": 8, "max": 8, "status": "playing"},
    {"game_id": "avalon", "name": "圆桌骑士", "host": "King_Arthur", "players": 5, "max": 10, "status": "waiting"},
    {"game_id": "avalon", "name": "湖中仙女", "host": "Lady_Lake", "players": 2, "max": 9, "status": "waiting"},
    # 血染钟楼房间
    {"game_id": "botc", "name": "说书人剧场", "host": "Storyteller", "players": 8, "max": 15, "status": "waiting"},
    {"game_id": "botc", "name": "恶魔之夜", "host": "Demon_Lord", "players": 12, "max": 12, "status": "playing"},
    # 间谍危机房间
    {"game_id": "spyfall", "name": "快速派对", "host": "Spy_Master", "players": 3, "max": 8, "status": "waiting"},
    {"game_id": "spyfall", "name": "谁是间谍", "host": "Detective", "players": 6, "max": 6, "status": "playing"},
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
            status=mock["status"]  # 保存房间状态
        )
        
        # 添加假玩家
        for j in range(mock["players"]):
            player_id = f"p_{i}_{j}"
            player_name = f"玩家{j+1}"
            db.create_user(player_id, player_name)
            db.add_player_to_room(room_id, player_id, player_name)
    
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
    
    return {
        "success": True,
        "player": new_player,
        "room": RoomResponse(**room)
    }


@router.post("/{room_id}/messages")
async def send_message(room_id: str, request: MessageRequest):
    """发送房间消息"""
    room = db.get_room_with_session(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    players = db.get_room_players(room_id)
    player_name = next((p["player_name"] for p in players if p["player_id"] == request.player_id), "Unknown")
    
    db.add_message(room_id, request.content, request.message_type, request.player_id, player_name)
    
    return {"success": True, "message": message}


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


@router.delete("/{room_id}")
async def delete_room(room_id: str):
    """删除房间"""
    if room_id not in ROOMS_DB:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    del ROOMS_DB[room_id]
    
    return {"success": True, "message": "房间已删除"}

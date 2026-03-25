from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

# 游戏数据（暂时用内存存储，后续可以接数据库）
GAMES_DB = [
    {
        "id": "werewolf",
        "name": "狼人杀",
        "description": "经典的社交推理游戏，6-12 人参与",
        "min_players": 6,
        "max_players": 12,
        "duration_minutes": "30-60",
        "type": "社交推理",
        "status": "active",
        "active_rooms": 128,
        "active_players": 10730,
    },
    {
        "id": "avalon",
        "name": "阿瓦隆",
        "description": "梅林与刺客的较量，5-10 人参与",
        "min_players": 5,
        "max_players": 10,
        "duration_minutes": "30-45",
        "type": "社交推理",
        "status": "active",
        "active_rooms": 95,
        "active_players": 8955,
    },
    {
        "id": "botc",
        "name": "血染钟楼",
        "description": "说书人主导的复杂推理游戏，5-20 人参与",
        "min_players": 5,
        "max_players": 20,
        "duration_minutes": "60-120",
        "type": "社交推理",
        "status": "coming_soon",
        "active_rooms": 0,
        "active_players": 0,
    },
    {
        "id": "spyfall",
        "name": "间谍危机",
        "description": "快速派对游戏，找出隐藏的间谍",
        "min_players": 3,
        "max_players": 8,
        "duration_minutes": "15-30",
        "type": "派对游戏",
        "status": "coming_soon",
        "active_rooms": 0,
        "active_players": 0,
    },
]


class GameResponse(BaseModel):
    id: str
    name: str
    description: str
    min_players: int
    max_players: int
    duration_minutes: str
    type: str
    status: str
    active_rooms: int
    active_players: int


@router.get("", response_model=List[GameResponse])
async def list_games():
    """获取所有可用游戏列表"""
    return GAMES_DB


@router.get("/{game_id}", response_model=GameResponse)
async def get_game(game_id: str):
    """获取指定游戏详情"""
    for game in GAMES_DB:
        if game["id"] == game_id:
            return game
    raise HTTPException(status_code=404, detail="游戏不存在")

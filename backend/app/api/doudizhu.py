from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel

router = APIRouter()


class StartGameRequest(BaseModel):
    game_type: str = "doudizhu"


class CallLandlordRequest(BaseModel):
    call_score: int  # 叫分：0=不叫，1=1 分，2=2 分，3=3 分


class PlayCardsRequest(BaseModel):
    cards: List[Dict]  # 牌面数据，如 [{"rank": 14, "suit": "heart"}, ...]


class PassTurnRequest(BaseModel):
    pass


@router.post("/{room_id}/start")
async def start_doudizhu_game(room_id: str, request: StartGameRequest):
    """开始斗地主游戏"""
    from app import db
    from app.games import game_manager
    from app.games.doudizhu import DouDizhuGame, Player
    
    # 获取房间信息
    room = db.get_room_with_session(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    players = db.get_room_players(room_id)
    if len(players) != 3:
        raise HTTPException(status_code=400, detail="斗地主需要恰好 3 名玩家")
    
    # 创建游戏实例
    game = game_manager.create_game(room_id, request.game_type)
    if not game:
        raise HTTPException(status_code=500, detail="不支持的游戏类型")
    
    # 添加玩家到游戏
    for i, player_data in enumerate(players):
        player = Player(
            id=player_data["player_id"],
            name=player_data["player_name"],
            position=i,
            is_host=(player_data.get("role") == "host")
        )
        game.add_player(player_data["player_id"], player_data["player_name"])
    
    # 开始游戏（发牌）
    result = game.start_game()
    
    # 创建对局记录
    import uuid
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    db.create_game_session(session_id, room_id, "doudizhu")
    db.update_room_session(room_id, session_id)
    db.update_room_status(room_id, "playing")
    
    return {
        "success": True,
        "session_id": session_id,
        "message": "游戏已开始，进入叫地主阶段",
        "game_state": result
    }


@router.get("/{room_id}/state")
async def get_game_state(room_id: str, player_id: str):
    """获取游戏状态"""
    from app.games import game_manager
    
    game = game_manager.get_game(room_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    return game.get_game_state(player_id)


@router.post("/{room_id}/call-landlord")
async def call_landlord(room_id: str, player_id: str, request: CallLandlordRequest):
    """叫地主"""
    from app.games import game_manager
    
    game = game_manager.get_game(room_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    result = game.call_landlord(player_id, request.call_score)
    return {"success": True, "game_state": result}


@router.post("/{room_id}/play-cards")
async def play_cards(room_id: str, player_id: str, request: PlayCardsRequest):
    """出牌"""
    from app.games import game_manager
    
    game = game_manager.get_game(room_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    result = game.play_cards(player_id, request.cards)
    return {"success": True, "game_state": result}


@router.post("/{room_id}/pass-turn")
async def pass_turn(room_id: str, player_id: str, request: PassTurnRequest):
    """过牌"""
    from app.games import game_manager
    
    game = game_manager.get_game(room_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    result = game.pass_turn(player_id)
    return {"success": True, "game_state": result}

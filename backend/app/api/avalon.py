from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from app.games.avalon import AvalonGame, GamePhase, Faction
from app.games import game_manager

router = APIRouter()


class StartGameRequest(BaseModel):
    game_type: str = "avalon"


class ProposeTeamRequest(BaseModel):
    team_player_ids: list[str]


class VoteRequest(BaseModel):
    approve: bool


class QuestVoteRequest(BaseModel):
    is_success: bool


class AssassinateRequest(BaseModel):
    target_id: str


@router.post("/{room_id}/start")
async def start_avalon_game(room_id: str, request: StartGameRequest):
    """开始阿瓦隆游戏"""
    from app.api.rooms import ROOMS_DB
    
    if room_id not in ROOMS_DB:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room = ROOMS_DB[room_id]
    if len(room["players"]) < 5:
        raise HTTPException(status_code=400, detail="阿瓦隆需要至少 5 名玩家")
    
    # 创建游戏实例
    game = game_manager.create_game(room_id, request.game_type)
    if not game:
        raise HTTPException(status_code=500, detail="不支持的游戏类型")
    
    # 添加玩家到游戏
    for player_data in room["players"]:
        from app.games.avalon import Player
        player = Player(
            id=player_data["id"],
            name=player_data["name"],
            is_host=(player_data.get("role") == "host")
        )
        game.players.append(player)
    
    # 分配角色
    game.assign_roles()
    
    # 选择随机队长
    import random
    game.team_leader_index = random.randint(0, len(game.players) - 1)
    game.phase = GamePhase.TEAM_LEADER
    
    leader = game.players[game.team_leader_index]
    game.add_system_message(f"游戏开始！第 1 轮队长：{leader.name}")
    
    return {"success": True, "message": "游戏已开始"}


@router.get("/{room_id}/state")
async def get_game_state(room_id: str, player_id: str):
    """获取游戏状态"""
    game = game_manager.get_game(room_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    return game.get_game_state(player_id)


@router.post("/{room_id}/propose-team")
async def propose_team(room_id: str, player_id: str, request: ProposeTeamRequest):
    """队长提议队伍"""
    game = game_manager.get_game(room_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    player = next((p for p in game.players if p.id == player_id), None)
    if not player:
        raise HTTPException(status_code=404, detail="玩家不存在")
    
    if game.players[game.team_leader_index].id != player_id:
        raise HTTPException(status_code=403, detail="只有队长可以提议队伍")
    
    success = game.propose_team(set(request.team_player_ids))
    if not success:
        raise HTTPException(status_code=400, detail="组队失败")
    
    return {"success": True}


@router.post("/{room_id}/vote-team")
async def vote_team(room_id: str, player_id: str, request: VoteRequest):
    """对队伍投票"""
    game = game_manager.get_game(room_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    success = game.vote_team(player_id, request.approve)
    if not success and game.phase != GamePhase.TEAM_VOTE:
        # 投票已完成，返回最新状态
        pass
    
    return {"success": True}


@router.post("/{room_id}/submit-quest-vote")
async def submit_quest_vote(room_id: str, player_id: str, request: QuestVoteRequest):
    """提交任务投票"""
    game = game_manager.get_game(room_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    success = game.submit_quest_vote(player_id, request.is_success)
    if not success and game.phase != GamePhase.QUEST:
        # 投票已完成，返回最新状态
        pass
    
    return {"success": True}


@router.post("/{room_id}/assassinate")
async def assassinate(room_id: str, player_id: str, request: AssassinateRequest):
    """刺客刺杀"""
    game = game_manager.get_game(room_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    success = game.assassinate(player_id, request.target_id)
    if not success:
        raise HTTPException(status_code=400, detail="刺杀失败")
    
    return {"success": True}


@router.get("/{room_id}/reveal-roles")
async def reveal_roles(room_id: str, player_id: str):
    """梅林展示视角（给梅林看坏人）"""
    game = game_manager.get_game(room_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    player = next((p for p in game.players if p.id == player_id), None)
    if not player or player.role.value != "merlin":
        raise HTTPException(status_code=403, detail="只有梅林可以查看")
    
    evil_players = [
        {"id": p.id, "name": p.name, "role": p.role.value}
        for p in game.players
        if p.get_faction() == Faction.EVIL and p.role.value != "mordred"
    ]
    
    return {"evil_players": evil_players}


@router.get("/{room_id}/percival-info")
async def percival_info(room_id: str, player_id: str):
    """派西维尔展示视角（给派西维尔看梅林和莫甘娜）"""
    game = game_manager.get_game(room_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    player = next((p for p in game.players if p.id == player_id), None)
    if not player or player.role.value != "percival":
        raise HTTPException(status_code=403, detail="只有派西维尔可以查看")
    
    merlin_morgana = [
        {"id": p.id, "name": p.name, "role": p.role.value}
        for p in game.players
        if p.role.value in ["merlin", "morgana"]
    ]
    
    return {"merlin_and_morgana": merlin_morgana}

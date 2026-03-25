"""
阿瓦隆游戏核心逻辑
"""
import random
from enum import Enum
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime


class Role(Enum):
    """角色定义"""
    # 好人阵营
    MERLIN = "merlin"  # 梅林 - 知道所有坏人（除莫德雷德）
    PERCIVAL = "percival"  # 派西维尔 - 知道梅林和莫甘娜
    LOYAL_SERVANT = "loyal_servant"  # 忠臣 - 无特殊能力
    
    # 坏人阵营
    MORGANA = "morgana"  # 莫甘娜 - 冒充梅林
    ASSASSIN = "assassin"  # 刺客 - 最后刺杀梅林
    MORDRED = "mordred"  # 莫德雷德 - 梅林看不到


class Faction(Enum):
    """阵营"""
    GOOD = "good"
    EVIL = "evil"


class GamePhase(Enum):
    """游戏阶段"""
    WAITING = "waiting"  # 等待开始
    ROLE_REVEAL = "role_reveal"  # 展示角色
    TEAM_LEADER = "team_leader"  # 队长组队
    TEAM_VOTE = "team_vote"  # 投票表决
    QUEST = "quest"  # 执行任务
    ASSASSINATION = "assassination"  # 刺杀阶段
    GAME_OVER = "game_over"  # 游戏结束


@dataclass
class Player:
    """玩家"""
    id: str
    name: str
    role: Optional[Role] = None
    is_alive: bool = True
    is_host: bool = False
    
    def get_faction(self) -> Optional[Faction]:
        if self.role is None:
            return None
        if self.role in [Role.MERLIN, Role.PERCIVAL, Role.LOYAL_SERVANT]:
            return Faction.GOOD
        return Faction.EVIL


@dataclass
class QuestConfig:
    """任务配置"""
    quest_number: int
    team_size: int
    fail_count_needed: int  # 需要几个失败票


# 标准阿瓦隆任务配置（5-10 人）
QUEST_CONFIGS = {
    5: [
        QuestConfig(1, 2, 1),
        QuestConfig(2, 3, 1),
        QuestConfig(3, 2, 1),
        QuestConfig(4, 3, 1),
        QuestConfig(5, 3, 1),  # 第 5 轮需要 2 个失败
    ],
    6: [
        QuestConfig(1, 2, 1),
        QuestConfig(2, 3, 1),
        QuestConfig(3, 4, 1),
        QuestConfig(4, 3, 1),
        QuestConfig(5, 3, 1),
    ],
    7: [
        QuestConfig(1, 2, 1),
        QuestConfig(2, 3, 1),
        QuestConfig(3, 3, 1),
        QuestConfig(4, 4, 1),
        QuestConfig(5, 3, 1),
    ],
    8: [
        QuestConfig(1, 3, 1),
        QuestConfig(2, 4, 1),
        QuestConfig(3, 4, 1),
        QuestConfig(4, 5, 1),
        QuestConfig(5, 3, 1),
    ],
    9: [
        QuestConfig(1, 3, 1),
        QuestConfig(2, 4, 1),
        QuestConfig(3, 4, 1),
        QuestConfig(4, 5, 1),
        QuestConfig(5, 3, 1),
    ],
    10: [
        QuestConfig(1, 3, 1),
        QuestConfig(2, 4, 1),
        QuestConfig(3, 4, 1),
        QuestConfig(4, 5, 1),
        QuestConfig(5, 3, 1),
    ],
}

# 角色配置 (玩家数：各角色数量)
ROLE_CONFIGS = {
    5: {"merlin": 1, "percival": 1, "morgana": 1, "assassin": 1, "loyal_servant": 1},
    6: {"merlin": 1, "percival": 1, "morgana": 1, "assassin": 1, "loyal_servant": 2},
    7: {"merlin": 1, "percival": 1, "morgana": 1, "assassin": 1, "mordred": 1, "loyal_servant": 2},
    8: {"merlin": 1, "percival": 1, "morgana": 1, "assassin": 1, "mordred": 1, "loyal_servant": 3},
    9: {"merlin": 1, "percival": 1, "morgana": 1, "assassin": 1, "mordred": 1, "loyal_servant": 4},
    10: {"merlin": 1, "percival": 1, "morgana": 1, "assassin": 1, "mordred": 1, "loyal_servant": 5},
}


@dataclass
class AvalonGame:
    """阿瓦隆游戏状态"""
    room_id: str
    players: List[Player] = field(default_factory=list)
    phase: GamePhase = GamePhase.WAITING
    
    # 游戏进度
    current_quest: int = 0  # 当前第几轮 (0-4)
    quest_successes: int = 0  # 成功次数
    quest_failures: int = 0  # 失败次数
    
    # 组队相关
    team_leader_index: int = 0  # 当前队长索引
    proposed_team: Set[str] = field(default_factory=set)  # 提议的队伍
    team_votes: Dict[str, bool] = field(default_factory=dict)  # 投票结果
    
    # 任务结果
    quest_votes: List[str] = field(default_factory=list)  # 任务投票
    
    # 刺杀阶段
    assassination_target: Optional[str] = None  # 刺杀目标
    
    # 游戏结果
    winner: Optional[Faction] = None
    end_reason: Optional[str] = None
    
    # 消息日志
    messages: List[Dict] = field(default_factory=list)
    
    def get_player_count(self) -> int:
        return len(self.players)
    
    def get_alive_players(self) -> List[Player]:
        return [p for p in self.players if p.is_alive]
    
    def get_evil_players(self) -> List[Player]:
        return [p for p in self.players if p.get_faction() == Faction.EVIL]
    
    def get_merlin(self) -> Optional[Player]:
        for p in self.players:
            if p.role == Role.MERLIN:
                return p
        return None
    
    def assign_roles(self):
        """分配角色"""
        player_count = len(self.players)
        if player_count < 5 or player_count > 10:
            raise ValueError("玩家数量必须在 5-10 之间")
        
        role_config = ROLE_CONFIGS[player_count]
        roles = []
        for role, count in role_config.items():
            roles.extend([Role(role)] * count)
        
        random.shuffle(roles)
        for i, player in enumerate(self.players):
            player.role = roles[i]
        
        self.add_system_message(f"角色已分配！共{player_count}名玩家")
    
    def get_quest_config(self) -> Optional[QuestConfig]:
        """获取当前任务配置"""
        player_count = len(self.players)
        if player_count not in QUEST_CONFIGS:
            return None
        if self.current_quest >= 5:
            return None
        return QUEST_CONFIGS[player_count][self.current_quest]
    
    def propose_team(self, team_player_ids: Set[str]) -> bool:
        """队长提议队伍"""
        if self.phase != GamePhase.TEAM_LEADER:
            return False
        
        config = self.get_quest_config()
        if not config:
            return False
        
        if len(team_player_ids) != config.team_size:
            return False
        
        # 验证所有玩家都在游戏中
        valid_ids = {p.id for p in self.players if p.is_alive}
        if not team_player_ids.issubset(valid_ids):
            return False
        
        self.proposed_team = team_player_ids
        self.phase = GamePhase.TEAM_VOTE
        self.team_votes = {}
        
        leader = self.players[self.team_leader_index]
        team_names = [p.name for p in self.players if p.id in team_player_ids]
        self.add_system_message(f"{leader.name} 提议队伍：{', '.join(team_names)}")
        
        return True
    
    def vote_team(self, player_id: str, approve: bool) -> bool:
        """玩家对队伍投票"""
        if self.phase != GamePhase.TEAM_VOTE:
            return False
        
        if player_id in self.team_votes:
            return False
        
        player = next((p for p in self.players if p.id == player_id), None)
        if not player or not player.is_alive:
            return False
        
        self.team_votes[player_id] = approve
        
        # 检查是否所有人都投票了
        alive_count = len(self.get_alive_players())
        if len(self.team_votes) == alive_count:
            return self._count_team_votes()
        
        return True
    
    def _count_team_votes(self) -> bool:
        """统计投票结果"""
        approve_count = sum(1 for v in self.team_votes.values() if v)
        reject_count = len(self.team_votes) - approve_count
        
        if approve_count > reject_count:
            self.add_system_message(f"投票通过！{approve_count} 赞成 vs {reject_count} 反对")
            self.phase = GamePhase.QUEST
            self.quest_votes = []
            return True
        else:
            self.add_system_message(f"投票失败！{approve_count} 赞成 vs {reject_count} 反对")
            # 更换队长
            self.team_leader_index = (self.team_leader_index + 1) % len(self.players)
            self.proposed_team = set()
            self.team_votes = {}
            self.phase = GamePhase.TEAM_LEADER
            
            # 5 次失败直接游戏结束
            if self.quest_failures >= 5:
                self.winner = Faction.EVIL
                self.end_reason = "组队失败 5 次"
                self.phase = GamePhase.GAME_OVER
                self.add_system_message("游戏结束！坏人获胜（组队失败 5 次）")
                return False
            
            leader = self.players[self.team_leader_index]
            self.add_system_message(f"新队长：{leader.name}")
            return False
    
    def submit_quest_vote(self, player_id: str, is_success: bool) -> bool:
        """提交任务投票"""
        if self.phase != GamePhase.QUEST:
            return False
        
        if player_id not in self.proposed_team:
            return False
        
        if player_id in self.quest_votes:
            return False
        
        # 坏人可以选择失败或成功（除了第 4 轮需要 2 个失败）
        player = next((p for p in self.players if p.id == player_id), None)
        if player and player.get_faction() == Faction.EVIL:
            config = self.get_quest_config()
            if config and self.current_quest == 4:
                # 第 5 轮任务，坏人可以选择失败或成功
                pass
            # 其他轮次坏人只能投失败
            is_success = False
        
        self.quest_votes.append("success" if is_success else "fail")
        
        # 检查是否所有人都投票了
        config = self.get_quest_config()
        if config and len(self.quest_votes) == config.team_size:
            return self._count_quest_votes()
        
        return True
    
    def _count_quest_votes(self) -> bool:
        """统计任务结果"""
        fail_count = sum(1 for v in self.quest_votes if v == "fail")
        config = self.get_quest_config()
        
        if not config:
            return False
        
        # 第 5 轮任务需要 2 个失败
        required_fails = 2 if self.current_quest == 4 and len(self.players) >= 5 else 1
        
        if fail_count >= required_fails:
            self.quest_failures += 1
            self.add_system_message(f"任务失败！{fail_count} 个失败票")
        else:
            self.quest_successes += 1
            self.add_system_message(f"任务成功！")
        
        # 检查游戏是否结束
        if self.quest_successes >= 3:
            self.winner = Faction.GOOD
            self.end_reason = "任务成功 3 次"
            self.phase = GamePhase.GAME_OVER
            self.add_system_message("游戏结束！好人获胜！")
            return True
        elif self.quest_failures >= 3:
            self.winner = Faction.EVIL
            self.end_reason = "任务失败 3 次"
            self.phase = GamePhase.GAME_OVER
            self.add_system_message("游戏结束！坏人获胜！")
            return True
        
        # 进入下一轮
        self.current_quest += 1
        self.team_leader_index = (self.team_leader_index + 1) % len(self.players)
        self.proposed_team = set()
        self.team_votes = {}
        self.quest_votes = []
        self.phase = GamePhase.TEAM_LEADER
        
        leader = self.players[self.team_leader_index]
        self.add_system_message(f"第{self.current_quest + 1}轮开始，队长：{leader.name}")
        
        return True
    
    def assassinate(self, assassin_id: str, target_id: str) -> bool:
        """刺客刺杀"""
        if self.phase != GamePhase.ASSASSINATION:
            return False
        
        assassin = next((p for p in self.players if p.id == assassin_id), None)
        if not assassin or assassin.role != Role.ASSASSIN:
            return False
        
        target = next((p for p in self.players if p.id == target_id), None)
        if not target or not target.is_alive:
            return False
        
        self.assassination_target = target_id
        
        if target.role == Role.MERLIN:
            self.winner = Faction.EVIL
            self.end_reason = "刺客成功刺杀梅林"
            self.add_system_message(f"刺客刺杀了 {target.name}（梅林）！坏人翻盘获胜！")
        else:
            self.winner = Faction.GOOD
            self.end_reason = "刺客刺杀失败"
            self.add_system_message(f"刺客刺杀了 {target.name}（不是梅林）！好人获胜！")
        
        self.phase = GamePhase.GAME_OVER
        return True
    
    def add_system_message(self, text: str):
        """添加系统消息"""
        self.messages.append({
            "id": f"sys_{len(self.messages)}",
            "type": "system",
            "content": text,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_game_state(self, player_id: str) -> Dict:
        """获取玩家视角的游戏状态"""
        player = next((p for p in self.players if p.id == player_id), None)
        if not player:
            return {}
        
        # 根据角色返回不同信息
        state = {
            "room_id": self.room_id,
            "phase": self.phase.value,
            "current_quest": self.current_quest,
            "quest_successes": self.quest_successes,
            "quest_failures": self.quest_failures,
            "team_leader_index": self.team_leader_index,
            "players": [],
            "messages": self.messages[-20:],  # 最近 20 条消息
        }
        
        for p in self.players:
            player_info = {
                "id": p.id,
                "name": p.name,
                "is_alive": p.is_alive,
                "is_host": p.is_host,
            }
            
            # 只有自己能看到自己的角色
            if p.id == player_id:
                player_info["role"] = p.role.value if p.role else None
                player_info["faction"] = p.get_faction().value if p.get_faction() else None
            
            state["players"].append(player_info)
        
        # 组队阶段
        if self.phase == GamePhase.TEAM_LEADER:
            state["proposed_team"] = list(self.proposed_team)
        elif self.phase == GamePhase.TEAM_VOTE:
            state["proposed_team"] = list(self.proposed_team)
            state["my_vote"] = self.team_votes.get(player_id)
        elif self.phase == GamePhase.QUEST:
            state["proposed_team"] = list(self.proposed_team)
            state["is_in_team"] = player_id in self.proposed_team
        
        if self.phase == GamePhase.GAME_OVER:
            state["winner"] = self.winner.value if self.winner else None
            state["end_reason"] = self.end_reason
            # 游戏结束后展示所有角色
            for p_info in state["players"]:
                p = next((p for p in self.players if p.id == p_info["id"]), None)
                if p:
                    p_info["role"] = p.role.value if p.role else None
                    p_info["faction"] = p.get_faction().value if p.get_faction() else None
        
        return state

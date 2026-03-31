"""
斗地主游戏核心逻辑
支持标准斗地主规则 + 癞子牌（万能牌）
"""
import random
from enum import Enum
from typing import List, Dict, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime

# 游戏事件回调类型
GameEventCallback = Callable[[str, str, Dict[str, Any]], None]


class CardRank(Enum):
    """牌面值"""
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    J = 11
    Q = 12
    K = 13
    A = 14
    TWO = 15
    SMALL_JOKER = 16  # 小王（白板）
    BIG_JOKER = 17   # 大王（王八）


class CardSuit(Enum):
    """花色（斗地主中花色无大小作用）"""
    SPADE = "spade"      # 黑桃 ♠
    HEART = "heart"      # 红心 ♥
    CLUB = "club"        # 梅花 ♣
    DIAMOND = "diamond"  # 方块 ♦


@dataclass
class Card:
    """一张牌"""
    rank: CardRank
    suit: CardSuit
    is_laizi: bool = False  # 是否为癞子牌

    def __lt__(self, other):
        if self.rank.value != other.rank.value:
            return self.rank.value < other.rank.value
        return self.suit.value < other.suit.value

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit, self.is_laizi))

    @property
    def display(self) -> str:
        """显示名称"""
        suit_symbols = {"spade": "♠", "heart": "♥", "club": "♣", "diamond": "♦"}
        rank_names = {
            CardRank.THREE: "3", CardRank.FOUR: "4", CardRank.FIVE: "5",
            CardRank.SIX: "6", CardRank.SEVEN: "7", CardRank.EIGHT: "8",
            CardRank.NINE: "9", CardRank.TEN: "10", CardRank.J: "J",
            CardRank.Q: "Q", CardRank.K: "K", CardRank.A: "A",
            CardRank.TWO: "2", CardRank.SMALL_JOKER: "小王",
            CardRank.BIG_JOKER: "大王"
        }
        if self.rank in [CardRank.SMALL_JOKER, CardRank.BIG_JOKER]:
            return rank_names[self.rank]
        laizi_mark = "*" if self.is_laizi else ""
        return f"{suit_symbols[self.suit.value]}{rank_names[self.rank]}{laizi_mark}"


class GamePhase(Enum):
    """游戏阶段"""
    WAITING = "waiting"           # 等待玩家
    DEALING = "dealing"           # 发牌中
    LANDLORD_ELECTION = "landlord_election"  # 叫地主阶段
    LANDLORD_REVEAL = "landlord_reveal"      # 展示地主
    PLAYING = "playing"           # 出牌阶段
    GAME_OVER = "game_over"       # 游戏结束


@dataclass
class Player:
    """玩家"""
    id: str
    name: str
    position: int = 0  # 0=房东左边, 1=对家, 2=房东右边
    hand: List[Card] = field(default_factory=list)
    is_landlord: bool = False
    is_alive: bool = True
    is_host: bool = False

    def sort_hand(self):
        """整理手牌"""
        self.hand.sort()

    def has_card(self, card: Card) -> bool:
        return card in self.hand

    def remove_card(self, card: Card) -> bool:
        if card in self.hand:
            self.hand.remove(card)
            return True
        return False

    def remove_cards(self, cards: List[Card]) -> bool:
        """批量移除手牌"""
        for card in cards:
            if card not in self.hand:
                return False
        for card in cards:
            self.hand.remove(card)
        return True


class DouDizhuGame:
    """斗地主游戏"""

    # 单局游戏配置
    LAIZI_COUNT = 2        # 癞子牌数量
    CARDS_PER_PLAYER = 17  # 每个玩家手牌数
    BOTTOM_CARDS = 3       # 底牌数量

    def __init__(self, room_id: str, event_callback: Optional[GameEventCallback] = None):
        self.room_id = room_id
        self.players: List[Player] = []
        self.event_callback = event_callback
        self.landlord_position: int = -1  # 地主位置
        self.bottom_cards: List[Card] = []  # 底牌
        self.laizi_rank: Optional[CardRank] = None  # 癞子对应的牌值
        self.landlord_cards: List[Card] = []  # 地主的手牌（含底牌）
        self.phase: GamePhase = GamePhase.WAITING
        self.current_player_index: int = 0  # 当前出牌玩家
        self.last_play_player_index: int = -1  # 上一个出牌的玩家
        self.last_cards: List[Card] = []  # 上一次出的牌
        self.last_card_type: Optional[str] = None  # 上一次出的牌型
        self.turn_count: int = 0  # 当前轮次
        self.winner: Optional[str] = None  # 胜利者ID
        self.creation_time: datetime = datetime.now()

    def add_player(self, player_id: str, player_name: str) -> bool:
        """添加玩家"""
        if len(self.players) >= 3:
            return False
        if any(p.id == player_id for p in self.players):
            return False
        player = Player(id=player_id, name=player_name, position=len(self.players))
        if len(self.players) == 0:
            player.is_host = True
        self.players.append(player)
        return True

    def remove_player(self, player_id: str) -> bool:
        """移除玩家"""
        for i, p in enumerate(self.players):
            if p.id == player_id:
                self.players.pop(i)
                for j, player in enumerate(self.players):
                    player.position = j
                return True
        return False

    def get_player(self, player_id: str) -> Optional[Player]:
        for p in self.players:
            if p.id == player_id:
                return p
        return None

    def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """发送游戏事件"""
        if self.event_callback:
            self.event_callback(self.room_id, event_type, data)
    
    def can_start(self) -> bool:
        """是否可以开始游戏"""
        return len(self.players) == 3 and self.phase == GamePhase.WAITING

    def start_game(self) -> Dict:
        """开始游戏，发牌"""
        if not self.can_start():
            return {"success": False, "error": "无法开始游戏"}

        self.phase = GamePhase.DEALING

        deck = self._create_deck()
        self._shuffle_deck(deck)

        laizis = random.sample(deck, self.LAIZI_COUNT)
        for laizi in laizis:
            laizi.is_laizi = True
        self.laizi_rank = self._determine_laizi_rank(deck, laizis)

        for i, card in enumerate(deck[:self.CARDS_PER_PLAYER]):
            self.players[0].hand.append(card)
        for i, card in enumerate(deck[self.CARDS_PER_PLAYER:self.CARDS_PER_PLAYER*2]):
            self.players[1].hand.append(card)
        for i, card in enumerate(deck[self.CARDS_PER_PLAYER*2:self.CARDS_PER_PLAYER*3]):
            self.players[2].hand.append(card)
        self.bottom_cards = deck[-self.BOTTOM_CARDS:]

        for p in self.players:
            p.sort_hand()

        self.phase = GamePhase.LANDLORD_ELECTION
        self.current_player_index = random.randint(0, 2)

        return {
            "success": True,
            "phase": self.phase.value,
            "laizi_count": self.LAIZI_COUNT,
            "bottom_count": self.BOTTOM_CARDS,
            "current_player": self.players[self.current_player_index].id,
            "players": [
                {
                    "id": p.id,
                    "name": p.name,
                    "position": p.position,
                    "card_count": len(p.hand),
                    "is_host": p.is_host
                }
                for p in self.players
            ]
        }

    def _create_deck(self) -> List[Card]:
        """创建一副牌"""
        deck = []
        for suit in CardSuit:
            for rank in [r for r in CardRank if r not in [CardRank.SMALL_JOKER, CardRank.BIG_JOKER]]:
                deck.append(Card(rank=rank, suit=suit))
        deck.append(Card(rank=CardRank.SMALL_JOKER, suit=CardSuit.SPADE))
        deck.append(Card(rank=CardRank.BIG_JOKER, suit=CardSuit.SPADE))
        return deck

    def _shuffle_deck(self, deck: List[Card]):
        """洗牌"""
        random.shuffle(deck)

    def _determine_laizi_rank(self, deck: List[Card], laizis: List[Card]) -> CardRank:
        """确定癞子对应的牌值"""
        remaining = [c for c in deck if c not in laizis]
        if remaining:
            return random.choice(remaining).rank
        return CardRank.THREE

    def call_landlord(self, player_id: str, call_score: int) -> Dict:
        """
        叫地主
        call_score: 0=不叫, 1=1分, 2=2分, 3=3分
        """
        player = self.get_player(player_id)
        if not player:
            return {"success": False, "error": "玩家不存在"}
        if self.players[self.current_player_index].id != player_id:
            return {"success": False, "error": "不是你的回合"}

        if call_score == 0:
            self.turn_count += 1
        else:
            self.turn_count = 0
            self.landlord_position = self.current_player_index

        if self.turn_count >= 3 or call_score == 3 or (self.turn_count >= 2 and self.landlord_position >= 0):
            return self._finish_landlord_selection()
        else:
            self.current_player_index = (self.current_player_index + 1) % 3
            # 广播叫地主事件
            self._emit_event("landlord_called", {
                "player_id": player_id,
                "player_name": player.name,
                "score": call_score,
                "current_player": self.players[self.current_player_index].id
            })
            return {
                "success": True,
                "current_player": self.players[self.current_player_index].id,
                "called": {"player_id": player_id, "score": call_score}
            }

    def _finish_landlord_selection(self) -> Dict:
        """完成叫地主"""
        if self.landlord_position < 0:
            self.landlord_position = 0

        landlord = self.players[self.landlord_position]
        landlord.is_landlord = True
        landlord.hand.extend(self.bottom_cards)
        landlord.sort_hand()
        self.landlord_cards = list(landlord.hand)

        self.phase = GamePhase.LANDLORD_REVEAL
        self.current_player_index = self.landlord_position

        return {
            "success": True,
            "landlord": {
                "player_id": landlord.id,
                "player_name": landlord.name,
                "position": landlord.position
            },
            "bottom_cards": [c.display for c in self.bottom_cards],
            "laizi_rank": self.laizi_rank.value if self.laizi_rank else None,
            "phase": self.phase.value
        }

    def play_cards(self, player_id: str, cards: List[Dict]) -> Dict:
        """出牌"""
        player = self.get_player(player_id)
        if not player:
            return {"success": False, "error": "玩家不存在"}

        current = self.players[self.current_player_index]
        if current.id != player_id:
            return {"success": False, "error": "不是你的回合"}

        if self.last_play_player_index == self.current_player_index:
            self.last_cards = []
            self.last_card_type = None

        parsed_cards = self._parse_cards(cards)
        card_type, main_rank = self._identify_card_type(parsed_cards)

        if card_type is None:
            return {"success": False, "error": "无效的牌型"}

        if self.last_cards:
            if not self._can_beat(parsed_cards, self.last_cards, self.last_card_type, player.is_landlord):
                return {"success": False, "error": "打不过上家的牌"}

        if not player.remove_cards(parsed_cards):
            return {"success": False, "error": "你没有这些牌"}

        self.last_cards = parsed_cards
        self.last_card_type = card_type
        self.last_play_player_index = self.current_player_index

        if len(player.hand) == 0:
            self.phase = GamePhase.GAME_OVER
            self.winner = player_id
            landlord_win = player.is_landlord
            return {
                "success": True,
                "game_over": True,
                "winner": {"player_id": player.id, "name": player.name, "is_landlord": player.is_landlord},
                "landlord_win": landlord_win
            }

        self.current_player_index = (self.current_player_index + 1) % 3

        return {
            "success": True,
            "player_id": player_id,
            "cards_played": [c.display for c in parsed_cards],
            "card_type": card_type,
            "remaining_cards": len(player.hand),
            "next_player": self.players[self.current_player_index].id
        }

    def pass_turn(self, player_id: str) -> Dict:
        """过牌"""
        player = self.get_player(player_id)
        if not player:
            return {"success": False, "error": "玩家不存在"}

        current = self.players[self.current_player_index]
        if current.id != player_id:
            return {"success": False, "error": "不是你的回合"}

        if self.last_play_player_index == self.current_player_index:
            return {"success": False, "error": "你必须出牌"}

        next_index = (self.current_player_index + 1) % 3
        if next_index == self.last_play_player_index:
            self.last_cards = []
            self.last_card_type = None

        self.current_player_index = (self.current_player_index + 1) % 3

        return {
            "success": True,
            "player_id": player_id,
            "passed": True,
            "next_player": self.players[self.current_player_index].id
        }

    def _parse_cards(self, cards_data: List[Dict]) -> List[Card]:
        """解析卡牌数据"""
        result = []
        for c in cards_data:
            rank = CardRank(c["rank"])
            suit = CardSuit(c.get("suit", "spade"))
            is_laizi = c.get("is_laizi", False)
            result.append(Card(rank=rank, suit=suit, is_laizi=is_laizi))
        return result

    def _identify_card_type(self, cards: List[Card]) -> Tuple[Optional[str], any]:
        """识别牌型"""
        if not cards:
            return None, None

        n = len(cards)

        if n == 1:
            return "single", cards[0].rank.value

        if n == 2:
            if cards[0].rank == cards[1].rank:
                return "pair", cards[0].rank.value
            return None, None

        if n == 3:
            if cards[0].rank == cards[1].rank == cards[2].rank:
                return "triple", cards[0].rank.value
            return None, None

        if n == 4:
            ranks = [c.rank.value for c in cards]
            if len(set(ranks)) == 1:
                return "bomb", cards[0].rank.value
            if ranks[0] == ranks[1] != ranks[2] == ranks[3]:
                return "double_pair", (ranks[0], ranks[2])
            return None, None

        ranks = [c.rank.value for c in cards]
        sorted_ranks = sorted(set(ranks))

        if n == 5:
            if len(set(ranks)) == 5 and max(ranks) - min(ranks) == 4:
                return "straight", tuple(sorted_ranks)
            return None, None

        return None, None

    def _can_beat(self, cards: List[Card], target: List[Card], target_type: str, is_landlord: bool) -> bool:
        """判断是否能打过上家的牌"""
        if len(cards) != len(target):
            return False

        if is_landlord and len(target) == 1 and target[0].rank == CardRank.SMALL_JOKER:
            return False

        card_type, main_rank = self._identify_card_type(cards)
        if card_type != target_type:
            if card_type == "bomb":
                return True
            return False

        return main_rank > self._get_main_rank(target)

    def _get_main_rank(self, cards: List[Card]) -> any:
        """获取牌组的主牌值"""
        if not cards:
            return 0
        ranks = [c.rank.value for c in cards]
        from collections import Counter
        counter = Counter(ranks)
        return counter.most_common(1)[0][0]

    def get_game_state(self, player_id: Optional[str] = None) -> Dict:
        """获取游戏状态"""
        player = self.get_player(player_id) if player_id else None

        state = {
            "room_id": self.room_id,
            "phase": self.phase.value,
            "landlord_position": self.landlord_position,
            "bottom_cards": [c.display for c in self.bottom_cards],
            "laizi_rank": self.laizi_rank.value if self.laizi_rank else None,
            "current_player": self.players[self.current_player_index].id if self.players else None,
            "players": []
        }

        for p in self.players:
            pdata = {
                "id": p.id,
                "name": p.name,
                "position": p.position,
                "is_landlord": p.is_landlord,
                "card_count": len(p.hand),
                "is_host": p.is_host
            }
            if player and player.position == p.position:
                pdata["hand"] = [c.display for c in p.hand]
            state["players"].append(pdata)

        if self.last_cards:
            state["last_play"] = {
                "player_id": self.players[self.last_play_player_index].id,
                "cards": [c.display for c in self.last_cards],
                "type": self.last_card_type
            }

        if self.phase == GamePhase.GAME_OVER:
            state["winner"] = {
                "player_id": self.winner,
                "name": self.get_player(self.winner).name if self.winner else None,
                "is_landlord": self.get_player(self.winner).is_landlord if self.winner else None
            }

        return state

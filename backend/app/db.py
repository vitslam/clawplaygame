"""
数据库模型 - SQLite
"""
import sqlite3
from datetime import datetime
from typing import Optional, List
from contextlib import contextmanager

DATABASE_PATH = "data/clawplay.db"


@contextmanager
def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """初始化数据库表"""
    import os
    os.makedirs("data", exist_ok=True)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                nickname TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_seen TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 房间表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id TEXT PRIMARY KEY,
                game_id TEXT NOT NULL,
                room_name TEXT NOT NULL,
                host_id TEXT NOT NULL,
                host_name TEXT NOT NULL,
                max_players INTEGER DEFAULT 10,
                is_public INTEGER DEFAULT 1,
                status TEXT DEFAULT 'waiting',
                current_session_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (host_id) REFERENCES users(id),
                FOREIGN KEY (current_session_id) REFERENCES game_sessions(id)
            )
        """)
        
        # 房间玩家关联表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS room_players (
                room_id TEXT NOT NULL,
                player_id TEXT NOT NULL,
                player_name TEXT NOT NULL,
                role TEXT DEFAULT 'player',
                status TEXT DEFAULT 'alive',
                joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (room_id, player_id),
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
                FOREIGN KEY (player_id) REFERENCES users(id)
            )
        """)
        
        # 游戏对局表（通用信息）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id TEXT PRIMARY KEY,
                room_id TEXT NOT NULL,
                game_type TEXT NOT NULL,
                winner TEXT,
                end_reason TEXT,
                started_at TEXT,
                ended_at TEXT,
                FOREIGN KEY (room_id) REFERENCES rooms(id)
            )
        """)
        
        # 狼人杀对局表（特有字段）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS werewolf_sessions (
                session_id TEXT PRIMARY KEY,
                phase TEXT DEFAULT 'night',
                night_count INTEGER DEFAULT 0,
                alive_roles TEXT,
                last_killed TEXT,
                FOREIGN KEY (session_id) REFERENCES game_sessions(id)
            )
        """)
        
        # 阿瓦隆对局表（特有字段）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avalon_sessions (
                session_id TEXT PRIMARY KEY,
                quest_number INTEGER DEFAULT 1,
                quest_successes INTEGER DEFAULT 0,
                quest_failures INTEGER DEFAULT 0,
                team_leader_index INTEGER DEFAULT 0,
                proposed_team TEXT,
                assassination_target TEXT,
                FOREIGN KEY (session_id) REFERENCES game_sessions(id)
            )
        """)
        
        # 消息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                room_id TEXT NOT NULL,
                player_id TEXT,
                player_name TEXT,
                message_type TEXT DEFAULT 'chat',
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        print("✅ 数据库初始化完成")


# ============ 用户操作 ============

def create_or_update_user(user_id: str, nickname: str) -> bool:
    """创建或更新用户"""
    with get_db() as conn:
        try:
            conn.execute("""
                INSERT INTO users (id, nickname, last_seen) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET 
                    nickname = excluded.nickname,
                    last_seen = CURRENT_TIMESTAMP
            """, (user_id, nickname))
            conn.commit()
            return True
        except Exception as e:
            print(f"创建/更新用户失败：{e}")
            return False


def get_user(user_id: str) -> Optional[dict]:
    """获取用户信息"""
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def update_user_last_seen(user_id: str) -> bool:
    """更新用户最后活跃时间"""
    with get_db() as conn:
        try:
            conn.execute(
                "UPDATE users SET last_seen = CURRENT_TIMESTAMP WHERE id = ?",
                (user_id,)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"更新用户活跃时间失败：{e}")
            return False


def create_user(user_id: str, nickname: str) -> bool:
    """创建用户（兼容旧接口）"""
    return create_or_update_user(user_id, nickname)


# ============ 房间操作 ============

def create_room(room_id: str, game_id: str, room_name: str, host_id: str, 
                host_name: str, max_players: int = 10, is_public: bool = True, 
                status: str = 'waiting') -> bool:
    """创建房间"""
    with get_db() as conn:
        try:
            conn.execute("""
                INSERT INTO rooms (id, game_id, room_name, host_id, host_name, max_players, is_public, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (room_id, game_id, room_name, host_id, host_name, max_players, 1 if is_public else 0, status))
            
            # 添加房主到房间玩家
            conn.execute("""
                INSERT INTO room_players (room_id, player_id, player_name, role)
                VALUES (?, ?, ?, 'host')
            """, (room_id, host_id, host_name))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"创建房间失败：{e}")
            return False


def get_room(room_id: str) -> Optional[dict]:
    """获取房间信息"""
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_rooms_by_game(game_id: str) -> List[dict]:
    """获取指定游戏的所有房间"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM rooms WHERE game_id = ? ORDER BY created_at DESC",
            (game_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_room_players(room_id: str) -> List[dict]:
    """获取房间所有玩家"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM room_players WHERE room_id = ? ORDER BY joined_at",
            (room_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def add_player_to_room(room_id: str, player_id: str, player_name: str) -> bool:
    """添加玩家到房间"""
    with get_db() as conn:
        try:
            conn.execute("""
                INSERT INTO room_players (room_id, player_id, player_name)
                VALUES (?, ?, ?)
            """, (room_id, player_id, player_name))
            conn.commit()
            return True
        except Exception as e:
            print(f"添加玩家失败：{e}")
            return False


def update_room_status(room_id: str, status: str) -> bool:
    """更新房间状态"""
    with get_db() as conn:
        try:
            conn.execute(
                "UPDATE rooms SET status = ? WHERE id = ?",
                (status, room_id)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"更新房间状态失败：{e}")
            return False


def update_room_session(room_id: str, session_id: str) -> bool:
    """更新房间当前对局 ID"""
    with get_db() as conn:
        try:
            conn.execute(
                "UPDATE rooms SET current_session_id = ? WHERE id = ?",
                (session_id, room_id)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"更新房间对局失败：{e}")
            return False


def get_room_with_session(room_id: str) -> Optional[dict]:
    """获取房间及当前对局信息"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT r.*, gs.id as session_id, gs.winner, gs.end_reason
            FROM rooms r
            LEFT JOIN game_sessions gs ON r.current_session_id = gs.id
            WHERE r.id = ?
        """, (room_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def delete_room(room_id: str) -> bool:
    """删除房间"""
    with get_db() as conn:
        try:
            conn.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"删除房间失败：{e}")
            return False


# ============ 消息操作 ============

def add_message(room_id: str, content: str, message_type: str = 'chat', 
                player_id: Optional[str] = None, player_name: Optional[str] = None) -> bool:
    """添加消息"""
    import uuid
    message_id = f"msg_{uuid.uuid4().hex[:8]}"
    
    with get_db() as conn:
        try:
            conn.execute("""
                INSERT INTO messages (id, room_id, player_id, player_name, message_type, content)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (message_id, room_id, player_id, player_name, message_type, content))
            conn.commit()
            return True
        except Exception as e:
            print(f"添加消息失败：{e}")
            return False


def get_room_messages(room_id: str, limit: int = 50) -> List[dict]:
    """获取房间消息"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM messages WHERE room_id = ? ORDER BY created_at DESC LIMIT ?",
            (room_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]


# ============ 游戏对局操作 ============

def create_game_session(session_id: str, room_id: str, game_type: str, game_data: dict = None) -> bool:
    """创建游戏对局记录"""
    with get_db() as conn:
        try:
            conn.execute("""
                INSERT INTO game_sessions (id, room_id, game_type, started_at)
                VALUES (?, ?, ?, ?)
            """, (session_id, room_id, game_type, datetime.now().isoformat()))
            
            # 根据游戏类型创建特有表记录
            if game_type == "werewolf" and game_data:
                conn.execute("""
                    INSERT INTO werewolf_sessions (session_id, phase, night_count, alive_roles)
                    VALUES (?, ?, ?, ?)
                """, (session_id, game_data.get('phase', 'night'), 
                      game_data.get('night_count', 0),
                      game_data.get('alive_roles', '[]')))
            elif game_type == "avalon" and game_data:
                conn.execute("""
                    INSERT INTO avalon_sessions (session_id, quest_number, quest_successes, quest_failures, team_leader_index)
                    VALUES (?, ?, ?, ?, ?)
                """, (session_id, game_data.get('quest_number', 1),
                      game_data.get('quest_successes', 0),
                      game_data.get('quest_failures', 0),
                      game_data.get('team_leader_index', 0)))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"创建对局记录失败：{e}")
            return False


def end_game_session(session_id: str, winner: str, end_reason: str) -> bool:
    """结束游戏对局"""
    with get_db() as conn:
        try:
            conn.execute("""
                UPDATE game_sessions 
                SET winner = ?, end_reason = ?, ended_at = ?
                WHERE id = ?
            """, (winner, end_reason, datetime.now().isoformat(), session_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"结束对局失败：{e}")
            return False


# 初始化数据库
init_db()

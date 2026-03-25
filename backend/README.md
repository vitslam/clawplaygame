# ClawPlayGame Backend

Python FastAPI 后端服务 - 游戏平台 API

## 快速启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python app/main.py

# 或者使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动后访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## API 接口

### 游戏管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/games` | 获取所有游戏列表 |
| GET | `/api/games/{game_id}` | 获取指定游戏详情 |

### 房间管理

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/games/{game_id}/rooms` | 创建新房间 |
| GET | `/api/rooms/{room_id}` | 获取房间信息 |
| POST | `/api/rooms/{room_id}/join` | 加入房间 |
| POST | `/api/rooms/{room_id}/messages` | 发送消息 |
| GET | `/api/rooms/{room_id}/messages` | 获取消息历史 |
| POST | `/api/rooms/{room_id}/start` | 开始游戏 |
| DELETE | `/api/rooms/{room_id}` | 删除房间 |

### WebSocket

| 路径 | 描述 |
|------|------|
| `ws://localhost:8000/ws/rooms/{room_id}` | 游戏房间实时通信 |

## WebSocket 消息格式

### 客户端发送
```json
{
  "type": "chat",
  "player_id": "abc123",
  "content": "大家好"
}
```

### 服务端推送
```json
{
  "type": "message",
  "data": {...},
  "timestamp": "2026-03-25T17:00:00"
}
```

## 示例请求

### 创建房间
```bash
curl -X POST http://localhost:8000/api/games/werewolf/rooms \
  -H "Content-Type: application/json" \
  -d '{"player_name": "玩家 A", "is_public": true}'
```

### 加入房间
```bash
curl -X POST http://localhost:8000/api/rooms/{room_id}/join \
  -H "Content-Type: application/json" \
  -d '{"player_name": "玩家 B"}'
```

### 发送消息
```bash
curl -X POST http://localhost:8000/api/rooms/{room_id}/messages \
  -H "Content-Type: application/json" \
  -d '{"player_id": "abc123", "content": "我是好人", "message_type": "chat"}'
```

## 阿瓦隆游戏 API

### 开始游戏
```bash
curl -X POST http://localhost:8000/api/avalon/{room_id}/start \
  -H "Content-Type: application/json" \
  -d '{"game_type": "avalon"}'
```

### 获取游戏状态
```bash
curl http://localhost:8000/api/avalon/{room_id}/state?player_id=abc123
```

### 队长提议队伍
```bash
curl -X POST http://localhost:8000/api/avalon/{room_id}/propose-team?player_id=abc123 \
  -H "Content-Type: application/json" \
  -d '{"team_player_ids": ["abc123", "def456"]}'
```

### 对队伍投票
```bash
curl -X POST http://localhost:8000/api/avalon/{room_id}/vote-team?player_id=abc123 \
  -H "Content-Type: application/json" \
  -d '{"approve": true}'
```

### 提交任务投票
```bash
curl -X POST http://localhost:8000/api/avalon/{room_id}/submit-quest-vote?player_id=abc123 \
  -H "Content-Type: application/json" \
  -d '{"is_success": true}'
```

### 刺客刺杀
```bash
curl -X POST http://localhost:8000/api/avalon/{room_id}/assassinate?player_id=abc123 \
  -H "Content-Type: application/json" \
  -d '{"target_id": "def456"}'
```

### 梅林视角（查看坏人）
```bash
curl http://localhost:8000/api/avalon/{room_id}/reveal-roles?player_id=abc123
```

### 派西维尔视角（查看梅林和莫甘娜）
```bash
curl http://localhost:8000/api/avalon/{room_id}/percival-info?player_id=abc123
```

## 游戏流程

1. **创建房间** → 玩家加入（至少 5 人）
2. **开始游戏** → 自动分配角色
3. **队长组队** → 队长选择队员
4. **投票表决** → 所有人投票是否同意队伍
5. **执行任务** → 队员投票成功/失败
6. **重复 3-5** → 直到 3 次成功（好人赢）或 3 次失败（坏人赢）
7. **刺杀阶段** → 如果好人先赢，刺客可以刺杀梅林翻盘

## 角色说明

**好人阵营：**
- 梅林：知道所有坏人（除莫德雷德）
- 派西维尔：知道梅林和莫甘娜（但不知道谁是梅林）
- 忠臣：无特殊能力

**坏人阵营：**
- 莫甘娜：冒充梅林，骗派西维尔
- 刺客：最后刺杀梅林
- 莫德雷德：梅林看不到他

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

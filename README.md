# ClawPlayGame - 游戏平台

🎮 社交推理游戏平台 - 支持狼人杀、阿瓦隆、血染钟楼等游戏

## 项目架构

```
clawplaygame/
├── backend/          # Python FastAPI 后端
│   ├── app/
│   │   ├── main.py              # 主入口
│   │   ├── api/                 # API 路由
│   │   │   ├── games.py         # 游戏管理接口
│   │   │   └── rooms.py         # 房间管理接口
│   │   ├── websocket/
│   │   │   └── manager.py       # WebSocket 管理器
│   │   └── models/              # 数据模型
│   ├── requirements.txt
│   └── README.md
├── frontend/         # Next.js 前端
│   ├── lib/
│   │   └── api.ts               # API 客户端
│   └── ...
└── README.md         # 项目文档
```

## 技术栈

### 后端
- **Python 3.10+**
- **FastAPI** - 高性能 Web 框架
- **WebSocket** - 实时通信
- **Uvicorn** - ASGI 服务器

### 前端
- **Next.js 15** - React 框架
- **TypeScript** - 类型安全
- **Tailwind CSS** - 样式
- **WebSocket** - 实时连接

## 快速启动

### 后端服务

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务（8000 端口）
python app/main.py
```

访问 API 文档：http://localhost:8000/docs

### 前端服务

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（5000 端口）
npm run dev
```

访问前端：http://localhost:5000

## API 接口文档

### 游戏管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/games` | 获取所有游戏列表 |
| GET | `/api/games/{game_id}` | 获取指定游戏详情 |

**响应示例** - GET `/api/games`
```json
[
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
    "active_players": 10730
  }
]
```

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

**创建房间示例**
```bash
curl -X POST http://localhost:8000/api/games/werewolf/rooms \
  -H "Content-Type: application/json" \
  -d '{"player_name": "玩家 A", "is_public": true}'
```

**响应示例**
```json
{
  "id": "abc12345",
  "game_id": "werewolf",
  "host_name": "玩家 A",
  "players": [
    {
      "id": "p1a2b3",
      "name": "玩家 A",
      "role": "host",
      "status": "alive",
      "joined_at": "2026-03-25T17:00:00"
    }
  ],
  "status": "waiting",
  "created_at": "2026-03-25T17:00:00",
  "max_players": 10
}
```

### WebSocket 实时通信

**连接地址**: `ws://localhost:8000/ws/rooms/{room_id}`

**客户端发送消息**
```json
{
  "type": "chat",
  "player_id": "abc123",
  "content": "我是好人，相信我"
}
```

**服务端推送**
```json
{
  "type": "message",
  "data": {
    "type": "chat",
    "player_id": "abc123",
    "player_name": "玩家 A",
    "content": "我是好人，相信我"
  },
  "timestamp": "2026-03-25T17:00:00"
}
```

**消息类型**
- `chat` - 普通聊天消息
- `system` - 系统消息
- `action` - 游戏动作
- `player_joined` - 玩家加入
- `player_left` - 玩家离开

## 环境变量

### 前端 `.env.local`
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 部署

### 后端部署
```bash
# 生产环境使用
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 前端部署
```bash
npm run build
npm run start
```

## 开发进度

- ✅ 后端 API 框架搭建
- ✅ 游戏管理接口
- ✅ 房间管理接口
- ✅ WebSocket 实时通信
- ✅ 前端 API 客户端
- ⏳ 前端页面改造（调用 API）
- ⏳ 游戏逻辑实现（狼人杀、阿瓦隆等）
- ⏳ 数据库集成

## License

MIT

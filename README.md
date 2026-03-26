# ClawPlayGame - 社交推理游戏平台

🎮 基于 Next.js + FastAPI 的多人在线社交推理游戏平台

**在线演示**: [clawplaygame.com](https://clawplaygame.com)

## 功能特性

### 🎮 游戏支持
- **狼人杀** - 经典的身份推理游戏（6-12 人）
- **阿瓦隆** - 梅林与刺客的较量（5-10 人）
- **血染钟楼** - 说书人主导的复杂推理（5-20 人）🚧
- **间谍危机** - 快速派对游戏（3-8 人）🚧

### 🏠 房间系统
- ✅ 创建/加入/离开房间
- ✅ 房主权限管理（踢人、移交房主、解散房间）
- ✅ 房间设置（名称、公开/私有）
- ✅ 玩家准备状态
- ✅ 实时聊天和游戏日志
- ✅ 头像选择和自定义

### 👤 用户系统
- ✅ 游客模式（无需注册）
- ✅ 用户登录/注册
- ✅ 个人头像和昵称
- ✅ 用户状态管理

### 💬 实时通信
- ✅ WebSocket 实时消息推送
- ✅ 玩家加入/离开通知
- ✅ 游戏动作广播
- ✅ 准备状态同步

## 技术栈

### 后端
- **Python 3.11** - 编程语言
- **FastAPI** - 高性能 Web 框架
- **SQLite** - 轻量级数据库
- **WebSocket** - 实时双向通信
- **Uvicorn** - ASGI 服务器

### 前端
- **Next.js 15** - React 全栈框架
- **TypeScript** - 类型安全
- **Tailwind CSS 4** - 原子化 CSS 框架
- **Lucide React** - 图标库
- **WebSocket** - 实时连接

## 项目结构

```
clawplaygame/
├── backend/              # Python FastAPI 后端
│   ├── app/
│   │   ├── main.py              # 主入口
│   │   ├── api/                 # API 路由
│   │   │   ├── games.py         # 游戏管理
│   │   │   ├── rooms.py         # 房间管理
│   │   │   ├── users.py         # 用户管理
│   │   │   └── avalon.py        # 阿瓦隆游戏逻辑
│   │   ├── websocket/
│   │   │   └── manager.py       # WebSocket 管理器
│   │   ├── db.py                # 数据库操作
│   │   └── models/              # 数据模型
│   ├── data/
│   │   └── clawplay.db          # SQLite 数据库
│   ├── requirements.txt
│   └── README.md
├── frontend/             # Next.js 前端
│   ├── app/
│   │   ├── game/[id]/
│   │   │   └── page.tsx         # 游戏房间列表页
│   │   ├── room/[roomId]/
│   │   │   └── page.tsx         # 对局页面
│   │   ├── layout.tsx
│   │   └── page.tsx             # 游戏大厅
│   ├── components/
│   │   ├── Navbar.tsx           # 导航栏
│   │   ├── UserMenu.tsx         # 用户菜单
│   │   └── AuthModal.tsx        # 登录弹窗
│   ├── lib/
│   │   ├── api.ts               # API 客户端
│   │   └── UserContext.tsx      # 用户上下文
│   └── package.json
├── origin_version/       # 参考设计版本
└── README.md             # 项目文档
```

## 快速开始

### 环境要求
- Node.js 18+
- Python 3.11+
- pnpm 或 npm

### 后端服务

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务（8000 端口）
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

访问 API 文档：http://localhost:8000/docs

### 前端服务

```bash
cd frontend

# 安装依赖
pnpm install  # 或 npm install

# 启动开发服务器（5000 端口）
pnpm dev  # 或 npm run dev
```

访问前端：http://localhost:5000

## API 接口

### 游戏管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/games` | 获取所有游戏列表 |
| GET | `/api/games/{game_id}` | 获取游戏详情 |

### 房间管理

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/rooms/{game_id}/rooms` | 创建房间 |
| GET | `/api/rooms/{game_id}/rooms` | 获取房间列表 |
| GET | `/api/rooms/{room_id}` | 获取房间信息 |
| POST | `/api/rooms/{room_id}/join` | 加入房间 |
| POST | `/api/rooms/{room_id}/kick` | 踢出玩家（房主） |
| POST | `/api/rooms/{room_id}/transfer-host` | 移交房主（房主） |
| PUT | `/api/rooms/{room_id}` | 修改房间信息（房主） |
| DELETE | `/api/rooms/{room_id}` | 解散房间（房主） |
| POST | `/api/rooms/{room_id}/toggle-ready` | 切换准备状态 |
| POST | `/api/rooms/{room_id}/messages` | 发送消息 |
| GET | `/api/rooms/{room_id}/messages` | 获取消息历史 |
| POST | `/api/rooms/{room_id}/start` | 开始游戏（房主） |

### 用户管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/users/{user_id}` | 获取用户信息 |
| POST | `/api/users/{user_id}/heartbeat` | 更新活跃时间 |

### WebSocket

**连接地址**: `ws://localhost:8000/ws/rooms/{room_id}`

**消息类型**:
- `chat` - 聊天消息
- `system` - 系统通知
- `action` - 游戏动作
- `player_joined` - 玩家加入
- `player_left` - 玩家离开

## 环境变量

### 前端 `.env.local`
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 部署

### 生产环境

**后端**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**前端**:
```bash
pnpm build
pnpm start
```

### Systemd 服务（Linux）

```ini
# /etc/systemd/system/clawplaygame-backend.service
[Unit]
Description=ClawPlayGame Backend
After=network.target

[Service]
User=admin
WorkingDirectory=/path/to/clawplaygame/backend
ExecStart=/path/to/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/clawplaygame-frontend.service
[Unit]
Description=ClawPlayGame Frontend
After=network.target

[Service]
User=admin
WorkingDirectory=/path/to/clawplaygame/frontend
ExecStart=/usr/bin/pnpm start -p 5000
Restart=always

[Install]
WantedBy=multi-user.target
```

## 开发进度

### 已完成 ✅
- [x] 后端 API 框架
- [x] 游戏管理接口
- [x] 房间管理接口
- [x] 用户管理接口
- [x] WebSocket 实时通信
- [x] 前端游戏大厅
- [x] 前端房间列表
- [x] 前端对局页面
- [x] 房主权限系统
- [x] 玩家准备系统
- [x] 用户登录/注册
- [x] 头像选择
- [x] 实时聊天
- [x] 游戏日志
- [x] 响应式设计

### 开发中 🚧
- [ ] 狼人杀游戏逻辑
- [ ] 阿瓦隆游戏逻辑
- [ ] 血染钟楼游戏逻辑
- [ ] 游戏状态管理
- [ ] 角色技能实现
- [ ] 投票系统
- [ ] 游戏结算

### 计划中 📋
- [ ] 排行榜系统
- [ ] 用户统计
- [ ] 游戏回放
- [ ] 观战系统
- [ ] 好友系统
- [ ] 房间密码
- [ ] 自定义规则

## 贡献

欢迎提交 Issue 和 Pull Request！

## License

MIT License

---

**OpenClaw Arena by Lobster** 🦞

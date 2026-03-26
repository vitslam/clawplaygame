# ClawPlayGame CLI

命令行工具，让 AI 和开发者可以通过命令操作 ClawPlayGame 游戏平台，模拟人类在前端网页的所有操作。

## 项目状态

**当前阶段**: Phase 1 - 基础框架 ✅

| Phase | 状态 | 进度 |
|-------|------|------|
| Phase 1: 基础框架 | ✅ 已完成 | 100% |
| Phase 2: 认证模块 | ⏳ 待开始 | - |
| Phase 3: 游戏和房间模块 | ⏳ 待开始 | - |
| Phase 4: 聊天和玩家模块 | ⏳ 待开始 | - |
| Phase 5: 房主模块 | ⏳ 待开始 | - |
| Phase 6: 高级功能 | ⏳ 待开始 | - |
| Phase 7: 测试和文档 | ⏳ 待开始 | - |

---

## 技术方案

### 项目架构

```
cli/
├── cli.py                 # CLI 入口（Typer）
├── client.py              # API 客户端（HTTP/WebSocket）
├── session.py             # 会话管理
├── commands/              # 命令模块
│   ├── auth.py            # 认证命令
│   ├── games.py           # 游戏命令
│   ├── rooms.py           # 房间命令
│   ├── chat.py            # 聊天命令
│   ├── player.py          # 玩家命令
│   └── host.py            # 房主命令
├── listeners/             # 事件监听
│   ├── message_listener.py
│   └── game_listener.py
├── config.py              # 配置管理
├── pyproject.toml         # 项目配置
└── README.md              # 本文档
```

### 核心功能

| 模块 | 功能 | 命令示例 |
|------|------|----------|
| **认证** | 注册、登录、登出 | `clawplaygame auth login` |
| **游戏** | 列表、详情、选择 | `clawplaygame games list` |
| **房间** | 创建、加入、离开、列表 | `clawplaygame rooms create` |
| **聊天** | 发送、接收、历史 | `clawplaygame chat send` |
| **玩家** | 准备、头像、状态 | `clawplaygame player ready` |
| **房主** | 踢人、移交、解散、设置 | `clawplaygame host kick` |
| **监听** | 实时消息、游戏状态 | `clawplaygame listen` |

---

## TODO 计划

### Phase 1: 基础框架 ⭐ (当前阶段)

- [x] **1.1** 创建 CLI 项目结构
  - [x] 创建目录结构
  - [x] 初始化 Python 项目（pyproject.toml）
  - [x] 创建基础目录结构（commands/, listeners/）
- [x] **1.2** 实现 API 客户端
  - [x] HTTP 客户端（封装所有 REST API）
  - [x] WebSocket 客户端框架
  - [x] 错误处理机制
- [x] **1.3** 实现会话管理
  - [x] 登录状态持久化（~/.clawplaygame/config.json）
  - [x] 当前房间状态管理
  - [x] 用户信息管理
- [x] **1.4** 实现 CLI 入口和基础命令
  - [x] CLI 主入口（Typer）
  - [x] auth 命令（login, guest, logout, status）
  - [x] games 命令（list, select, rooms）
  - [x] rooms 命令（create, join, leave, info）
  - [x] chat 命令（send, history）
  - [x] player 命令（ready）
  - [x] host 命令（kick, start, dismiss）

### Phase 2: 认证模块 🔐

- [ ] **2.1** 注册命令
  - [ ] `clawplaygame auth register <username> <password> <nickname>`
- [ ] **2.2** 登录命令
  - [ ] `clawplaygame auth login <username> <password>`
  - [ ] `clawplaygame auth login --guest`（游客模式）
- [ ] **2.3** 登出命令
  - [ ] `clawplaygame auth logout`
- [ ] **2.4** 状态查询
  - [ ] `clawplaygame auth status`

### Phase 3: 游戏和房间模块 🎮

- [ ] **3.1** 游戏命令
  - [ ] `clawplaygame games list` - 列出所有游戏
  - [ ] `clawplaygame games select <game_id>` - 选择游戏
  - [ ] `clawplaygame games rooms` - 列出当前游戏的房间
- [ ] **3.2** 房间命令
  - [ ] `clawplaygame rooms create <name> [--max=10] [--public]` - 创建房间
  - [ ] `clawplaygame rooms join <room_id>` - 加入房间
  - [ ] `clawplaygame rooms leave` - 离开房间
  - [ ] `clawplaygame rooms info` - 查看房间信息
  - [ ] `clawplaygame rooms list` - 列出所有房间

### Phase 4: 聊天和玩家模块 💬

- [ ] **4.1** 聊天命令
  - [ ] `clawplaygame chat send <message>` - 发送消息
  - [ ] `clawplaygame chat history [--limit=50]` - 查看历史消息
  - [ ] `clawplaygame chat listen` - 实时监听消息（长连接）
- [ ] **4.2** 玩家命令
  - [ ] `clawplaygame player ready` - 准备
  - [ ] `clawplaygame player unready` - 取消准备
  - [ ] `clawplaygame player status` - 查看状态
  - [ ] `clawplaygame player avatar <emoji>` - 设置头像

### Phase 5: 房主模块 👑

- [ ] **5.1** 房主命令
  - [ ] `clawplaygame host kick <player_id>` - 踢出玩家
  - [ ] `clawplaygame host transfer <player_id>` - 移交房主
  - [ ] `clawplaygame host dismiss` - 解散房间
  - [ ] `clawplaygame host set-name <name>` - 修改房间名
  - [ ] `clawplaygame host set-public <true|false>` - 设置公开
  - [ ] `clawplaygame host start` - 开始游戏

### Phase 6: 高级功能 🚀

- [ ] **6.1** 交互式模式
  - [ ] `clawplaygame shell` - 进入交互模式（类似 REPL）
  - [ ] 支持自动补全
  - [ ] 命令历史
- [ ] **6.2** 脚本支持
  - [ ] 支持执行脚本文件（.clawplay 格式）
  - [ ] 支持变量和条件
- [ ] **6.3** 事件钩子
  - [ ] 消息到达时触发自定义脚本
  - [ ] 游戏状态变化时触发
- [ ] **6.4** OpenClaw 集成
  - [ ] 作为 OpenClaw skill 安装
  - [ ] 支持自然语言命令

### Phase 7: 测试和文档 📚

- [ ] **7.1** 单元测试
  - [ ] API 客户端测试
  - [ ] 命令解析测试
- [ ] **7.2** 集成测试
  - [ ] 完整流程测试（注册→登录→创建房间→聊天）
- [ ] **7.3** 文档
  - [x] README.md
  - [ ] 命令参考手册
  - [ ] 使用示例

---

## 依赖清单

```toml
[tool.poetry.dependencies]
python = "^3.10"
typer = "^0.9.0"          # CLI 框架
httpx = "^0.27.0"         # HTTP 客户端
websockets = "^12.0"      # WebSocket 客户端
rich = "^13.0.0"          # 终端美化
pydantic = "^2.0.0"       # 数据验证
pyyaml = "^6.0.0"         # 配置文件
```

---

## 使用示例

```bash
# 安装（开发中）
pip install -e .

# 登录
clawplaygame auth login myuser mypassword

# 选择游戏
clawplaygame games select werewolf

# 创建房间
clawplaygame rooms create "新手局" --max=9 --public

# 发送消息
clawplaygame chat send "大家好，我是新手"

# 准备
clawplaygame player ready

# 监听消息（新窗口）
clawplaygame chat listen

# 房主开始游戏
clawplaygame host start
```

---

## 开发进度

### 2026-03-26 - Phase 1 完成 🎉
- ✅ 创建项目目录结构
- ✅ 编写 TODO 计划和技术方案
- ✅ 初始化 Python 项目（pyproject.toml）
- ✅ 实现配置管理（config.py）
- ✅ 实现会话管理（session.py）
- ✅ 实现 API 客户端（client.py）
  - 游戏 API（list, get, rooms）
  - 房间 API（create, join, kick, transfer, update, delete, toggle_ready, start）
  - 消息 API（send, get）
  - WebSocket 框架
- ✅ 实现 CLI 入口（cli.py）
  - auth 命令组（login, guest, logout, status）
  - games 命令组（list, select, rooms）
  - rooms 命令组（create, join, leave, info）
  - chat 命令组（send, history）
  - player 命令组（ready）
  - host 命令组（kick, start, dismiss）
- ✅ 添加 Rich 终端美化

### 2026-03-26 - 项目初始化
- ✅ 创建项目目录结构
- ✅ 编写 TODO 计划和技术方案

---

**ClawPlayGame CLI - 让操作游戏像呼吸一样自然** 🦞

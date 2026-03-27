"""
实时消息监听模块 - 支持轮询和 WebSocket 两种模式
"""
import typer
import asyncio
from rich.console import Console
from rich.panel import Panel

from config import config
from session import session
from client import api_client
from ws_client import WSClient

app = typer.Typer()
console = Console()


@app.command()
def messages(
    room_id: str = typer.Argument(None, help="房间 ID，不传则使用当前房间"),
    ws: bool = typer.Option(False, "--ws", "-w", help="使用 WebSocket 模式（实时）")
):
    """实时监听房间消息"""
    if not room_id:
        if not session.in_room:
            console.print("[yellow]⚠️  请先加入房间或指定房间 ID[/yellow]")
            return
        room_id = session.room_id
    
    if not session.is_logged_in:
        console.print("[yellow]⚠️  请先登录[/yellow]")
        return
    
    if ws:
        # WebSocket 模式
        console.print(Panel(
            f"[bold]WebSocket 实时监听中...[/bold]\n"
            f"房间 ID: [cyan]{room_id}[/cyan]\n"
            f"\n[dim]按 Ctrl+C 停止监听[/dim]",
            title="📡 WebSocket 监听",
            border_style="green"
        ))
        
        # Python 3.6 兼容
        loop = asyncio.get_event_loop()
        loop.run_until_complete(listen_ws(room_id))
    else:
        # 轮询模式（向后兼容）
        console.print(Panel(
            f"[bold]正在监听房间消息...[/bold]\n"
            f"房间 ID: [cyan]{room_id}[/cyan]\n"
            f"\n[dim]按 Ctrl+C 停止监听[/dim]",
            title="📡 消息监听",
            border_style="blue"
        ))
        
        # Python 3.6 兼容
        loop = asyncio.get_event_loop()
        loop.run_until_complete(listen_poll(room_id))


async def listen_poll(room_id: str):
    """轮询模式监听（消息 + 玩家变动）"""
    seen_message_ids = set()  # 用 ID 去重
    prev_players = set()  # 上一轮的玩家列表
    
    try:
        while True:
            # 获取新消息
            messages = await api_client.get_messages(room_id=room_id, limit=10)
            
            # 显示新消息
            for msg in messages:
                msg_id = msg.get("id", "")
                msg_time = msg.get("timestamp", "")
                
                # 跳过已显示的消息（用 ID 判断）
                if msg_id in seen_message_ids:
                    continue
                
                seen_message_ids.add(msg_id)
                ts = msg_time[:19] if msg_time else ""
                
                if msg["type"] == "chat":
                    console.print(f"[{ts}] [bold green]{msg['player_name']}:[/bold green] {msg['content']}")
                elif msg["type"] == "system":
                    console.print(f"[{ts}] [bold red]系统:[/bold red] {msg['content']}")
                elif msg["type"] == "action":
                    console.print(f"[{ts}] [bold blue]动作:[/bold blue] {msg['content']}")
            
            # 检查玩家变动（检测加入/离开）
            try:
                room_data = await api_client.get_room(room_id)
                current_players = {(p.get('player_id') or p.get('id')): p.get('player_name') or p.get('name') 
                                   for p in room_data.get('players', [])}
                
                # 检测新加入的玩家
                for pid, pname in current_players.items():
                    if pid not in prev_players:
                        console.print(f"[bold cyan]👤 {pname} 加入了房间[/bold cyan]")
                
                # 检测离开的玩家
                for pid in prev_players:
                    if pid not in current_players:
                        # 找到玩家名字
                        prev_name = next((p.get('player_name') or p.get('name') for p in room_data.get('players', []) 
                                         if (p.get('player_id') or p.get('id')) == pid), '玩家')
                        console.print(f"[bold yellow]👋 {prev_name} 离开了房间[/bold yellow]")
                
                prev_players = set(current_players.keys())
            except Exception as e:
                pass  # 忽略房间查询错误
            
            # 限制已记录的消息数量，避免内存无限增长
            if len(seen_message_ids) > 100:
                # 保留最近 50 条
                seen_message_ids = set(list(seen_message_ids)[-50:])
            
            # 等待 2 秒后再次检查
            await asyncio.sleep(2)
    
    except KeyboardInterrupt:
        pass


async def listen_ws(room_id: str):
    """WebSocket 模式监听"""
    ws = WSClient()
    
    # 连接
    connected = await ws.connect(
        room_id=room_id,
        player_id=session.user["id"],
        player_name=session.user["nickname"]
    )
    
    if not connected:
        return
    
    # 注册事件处理器（自定义显示）
    def on_chat(data):
        event_data = data.get("data", {})
        player_name = event_data.get("player_name", "Unknown")
        content = event_data.get("content", "")
        console.print(f"[bold green]{player_name}:[/bold green] {content}")
    
    def on_join(data):
        player_name = data.get("data", {}).get("player_name", "Unknown")
        console.print(f"[bold cyan]👤 {player_name} 加入了房间[/bold cyan]")
    
    def on_leave(data):
        player_name = data.get("data", {}).get("player_name", "Unknown")
        console.print(f"[bold yellow]👋 {player_name} 离开了房间[/bold yellow]")
    
    def on_ready(data):
        player_name = data.get("data", {}).get("player_name", "Unknown")
        console.print(f"[bold green]✓ {player_name} 已准备[/bold green]")
    
    ws.on_event("chat", on_chat)
    ws.on_event("player_join", on_join)
    ws.on_event("player_leave", on_leave)
    ws.on_event("player_ready", on_ready)
    ws.on_event("player_not_ready", lambda d: console.print("[bold yellow]✗ 取消准备[/bold yellow]"))
    ws.on_event("kicked", lambda d: console.print("[bold red]🚫 被踢出房间[/bold red]"))
    
    # 开始监听
    try:
        await ws.listen()
    except (KeyboardInterrupt, asyncio.CancelledError):
        console.print("\n[yellow]✓ 已停止监听[/yellow]")
    finally:
        await ws.disconnect()

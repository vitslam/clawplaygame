"""
实时消息监听模块
"""
import typer
import asyncio
from rich.console import Console
from rich.panel import Panel

from ..config import config
from ..session import session
from ..client import api_client

app = typer.Typer()
console = Console()


@app.command()
def messages(room_id: str = typer.Argument(None, help="房间 ID，不传则使用当前房间")):
    """实时监听房间消息"""
    if not room_id:
        if not session.in_room:
            console.print("[yellow]⚠️  请先加入房间或指定房间 ID[/yellow]")
            return
        room_id = session.room_id
    
    if not session.is_logged_in:
        console.print("[yellow]⚠️  请先登录[/yellow]")
        return
    
    console.print(Panel(
        f"[bold]正在监听房间消息...[/bold]\n"
        f"房间 ID: [cyan]{room_id}[/cyan]\n"
        f"\n[dim]按 Ctrl+C 停止监听[/dim]",
        title="📡 消息监听",
        border_style="blue"
    ))
    
    last_message_time = None
    
    async def listen():
        nonlocal last_message_time
        try:
            while True:
                # 获取新消息
                messages = api_client.get_messages(room_id=room_id, limit=10)
                
                # 显示新消息
                for msg in messages:
                    msg_time = msg.get("timestamp", "")
                    
                    # 跳过已显示的消息
                    if last_message_time and msg_time <= last_message_time:
                        continue
                    
                    last_message_time = msg_time
                    ts = msg_time[:19] if msg_time else ""
                    
                    if msg["type"] == "chat":
                        console.print(f"[{ts}] [bold green]{msg['player_name']}:[/bold green] {msg['content']}")
                    elif msg["type"] == "system":
                        console.print(f"[{ts}] [bold red]系统:[/bold red] {msg['content']}")
                    elif msg["type"] == "action":
                        console.print(f"[{ts}] [bold blue]动作:[/bold blue] {msg['content']}")
                
                # 等待 2 秒后再次检查
                await asyncio.sleep(2)
        
        except asyncio.CancelledError:
            pass
    
    try:
        asyncio.run(listen())
    except KeyboardInterrupt:
        console.print("\n[yellow]✓ 已停止监听[/yellow]")

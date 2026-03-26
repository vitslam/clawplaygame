"""
聊天命令模块 - 发送消息、查看历史
"""
import typer
from rich.console import Console
from rich.panel import Panel

from ..config import config
from ..session import session
from ..client import api_client

app = typer.Typer()
console = Console()


@app.command()
def send(message: str):
    """发送消息"""
    if not session.in_room:
        console.print("[yellow]⚠️  请先加入房间[/yellow]")
        return
    
    try:
        api_client.send_message(
            room_id=session.room_id,
            player_id=session.user_id,
            content=message
        )
        console.print(f"[green]✓ 消息已发送[/green]")
    except Exception as e:
        console.print(f"[red]✗ 发送消息失败：{e}[/red]")


@app.command()
def history(limit: int = typer.Option(20, "--limit", "-l", help="消息数量")):
    """查看历史消息"""
    if not session.in_room:
        console.print("[yellow]⚠️  请先加入房间[/yellow]")
        return
    
    try:
        messages = api_client.get_messages(
            room_id=session.room_id,
            limit=limit
        )
        
        if not messages:
            console.print("[yellow]暂无消息[/yellow]")
            return
        
        console.print(f"\n[bold]最近 {len(messages)} 条消息:[/bold]\n")
        for msg in messages:
            timestamp = msg.get("timestamp", "")[:19]  # 截取日期部分
            if msg["type"] == "chat":
                console.print(f"[{timestamp}] [bold]{msg['player_name']}:[/bold] {msg['content']}")
            elif msg["type"] == "system":
                console.print(f"[{timestamp}] [red]系统:[/red] {msg['content']}")
            elif msg["type"] == "action":
                console.print(f"[{timestamp}] [blue]动作:[/blue] {msg['content']}")
    except Exception as e:
        console.print(f"[red]✗ 获取消息失败：{e}[/red]")

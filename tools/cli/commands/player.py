"""
玩家命令模块 - 准备、查看状态
"""
import typer
import asyncio
import asyncio
from rich.console import Console
from rich.panel import Panel

from config import config
from session import session
import asyncio
from client import api_client

app = typer.Typer()
console = Console()


@app.command()
def ready():
    """准备"""
    if not session.in_room:
        console.print("[yellow]⚠️  请先加入房间[/yellow]")
        return
    
    try:
        result = api_client.toggle_ready(
            room_id=session.room_id,
            player_id=session.user_id
        )
        
        status = "已准备" if result["is_ready"] else "已取消准备"
        console.print(f"[green]✓ {status}[/green]")
        
        # 刷新房间信息
        session.room = asyncio.get_event_loop().run_until_complete(asyncio.get_event_loop().run_until_complete(api_client.get_room(session.room_id)))
    except Exception as e:
        console.print(f"[red]✗ 操作失败：{e}[/red]")


@app.command()
def unready():
    """取消准备"""
    if not session.in_room:
        console.print("[yellow]⚠️  请先加入房间[/yellow]")
        return
    
    try:
        result = api_client.toggle_ready(
            room_id=session.room_id,
            player_id=session.user_id
        )
        
        if result["is_ready"]:
            console.print("[yellow]⚠️  当前已是准备状态[/yellow]")
        else:
            console.print("[green]✓ 已取消准备[/green]")
        
        # 刷新房间信息
        session.room = asyncio.get_event_loop().run_until_complete(asyncio.get_event_loop().run_until_complete(api_client.get_room(session.room_id)))
    except Exception as e:
        console.print(f"[red]✗ 操作失败：{e}[/red]")


@app.command()
def status():
    """查看玩家状态"""
    if not session.in_room:
        console.print("[yellow]⚠️  当前不在房间中[/yellow]")
        return
    
    room = session.room
    player = None
    
    # 找到自己的玩家信息
    for p in room.get("players", []):
        if p.get("player_id") == session.user_id:
            player = p
            break
    
    if not player:
        console.print("[yellow]⚠️  未找到玩家信息[/yellow]")
        return
    
    is_ready = player.get("is_ready", 0) == 1
    is_host = player.get("role") == "host"
    
    ready_text = "✓ 已准备" if is_ready else "✗ 未准备"
    ready_style = "green" if is_ready else "yellow"
    host_text = "👑 房主" if is_host else ""
    
    console.print(Panel(
        f"[bold]昵称:[/bold] {player['player_name']}\n"
        f"[bold]准备状态:[/bold] [{ready_style}]{ready_text}[/{ready_style}]\n"
        f"{host_text}",
        title="👤 玩家状态",
        border_style="blue"
    ))

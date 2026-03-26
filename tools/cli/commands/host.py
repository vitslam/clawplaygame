"""
房主命令模块 - 踢人、移交、解散、开始游戏
"""
import typer
import asyncio
from rich.console import Console
from rich.panel import Panel

from config import config
from session import session
from client import api_client

app = typer.Typer()
console = Console()


@app.command()
def kick(player_id: str):
    """踢出玩家"""
    if not session.in_room:
        console.print("[yellow]⚠️  当前不在房间中[/yellow]")
        return
    
    if not session.is_host():
        console.print("[red]✗ 只有房主有此权限[/red]")
        return
    
    try:
        asyncio.get_event_loop().run_until_complete(api_client.kick_player(
            room_id=session.room_id,
            player_id=player_id,
            host_id=session.user_id
        ))
        console.print(f"[green]✓ 玩家已踢出[/green]")
        
        # 刷新房间信息
        session.room = asyncio.get_event_loop().run_until_complete(api_client.get_room(session.room_id))
    except Exception as e:
        console.print(f"[red]✗ 踢出失败：{e}[/red]")


@app.command()
def transfer(player_id: str):
    """移交房主"""
    if not session.in_room:
        console.print("[yellow]⚠️  当前不在房间中[/yellow]")
        return
    
    if not session.is_host():
        console.print("[red]✗ 只有房主有此权限[/red]")
        return
    
    try:
        asyncio.get_event_loop().run_until_complete(api_client.transfer_host(
            room_id=session.room_id,
            new_host_id=player_id,
            host_id=session.user_id
        ))
        console.print(f"[green]✓ 房主已移交给玩家 {player_id}[/green]")
        
        # 刷新房间信息
        session.room = asyncio.get_event_loop().run_until_complete(api_client.get_room(session.room_id))
    except Exception as e:
        console.print(f"[red]✗ 移交失败：{e}[/red]")


@app.command()
def start():
    """开始游戏"""
    if not session.in_room:
        console.print("[yellow]⚠️  当前不在房间中[/yellow]")
        return
    
    if not session.is_host():
        console.print("[red]✗ 只有房主有此权限[/red]")
        return
    
    try:
        asyncio.get_event_loop().run_until_complete(api_client.start_game(session.room_id))
        console.print("[green]✓ 游戏已开始[/green]")
        
        # 刷新房间信息
        session.room = asyncio.get_event_loop().run_until_complete(api_client.get_room(session.room_id))
    except Exception as e:
        console.print(f"[red]✗ 开始游戏失败：{e}[/red]")


@app.command()
def dismiss():
    """解散房间"""
    if not session.in_room:
        console.print("[yellow]⚠️  当前不在房间中[/yellow]")
        return
    
    if not session.is_host():
        console.print("[red]✗ 只有房主有此权限[/red]")
        return
    
    console.print("[yellow]⚠️  确定要解散房间吗？此操作不可恢复！[/yellow]")
    console.print("房间名称：" + session.room.get("room_name", "未知"))
    
    confirm = typer.confirm("是否继续？")
    if not confirm:
        console.print("[yellow]已取消[/yellow]")
        return
    
    try:
        asyncio.get_event_loop().run_until_complete(api_client.delete_room(
            room_id=session.room_id,
            host_id=session.user_id
        ))
        console.print("[green]✓ 房间已解散[/green]")
        session.room = None
    except Exception as e:
        console.print(f"[red]✗ 解散失败：{e}[/red]")


@app.command("set-name")
def set_room_name(name: str):
    """修改房间名称"""
    if not session.in_room:
        console.print("[yellow]⚠️  当前不在房间中[/yellow]")
        return
    
    if not session.is_host():
        console.print("[red]✗ 只有房主有此权限[/red]")
        return
    
    try:
        asyncio.get_event_loop().run_until_complete(api_client.update_room(
            room_id=session.room_id,
            host_id=session.user_id,
            room_name=name
        ))
        console.print(f"[green]✓ 房间名称已修改为：{name}[/green]")
        
        # 刷新房间信息
        session.room = asyncio.get_event_loop().run_until_complete(api_client.get_room(session.room_id))
    except Exception as e:
        console.print(f"[red]✗ 修改失败：{e}[/red]")


@app.command("set-public")
def set_room_public(is_public: bool):
    """设置房间公开状态"""
    if not session.in_room:
        console.print("[yellow]⚠️  当前不在房间中[/yellow]")
        return
    
    if not session.is_host():
        console.print("[red]✗ 只有房主有此权限[/red]")
        return
    
    try:
        asyncio.get_event_loop().run_until_complete(api_client.update_room(
            room_id=session.room_id,
            host_id=session.user_id,
            is_public=is_public
        ))
        status = "公开" if is_public else "私有"
        console.print(f"[green]✓ 房间已设置为{status}[/green]")
        
        # 刷新房间信息
        session.room = asyncio.get_event_loop().run_until_complete(api_client.get_room(session.room_id))
    except Exception as e:
        console.print(f"[red]✗ 设置失败：{e}[/red]")

"""
认证命令模块 - 注册、登录、登出
"""
import typer
import asyncio
import getpass
from rich.console import Console
from rich.panel import Panel

from config import config
from session import session
from client import api_client

app = typer.Typer()
console = Console()


@app.command()
def register(username: str = typer.Argument(..., help="用户名"), nickname: str = typer.Argument(..., help="昵称")):
    """注册新用户"""
    console.print("[bold]注册新用户[/bold]\n")
    
    # 输入密码
    password = getpass.getpass("请输入密码：")
    password_confirm = getpass.getpass("请确认密码：")
    
    if password != password_confirm:
        console.print("[red]✗ 两次输入的密码不一致[/red]")
        return
    
    if len(password) < 6:
        console.print("[red]✗ 密码长度至少为 6 位[/red]")
        return
    
    try:
        # 调用注册 API
        result = asyncio.get_event_loop().run_until_complete(api_client.register(username, password, nickname))
        
        # 保存登录状态
        session.user = result["user"]
        
        console.print(Panel(
            f"[bold]用户名:[/bold] {username}\n"
            f"[bold]昵称:[/bold] {nickname}\n"
            f"[bold]用户 ID:[/bold] {result['user']['id']}",
            title="✅ 注册成功",
            border_style="green"
        ))
    except Exception as e:
        error_msg = str(e)
        if "400" in error_msg:
            console.print("[red]✗ 用户名已存在[/red]")
        else:
            console.print(f"[red]✗ 注册失败：{error_msg}[/red]")


@app.command()
def login(username: str = typer.Argument(..., help="用户名"), password: str = typer.Argument(None, help="密码")):
    """登录"""
    console.print("[bold]用户登录[/bold]\n")
    
    # 如果未提供密码，则提示输入
    if not password:
        password = getpass.getpass("请输入密码：")
    
    try:
        # 调用登录 API
        result = asyncio.get_event_loop().run_until_complete(api_client.login(username, password))
        
        # 保存登录状态
        session.user = result["user"]
        
        console.print(Panel(
            f"[bold]欢迎回来，{result['user']['nickname']}![/bold]\n"
            f"[bold]用户 ID:[/bold] {result['user']['id']}\n"
            f"[bold]API:[/bold] {config.api_url}",
            title="✅ 登录成功",
            border_style="green"
        ))
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "404" in error_msg:
            console.print("[red]✗ 用户名或密码错误[/red]")
        else:
            console.print(f"[red]✗ 登录失败：{error_msg}[/red]")


@app.command("guest")
def guest_login():
    """以游客身份登录"""
    console.print("[bold]游客登录[/bold]\n")
    
    # 生成游客 ID
    import uuid
    guest_id = f"guest_{uuid.uuid4().hex[:8]}"
    guest_name = f"游客_{uuid.uuid4().hex[:4]}"
    
    # 保存游客会话
    session.user = {
        "id": guest_id,
        "nickname": guest_name,
        "is_guest": True
    }
    
    console.print(Panel(
        f"[bold]游客 ID:[/bold] {guest_id}\n"
        f"[bold]昵称:[/bold] {guest_name}\n"
        f"[yellow]⚠️  游客模式功能受限，建议注册账号[/yellow]",
        title="✅ 游客登录成功",
        border_style="yellow"
    ))


@app.command()
def logout():
    """登出"""
    if not session.is_logged_in:
        console.print("[yellow]⚠️  当前未登录[/yellow]")
        return
    
    user_name = session.user_name
    session.clear()
    
    console.print(Panel(
        f"[bold]{user_name}[/bold]，再见！\n"
        "使用 [bold]clawplaygame auth guest[/bold] 快速登录",
        title="✅ 已登出",
        border_style="blue"
    ))


@app.command()
def status():
    """查看登录状态"""
    if session.is_logged_in:
        is_guest = session.user.get("is_guest", False)
        mode = "[yellow]游客模式[/yellow]" if is_guest else "[green]正式用户[/green]"
        
        console.print(Panel(
            f"[bold]用户:[/bold] {session.user_name}\n"
            f"[bold]ID:[/bold] {session.user_id}\n"
            f"[bold]模式:[/bold] {mode}\n"
            f"[bold]API:[/bold] {config.api_url}\n"
            f"[bold]房间:[/bold] {'在房间中' if session.in_room else '不在房间'}",
            title="👤 已登录",
            border_style="green"
        ))
    else:
        console.print(Panel(
            "[yellow]未登录[/yellow]\n\n"
            "可用命令：\n"
            "  [bold]clawplaygame auth register[/bold] <用户名> <昵称> - 注册\n"
            "  [bold]clawplaygame auth login[/bold] <用户名> - 登录\n"
            "  [bold]clawplaygame auth guest[/bold] - 游客登录",
            title="⚠️  未登录",
            border_style="yellow"
        ))


@app.command()
def change_password(old_password: str = typer.Argument(..., help="旧密码"), 
                    new_password: str = typer.Argument(..., help="新密码")):
    """修改密码（开发中）"""
    if not session.is_logged_in:
        console.print("[red]✗ 请先登录[/red]")
        return
    
    console.print("[yellow]⚠️  修改密码功能开发中...[/yellow]")


@app.command()
def info():
    """查看用户信息"""
    if not session.is_logged_in:
        console.print("[red]✗ 请先登录[/red]")
        return
    
    user = session.user
    console.print(Panel(
        f"[bold]用户 ID:[/bold] {user.get('id')}\n"
        f"[bold]用户名:[/bold] {user.get('username', 'N/A')}\n"
        f"[bold]昵称:[/bold] {user.get('nickname')}\n"
        f"[bold]注册时间:[/bold] {user.get('created_at', 'N/A')}\n"
        f"[bold]最后活跃:[/bold] {user.get('last_seen', 'N/A')}",
        title="👤 用户信息",
        border_style="blue"
    ))

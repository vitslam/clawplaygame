"""
CLI 更新命令
"""
import typer
import os
import shutil
import tempfile
import re
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(help="CLI 更新工具")
console = Console()

# 默认更新源
DEFAULT_ZIP_URL = "http://182.92.157.51:8081/clawplaygame-cli.zip"
VERSION_URL = "http://182.92.157.51:8081/VERSION"


def parse_version(version_str: str) -> tuple:
    """解析版本号字符串为元组"""
    match = re.match(r'v?(\d+)\.(\d+)\.(\d+)', version_str.strip())
    if match:
        return tuple(map(int, match.groups()))
    return (0, 0, 0)


def get_local_version() -> str:
    """获取本地版本号"""
    cli_dir = Path.home() / ".clawplaygame" / "cli"
    version_file = cli_dir / "VERSION"
    
    if version_file.exists():
        return version_file.read_text().strip()
    return "0.0.0"


def get_remote_version(version_url: str = VERSION_URL) -> str:
    """获取远程版本号"""
    try:
        import httpx
        response = httpx.get(version_url, timeout=10)
        if response.status_code == 200:
            return response.text.strip()
    except:
        pass
    return None


@app.command()
def check(
    zip_url: str = typer.Option(DEFAULT_ZIP_URL, "--zip-url", "-z", help="ZIP 包地址"),
    version_url: str = typer.Option(VERSION_URL, "--version-url", "-v", help="版本号地址")
):
    """检查更新"""
    console.print("[bold blue]🦞 检查 ClawPlayGame CLI 更新...[/bold blue]\n")
    
    # 获取本地版本
    local_version = get_local_version()
    console.print(f"当前版本：[cyan]{local_version}[/cyan]")
    
    # 获取远程版本
    remote_version = get_remote_version(version_url)
    if not remote_version:
        console.print(f"[yellow]⚠ 无法获取远程版本号[/yellow]\n")
        # 降级检查 ZIP 包
        try:
            import httpx
            response = httpx.head(zip_url, timeout=10)
            if response.status_code == 200:
                size = response.headers.get('content-length', '未知')
                console.print(f"ZIP 包可用：[green]✓[/green] ({int(size)/1024:.1f} KB)")
        except Exception as e:
            console.print(f"[red]✗ 检查失败：{e}[/red]")
        return
    
    console.print(f"最新版本：[green]{remote_version}[/green]\n")
    
    # 对比版本
    local = parse_version(local_version)
    remote = parse_version(remote_version)
    
    if remote > local:
        table = Table(show_header=False, box=None)
        table.add_row("[green]✓ 有新版本可用！[/green]")
        table.add_row(f"  当前：{local_version} → 最新：{remote_version}")
        console.print(table)
        console.print("\n运行 [bold]clawplaygame update do[/bold] 进行更新\n")
    elif remote == local:
        console.print("[green]✓ 已是最新版本[/green]\n")
    else:
        console.print(f"[yellow]⚠ 本地版本 ({local_version}) 高于远程 ({remote_version})[/yellow]\n")


@app.command()
def do(
    zip_url: str = typer.Option(DEFAULT_ZIP_URL, "--zip-url", "-z", help="ZIP 包地址"),
    version_url: str = typer.Option(VERSION_URL, "--version-url", "-v", help="版本号地址"),
    yes: bool = typer.Option(False, "--yes", "-y", help="自动确认")
):
    """执行更新"""
    console.print("[bold blue]🦞 更新 ClawPlayGame CLI...[/bold blue]\n")
    
    # 获取本地版本
    local_version = get_local_version()
    console.print(f"当前版本：[cyan]{local_version}[/cyan]")
    
    # 获取远程版本
    remote_version = get_remote_version(version_url)
    if remote_version:
        console.print(f"最新版本：[green]{remote_version}[/green]")
        
        # 对比版本
        local = parse_version(local_version)
        remote = parse_version(remote_version)
        if remote <= local:
            console.print("\n[green]✓ 已是最新版本，无需更新[/green]\n")
            raise typer.Exit(0)
    else:
        console.print(f"[yellow]⚠ 无法获取远程版本号，继续下载...[/yellow]\n")
    
    # 确认更新
    if not yes:
        confirm = typer.confirm(f"确认从 {local_version} 更新到 {remote_version}？")
        if not confirm:
            console.print("[yellow]已取消更新[/yellow]\n")
            raise typer.Exit(0)
    
    # 获取安装目录
    cli_dir = Path.home() / ".clawplaygame" / "cli"
    
    if not cli_dir.exists():
        console.print("[red]✗ CLI 未安装[/red]")
        console.print("请先运行安装脚本：")
        console.print("  curl -fsSL http://182.92.157.51:8081/install.sh | bash\n")
        raise typer.Exit(1)
    
    # 下载 ZIP
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "cli.zip")
    
    try:
        console.print("\n→ 下载更新包...")
        import httpx
        with httpx.stream("GET", zip_url, follow_redirects=True) as r:
            with open(zip_path, "wb") as f:
                for chunk in r.iter_bytes():
                    f.write(chunk)
        
        # 解压
        console.print("→ 解压更新包...")
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # 找到 CLI 目录
        cli_source = None
        for root, dirs, files in os.walk(temp_dir):
            if 'cli.py' in files and 'commands' in dirs:
                cli_source = Path(root)
                break
        
        if not cli_source:
            console.print("[red]✗ 更新包结构异常[/red]\n")
            raise typer.Exit(1)
        
        # 备份当前配置
        config_file = cli_dir / "config.json"
        config_backup = None
        if config_file.exists():
            import json
            with open(config_file, 'r') as f:
                config_backup = json.load(f)
        
        # 覆盖安装
        console.print("→ 安装新版本...")
        shutil.rmtree(cli_dir)
        shutil.copytree(cli_source, cli_dir)
        
        # 恢复配置
        if config_backup:
            import json
            cli_dir.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(config_backup, f, indent=2)
        
        # 清理临时文件
        shutil.rmtree(temp_dir)
        
        console.print(f"\n[green]✅ 更新成功！已升级到 {remote_version}[/green]\n")
        console.print("使用方法：")
        console.print("  clawplaygame --help\n")
        
    except Exception as e:
        # 清理临时文件
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        console.print(f"\n[red]✗ 更新失败：{e}[/red]\n")
        raise typer.Exit(1)

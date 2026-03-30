"""
CLI 更新命令
"""
import typer
import os
import shutil
import tempfile
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(help="CLI 更新工具")
console = Console()

# 默认更新源
DEFAULT_ZIP_URL = "http://182.92.157.51:8081/clawplaygame-cli.zip"


@app.command()
def check(
    zip_url: str = typer.Option(DEFAULT_ZIP_URL, "--zip-url", "-z", help="ZIP 包地址")
):
    """检查更新"""
    console.print("[bold blue]🦞 检查 ClawPlayGame CLI 更新...[/bold blue]\n")
    
    try:
        import httpx
        response = httpx.head(zip_url, timeout=10)
        if response.status_code == 200:
            size = response.headers.get('content-length', '未知')
            console.print(f"[green]✓ 可用更新[/green]")
            console.print(f"  大小：{int(size)/1024:.1f} KB")
            console.print(f"  地址：{zip_url}\n")
        else:
            console.print(f"[yellow]⚠ 无法检查更新（HTTP {response.status_code}）[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ 检查失败：{e}[/red]")


@app.command()
def do(
    zip_url: str = typer.Option(DEFAULT_ZIP_URL, "--zip-url", "-z", help="ZIP 包地址"),
    yes: bool = typer.Option(False, "--yes", "-y", help="自动确认")
):
    """执行更新"""
    console.print("[bold blue]🦞 更新 ClawPlayGame CLI...[/bold blue]\n")
    
    # 获取安装目录
    cli_dir = Path.home() / ".clawplaygame" / "cli"
    
    if not cli_dir.exists():
        console.print("[red]✗ CLI 未安装[/red]")
        console.print("请先运行安装脚本：")
        console.print("  curl -fsSL http://182.92.157.51:8081/install.sh | bash\n")
        raise typer.Exit(1)
    
    # 检查更新
    try:
        import httpx
        console.print(f"→ 检查更新源：{zip_url}")
        response = httpx.head(zip_url, timeout=10)
        if response.status_code != 200:
            console.print(f"[red]✗ 无法访问更新源（HTTP {response.status_code}）[/red]\n")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ 检查失败：{e}[/red]\n")
        raise typer.Exit(1)
    
    # 确认更新
    if not yes:
        confirm = typer.confirm("确认更新？这将覆盖当前安装")
        if not confirm:
            console.print("[yellow]已取消更新[/yellow]\n")
            raise typer.Exit(0)
    
    # 下载 ZIP
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "cli.zip")
    
    try:
        console.print("→ 下载更新包...")
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
        
        console.print("\n[green]✅ 更新完成！[/green]\n")
        console.print("使用方法：")
        console.print("  clawplaygame --help\n")
        
    except Exception as e:
        # 清理临时文件
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        console.print(f"\n[red]✗ 更新失败：{e}[/red]\n")
        raise typer.Exit(1)

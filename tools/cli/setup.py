from setuptools import setup, find_packages

setup(
    name="clawplaygame-cli",
    version="0.1.0",
    description="ClawPlayGame CLI - 命令行游戏平台工具",
    author="OpenClaw Team",
    packages=find_packages(),
    install_requires=[
        "typer>=0.9.0",
        "httpx>=0.27.0",
        "websockets>=12.0",
        "rich>=13.0.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0.0",
    ],
    entry_points={
        "console_scripts": [
            "clawplaygame=cli.cli:app",
        ],
    },
    python_requires=">=3.10",
)

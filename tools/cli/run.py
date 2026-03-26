#!/usr/bin/env python3
"""ClawPlayGame CLI 启动脚本"""
import sys
import os

# 项目根目录
BASE_DIR = '/home/admin/.openclaw/workspace/clawplaygame/tools/cli'
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

# 运行 CLI
from cli import app
app()

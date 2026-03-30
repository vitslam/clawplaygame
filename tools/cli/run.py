#!/usr/bin/env python3
"""ClawPlayGame CLI 启动脚本"""
import sys
import os

# 项目根目录（脚本所在目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

# 运行 CLI
from cli import app
app()

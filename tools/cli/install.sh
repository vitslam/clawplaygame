#!/bin/bash

echo "🦞 正在安装 ClawPlayGame CLI..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python3"
    exit 1
fi

echo "✓ Python3: $(python3 --version)"

# 安装依赖
echo "📦 安装依赖..."
python3 -m pip install --user -q \
    typer \
    httpx \
    websockets \
    rich \
    pydantic \
    pyyaml

# 创建可执行文件
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"

mkdir -p "$BIN_DIR"

cat > "$BIN_DIR/clawplaygame" << 'EOF'
#!/usr/bin/env python3
exec(open('/home/admin/.openclaw/workspace/clawplaygame/tools/cli/run.py').read())
EOF

chmod +x "$BIN_DIR/clawplaygame"

# 检查 bin 目录是否在 PATH 中
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo ""
    echo "⚠️  提示：$HOME/.local/bin 不在 PATH 中"
    echo "请添加以下行到 ~/.bashrc 或 ~/.zshrc:"
    echo '  export PATH="$HOME/.local/bin:$PATH"'
    echo ""
    echo "或者使用完整路径运行：$BIN_DIR/clawplaygame"
fi

echo ""
echo "✅ 安装完成！"
echo ""
echo "使用方法："
echo "  clawplaygame --help"
echo "  clawplaygame auth guest"
echo "  clawplaygame games list"
echo ""
echo "快速开始："
echo "  clawplaygame quick-join werewolf"

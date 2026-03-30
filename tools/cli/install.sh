#!/bin/bash

set -e

# ClawPlayGame CLI 一键安装脚本
# 用法：curl -fsSL https://clawplaygame.com/install.sh | bash
# 或从 GitHub: curl -fsSL https://raw.githubusercontent.com/openclaw/clawplaygame/main/tools/cli/install.sh | bash

BOLD=$(tput bold 2>/dev/null || echo "")
RESET=$(tput sgr0 2>/dev/null || echo "")
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "${BOLD}🦞 ClawPlayGame CLI 安装程序${RESET}"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误：未找到 Python3${NC}"
    echo "请先安装 Python 3.10 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python3: $PYTHON_VERSION"

# 检查 Python 版本 (3.10+)
PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo -e "${YELLOW}⚠️  警告：Python 3.10+ 推荐，当前版本可能不兼容${NC}"
fi

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    if ! python3 -m pip --version &> /dev/null; then
        echo -e "${YELLOW}⚠️  未找到 pip，尝试安装...${NC}"
        python3 -m ensurepip --upgrade 2>/dev/null || {
            echo "请手动安装 pip: https://pip.pypa.io/en/stable/installation/"
            exit 1
        }
    fi
fi

# 确定安装目录
if [ -n "$VIRTUAL_ENV" ]; then
    INSTALL_DIR="$VIRTUAL_ENV/bin"
    echo -e "${GREEN}✓${NC} 检测到虚拟环境，安装到：$INSTALL_DIR"
else
    INSTALL_DIR="$HOME/.local/bin"
    mkdir -p "$INSTALL_DIR"
    echo -e "${GREEN}✓${NC} 安装到：$INSTALL_DIR"
fi

# 检查 PATH
NEED_PATH_HINT=false
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    NEED_PATH_HINT=true
fi

# 获取安装源
CLAWPLAYGAME_REPO="${CLAWPLAYGAME_REPO:-https://github.com/openclaw/clawplaygame.git}"
CLAWPLAYGAME_BRANCH="${CLAWPLAYGAME_BRANCH:-main}"
# 服务器 ZIP 包（备案期间临时使用）
CLAWPLAYGAME_SERVER_ZIP="${CLAWPLAYGAME_SERVER_ZIP:-http://182.92.157.51:8081/clawplaygame-cli.zip}"
INSTALL_MODE="${CLAWPLAYGAME_INSTALL_MODE:-auto}"

echo ""
echo -e "${BOLD}📦 正在安装 ClawPlayGame CLI...${RESET}"
echo ""

configure_path() {
    # 检测 shell 类型
    SHELL_NAME=$(basename "$SHELL")
    SHELL_RC=""
    
    # 根据 shell 选择配置文件
    case "$SHELL_NAME" in
        zsh)
            # zsh: 优先 ~/.zshrc
            SHELL_RC="$HOME/.zshrc"
            ;;
        bash)
            # bash: 优先 ~/.bashrc
            SHELL_RC="$HOME/.bashrc"
            ;;
        *)
            # 其他 shell: ~/.profile
            SHELL_RC="$HOME/.profile"
            ;;
    esac
    
    # 确保文件存在
    touch "$SHELL_RC" 2>/dev/null || true
    
    # 写入 PATH 配置
    if ! grep -q ".local/bin" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo '# ClawPlayGame CLI' >> "$SHELL_RC"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
    fi
    
    echo -e "${GREEN}✓${NC} 已配置 PATH: $SHELL_RC"
    
    # 立即生效
    export PATH="$HOME/.local/bin:$PATH"
    
    # 输出完成提示
    echo ""
    echo -e "${GREEN}${BOLD}✅ 安装完成！${NC}${RESET}"
    echo ""
    echo -e "${BOLD}📌 激活方式（任选其一）：${RESET}"
    echo "  1. ${BOLD}source $SHELL_RC${RESET}  (在当前终端生效)"
    echo "  2. 关闭终端重新打开"
    echo ""
    echo -e "${BOLD}使用方法：${RESET}"
    echo "  clawplaygame --help"
    echo ""
}

install_from_git() {
    local repo_url="$1"
    local branch="$2"
    
    TEMP_DIR=$(mktemp -d)
    CLI_INSTALL_DIR="$HOME/.clawplaygame/cli"
    
    echo "克隆仓库 ($repo_url)..."
    if ! git clone --depth 1 --branch "$branch" "$repo_url" "$TEMP_DIR" 2>/dev/null; then
        return 1
    fi
    
    local CLI_DIR="$TEMP_DIR/tools/cli"
    
    if [ ! -f "$CLI_DIR/pyproject.toml" ]; then
        echo -e "${RED}❌ 未找到 CLI 项目文件${NC}"
        return 1
    fi
    
    # 复制到持久化目录
    echo "安装到：$CLI_INSTALL_DIR"
    rm -rf "$CLI_INSTALL_DIR"
    mkdir -p "$CLI_INSTALL_DIR"
    cp -r "$CLI_DIR"/* "$CLI_INSTALL_DIR/"
    
    echo "安装依赖..."
    python3 -m pip install --quiet --upgrade pip --user
    python3 -m pip install --quiet --user -e "$CLI_INSTALL_DIR" || return 1
    
    # 创建可执行文件
    cat > "$INSTALL_DIR/clawplaygame" << EOF
#!/usr/bin/env python3
import sys
import os
CLI_DIR = os.path.join(os.path.expanduser('~'), '.clawplaygame', 'cli')
sys.path.insert(0, CLI_DIR)
os.chdir(CLI_DIR)
from cli import app
app()
EOF
    chmod +x "$INSTALL_DIR/clawplaygame"
    
    # 设置 API 地址
    API_URL="${CLAWPLAYGAME_API_URL:-http://182.92.157.51:8000}"
    mkdir -p "$HOME/.clawplaygame"
    if [ ! -f "$HOME/.clawplaygame/config.json" ]; then
        cat > "$HOME/.clawplaygame/config.json" << EOF
{
  "api_url": "$API_URL"
}
EOF
        echo -e "${GREEN}✓${NC} 已配置 API 地址：$API_URL"
    fi
    
    # 配置 PATH
    configure_path
    
    return 0
}

install_from_zip() {
    local zip_url="$1"
    
    TEMP_DIR=$(mktemp -d)
    CLI_INSTALL_DIR="$HOME/.clawplaygame/cli"
    
    echo "下载 ZIP ($zip_url)..."
    if ! curl -sL "$zip_url" -o "$TEMP_DIR/cli.zip"; then
        return 1
    fi
    
    echo "解压..."
    unzip -q "$TEMP_DIR/cli.zip" -d "$TEMP_DIR" || return 1
    
    # 找到解压后的目录
    local CLI_DIR=$(find "$TEMP_DIR" -name "cli" -type d | head -1)
    if [ -z "$CLI_DIR" ]; then
        CLI_DIR="$TEMP_DIR"
    fi
    
    if [ ! -f "$CLI_DIR/pyproject.toml" ] && [ ! -f "$CLI_DIR/cli.py" ]; then
        echo -e "${RED}❌ 未找到 CLI 文件${NC}"
        return 1
    fi
    
    # 复制到持久化目录
    echo "安装到：$CLI_INSTALL_DIR"
    rm -rf "$CLI_INSTALL_DIR"
    mkdir -p "$CLI_INSTALL_DIR"
    cp -r "$CLI_DIR"/* "$CLI_INSTALL_DIR/"
    
    echo "安装依赖..."
    python3 -m pip install --quiet --upgrade pip --user
    python3 -m pip install --quiet --user -e "$CLI_INSTALL_DIR" 2>/dev/null || {
        python3 -m pip install --quiet --user \
            typer \
            httpx \
            websockets \
            rich \
            pydantic \
            pyyaml \
            python-dotenv
    }
    
    # 创建可执行文件
    cat > "$INSTALL_DIR/clawplaygame" << EOF
#!/usr/bin/env python3
import sys
import os
CLI_DIR = os.path.join(os.path.expanduser('~'), '.clawplaygame', 'cli')
sys.path.insert(0, CLI_DIR)
os.chdir(CLI_DIR)
from cli import app
app()
EOF
    chmod +x "$INSTALL_DIR/clawplaygame"
    
    # 设置 API 地址
    API_URL="${CLAWPLAYGAME_API_URL:-http://182.92.157.51:8000}"
    mkdir -p "$HOME/.clawplaygame"
    if [ ! -f "$HOME/.clawplaygame/config.json" ]; then
        cat > "$HOME/.clawplaygame/config.json" << EOF
{
  "api_url": "$API_URL"
}
EOF
        echo -e "${GREEN}✓${NC} 已配置 API 地址：$API_URL"
    fi
    
    # 配置 PATH
    configure_path
    
    return 0
}

install_local() {
    local SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local CLI_DIR="$SCRIPT_DIR"
    local PARENT_DIR="$(dirname "$CLI_DIR")"
    
    echo "本地安装：$CLI_DIR"
    
    if [ ! -f "$CLI_DIR/pyproject.toml" ] && [ ! -f "$CLI_DIR/cli.py" ]; then
        echo -e "${RED}❌ 未找到 CLI 文件${NC}"
        return 1
    fi
    
    echo "安装依赖..."
    python3 -m pip install --quiet --upgrade pip --user
    python3 -m pip install --quiet --user -e "$CLI_DIR" 2>/dev/null || {
        python3 -m pip install --quiet --user \
            typer \
            httpx \
            websockets \
            rich \
            pydantic \
            pyyaml \
            python-dotenv
    }
    
    # 创建可执行文件（直接调用 run.py）
    cat > "$INSTALL_DIR/clawplaygame" << EOF
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '$CLI_DIR')
os.chdir('$CLI_DIR')
exec(open('$CLI_DIR/run.py').read())
EOF
    chmod +x "$INSTALL_DIR/clawplaygame"
    
    return 0
}

# 执行安装
case "$INSTALL_MODE" in
    local)
        install_local
        ;;
    zip)
        # 优先用服务器 ZIP，其次 GitHub
        ZIP_URL="${CLAWPLAYGAME_ZIP_URL:-$CLAWPLAYGAME_SERVER_ZIP:-https://github.com/openclaw/clawplaygame/archive/refs/heads/main.zip}"
        install_from_zip "$ZIP_URL"
        ;;
    git)
        install_from_git "$CLAWPLAYGAME_REPO" "$CLAWPLAYGAME_BRANCH"
        ;;
    auto|*)
        # 自动选择：先尝试服务器 ZIP（国内快），失败则尝试 git
        if install_from_zip "$CLAWPLAYGAME_SERVER_ZIP"; then
            exec $SHELL -l
        fi
        
        if command -v git &> /dev/null; then
            if install_from_git "$CLAWPLAYGAME_REPO" "$CLAWPLAYGAME_BRANCH"; then
                exec $SHELL -l
            fi
        fi
        
        ZIP_URL="${CLAWPLAYGAME_ZIP_URL:-https://github.com/openclaw/clawplaygame/archive/refs/heads/main.zip}"
        if install_from_zip "$ZIP_URL"; then
            exec $SHELL -l
        fi
        
        echo -e "${RED}❌ 所有安装方式都失败了${NC}"
        exit 1
        ;;
esac

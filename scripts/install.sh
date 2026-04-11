#!/usr/bin/env bash
# Daily Watchlist Install Script (Unix/macOS/Linux)
# Usage: bash scripts/install.sh --target-dir ./daily-watchlist [--force]

set -euo pipefail

TARGET_DIR="./daily-watchlist"
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --target-dir) TARGET_DIR="$2"; shift 2 ;;
        --force) FORCE=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

copy_if_needed() {
    local source="$1"
    local destination="$2"
    if [[ ! -e "$destination" || "$FORCE" == true ]]; then
        cp "$source" "$destination"
    fi
}

echo "=== Daily Watchlist 安装器 ==="
echo "目标目录: $TARGET_DIR"

# --- 检查 Python ---
PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo ""
    echo "❌ 未找到 Python。请先安装 Python >= 3.10："
    echo "   https://www.python.org/downloads/"
    echo ""
    echo "安装完成后重新运行本脚本。"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_OK=$($PYTHON_CMD -c "import sys; print(1 if sys.version_info >= (3, 10) else 0)")
if [[ "$PYTHON_OK" != "1" ]]; then
    echo ""
    echo "❌ Python 版本太低（当前: $PYTHON_VERSION，需要: >= 3.10）"
    echo "   https://www.python.org/downloads/"
    exit 1
fi
echo "✅ Python $PYTHON_VERSION"

# --- 检查目标目录 ---
if [[ -e "$TARGET_DIR" && ! -d "$TARGET_DIR" ]]; then
    echo "❌ $TARGET_DIR 已存在且不是目录。"
    exit 1
fi

if [[ -d "$TARGET_DIR" ]]; then
    echo "目标目录已存在，将安装到现有工作区。"
fi

# --- 创建目录结构 ---
mkdir -p \
    "$TARGET_DIR/config" \
    "$TARGET_DIR/scripts" \
    "$TARGET_DIR/templates" \
    "$TARGET_DIR/daily-watchlist-reports" \
    "$TARGET_DIR/.claude/skills"

# --- 拷贝脚本文件 ---
cp "$REPO_DIR/scripts/generate_daily_report.py" "$TARGET_DIR/scripts/"
cp "$REPO_DIR/scripts/fetch_market_data.py" "$TARGET_DIR/scripts/"
cp "$REPO_DIR/scripts/fetch_macro_data.py" "$TARGET_DIR/scripts/"
cp "$REPO_DIR/scripts/check_setup.py" "$TARGET_DIR/scripts/"
cp "$REPO_DIR/scripts/workspace_paths.py" "$TARGET_DIR/scripts/"
cp "$REPO_DIR/templates/daily-watchlist-report-template.md" "$TARGET_DIR/templates/"
cp "$REPO_DIR/skills/daily-watchlist-today.md" "$TARGET_DIR/.claude/skills/"
cp "$REPO_DIR/skills/daily-watchlist-import.md" "$TARGET_DIR/.claude/skills/"

# --- 拷贝配置文件（只拷贝工作文件，不拷贝 .example 副本） ---
copy_if_needed "$REPO_DIR/config/daily-watchlist.env.example" "$TARGET_DIR/config/daily-watchlist.env"
copy_if_needed "$REPO_DIR/config/daily-watchlist.example.yaml" "$TARGET_DIR/config/daily-watchlist.yaml"
copy_if_needed "$REPO_DIR/config/daily-watchlist.watchlist.example.md" "$TARGET_DIR/config/daily-watchlist-watchlist.md"

# --- CLAUDE.md 整合（轻量入口，不拷贝完整协议副本） ---
PROTOCOL_HEADING="## Daily Watchlist Protocols"

if [[ ! -f "$TARGET_DIR/CLAUDE.md" ]]; then
    cat > "$TARGET_DIR/CLAUDE.md" <<'EOF'
# 工作区说明

## Daily Watchlist Protocols

当用户要求 Daily Watchlist 工作流（`/dw-today` 或 `/dw-import`；`/watchlist-today` 和 `/watchlist-import` 是兼容别名；只有在不冲突时才使用 `/today` 和 `/import`）时，先读取：
- `./config/daily-watchlist.yaml`
- `./templates/daily-watchlist-report-template.md`
- `./.claude/skills/daily-watchlist-today.md`

报告写入 `./daily-watchlist-reports/YYYY-MM/`。默认按保存的模板输出，并告诉用户模板可以随时自行编辑。
EOF
elif ! grep -Fq "$PROTOCOL_HEADING" "$TARGET_DIR/CLAUDE.md"; then
    cat >> "$TARGET_DIR/CLAUDE.md" <<'EOF'

## Daily Watchlist Protocols

当用户要求 Daily Watchlist 工作流（`/dw-today` 或 `/dw-import`；`/watchlist-today` 和 `/watchlist-import` 是兼容别名；只有在不冲突时才使用 `/today` 和 `/import`）时，先读取：
- `./config/daily-watchlist.yaml`
- `./templates/daily-watchlist-report-template.md`
- `./.claude/skills/daily-watchlist-today.md`

报告写入 `./daily-watchlist-reports/YYYY-MM/`。默认按保存的模板输出，并告诉用户模板可以随时自行编辑。
EOF
fi

# --- 安装 Python 依赖 ---
echo ""
echo "正在安装 Python 依赖..."
if $PYTHON_CMD -m pip install -r "$REPO_DIR/requirements.txt" --quiet; then
    echo "✅ Python 依赖安装完成"
else
    echo ""
    echo "⚠️  依赖安装失败。请手动运行："
    echo "   $PYTHON_CMD -m pip install -r requirements.txt"
    echo ""
fi

# --- 运行环境检查 ---
echo ""
echo "正在运行环境检查..."
if $PYTHON_CMD "$TARGET_DIR/scripts/check_setup.py"; then
    echo ""
    echo "✅ 安装完成！所有检查通过。"
else
    echo ""
    echo "⚠️  安装完成，但环境检查未通过。请按上面的提示修复后再使用。"
    echo ""
fi

echo ""
echo "已安装到 $TARGET_DIR"
echo ""
echo "下一步："
echo "  1. 编辑 API key：  $TARGET_DIR/config/daily-watchlist.env"
echo "  2. 检查配置：      $TARGET_DIR/config/daily-watchlist.yaml"
echo "  3. 检查监控池：    $TARGET_DIR/config/daily-watchlist-watchlist.md"
echo "  4. 编辑模板（可选）：$TARGET_DIR/templates/daily-watchlist-report-template.md"
echo "  5. 生成日报：      在 Claude Code 中运行 /dw-today"

#!/usr/bin/env bash
# Daily Watchlist Install Script (Unix/macOS/Linux)
# Usage: bash scripts/install.sh --target-dir ./daily-watchlist [--force]

set -euo pipefail

TARGET_DIR="./daily-watchlist"
FORCE=false
PROTOCOL_FILE_NAME="_daily-watchlist-protocols.md"
PROTOCOL_HEADING="## Daily Watchlist Protocols"

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

if [[ -e "$TARGET_DIR" && ! -d "$TARGET_DIR" ]]; then
    echo "错误: $TARGET_DIR 已存在且不是目录。"
    exit 1
fi

if [[ -d "$TARGET_DIR" ]]; then
    echo "目标目录已存在，将安装到现有工作区。"
fi

mkdir -p \
    "$TARGET_DIR/config" \
    "$TARGET_DIR/scripts" \
    "$TARGET_DIR/templates" \
    "$TARGET_DIR/daily-watchlist-reports" \
    "$TARGET_DIR/.claude/skills"

cp "$REPO_DIR/scripts/generate_daily_report.py" "$TARGET_DIR/scripts/"
cp "$REPO_DIR/scripts/fetch_market_data.py" "$TARGET_DIR/scripts/"
cp "$REPO_DIR/scripts/fetch_macro_data.py" "$TARGET_DIR/scripts/"
cp "$REPO_DIR/scripts/check_setup.py" "$TARGET_DIR/scripts/"
cp "$REPO_DIR/scripts/workspace_paths.py" "$TARGET_DIR/scripts/"
cp "$REPO_DIR/templates/daily-watchlist-report-template.md" "$TARGET_DIR/templates/"
cp "$REPO_DIR/skills/daily-watchlist-today.md" "$TARGET_DIR/.claude/skills/"
cp "$REPO_DIR/skills/daily-watchlist-import.md" "$TARGET_DIR/.claude/skills/"

copy_if_needed "$REPO_DIR/config/daily-watchlist.env.example" "$TARGET_DIR/config/daily-watchlist.env.example"
copy_if_needed "$REPO_DIR/config/daily-watchlist.example.yaml" "$TARGET_DIR/config/daily-watchlist.example.yaml"
copy_if_needed "$REPO_DIR/config/daily-watchlist.watchlist.example.md" "$TARGET_DIR/config/daily-watchlist.watchlist.example.md"
copy_if_needed "$REPO_DIR/config/daily-watchlist.example.yaml" "$TARGET_DIR/config/daily-watchlist.yaml"
copy_if_needed "$REPO_DIR/config/daily-watchlist.watchlist.example.md" "$TARGET_DIR/config/daily-watchlist-watchlist.md"

copy_if_needed "$REPO_DIR/CLAUDE.md" "$TARGET_DIR/$PROTOCOL_FILE_NAME"

if [[ ! -f "$TARGET_DIR/CLAUDE.md" ]]; then
    cat > "$TARGET_DIR/CLAUDE.md" <<'EOF'
# 工作区说明

## Daily Watchlist Protocols

当用户要求 Daily Watchlist 工作流（`/dw-today` 或 `/dw-import`；`/watchlist-today` 和 `/watchlist-import` 是兼容别名；只有在不冲突时才使用 `/today` 和 `/import`）时，先读取：
- `./_daily-watchlist-protocols.md`
- `./config/daily-watchlist.yaml`
- `./templates/daily-watchlist-report-template.md`

报告写入 `./daily-watchlist-reports/YYYY-MM/`。默认按保存的模板输出，并告诉用户模板可以随时自行编辑。
EOF
elif ! grep -Fq "$PROTOCOL_HEADING" "$TARGET_DIR/CLAUDE.md"; then
    cat >> "$TARGET_DIR/CLAUDE.md" <<'EOF'

## Daily Watchlist Protocols

当用户要求 Daily Watchlist 工作流（`/dw-today` 或 `/dw-import`；`/watchlist-today` 和 `/watchlist-import` 是兼容别名；只有在不冲突时才使用 `/today` 和 `/import`）时，先读取：
- `./_daily-watchlist-protocols.md`
- `./config/daily-watchlist.yaml`
- `./templates/daily-watchlist-report-template.md`

报告写入 `./daily-watchlist-reports/YYYY-MM/`。默认按保存的模板输出，并告诉用户模板可以随时自行编辑。
EOF
fi

echo ""
echo "已安装到 $TARGET_DIR"
echo ""
echo "下一步："
echo "  1. 复制 env：    cp $TARGET_DIR/config/daily-watchlist.env.example $TARGET_DIR/config/daily-watchlist.env"
echo "  2. 编辑 env：    $TARGET_DIR/config/daily-watchlist.env"
echo "  3. 检查配置：    $TARGET_DIR/config/daily-watchlist.yaml"
echo "  4. 检查监控池：  $TARGET_DIR/config/daily-watchlist-watchlist.md"
echo "  5. 编辑模板：    $TARGET_DIR/templates/daily-watchlist-report-template.md（可选）"
echo "  6. 运行检查：    python $TARGET_DIR/scripts/check_setup.py"
echo "  7. 生成日报：    python $TARGET_DIR/scripts/generate_daily_report.py"
echo ""

if command -v python3 >/dev/null 2>&1; then
    echo "正在运行环境检查..."
    python3 "$TARGET_DIR/scripts/check_setup.py" || true
elif command -v python >/dev/null 2>&1; then
    echo "正在运行环境检查..."
    python "$TARGET_DIR/scripts/check_setup.py" || true
else
    echo "未找到 Python。请先安装 Python >= 3.8，然后运行: python $TARGET_DIR/scripts/check_setup.py"
fi

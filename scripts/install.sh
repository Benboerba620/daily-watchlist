#!/usr/bin/env bash
# Daily Watchlist Install Script (Unix/macOS/Linux)
# Usage: bash scripts/install.sh --target-dir ./daily-watchlist [--force]

set -euo pipefail

TARGET_DIR="./daily-watchlist"
FORCE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
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

echo "=== Daily Watchlist Installer ==="
echo "Target directory: $TARGET_DIR"

# --- Check Python ---
PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo ""
    echo "ERROR: Python not found. Please install Python >= 3.10:"
    echo "  https://www.python.org/downloads/"
    echo ""
    echo "Then re-run this installer."
    exit 1
fi

PYTHON_VERSION="$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")"
PYTHON_OK="$($PYTHON_CMD -c "import sys; print(1 if sys.version_info >= (3, 10) else 0)")"
if [[ "$PYTHON_OK" != "1" ]]; then
    echo ""
    echo "ERROR: Python version too old (current: $PYTHON_VERSION, required: >= 3.10)"
    echo "  https://www.python.org/downloads/"
    exit 1
fi
echo "OK Python $PYTHON_VERSION"

# --- Check target directory ---
if [[ -e "$TARGET_DIR" && ! -d "$TARGET_DIR" ]]; then
    echo "ERROR: $TARGET_DIR already exists and is not a directory."
    exit 1
fi

if [[ -d "$TARGET_DIR" ]]; then
    echo "Target directory already exists. Installing into existing workspace."
fi

# --- Create directory structure ---
mkdir -p \
    "$TARGET_DIR/config" \
    "$TARGET_DIR/scripts" \
    "$TARGET_DIR/templates" \
    "$TARGET_DIR/daily-watchlist-reports" \
    "$TARGET_DIR/.claude/commands" \
    "$TARGET_DIR/.claude/skills"

# --- Copy script files ---
cp "$REPO_DIR/scripts/generate_daily_report.py" "$TARGET_DIR/scripts/"
cp "$REPO_DIR/scripts/fetch_market_data.py" "$TARGET_DIR/scripts/"
cp "$REPO_DIR/scripts/fetch_macro_data.py" "$TARGET_DIR/scripts/"
cp "$REPO_DIR/scripts/check_setup.py" "$TARGET_DIR/scripts/"
cp "$REPO_DIR/scripts/workspace_paths.py" "$TARGET_DIR/scripts/"
cp "$REPO_DIR/templates/daily-watchlist-report-template.md" "$TARGET_DIR/templates/"
# Remove legacy filenames from prior installs (pre-1.0.4 rename)
rm -f "$TARGET_DIR/.claude/skills/daily-watchlist-today.md"
rm -f "$TARGET_DIR/.claude/skills/daily-watchlist-import.md"
rm -f "$TARGET_DIR/.claude/commands/daily-watchlist-today.md"
rm -f "$TARGET_DIR/.claude/commands/daily-watchlist-import.md"
cp "$REPO_DIR/.claude/commands/dw-today.md" "$TARGET_DIR/.claude/commands/"
cp "$REPO_DIR/.claude/commands/dw-import.md" "$TARGET_DIR/.claude/commands/"
cp "$REPO_DIR/skills/dw-today.md" "$TARGET_DIR/.claude/skills/"
cp "$REPO_DIR/skills/dw-import.md" "$TARGET_DIR/.claude/skills/"

# --- Copy config files (working copies only, no .example duplicates) ---
copy_if_needed "$REPO_DIR/config/daily-watchlist.env.example" "$TARGET_DIR/config/daily-watchlist.env"
copy_if_needed "$REPO_DIR/config/daily-watchlist.example.yaml" "$TARGET_DIR/config/daily-watchlist.yaml"
copy_if_needed "$REPO_DIR/config/daily-watchlist.watchlist.example.md" "$TARGET_DIR/config/daily-watchlist-watchlist.md"

# --- Workspace-level CLAUDE.md (always written inside $TARGET_DIR) ---
PROTOCOL_HEADING="## Daily Watchlist"
LEGACY_PROTOCOL_HEADING="## Daily Watchlist Protocols"

if [[ ! -f "$TARGET_DIR/CLAUDE.md" ]]; then
    cat > "$TARGET_DIR/CLAUDE.md" <<'EOF'
# Workspace Instructions

## Daily Watchlist

For Daily Watchlist requests, prefer `/dw-today` and `/dw-import`.

Read these first:
- `./.claude/commands/dw-today.md`
- `./.claude/commands/dw-import.md`
- `./.claude/skills/dw-today.md`
- `./.claude/skills/dw-import.md`
- `./config/daily-watchlist.yaml`
- `./config/daily-watchlist-watchlist.md`
- `./templates/daily-watchlist-report-template.md`

Write reports to `./daily-watchlist-reports/YYYY-MM/`.
EOF
elif ! grep -Fq "$PROTOCOL_HEADING" "$TARGET_DIR/CLAUDE.md" && ! grep -Fq "$LEGACY_PROTOCOL_HEADING" "$TARGET_DIR/CLAUDE.md"; then
    cat >> "$TARGET_DIR/CLAUDE.md" <<'EOF'

## Daily Watchlist

For Daily Watchlist requests, prefer `/dw-today` and `/dw-import`.

Read these first:
- `./.claude/commands/dw-today.md`
- `./.claude/commands/dw-import.md`
- `./.claude/skills/dw-today.md`
- `./.claude/skills/dw-import.md`
- `./config/daily-watchlist.yaml`
- `./config/daily-watchlist-watchlist.md`
- `./templates/daily-watchlist-report-template.md`

Write reports to `./daily-watchlist-reports/YYYY-MM/`.
EOF
fi

# --- Project-root CLAUDE.md pointer (only if TARGET_DIR is strictly under cwd) ---
CWD="$(pwd)"
ABS_TARGET="$(cd "$TARGET_DIR" 2>/dev/null && pwd || echo "")"
# Trailing slash guard avoids prefix collisions (e.g. /foo/bar vs /foo/barbaz)
if [[ -n "$ABS_TARGET" && "$ABS_TARGET" != "$CWD" && "${ABS_TARGET}/" == "${CWD}/"* ]]; then
    ROOT_CLAUDE="$CWD/CLAUDE.md"
    REL_TARGET="${TARGET_DIR#./}"
    REL_TARGET="${REL_TARGET%/}"
    if [[ -f "$ROOT_CLAUDE" ]]; then
        if ! grep -Fq "$PROTOCOL_HEADING" "$ROOT_CLAUDE" && ! grep -Fq "$LEGACY_PROTOCOL_HEADING" "$ROOT_CLAUDE"; then
            cat >> "$ROOT_CLAUDE" <<EOF

## Daily Watchlist

Installed under \`$REL_TARGET/\`. For Daily Watchlist requests, prefer /dw-today and /dw-import.

Workspace-level instructions (read these first when handling /dw-*):
- $REL_TARGET/CLAUDE.md
- $REL_TARGET/.claude/commands/dw-today.md
- $REL_TARGET/.claude/commands/dw-import.md
- $REL_TARGET/.claude/skills/dw-today.md
- $REL_TARGET/.claude/skills/dw-import.md
- $REL_TARGET/config/daily-watchlist.yaml
- $REL_TARGET/config/daily-watchlist-watchlist.md

Reports are written to $REL_TARGET/daily-watchlist-reports/YYYY-MM/.
EOF
            echo "OK Added Daily Watchlist pointer to project-root CLAUDE.md"
        fi
    fi
fi

# --- Install Python dependencies ---
echo ""
echo "Installing Python dependencies..."
if $PYTHON_CMD -m pip install -r "$REPO_DIR/requirements.txt" --quiet; then
    echo "OK Python dependencies installed"
else
    echo ""
    echo "WARNING: Dependency install failed. Please run manually:"
    echo "  $PYTHON_CMD -m pip install -r requirements.txt"
    echo ""
fi

# --- Run setup check ---
echo ""
echo "Running setup check..."
if $PYTHON_CMD "$TARGET_DIR/scripts/check_setup.py"; then
    echo ""
    echo "OK Installation complete! All checks passed."
else
    echo ""
    echo "WARNING: Installation complete, but setup check found issues."
    echo "If the only missing item is FMP_API_KEY, that is expected on first install."
    echo ""
fi

echo ""
echo "Installed to $TARGET_DIR"
echo ""
echo "Next steps:"
echo "  1. Edit API key:     $TARGET_DIR/config/daily-watchlist.env"
echo "  2. Review config:    $TARGET_DIR/config/daily-watchlist.yaml"
echo "  3. Review watchlist: $TARGET_DIR/config/daily-watchlist-watchlist.md"
echo "  4. Edit template:    $TARGET_DIR/templates/daily-watchlist-report-template.md (optional)"
echo "  5. Generate report:  Run /dw-today in Claude Code"

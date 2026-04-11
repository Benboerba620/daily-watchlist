# Daily Watchlist Install Script (Windows PowerShell)
# Usage: .\scripts\install.ps1 -TargetDir .\daily-watchlist [-Force]
#
# 如果 PowerShell 阻止运行脚本，请先执行：
#   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

param(
    [string]$TargetDir = ".\daily-watchlist",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoDir = Split-Path -Parent $ScriptDir

$ProtocolHeading = "## Daily Watchlist Protocols"
$ProtocolLines = @(
    "## Daily Watchlist Protocols",
    "",
    "When the user asks for the Daily Watchlist workflow (/dw-today or /dw-import; /watchlist-today and /watchlist-import are compatibility aliases; use /today and /import only when unambiguous), read these first:",
    "- ./config/daily-watchlist.yaml",
    "- ./templates/daily-watchlist-report-template.md",
    "- ./.claude/skills/daily-watchlist-today.md",
    "",
    "Write reports to ./daily-watchlist-reports/YYYY-MM/ . Follow the saved template by default and tell the user the template can be edited at any time."
)
$RootClaudeLines = @(
    "# Workspace Instructions",
    ""
) + $ProtocolLines

function Copy-IfNeeded {
    param(
        [string]$Source,
        [string]$Destination
    )
    if ((-not (Test-Path $Destination)) -or $Force) {
        Copy-Item $Source $Destination -Force
    }
}

Write-Host "=== Daily Watchlist Installer ==="
Write-Host "Target: $TargetDir"

# --- Check Python ---
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host ""
    Write-Host "X Python not found. Please install Python >= 3.10:" -ForegroundColor Red
    Write-Host "  https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installing, re-run this script."
    exit 1
}

$pyVersion = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$pyOk = & python -c "import sys; print(1 if sys.version_info >= (3, 10) else 0)"
if ($pyOk -ne "1") {
    Write-Host ""
    Write-Host "X Python version too old (current: $pyVersion, required: >= 3.10)" -ForegroundColor Red
    Write-Host "  https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "OK Python $pyVersion" -ForegroundColor Green

# --- Check target directory ---
if (Test-Path $TargetDir) {
    $existingItem = Get-Item -LiteralPath $TargetDir
    if (-not $existingItem.PSIsContainer) {
        Write-Host "ERROR: $TargetDir exists and is not a directory." -ForegroundColor Red
        exit 1
    }
    Write-Host "Target directory already exists. Installing into existing workspace."
}

# --- Create directory structure ---
$dirs = @(
    "config",
    "scripts",
    "templates",
    "daily-watchlist-reports",
    ".claude",
    ".claude\skills"
)
foreach ($d in $dirs) {
    $path = Join-Path $TargetDir $d
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
}

# --- Copy script files ---
$scripts = @(
    "generate_daily_report.py",
    "fetch_market_data.py",
    "fetch_macro_data.py",
    "check_setup.py",
    "workspace_paths.py"
)
foreach ($s in $scripts) {
    Copy-Item (Join-Path $RepoDir "scripts\$s") (Join-Path $TargetDir "scripts\$s") -Force
}

Copy-Item (Join-Path $RepoDir "templates\daily-watchlist-report-template.md") (Join-Path $TargetDir "templates\daily-watchlist-report-template.md") -Force

$skills = @("daily-watchlist-today.md", "daily-watchlist-import.md")
foreach ($s in $skills) {
    Copy-Item (Join-Path $RepoDir "skills\$s") (Join-Path $TargetDir ".claude\skills\$s") -Force
}

# --- Copy config files (working copies only, no .example duplicates) ---
Copy-IfNeeded (Join-Path $RepoDir "config\daily-watchlist.env.example") (Join-Path $TargetDir "config\daily-watchlist.env")
Copy-IfNeeded (Join-Path $RepoDir "config\daily-watchlist.example.yaml") (Join-Path $TargetDir "config\daily-watchlist.yaml")
Copy-IfNeeded (Join-Path $RepoDir "config\daily-watchlist.watchlist.example.md") (Join-Path $TargetDir "config\daily-watchlist-watchlist.md")

# --- CLAUDE.md integration (lightweight entry, no full protocol copy) ---
$targetClaude = Join-Path $TargetDir "CLAUDE.md"
if (-not (Test-Path $targetClaude)) {
    Set-Content -Path $targetClaude -Value ($RootClaudeLines -join "`r`n") -Encoding utf8
} else {
    $existingClaude = Get-Content $targetClaude -Raw
    if ($existingClaude -notmatch [regex]::Escape($ProtocolHeading)) {
        $content = $existingClaude.TrimEnd()
        if ($content) {
            $content += "`r`n`r`n"
        }
        $content += ($ProtocolLines -join "`r`n")
        Set-Content -Path $targetClaude -Value $content -Encoding utf8
    }
}

# --- Install Python dependencies ---
Write-Host ""
Write-Host "Installing Python dependencies..."
try {
    & python -m pip install -r (Join-Path $RepoDir "requirements.txt") --quiet
    Write-Host "OK Python dependencies installed" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "WARNING: Dependency install failed. Please run manually:" -ForegroundColor Yellow
    Write-Host "  python -m pip install -r requirements.txt"
    Write-Host ""
}

# --- Run setup check ---
Write-Host ""
Write-Host "Running setup check..."
& python (Join-Path $TargetDir "scripts\check_setup.py")
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "OK Installation complete! All checks passed." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "WARNING: Installation complete, but setup check found issues. Please fix them before use." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Installed to $TargetDir"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit API key:     $TargetDir\config\daily-watchlist.env"
Write-Host "  2. Review config:    $TargetDir\config\daily-watchlist.yaml"
Write-Host "  3. Review watchlist: $TargetDir\config\daily-watchlist-watchlist.md"
Write-Host "  4. Edit template:    $TargetDir\templates\daily-watchlist-report-template.md (optional)"
Write-Host "  5. Generate report:  Run /dw-today in Claude Code"

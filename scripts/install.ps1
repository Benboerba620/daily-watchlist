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

$ProtocolHeading = "## Daily Watchlist"
$LegacyProtocolHeading = "## Daily Watchlist Protocols"
$ProtocolLines = @(
    "## Daily Watchlist",
    "",
    "For Daily Watchlist requests, prefer /dw-today and /dw-import.",
    "For Hypothesis Tracker requests, prefer /ht-new, /ht-status, and /ht-trade.",
    "",
    "Read these first:",
    "- ./.claude/commands/dw-today.md",
    "- ./.claude/commands/dw-import.md",
    "- ./.claude/commands/ht-new.md",
    "- ./.claude/commands/ht-status.md",
    "- ./.claude/commands/ht-trade.md",
    "- ./.claude/skills/dw-today.md",
    "- ./.claude/skills/dw-import.md",
    "- ./.claude/skills/ht-new.md",
    "- ./.claude/skills/ht-status.md",
    "- ./.claude/skills/ht-trade.md",
    "- ./config/daily-watchlist.yaml",
    "- ./config/daily-watchlist-watchlist.md",
    "- ./config/hypothesis-tracker.yaml",
    "- ./config/hypothesis-tracker.rules.md",
    "- ./templates/daily-watchlist-report-template.md",
    "",
    "Write reports to ./daily-watchlist-reports/YYYY-MM/. Keep hypotheses in ./hypothesis/."
)
$RootClaudeLines = @(
    "# Workspace Instructions",
    ""
) + $ProtocolLines

function Get-RootPointerLines {
    param([string]$RelTarget)
    return @(
        "## Daily Watchlist",
        "",
        "Installed under ``$RelTarget/``. Prefer /dw-today, /dw-import, /ht-new, /ht-status, and /ht-trade.",
        "",
        "Workspace-level instructions (read these first when handling /dw-*):",
        "- $RelTarget/CLAUDE.md",
        "- $RelTarget/.claude/commands/dw-today.md",
        "- $RelTarget/.claude/commands/dw-import.md",
        "- $RelTarget/.claude/commands/ht-new.md",
        "- $RelTarget/.claude/commands/ht-status.md",
        "- $RelTarget/.claude/commands/ht-trade.md",
        "- $RelTarget/.claude/skills/dw-today.md",
        "- $RelTarget/.claude/skills/dw-import.md",
        "- $RelTarget/.claude/skills/ht-new.md",
        "- $RelTarget/.claude/skills/ht-status.md",
        "- $RelTarget/.claude/skills/ht-trade.md",
        "- $RelTarget/config/daily-watchlist.yaml",
        "- $RelTarget/config/daily-watchlist-watchlist.md",
        "- $RelTarget/config/hypothesis-tracker.yaml",
        "- $RelTarget/config/hypothesis-tracker.rules.md",
        "",
        "Reports are written to $RelTarget/daily-watchlist-reports/YYYY-MM/. Hypotheses live in $RelTarget/hypothesis/."
    )
}

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
    "hypothesis",
    "portfolio",
    "portfolio\journal",
    ".claude",
    ".claude\commands",
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
    "workspace_paths.py",
    "sync_hypothesis.py",
    "trade_stats.py"
)
foreach ($s in $scripts) {
    Copy-Item (Join-Path $RepoDir "scripts\$s") (Join-Path $TargetDir "scripts\$s") -Force
}

Copy-Item (Join-Path $RepoDir "templates\daily-watchlist-report-template.md") (Join-Path $TargetDir "templates\daily-watchlist-report-template.md") -Force
Copy-Item (Join-Path $RepoDir "templates\hypothesis-tracker-hypothesis-template.md") (Join-Path $TargetDir "templates\hypothesis-tracker-hypothesis-template.md") -Force
Copy-Item (Join-Path $RepoDir "templates\hypothesis-tracker-journal-template.md") (Join-Path $TargetDir "templates\hypothesis-tracker-journal-template.md") -Force
Copy-Item (Join-Path $RepoDir "templates\hypothesis-tracker-report-template.md") (Join-Path $TargetDir "templates\hypothesis-tracker-report-template.md") -Force

# Remove legacy filenames from prior installs (pre-1.0.4 rename)
$legacySkills = @("daily-watchlist-today.md", "daily-watchlist-import.md")
foreach ($s in $legacySkills) {
    $legacyPath = Join-Path $TargetDir ".claude\skills\$s"
    if (Test-Path $legacyPath) {
        Remove-Item -LiteralPath $legacyPath -Force
    }
}

$legacyCommands = @("daily-watchlist-today.md", "daily-watchlist-import.md")
foreach ($c in $legacyCommands) {
    $legacyPath = Join-Path $TargetDir ".claude\commands\$c"
    if (Test-Path $legacyPath) {
        Remove-Item -LiteralPath $legacyPath -Force
    }
}

$skills = @("dw-today.md", "dw-import.md", "ht-new.md", "ht-status.md", "ht-trade.md")
foreach ($s in $skills) {
    Copy-Item (Join-Path $RepoDir "skills\$s") (Join-Path $TargetDir ".claude\skills\$s") -Force
}

$commands = @("dw-today.md", "dw-import.md", "ht-new.md", "ht-status.md", "ht-trade.md")
foreach ($c in $commands) {
    Copy-Item (Join-Path $RepoDir ".claude\commands\$c") (Join-Path $TargetDir ".claude\commands\$c") -Force
}

# --- Copy config files (working copies only, no .example duplicates) ---
Copy-IfNeeded (Join-Path $RepoDir "config\daily-watchlist.env.example") (Join-Path $TargetDir "config\daily-watchlist.env")
Copy-IfNeeded (Join-Path $RepoDir "config\daily-watchlist.example.yaml") (Join-Path $TargetDir "config\daily-watchlist.yaml")
Copy-IfNeeded (Join-Path $RepoDir "config\daily-watchlist.watchlist.example.md") (Join-Path $TargetDir "config\daily-watchlist-watchlist.md")
Copy-IfNeeded (Join-Path $RepoDir "config\hypothesis-tracker.example.yaml") (Join-Path $TargetDir "config\hypothesis-tracker.yaml")
Copy-IfNeeded (Join-Path $RepoDir "config\hypothesis-tracker.rules.example.md") (Join-Path $TargetDir "config\hypothesis-tracker.rules.md")
Copy-IfNeeded (Join-Path $RepoDir "config\hypothesis-tracker.env.example") (Join-Path $TargetDir "config\hypothesis-tracker.env")

$tradesFile = Join-Path $TargetDir "portfolio\trades.csv"
if ((-not (Test-Path $tradesFile)) -or $Force) {
    Set-Content -Path $tradesFile -Value "date,ticker,market,action,shares,price,currency,reasoning,kill_thesis,outcome_note" -Encoding utf8
}

$holdingsFile = Join-Path $TargetDir "portfolio\holdings.csv"
if ((-not (Test-Path $holdingsFile)) -or $Force) {
    Set-Content -Path $holdingsFile -Value "ticker,market,name,shares,avg_cost,currency,date_opened,hypothesis,stop_loss,status" -Encoding utf8
}

# --- Workspace-level CLAUDE.md (always written inside $TargetDir) ---
$targetClaude = Join-Path $TargetDir "CLAUDE.md"
if (-not (Test-Path $targetClaude)) {
    Set-Content -Path $targetClaude -Value ($RootClaudeLines -join "`r`n") -Encoding utf8
} else {
    $existingClaude = Get-Content $targetClaude -Raw
    if (
        ($existingClaude -notmatch [regex]::Escape($ProtocolHeading)) -and
        ($existingClaude -notmatch [regex]::Escape($LegacyProtocolHeading))
    ) {
        $content = $existingClaude.TrimEnd()
        if ($content) {
            $content += "`r`n`r`n"
        }
        $content += ($ProtocolLines -join "`r`n")
        Set-Content -Path $targetClaude -Value $content -Encoding utf8
    }
}

# --- Project-root CLAUDE.md pointer (only if TargetDir is strictly under cwd) ---
$cwd = (Get-Location).Path
$absTarget = (Resolve-Path -LiteralPath $TargetDir -ErrorAction SilentlyContinue).Path
# Trailing-sep guard avoids prefix collisions (e.g. C:\foo\bar vs C:\foo\barbaz)
$cwdWithSep = $cwd.TrimEnd('\','/') + [System.IO.Path]::DirectorySeparatorChar
$absTargetWithSep = if ($absTarget) { $absTarget.TrimEnd('\','/') + [System.IO.Path]::DirectorySeparatorChar } else { "" }
if ($absTarget -and ($absTarget -ne $cwd) -and $absTargetWithSep.StartsWith($cwdWithSep, [System.StringComparison]::OrdinalIgnoreCase)) {
    $rootClaude = Join-Path $cwd "CLAUDE.md"
    $relTarget = $TargetDir -replace "^\.[\\/]", "" -replace "\\", "/"
    $relTarget = $relTarget.TrimEnd("/")
    if (Test-Path $rootClaude) {
        $rootContent = Get-Content $rootClaude -Raw
        if (
            ($rootContent -notmatch [regex]::Escape($ProtocolHeading)) -and
            ($rootContent -notmatch [regex]::Escape($LegacyProtocolHeading))
        ) {
            $content = $rootContent.TrimEnd()
            if ($content) {
                $content += "`r`n`r`n"
            }
            $content += ((Get-RootPointerLines -RelTarget $relTarget) -join "`r`n")
            Set-Content -Path $rootClaude -Value $content -Encoding utf8
            Write-Host "OK Added Daily Watchlist pointer to project-root CLAUDE.md" -ForegroundColor Green
        }
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
$setupExitCode = $LASTEXITCODE
if ($setupExitCode -eq 0) {
    Write-Host ""
    Write-Host "OK Installation complete! All checks passed." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "WARNING: Installation complete, but setup check found issues. Please fix them before use." -ForegroundColor Yellow
    Write-Host "If the only missing item is FMP_API_KEY, that is expected on first install." -ForegroundColor Yellow
    $global:LASTEXITCODE = 0
}

Write-Host ""
Write-Host "Installed to $TargetDir"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit API key:     $TargetDir\config\daily-watchlist.env"
Write-Host "  2. Review config:    $TargetDir\config\daily-watchlist.yaml"
Write-Host "  3. Review watchlist: $TargetDir\config\daily-watchlist-watchlist.md"
Write-Host "  4. Review HT config: $TargetDir\config\hypothesis-tracker.yaml"
Write-Host "  5. Generate report:  Run /dw-today in Claude Code"
Write-Host "  6. Track theses:     Run /ht-new or /ht-status in Claude Code"

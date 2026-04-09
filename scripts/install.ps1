# Daily Watchlist Install Script (Windows PowerShell)
# Usage: .\scripts\install.ps1 -TargetDir .\daily-watchlist [-Force]

param(
    [string]$TargetDir = ".\daily-watchlist",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoDir = Split-Path -Parent $ScriptDir

$ProtocolFileName = "_daily-watchlist-protocols.md"
$ProtocolHeading = "## Daily Watchlist Protocols"
$ProtocolLines = @(
    "## Daily Watchlist Protocols",
    "",
    "When the user asks for the Daily Watchlist workflow (/dw-today or /dw-import; /watchlist-today and /watchlist-import are compatibility aliases; use /today and /import only when unambiguous), read these first:",
    "- ./_daily-watchlist-protocols.md",
    "- ./config/daily-watchlist.yaml",
    "- ./templates/daily-watchlist-report-template.md",
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

if ((Test-Path $TargetDir) -and (-not $Force)) {
    Write-Host "ERROR: $TargetDir already exists. Use -Force to overwrite." -ForegroundColor Red
    exit 1
}

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

Copy-IfNeeded (Join-Path $RepoDir "config\daily-watchlist.env.example") (Join-Path $TargetDir "config\daily-watchlist.env.example")
Copy-IfNeeded (Join-Path $RepoDir "config\daily-watchlist.example.yaml") (Join-Path $TargetDir "config\daily-watchlist.example.yaml")
Copy-IfNeeded (Join-Path $RepoDir "config\daily-watchlist.watchlist.example.md") (Join-Path $TargetDir "config\daily-watchlist.watchlist.example.md")
Copy-IfNeeded (Join-Path $RepoDir "config\daily-watchlist.example.yaml") (Join-Path $TargetDir "config\daily-watchlist.yaml")
Copy-IfNeeded (Join-Path $RepoDir "config\daily-watchlist.watchlist.example.md") (Join-Path $TargetDir "config\daily-watchlist-watchlist.md")

Copy-IfNeeded (Join-Path $RepoDir "CLAUDE.md") (Join-Path $TargetDir $ProtocolFileName)

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

Write-Host ""
Write-Host "Installed to $TargetDir"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Copy env:      Copy-Item $TargetDir\config\daily-watchlist.env.example $TargetDir\config\daily-watchlist.env"
Write-Host "  2. Edit env:      $TargetDir\config\daily-watchlist.env"
Write-Host "  3. Review config: $TargetDir\config\daily-watchlist.yaml"
Write-Host "  4. Review list:   $TargetDir\config\daily-watchlist-watchlist.md"
Write-Host "  5. Edit template: $TargetDir\templates\daily-watchlist-report-template.md (optional)"
Write-Host "  6. Run check:     python $TargetDir\scripts\check_setup.py"
Write-Host "  7. Generate:      python $TargetDir\scripts\generate_daily_report.py"
Write-Host ""

$py = Get-Command python -ErrorAction SilentlyContinue
if ($py) {
    Write-Host "Running setup check..."
    & python (Join-Path $TargetDir "scripts\check_setup.py")
} else {
    Write-Host "Python not found. Install Python >= 3.8, then run: python $TargetDir\scripts\check_setup.py"
}

from __future__ import annotations

from pathlib import Path

CONFIG_DIRNAME = "config"
REPORTS_DIRNAME = "daily-watchlist-reports"
ROOT_INTEGRATION_HEADING = "## Daily Watchlist Protocols"

ENV_FILE_CANDIDATES = (
    "daily-watchlist.env",
    ".env",
)

CONFIG_FILE_CANDIDATES = (
    "daily-watchlist.yaml",
    "config.yaml",
)

WATCHLIST_FILE_CANDIDATES = (
    "daily-watchlist-watchlist.md",
    "watchlist.md",
)

TEMPLATE_FILE_CANDIDATES = (
    "daily-watchlist-report-template.md",
    "report-template.md",
)

SKILL_FILE_CANDIDATES = (
    "dw-today.md",
    "dw-import.md",
    "daily-watchlist-today.md",
    "daily-watchlist-import.md",
)


def find_existing_path(directory: Path, candidates: tuple[str, ...]) -> Path | None:
    for candidate in candidates:
        path = directory / candidate
        if path.is_file():
            return path
    return None


def preferred_path(directory: Path, candidates: tuple[str, ...]) -> Path:
    return directory / candidates[0]


def find_workspace_root(start_dir: Path) -> Path:
    current = start_dir.resolve()
    for candidate in (current, *current.parents):
        config_dir = candidate / CONFIG_DIRNAME
        if find_existing_path(config_dir, CONFIG_FILE_CANDIDATES):
            return candidate
    raise FileNotFoundError(
        f"Could not locate workspace root from {start_dir} by searching for config files"
    )


def resolve_config_dir(workspace_root: Path) -> Path:
    return workspace_root / CONFIG_DIRNAME


def resolve_config_path(config_dir: Path) -> Path:
    return find_existing_path(config_dir, CONFIG_FILE_CANDIDATES) or preferred_path(
        config_dir, CONFIG_FILE_CANDIDATES
    )


def resolve_watchlist_path(config_dir: Path) -> Path:
    return find_existing_path(config_dir, WATCHLIST_FILE_CANDIDATES) or preferred_path(
        config_dir, WATCHLIST_FILE_CANDIDATES
    )


def resolve_env_path(config_dir: Path) -> Path:
    return find_existing_path(config_dir, ENV_FILE_CANDIDATES) or preferred_path(
        config_dir, ENV_FILE_CANDIDATES
    )


def resolve_template_path(workspace_root: Path) -> Path:
    templates_dir = workspace_root / "templates"
    return find_existing_path(templates_dir, TEMPLATE_FILE_CANDIDATES) or preferred_path(
        templates_dir, TEMPLATE_FILE_CANDIDATES
    )

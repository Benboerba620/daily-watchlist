# Daily Watchlist Protocols

This file is the source protocol for the Daily Watchlist workflow.

The installer does not copy this file wholesale into the target workspace.
Instead, it appends a short `CLAUDE.md` hint that points Claude Code to:

- `./.claude/skills/dw-today.md`
- `./.claude/skills/dw-import.md`
- `./config/daily-watchlist.yaml`
- `./config/daily-watchlist-watchlist.md`
- `./templates/daily-watchlist-report-template.md`

Recommended commands:

- `/dw-today`
- `/dw-import`

Compatibility aliases may still exist inside the skills, but they should not be the default recommendation in shared docs or injected workspace hints because they are more likely to conflict with other systems.

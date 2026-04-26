# Daily Watchlist Protocols

This file is the source protocol for the Daily Watchlist workflow.
Hypothesis Tracker is bundled in this repository as the thesis/evidence layer.

The installer does not copy this file wholesale into the target workspace.
Instead, it appends a short `CLAUDE.md` hint that points Claude Code to:

- `./.claude/commands/dw-today.md`
- `./.claude/commands/dw-import.md`
- `./.claude/commands/ht-new.md`
- `./.claude/commands/ht-status.md`
- `./.claude/commands/ht-trade.md`
- `./.claude/skills/dw-today.md`
- `./.claude/skills/dw-import.md`
- `./.claude/skills/ht-new.md`
- `./.claude/skills/ht-status.md`
- `./.claude/skills/ht-trade.md`
- `./config/daily-watchlist.yaml`
- `./config/daily-watchlist-watchlist.md`
- `./config/hypothesis-tracker.yaml`
- `./config/hypothesis-tracker.rules.md`
- `./templates/daily-watchlist-report-template.md`

Recommended commands:

- `/dw-today`
- `/dw-import`
- `/ht-new`
- `/ht-status`
- `/ht-trade`

Compatibility aliases may still exist inside the skills, but they should not be the default recommendation in shared docs or injected workspace hints because they are more likely to conflict with other systems.

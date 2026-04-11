# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project uses Semantic Versioning for tags and GitHub releases.

## [1.0.1] - 2026-04-11

### Changed

- Simplified the injected `CLAUDE.md` hint so installed workspaces keep a lightweight entrypoint instead of accumulating protocol-heavy instructions
- Updated docs and installer messaging to consistently recommend `/dw-today` and `/dw-import` as the default commands in shared workspaces
- Clarified first-install behavior so a missing `FMP_API_KEY` is reported as an expected setup warning rather than an installation failure

### Fixed

- Fixed the Windows installer exit code so CI and first-run installs do not fail just because the API key has not been filled in yet
- Aligned setup checks and docs around the actual Python requirement of 3.10+
- Removed outdated references to copying `.example` files into the installed workspace

### Added

- Added a cross-platform install test workflow covering Windows, macOS, and Ubuntu on Python 3.10, 3.11, and 3.12
- Added an offline smoke-report generator to verify that a freshly installed workspace can render a daily report skeleton without live API calls
- Added CI assertions that the installed `CLAUDE.md` stays lightweight and that report templates are fully rendered without unresolved placeholders

## [1.0.0] - 2026-04-10

First public release of Daily Watchlist.

### Added

- Claude Code workflow for `/dw-today` and `/dw-import`
- Template-driven daily report generation with configurable module toggles
- Market and macro data fetchers for watchlist monitoring and report scaffolding
- Windows PowerShell and Unix install scripts for bootstrapping a workspace
- Beginner-friendly README and AI-agent installation guide

### Notes

- This is the initial MVP release for the current repository history.

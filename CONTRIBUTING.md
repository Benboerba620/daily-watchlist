# Contributing

## Ground rules

- Keep changes small and scoped
- Preserve backward compatibility when possible
- Prefer namespaced files over generic filenames
- Run `python scripts/check_setup.py` before submitting changes
- For script changes, also run a real install test in a clean directory

## Good contributions

- bug fixes
- install and merge improvements
- documentation cleanup
- new data source adapters that keep the project free-tier friendly

## Out of scope

- trade execution
- GUI-only features
- paid-only integrations as the default path

## Releases

- Update `VERSION`, `CHANGELOG.md`, and any user-facing docs that mention the release number
- Commit the release on `main`
- Create an annotated tag such as `git tag -a v1.0.1 -m "Release v1.0.1"`
- Push `main` and the tag: `git push origin main && git push origin v1.0.1`
- The GitHub Actions `Release` workflow validates the scripts and creates or updates the GitHub release from `CHANGELOG.md`
- If needed, run the workflow manually with `workflow_dispatch` and provide an existing tag

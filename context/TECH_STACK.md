---
DATE: 2026-07-15
STATUS: CANONICAL
---

# honeybee_grasshopper_ph — Tech Stack

## Runtime

- **IronPython 2.7** for everything in `honeybee_ph_rhino/` (Rhino GHPython interpreter).
- **CPython 3** for `scripts/` (release helpers) only.

## Dependencies

This repo has no model logic of its own — it calls into upstream PyPI libraries, **pinned in `requirements.txt`**:

- `honeybee_ph` — the PH data model (and the test suite for the workers here).
- `PHX` — PHPP/WUFI serialization and export.
- `PH_units` — unit conversion.
- `honeybee_ref` — document/reference tracking.

Type stubs for the Rhino/GH APIs live in `stubs/` (see `stubs/ADDING_MORE_STUBS.md`).

## Packaging

- Not a pip package — `pyproject.toml` carries tooling config (black/ruff, bump-my-version) but no `[project]` metadata. Distribution is the `.ghuser` user objects installed via `hbph_installer.ghx`.

## Dev loop (fsdeploy)

`.vscode/settings.json` `fsdeploy` config auto-copies `honeybee_ph_rhino/` on save into the local `ladybug_tools` site-packages and the `PHX` venv, so edits are live in Rhino and the other repos immediately.

## Testing

- **No tests in this repo.** The worker suite lives in `honeybee_ph`. Lint/format only (black + ruff, line-length 120).

## Versioning & release (orchestrated — do not hand-edit)

- `RELEASE_VERSION` (`_component_info_.py`), the `requirements.txt` pins, and `hbph_installer.ghx` are **auto-updated by the release orchestrator** (`.github/workflows/release.yml`, manual `workflow_dispatch`): it fetches the latest PyPI versions of the PH-Tools libs, updates those three, bumps via `bump-my-version`, tags, and cuts a GitHub Release.
- Pushing to `main` does **not** release (unlike the PyPI library repos).
- Full ecosystem build/release detail: `WORKFLOW.md` (repo root).

## Docs

- `docs/` is a **generated Hugo static site** (`docs/public/`, `.hugo_build.lock`), deployed to GitHub Pages by `.github/workflows/hugo.yml` as redirect pages to passivehousetools.com. **Do not hand-edit or index `docs/`** — it is build output.

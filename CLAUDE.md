# honeybee_grasshopper_ph

The **Grasshopper UI layer** for Honeybee-PH — the Passive House modeling components users drop onto the Rhino/Grasshopper canvas. This repo contains *only* the components; the data model and logic live upstream (`honeybee_ph`, `PHX`, `PH_units`, `honeybee_ref`), pinned in `requirements.txt`.

> **Runtime constraint (critical):** everything in `honeybee_ph_rhino/` must run under **IronPython 2.7** (Rhino's GHPython interpreter). `scripts/` is normal Python 3 — that distinction matters. See `context/CODING_STANDARDS.md`.

Data flow: GH components (here) build a `honeybee_ph` model → `PHX` serializes it → exports to PHPP (`.xlsx`) or WUFI-Passive (`.xml`).

## Where things live — read before working

| Working on… | Read |
|-------------|------|
| What this repo is/isn't, scope | `context/PRD.md` |
| Component anatomy (worker + wrapper + registry), `gh_io.IGH`, `.ghuser` export | `context/ARCHITECTURE.md` |
| IronPython 2.7 rules, imports, type comments, formatting | `context/CODING_STANDARDS.md` |
| Deps, dev loop (fsdeploy), release orchestrator, versioning | `context/TECH_STACK.md` |
| Ecosystem build/release detail | `WORKFLOW.md` (repo root) |
| Current / in-flight work | `planning/STATUS.md` |

Full context index: `context/README.md`.

## Hard rules

1. **IronPython 2.7 in `honeybee_ph_rhino/`.** No f-strings/`pathlib`/modern stdlib. Never bare `import typing` — nest in `try/except ImportError: pass` and use type *comments*, not annotations. Wrap third-party imports in `try/except` that re-raises a helpful `ImportError`. Route all Rhino/GH API calls through `gh_io.IGH`, never import Rhino APIs into a worker.
2. **Every component needs a registry entry.** Adding/renaming a component requires an entry in `honeybee_ph_rhino/_component_info_.py` (`COMPONENT_PARAMS`) or `set_component_params()` raises `ComponentNameError`.
3. **`.ghuser` files are regenerated inside Grasshopper**, not editable here — run `src/__HBPH__Util_Update_GHCompos.py` on the canvas, then commit the regenerated `src/*.py` + `user_objects/*.ghuser`. See `context/ARCHITECTURE.md`.
4. **Do not hand-edit versions.** `RELEASE_VERSION`, `requirements.txt` pins, and `hbph_installer.ghx` are auto-updated by the release orchestrator (`.github/workflows/release.yml`). Pushing to `main` does not release.
5. **`docs/` is a generated Hugo site** (deployed by `.github/workflows/hugo.yml`) — do not hand-edit or index it.
6. **Tests live upstream.** There are no tests in this repo; the worker suite is in `honeybee_ph`.

## Related repos (all under `~/Dropbox/bldgtyp-00/00_PH_Tools/`)

`honeybee_ph` (data model + the tests) · `PHX` (PHPP/WUFI serialization) · `PH_units` (unit conversion) · `honeybee_ref` (document tracking). Logic changes often belong upstream, not here.

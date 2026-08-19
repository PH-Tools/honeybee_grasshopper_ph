---
DATE: 2026-07-15
STATUS: CANONICAL ENGINEERING STANDARD
---

# honeybee_grasshopper_ph — Coding Standards

## 1. IronPython 2.7 (the one that bites)

The generic dual-runtime rules (banned syntax and modules, comment-style type
hints, guarded `typing` imports, defensive third-party imports, and the lint
settings they imply) live in the **ironpython-27-compatibility** skill. Apply it
before editing anything on the Rhino load path. Only this repo's specifics are
recorded below.

**Zone split:** everything in `honeybee_ph_rhino/` runs inside Rhino's GHPython
interpreter and is IPy2.7. `scripts/` is normal Python 3. Keep the two mentally
separate.

Third-party imports here are `ladybug_rhino` and `ladybug_geometry`; follow the
wrapping pattern already used by the existing workers.

## 2. Route Rhino/GH calls through `gh_io.IGH`

Workers must not import Rhino/Grasshopper APIs directly. Everything goes through the `IGH` interface object so workers stay testable (the tests, in `honeybee_ph`, mock `IGH`).

## 3. The component contract

- Worker logic in `gh_compo_io/<name>.py` (`GHCompo_<Name>`, constructor takes `_IGH` + inputs, exposes `.run()`).
- Thin GHPython wrapper in `honeybee_grasshopper_ph/src/HBPH - <Name>.py`.
- **A registry entry in `_component_info_.py` is mandatory** for any new/renamed component.
- Re-export the worker from `gh_compo_io/__init__.py`.

See `ARCHITECTURE.md` for the full pattern and the `.ghuser` regeneration step.

## 4. Formatting

- **black** and **ruff**, `line-length = 120`.
- `F401` (unused import) is ignored repo-wide — it collides with the Py2.7 type-comment style.
- Wildcard imports are allowed in `__init__.py`.

## 5. Versions — hands off

Do not hand-edit `RELEASE_VERSION` (`_component_info_.py`), the `requirements.txt` pins, or `hbph_installer.ghx`. The release orchestrator manages all three (see `TECH_STACK.md`).

## Closeout checklist

- [ ] Worker is IronPython-2.7-safe (no f-strings/pathlib; guarded `typing`; type comments; wrapped 3rd-party imports).
- [ ] Rhino/GH access only via `gh_io.IGH`.
- [ ] Registry entry added/updated in `_component_info_.py`; worker re-exported in `gh_compo_io/__init__.py`.
- [ ] `.ghuser` + `src/*.py` regenerated on the canvas if I/O changed, and committed together.
- [ ] black + ruff clean.
- [ ] Related logic/tests handled upstream in `honeybee_ph` where they belong.

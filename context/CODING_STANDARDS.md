---
DATE: 2026-07-15
STATUS: CANONICAL ENGINEERING STANDARD
---

# honeybee_grasshopper_ph — Coding Standards

## 1. IronPython 2.7 (the one that bites)

**All code in `honeybee_ph_rhino/` must be Python 2.7 / IronPython 2.7 compatible** — it runs inside Rhino's GHPython interpreter. (`scripts/` is normal Python 3; keep the two mentally separate.)

- No f-strings — use `.format()`. No `pathlib`, no modern stdlib.
- **Never bare `import typing`** — IronPython lacks it and the component crashes on import. Nest type imports:
  ```python
  try:
      from typing import Any, Dict, List, Optional
  except ImportError:
      pass  # IronPython 2.7
  ```
  and use type **comments**, not annotations:
  ```python
  def run(self, name, value):
      # type: (str, float) -> bool
      ...
  ```
- Wrap all third-party imports (`ladybug_rhino`, `ladybug_geometry`, etc.) in `try/except` that re-raises a helpful `ImportError` — follow the pattern in existing workers.

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

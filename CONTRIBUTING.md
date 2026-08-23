Contributing
------------
We welcome contributions from anyone, even if you are new to open source we will be happy to help you to get started.

### Code contribution
This project follows PH-Tools contributing guideline. See [contributing to PH-Tools projects](https://github.com/PH-Tools/contributing).

---

## A few things specific to this repository

This repo is the **Grasshopper UI layer** — the Honeybee-PH components users drop onto the
Rhino canvas, plus the installer. It is the front door for most users, but it is deliberately
thin: almost no Passive House logic lives here. The data model is in
[honeybee_ph](https://github.com/PH-Tools/honeybee_ph) and the export logic is in
[PHX](https://github.com/PH-Tools/PHX).

That thinness is the most important thing to know before you start. **If the fix involves
what a value means, what values are allowed, or what gets written to PHPP, it belongs
upstream, not here.** See
[Changes that span repositories](https://github.com/PH-Tools/contributing#changes-that-span-repositories).

Orientation, in the order worth reading:

| Working on… | Read |
|---|---|
| What this repo is and is not | `context/PRD.md` |
| Component anatomy — worker, wrapper, registry, `gh_io.IGH` | `context/ARCHITECTURE.md` |
| IronPython 2.7 rules, imports, type comments | `context/CODING_STANDARDS.md` |
| Dependencies, the dev loop, releases | `context/TECH_STACK.md` and `WORKFLOW.md` |
| What is currently in flight | `planning/STATUS.md` |

### IronPython 2.7

Everything in `honeybee_ph_rhino/` runs inside Rhino's GHPython interpreter, so it must be
IronPython-2.7-safe: no f-strings, no `pathlib`, guarded `typing` imports, comment-style
type hints, and third-party imports wrapped in `try/except` that re-raises a helpful
`ImportError`. Rhino and Grasshopper API calls go through `gh_io.IGH` rather than being
imported into a worker.

`scripts/` is ordinary Python 3 — keep the two mentally separate.

### There are no tests in this repo

The worker test-suite lives upstream in `honeybee_ph`, where the logic is. If your change
needs a test — and most logic changes do — that is a sign the change itself probably belongs
upstream. We would rather help you move it than merge an untested one here.

There is also currently **no CI on pull requests** in this repo, which means review is by
hand and we may be slower than the other repos. Sorry about that.

### `.ghuser` files are regenerated, not edited

The files in `user_objects/` are binary Grasshopper artifacts. They are rebuilt *inside*
Grasshopper by running `src/__HBPH__Util_Update_GHCompos.py` on the canvas, and the
regenerated `src/*.py` and `user_objects/*.ghuser` are committed together.

**Most contributors cannot do this step, and that is completely fine** — it needs Rhino and
a working canvas. Open the pull request with the source change and say in the description
that the `.ghuser` regeneration is outstanding. A maintainer will run it. Please do not
hand-edit a `.ghuser`.

Two things that do *not* need regeneration:

- Changes to a worker in `gh_compo_io/` that do not alter the component's inputs or outputs.
- Tooltips and input nodes on the handful of components that build their inputs
  **dynamically at runtime** — `HBPH - PHI Certification` is the main one, where
  `get_component_inputs()` is called from the wrapper each time the component solves. Edit
  the description strings in the worker and you are done.

If you are not sure which case you are in, ask in the PR.

### Adding or renaming a component

1. Worker in `honeybee_ph_rhino/gh_compo_io/<name>.py` as `GHCompo_<Name>`, taking `_IGH`
   plus its inputs and exposing `.run()`.
2. Re-export it from `gh_compo_io/__init__.py`.
3. **A registry entry in `_component_info_.py` is mandatory** — without one,
   `set_component_params()` raises `ComponentNameError` and the component will not load.
4. A thin GHPython wrapper in `honeybee_grasshopper_ph/src/HBPH - <Name>.py`.
5. Regenerate the `.ghuser` on the canvas (or flag it for a maintainer, as above).

### Do not hand-edit versions

`RELEASE_VERSION` in `_component_info_.py`, the pins in `requirements.txt`, and
`hbph_installer.ghx` are all updated automatically by the release orchestrator
(`.github/workflows/release.yml`). Leave them alone — including the `requirements.txt` pin
bump that a cross-repo change depends on. Pushing to `main` does not cut a release; a
maintainer triggers it.

`docs/` is a generated Hugo site. Do not hand-edit it.

### Style

Black and Ruff, `line-length = 120`. Note that `F401` (unused import) is ignored repo-wide —
it collides with the Python-2.7 type-comment style, so an import that looks unused may not
be.

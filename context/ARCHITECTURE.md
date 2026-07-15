---
DATE: 2026-07-15
STATUS: CANONICAL
---

# honeybee_grasshopper_ph — Architecture

## How a component works — two files plus a registry entry

Each Grasshopper component is:

1. **Worker class** — `honeybee_ph_rhino/gh_compo_io/<name>.py`, class `GHCompo_<Name>`. Pure-ish, testable Python that holds all the logic. Its constructor takes `_IGH` (the Grasshopper interface) plus the component's inputs; it exposes `.run()` returning the outputs. **This is where you edit logic.**

2. **GHPython wrapper** — `honeybee_grasshopper_ph/src/HBPH - <Name>.py`. A thin GPL-licensed shim that runs *inside* the canvas: sets `ghenv.Component.Name`, builds `IGH = gh_io.IGH(...)`, instantiates the worker, calls `.run()`, assigns outputs. The `DEV` flag (`set_component_params(ghenv, dev=...)`) toggles a `reload()` of the worker module for live iteration.

3. **Registry entry** — `honeybee_ph_rhino/_component_info_.py` holds `RELEASE_VERSION`, `CATEGORY` (`HB-PH`), `SUB_CATEGORIES`, and `COMPONENT_PARAMS` (per-component NickName / Message / SubCategory). `set_component_params()` reads this to style the component. **Adding or renaming a component requires an entry here**, or `set_component_params` raises `ComponentNameError`.

`gh_compo_io/__init__.py` re-exports every `GHCompo_*` class so wrappers can `from honeybee_ph_rhino import gh_compo_io`.

## The `gh_io.IGH` seam

`honeybee_ph_rhino/gh_io.py` defines `IGH` — the single interface object that hides **all** Rhino/Grasshopper API calls. Workers talk to `IGH`, never to Rhino APIs directly, which is what makes them testable (mock the `IGH`). This is a hard rule: route GH/Rhino calls through `IGH`.

## Subpackage map

Domain subpackages under `gh_compo_io/` group related workers:

- `apertures/` — windows / frames / glazing
- `hvac/` — mechanical systems
- `shw/` — hot water & piping
- `shading/` — shading
- `program/` — loads / schedules
- `cert/` — PHI / Phius certification
- `openph/` — OpenPH

`make_spaces/` builds the PH space / volume / floor-segment geometry model from Honeybee rooms.

## `.ghuser` files and the export step

`honeybee_grasshopper_ph/user_objects/*.ghuser` are the compiled binaries users install; `src/*.py` are the human-readable source of the same components. **You cannot edit `.ghuser` from here** — they are regenerated *inside Grasshopper* by running `src/__HBPH__Util_Update_GHCompos.py`, which exports both the `.ghuser` and `.py` for every component on the canvas.

The round-trip:

```
edit worker in gh_compo_io/  →  (if I/O changed) edit the GHPython component in Grasshopper
  →  run the update util on the canvas  →  commit regenerated src/*.py + user_objects/*.ghuser
```

## Where the boundary is

This repo is UI only. Model logic → `honeybee_ph`; serialization/export → `PHX`; units → `PH_units`. See `PRD.md`.

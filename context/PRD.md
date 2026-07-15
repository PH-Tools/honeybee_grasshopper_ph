---
DATE: 2026-07-15
STATUS: CANONICAL PRD
---

# honeybee_grasshopper_ph — Product Requirements

## 1. Goal

Give Passive House practitioners the Grasshopper components that build a `honeybee_ph` model inside Rhino/Grasshopper — the visual, canvas-based front door to the Honeybee-PH toolchain. This repo is the **UI layer only**.

## 2. Who uses it

Passive House consultants modeling in Rhino/Grasshopper. They install the `.ghuser` components (via `hbph_installer.ghx`) and wire them on the canvas to add PH data to Honeybee models, then export via PHX to PHPP/WUFI.

## 3. What belongs here

- Grasshopper component **workers** (`honeybee_ph_rhino/gh_compo_io/`) and their **GHPython wrappers** (`honeybee_grasshopper_ph/src/`).
- The component **registry** (`_component_info_.py`).
- The `gh_io.IGH` seam over the Rhino/GH API.
- `make_spaces/` geometry building for PH spaces/volumes/floor-segments.
- Compiled `.ghuser` user objects and the installer.

## 4. Non-goals

- **No data model or business logic.** Those live upstream in `honeybee_ph` (model), `PHX` (serialization/export), `PH_units` (units), `honeybee_ref` (doc tracking). A component worker should call into those, not reimplement them. If logic needs to change, it usually changes upstream.
- **No tests here.** The worker test suite lives in `honeybee_ph`.
- **No export code.** PHPP/WUFI writing is PHX.

## 5. Success criteria

- Every component runs cleanly inside Rhino's IronPython 2.7 interpreter (no import/syntax errors on the canvas).
- Component I/O and metadata stay in sync across the worker, the GHPython wrapper, the registry, and the regenerated `.ghuser`.
- A model built with these components exports through PHX to PHPP and WUFI.

## 6. Direction

- Active/related planning in `planning/STATUS.md` (e.g. the PH-Tools website consolidation).

---
DATE: 2026-09-12
STATUS: In progress
AUTHOR: Ed May / Claude
ISSUE: https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/79
---

# Plan

## Phase 1: Worker inputs

File: `honeybee_ph_rhino/gh_compo_io/foundations_create.py` only. IronPython 2.7 rules apply.

1. Add the eight `ComponentInput` entries at the indexes in issue #79:
   - `inputs_slab_on_grade`: 9 `interior_wall_to_heated_area_m2` (`M2`), 10
     `interior_wall_to_heated_u_value` (`W/M2K`).
   - `inputs_unheated_basement`: 12, 13, same two fields.
   - `inputs_vented_crawlspace`: 9, 10, same two fields; 11 `wind_velocity_at_10m_m_s` (`M/S`); 12
     `wind_shield_factor` (float hint, no unit; D1).
   - `inputs_heated_basement`: unchanged.
2. Descriptions from the issue.
3. Gate (matches `ci.yml`): `black --check --diff .` and `isort --check-only --diff .`.
4. Scratch check (scratchpad, not committed), stubbing `GhPython`/`Grasshopper`:
   - group key sets and names match the issue; every new `_name` is an attribute of its class;
     heated basement has neither interior-wall field;
   - `run()` with the new inputs absent returns defaults (`4.0`, `0.05`, `0.0`);
   - `run()` with `"12 ft2"`, `"0.3"`, `"10 mph"`, `0.1` sets converted floats, and
     `wind_shield_factor` is a float;
   - `to_dict` / `PhFoundationFactory.from_dict` round trip keeps the set values.

## Phase 2: Canvas verification and UserObject

Walked through with Ed one step at a time; each step names what changes and what to look for.

1. Confirm Rhino's `site-packages` has the new `honeybee_ph` fields and the edited worker (fsdeploy).
2. Place the component; count input nodes. If fewer than 14, add nodes and rebuild the `.ghuser` via
   `src/__HBPH__Util_Update_GHCompos.py`; otherwise no UserObject change.
3. For each `_type` 1 to 4, check node names and order against the issue.
4. Unconnected new inputs: panel output shows upstream defaults.
5. Set values with units; confirm converted values; HBJSON write and reload keeps them.
6. Record results in `STATUS.md`.

## Phase 3: PR and release

1. PR `Closes #79`; description carries the four default corrections table.
2. Master `planning/STATUS.md` row updated.
3. After merge: Ed runs the release orchestrator; add the default-corrections note to the Release body.
4. Fold outcome into `context/` if anything changed there; archive the packet.

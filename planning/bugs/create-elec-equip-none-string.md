---
DATE: 2026-09-14
STATUS: Merged to main (PR #95, 2026-09-15) — canvas check in Rhino pending
AUTHOR: Claude (for Ed May)
ISSUE: https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/94
---

# Create Elec Equip: the string "None" in numeric equipment fields

## Defect

A production model's HBJSON carried `"energy_demand": "None"` (a JSON string)
on a `PhClothesDryer`. honeybee-ph and PHX pass the value through unchanged,
and it reaches the WUFI XML as `<EnergyDemandNorm>None</EnergyDemandNorm>`.
Downstream readers that do arithmetic on the field fail with a `TypeError`.

## Evidence

- The dryer's display name and comment were user-set, not the Phius/PHI
  default name. Both defaults set `energy_demand` to `0`.
- No code in `honeybee_grasshopper_ph`, `honeybee_grasshopper_ph_plus`,
  `honeybee_ph` or `PHX` writes the literal `"None"`.
- `GHCompo_CreateElecEquip.set_object_attributes`
  (`honeybee_ph_rhino/gh_compo_io/program/create_elec_equip.py`) copies any
  truthy input onto the equipment object with no conversion:
  `if input_val: setattr(obj, attr_name, input_val)`. Several inputs use a
  string type hint (`quantity`, `capacity_type`, `water_connection`,
  `dryer_type`, `cooktop_type`), so text can reach attributes that are numeric
  on the model.

## Ruled out

- **ph-navigator-v2 as the writer:** no `energy_demand` writes in its
  TS/Python sources.
- **honeybee_grasshopper_ph_plus:** builds no `PhClothesDryer`.
- **honeybee-ph defaults:** `ph_default_equip[...]["PHIUS"|"PHI"]` set
  `energy_demand` to `0`.

## Not verified

The exact canvas path that produced the string. `energy_demand` is declared
with a float type hint, which should reject the text `"None"`. A GH-side
reproduction still needs Rhino.

## Proposed correction

In `set_object_attributes`, normalize each input before `setattr`:

- `None`, `""` and the text `"None"` (case-insensitive, trimmed) → not set
  (keep the equipment default).
- For attributes whose current value on the freshly built equipment object is
  a `float`/`int` (not `bool`), convert the input to that type. Text that
  cannot convert raises a component error naming the input and the value.
- Other attributes (enum-backed string selectors, `comment`, booleans) keep
  today's pass-through.

The worker must stay IronPython 2.7-safe. There is no I/O change, so no
`.ghuser` or `src/` regeneration.

## Verification

- `black --check` and `ruff check` on the worker. This repo has no tests
  (worker tests live upstream in `honeybee_ph`, and none exist for this
  worker).
- A CPython scratch check that drives `set_object_attributes` with a stub IGH:
  `"None"` leaves the default, `"12.5"` → `12.5`, `"abc"` raises.
- A canvas check by Ed after the fsdeploy: the HBJSON has no string in
  numeric equipment fields.

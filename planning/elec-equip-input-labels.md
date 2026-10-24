---
DATE: 2026-10-24
STATUS: Implemented on branch (option B, canvas-verified 2026-10-24; docstrings drafted, not yet pasted)
AUTHOR: Ed May (with Claude)
ISSUE: none yet. Draft issue text at the end, for Ed's wording review before posting.
---

# Create PH Equipment: input labels and hover text

The dynamic `HBPH - Create PH Equipment` component reshapes its input nodes by `_type`, but the
node labels are raw honeybee-ph attribute names and several hover texts are placeholders
("() some WUFI stuff", "(float) usually kWh/yr", empty strings). A user filling in a Phius
appliance cannot tell which input WUFI-Passive or METr reads, in what unit, or which one PHPP
reads instead.

**Goal:** labels and hover text that name the WUFI-Passive / METr field each input feeds, and say
when PHPP reads a different input. **No behavior change.**

Files: `honeybee_ph_rhino/gh_compo_io/program/create_elec_equip.py` (input groups) and, for
option B, `honeybee_ph_rhino/gh_io.py`. Not `src/` (scrape only).

## 1. The constraint: the label is the lookup key

`setup_component_inputs()` sets a node's `Name` and `NickName` both from `ComponentInput.name`.
`get_component_input_values()` keys the input dict by `_input.Name`, and
`set_object_attributes()` matches those keys against the equipment object's attribute names.
So today a node cannot be renamed without breaking the value binding.

| Option | Change | Result |
|---|---|---|
| **A. Hover text only** | Rewrite `_description` strings; labels stay as attribute names | No code-path change at all. Labels stay cryptic (`reference_energy_norm`) |
| **B. Split label from key** (recommended) | `ComponentInput` gains an optional `_nickname`; `setup_component_inputs` sets `NickName = nickname or name` and keeps `Name = name` | Canvas shows the friendly label, the binding still uses `Name`. About 4 lines in `gh_io.py`, IronPython-safe, backwards compatible for every other dynamic component (the heat-pump component uses the same helper and is unaffected unless it opts in) |

Caveat for B: a user who turned on Grasshopper's "Draw full names" sees `Name` (the attribute)
instead of the label. The hover text names both, so that view still works.

## 2. What each target reads

Verified in PHX (`to_WUFI_XML/xml_schemas.py`, `to_METr_JSON/metr_schemas.py`,
`PHPP/phpp_model/electricity_item.py`) and against METr's own field definitions (`_c3r_.def`).

**The split that makes hints necessary.** WUFI and METr (Phius) read `energy_demand` through
`reference_energy_norm`. PHPP (PHI) ignores both and reads `energy_demand_per_use` for every
appliance row. The honeybee-ph defaults show it: the Phius dishwasher sets
`energy_demand = 269` (kWh/yr) with `energy_demand_per_use = 0`, and the PHI dishwasher sets
`energy_demand = 0` with `energy_demand_per_use = 1.1` (kWh/use).

### Common inputs (slots 2–9)

| Input (attribute) | WUFI-Passive | METr key / UI label | PHPP Electricity |
|---|---|---|---|
| `display_name` | not written | not written | not written. Honeybee model label only |
| `comment` | `Comment` | `Com` / Comment | not read |
| `reference_quantity` | `ReferenceQuantity` | `refQ` / Reference quantity | not read |
| `quantity` | `Quantity` | `quantity` / Quantity | not read (annual rows: demand × quantity) |
| `in_conditioned_space` | `InConditionedSpace` | `inCondSp` / In conditioned space | "inside" column: dishwasher, washer, dryer, freezer; annual rows as a fraction |
| `reference_energy_norm` | `ReferenceEnergyDemandNorm` (index into that device's dropdown) | `refED` / Energy demand (norm) reference. Translated for fridge types; fixed for dishwasher (Year), washer (Year), dryer (CEF) | not read |
| `energy_demand` | `EnergyDemandNorm` | `enDrY` / `enDrD` / `enDY` (the one `refED` points at) | not read for appliances; annual rows (lighting, MEL, custom) use demand × quantity [kWh/yr] |
| `energy_demand_per_use` | `EnergyDemandNormUse` | `enDrU` | **the appliance demand** for dishwasher, washer, dryer, fridge types, cooktop |
| `combined_energy_factor` | `CEF_CombinedEnergyFactor` | `CEFef` / CEF - Combined energy factor | not read |

`reference_quantity` codes (WUFI and METr share them): 1 PH-case occupants, 2 Zone occupants,
3 Bedrooms, 4 PH-case units, 5 User defined, 6 PH-case floor area, 7 Zone floor area, 8 n.a.
METr allows per type: dishwasher, washer, dryer, cooking 1/2/5; fridge types 4/5; Phius MEL 3/5;
interior and exterior lighting 6/7/5; garage lighting 8; custom types 5.

### Meaning of `reference_energy_norm` and `energy_demand` per type

WUFI's norm code is an index into each device's own dropdown, so the same number means different
things.

| `_type` | Norm codes | `energy_demand` unit (WUFI/METr) | `energy_demand_per_use` unit (PHPP) |
|---|---|---|---|
| 1 dishwasher | 2 = Year | kWh/yr | kWh/use |
| 2 clothes washer | 2 = Year | kWh/yr | kWh/use |
| 3 clothes dryer | 2 = CEF (reads `combined_energy_factor`) | not used | kWh/use |
| 4/5/6 fridge, freezer, combo | 1 = Day, 2 = Year | kWh/day or kWh/yr | kWh/day |
| 7 cooking | 1 = Use | kWh/use | kWh/use |
| 13–16 Phius MEL / lighting | n/a | to verify: WUFI/METr may compute these from the reference quantity | annual row, kWh/yr |
| 11/17/18 custom | n/a | kWh/yr per unit; PHX multiplies by `quantity` and writes quantity 1 | annual row, kWh/yr |

### Type-specific inputs

| `_type` | Input | WUFI | METr UI label | PHPP |
|---|---|---|---|---|
| dishwasher | `capacity_type` | `DishwasherCapacityPreselection` | Dishwasher capacity, preselection (1 Standard) | — |
| dishwasher | `capacity` | `DishwasherCapacityInPlace` | Dishwasher capacity, in place settings | — |
| dishwasher, washer | `water_connection` | `Connection` | Water connection (1 DHW, 2 Cold water) | connection selector |
| washer | `capacity` | `CapacityClothesWasher` | Capacity of clothes washer [m³; ft³ in IP] | — |
| washer | `modified_energy_factor` | `MEF_ModifiedEnergyFactor` | MEF - Modified energy factor | — |
| washer | `utilization_factor` | `UtilizationFactor` | (utilization factor) | — |
| dryer | `dryer_type` | `Dryer_Choice` | Type of laundry dryer | dryer selector |
| dryer | `gas_consumption` | `GasConsumption` | Gas consumption | gas row (type 6) |
| dryer | `gas_efficiency_factor` | `EfficiencyFactorGas` | CEF - Combined energy factor (gas) | — |
| dryer | `field_utilization_factor_type` | `FieldUtilizationFactorPreselection` | Field utilization factor, preselection (1 Timer controls) | — |
| dryer | `field_utilization_factor` | `FieldUtilizationFactor` | Field utilization factor | — |
| cooking | `cooktop_type` | `CookingWith` | Cooking with | cooking selector |
| lighting 14–16 | `frac_high_efficiency` | `FractionHightEfficiency` | fraction high efficiency (`fHEff`) | — |

## 3. Proposed labels and hover text (option B)

Labels keep the HBPH snake_case style. Hover text pattern: what it is, unit, valid values,
then which target reads it. Per-type groups override the common slots where the meaning differs
(the existing `copy(inputs_base).update({...})` pattern already supports this).

### Common slots

| Slot | Label | Hover text |
|---|---|---|
| 1 | `display_name` (static node; text via the component docstring, §6) | (str) Name in the Honeybee model only. WUFI, METr and PHPP do not show it; use `comment` for a note that reaches WUFI/METr |
| 2 | `comment` | (str) Note shown in WUFI-Passive and METr ("Comment"). Not used by PHPP |
| 3 | `ref_quantity` | (int) WUFI/METr "Reference quantity": what the demand is scaled by. 1 PH-case occupants, 2 Zone occupants, 3 Bedrooms, 4 PH-case units, 5 User defined, 6 PH-case floor area, 7 Zone floor area. Not used by PHPP. Allowed values for this type: … (per type) |
| 4 | `quantity` | (int) default 1. WUFI/METr "Quantity": number of units; the demand is per unit. Not used by PHPP |
| 5 | `in_conditioned_space` | (bool) default True. WUFI/METr "In conditioned space"; PHPP "inside" column. False when the waste heat should not count as an internal gain |
| 6 | `norm_reference` | (int) WUFI/METr "Energy demand (norm) reference": the period the energy demand is given for. Codes for this type: … (per type). Not used by PHPP |
| 7 | `energy_demand` | per type, see below |
| 8 | `energy_per_use_PHPP` | per type, see below |
| 9 | `CEF` | (float) WUFI/METr "CEF - Combined energy factor". Used by the clothes dryer only |

### Per-type overrides for slots 6–8

| `_type` | `norm_reference` codes | `energy_demand` hover | `energy_per_use_PHPP` hover |
|---|---|---|---|
| dishwasher | 2 Year | (float) kWh/yr per unit, WUFI/METr "Annual energy use rating". Phius default 269 | (float) kWh/use, PHPP only. PHI default 1.1 |
| clothes washer | 2 Year | (float) kWh/yr per unit, WUFI/METr "Annual energy use". Phius default 120 | (float) kWh/use, PHPP only. PHI default 1.1 |
| clothes dryer | 2 CEF (enter `CEF`) | not used (dryer uses `CEF`) | (float) kWh/use, PHPP only. PHI default 3.5 |
| fridge / freezer / combo | 1 Day, 2 Year | (float) kWh per day or per year (match `norm_reference`), per unit; WUFI/METr "Energy demand (rated)" | (float) kWh/day, PHPP only |
| cooking | 1 Use | (float) kWh/use; WUFI/METr "Energy demand (rated)" | (float) kWh/use, PHPP only |
| custom 11/17/18 | n/a | (float) kWh/yr per unit; WUFI/METr get demand × quantity on one line; PHPP annual row | not used |

The type-specific inputs keep their attribute names as labels (they already match the WUFI/METr
field names closely), except `MEF` (washer `modified_energy_factor`) and `gas_CEF` (dryer
`gas_efficiency_factor`), which use the METr names. Their hover text gets the METr label, the unit and the valid codes from
the §2 table, and the two existing typos (`capacity_type`: 'Input "1-Standard" or ',
cooktop `"3-LPG",`) are fixed.

## 3b. `HBPH - Add Process Equipment` (same workflow, static component)

Worker: `honeybee_ph_rhino/gh_compo_io/program/add_process_equip.py`. Its inputs are fixed
nodes defined in the GH component itself, so label and hover changes are delivered as
paste-ready text for the component, then the `.ghuser` export and the `src/` scrape (repo rule 3).

**The trap:** `_num_bedrooms`, `_num_occupants` and `_num_dwellings` only size the Honeybee
`Process` wattage (`annual_avg_wattage`, i.e. the EnergyPlus load). PHX builds the WUFI, METr
and PHPP appliances from the attached PH equipment and never reads the `Process` watts. The
bedroom and occupant counts that WUFI/METr scale by come from the zone (Set Res Occupancy), not
from these inputs. The current hover text says they "determine the total Phius appliance,
lighting, and Misc. Electrical loads", which reads as if they reach WUFI/METr.

| Input | Proposed hover text |
|---|---|
| `_equipment` | (list[str \| PhEquipment]) Equipment from Create PH Equipment, or a type string such as "1-dishwasher" for a Phius default (100 = all Phius defaults, 200 = all PHI defaults). Every item is added to every room input |
| `_num_bedrooms` | (float) Total bedrooms in the rooms input. Sizes the Honeybee/EnergyPlus process load only. WUFI/METr take bedrooms from the zone (Set Res Occupancy) |
| `_num_occupants` | (float) Total occupants in the rooms input. Sizes the Honeybee/EnergyPlus process load only. WUFI/METr take occupants from the zone |
| `_num_dwellings` | (float) default 1. Total dwelling units in the rooms input. Sizes the Honeybee/EnergyPlus process load only. WUFI/METr "PH-case units" come from the model's dwelling count |
| `hb_rooms_` (output) | The rooms with the equipment attached as Honeybee process loads (fixes "with the .... added") |

Two smaller fixes: the docstring typo "Cooktopto", and string inputs build a **Phius** default
even for a PHI project (`phius_default()` for any single type); say so in the hint.

## 4. Found while mapping (not fixed here)

1. **Cooktop code collision (PHX, METr writer).** honeybee-ph `cooktop_type` 3 = LPG; METr
   `tCook` 3 = Electric: Induction (1 Coil, 2 Natural gas, 3 Induction). The METr writer passes
   the code straight through, so an LPG cooktop opens in METr as induction. Separate PHX issue.
2. **PHI freezer default reaches PHPP as 0.** `PhFreezer.phi_default` sets
   `energy_demand = 1.0795` and `energy_demand_per_use = 0`, but PHPP reads `per_use`. To verify
   against a PHPP export before filing.
3. **Fridge "Size" in METr** (`fSize`) is fixed at 2 (15–20 ft³) by PHX; no component input.
4. **Hints that would change canvas coercion** (out of scope unless Ed says): `quantity` uses a
   string hint for an int attribute; `field_utilization_factor_type` uses a float hint for an
   int; `frac_high_efficiency` says "percentage" but the default is the fraction 1.0.
5. METr's dryer list has a 7th type (Ventless: Heat Pump) that honeybee-ph's `PhClothesDryerType`
   does not offer.

## 5. Verification

No tests live in this repo, and the worker imports `GhPython` at module level. The behavior
check is a canvas re-export: Ed re-exports a production model from Grasshopper before and
after, and the appliance entries in the HBJSON must be identical. The UX check is Ed reading
the hover text on each `_type` against the WUFI-Passive and METr screens.

Edits under `honeybee_ph_rhino/` deploy to Rhino immediately (fsdeploy hook) and must stay
IronPython 2.7.

## 6. Implementation (2026-10-24, option B)

**Two repos, because the component script calls the shared helper.** The Create PH Equipment
script runs `ph_gh_component_io.gh_io.setup_component_inputs`, while the worker builds its
`ComponentInput` objects from `honeybee_ph_rhino.gh_io`. So:

- `PH_GH_Component_IO`, branch `feat/component-input-nickname`: `ComponentInput` gains an
  optional `_nickname`; `setup_component_inputs` sets
  `NickName = getattr(item, "nickname", None) or item.name`. The getattr works for input objects
  from either package, and every existing caller is unchanged.
- `honeybee_grasshopper_ph`, branch `feat/elec-equip-input-labels`: the same two lines in
  `honeybee_ph_rhino/gh_io.py` (kept in step with the shared copy), and the rewritten input groups
  in `create_elec_equip.py`. A `_base_inputs()` builder replaces `copy(inputs_base).update(...)`,
  so slots 3 and 6–8 carry per-type text.

The labels need **both** packages updated in Rhino: `ph_gh_component_io` (reads `nickname`) and
`honeybee_ph_rhino` (sets it). With only one, the canvas shows the old attribute-name labels
with the new hover text, and no error. The fsdeploy hook does not list `ph_gh_component_io`, so
on 2026-10-24 the three edited files were copied by hand into
`~/ladybug_tools/python/lib/python3.10/site-packages` (the installed copies matched each repo's
HEAD beforehand).

**No-behavior-change check (done).** Both versions of `create_elec_equip.py` were imported under
CPython with the GH modules stubbed. For all 16 types, every slot has the same `name` (lookup
key), type hint and access mode as before, and the labels are unique within each type. Black and
isort pass. Canvas check (2026-10-24, Ed): a production model re-exported before and after gave identical
appliance entries in the HBJSON.

### Add Process Equipment: paste-ready docstring

GHPython takes the input hover text from the docstring's `Args:` section. Replace the
component's docstring with this, then export the `.ghuser` and run the `src/` scrape:

```python
"""
Add new PH Equipment (Appliances) to the HB-Rooms.
-
Note that ALL of the equipment input will be added to ALL of the Honeybee-Rooms.
This may not always be what you want, and so if you want to add equipment ONLY
to certain rooms (ie: add a Cooktop to ONLY the Kitchen), then break up your
Rooms accordingly and only pass in the relevant Honeybee-Room(s).
-
WUFI-Passive, METr and PHPP read the equipment's own values (set them with the
"Create PH Equipment" component). The '_num_bedrooms', '_num_occupants' and
'_num_dwellings' inputs below only size the Honeybee / EnergyPlus process load.
-
EM October 24, 2026
    Args:
        _equipment: (list[str | PhEquipment]) The equipment to add to the Honeybee-Rooms.
            Input either PH-Equipment from the "Create PH Equipment" component, or a
            type string to add a default: "1-dishwasher", "2-clothes_washer", ...
            "100" adds the full Phius default set, "200" the full PHI default set.
            Note: a single type string always builds the Phius default for that
            type, even on a PHI project. Use "Create PH Equipment" for PHI values.

        _num_bedrooms: (float) The TOTAL number of bedrooms in the Honeybee-Rooms input.
            Used ONLY to size the Honeybee / EnergyPlus process load. WUFI-Passive and
            METr take the bedroom count from the rooms' PH occupancy data instead.

        _num_occupants: (float) The TOTAL number of occupants in the Honeybee-Rooms input.
            Used ONLY to size the Honeybee / EnergyPlus process load. WUFI-Passive and
            METr take the occupant count from the rooms' PH occupancy data instead.

        _num_dwellings: (float) default=1. The TOTAL number of dwelling units in the
            Honeybee-Rooms input ('1' for a single-family home or non-residential).
            Used ONLY to size the Honeybee / EnergyPlus process load. WUFI-Passive and
            METr take the dwelling-unit count from the rooms' PH occupancy data instead.

        _hb_rooms: (list[Room]) The Honeybee-Rooms to add the PH-Equipment to.

    Returns:
        hb_rooms_: The Honeybee-Rooms with the PH-Equipment added as Honeybee
            process loads.
"""
```

### Create PH Equipment: paste-ready docstring (static nodes 0 and 1)

`setup_component_inputs` starts at slot 2, so `_type` and `display_name` are fixed nodes whose
hover text comes from this component's docstring. The current docstring documents
`_display_name`, but the node is named `display_name`, so that text never matches. Replace it:

```python
"""
Create a new detailed Passive House style equipment which can be added to the
honeybee Rooms.
-
The inputs change with the '_type'. Hover over each input to see which WUFI-Passive /
METr field it sets and its unit. WUFI-Passive and METr read 'energy_demand' (in the
period set by 'norm_reference'); PHPP reads 'energy_per_use_PHPP' instead.
-
EM October 24, 2026
    Args:
        _type: (str) Input either -
1-dishwasher,
2-clothes_washer,
3-clothes_dryer,
4-fridge,
5-freezer,
6-fridge_freezer,
7-cooking,
13-PHIUS_MEL,
14-PHIUS_Lighting_Int,
15-PHIUS_Lighting_Ext,
16-PHIUS_Lighting_Garage,
11-Custom_Electric_per_Year,
17-Custom_Electric_Lighting_per_Year,
18-Custom_Electric_MEL_per_Use,
100-PhiUS_Defaults,
200-Phi_Defaults,

        display_name: (str) Optional name in the Honeybee model only. WUFI-Passive,
            METr and PHPP do not show it; use 'comment' for a note that reaches
            WUFI-Passive and METr.

    Returns:
        equipment_: (list[PhEquipment]) New HBPH Electric Equipment which can be added to one
            or more Honeybee-Rooms using the "HBPH - Add Process Equipment" component.
"""
```

The `18-Custom_Electric_MEL_per_Use` label is wrong (type 18 is a per-year custom MEL) but it
lives in the `_type` value-list component too, so it is left for a separate export.

## Draft issue (for review before posting)

> **Create PH Equipment: input labels and hover text don't say what WUFI, METr or PHPP read**
>
> The dynamic Create PH Equipment component labels its inputs with raw attribute names and
> several hover texts are placeholders. Users can't tell which input WUFI-Passive / METr read,
> in what unit, or that PHPP reads `energy_demand_per_use` instead of `energy_demand`.
>
> Scope: relabel the inputs (label separate from the attribute key, so values still bind) and
> rewrite hover text per equipment type with the WUFI/METr field name, unit, valid codes and
> the PHPP difference. No behavior change. Plan: `planning/elec-equip-input-labels.md`.

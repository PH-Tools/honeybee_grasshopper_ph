# Already-exported models carry inflated window-type tables

**Status:** Open — code defect fixed, field impact not yet assessed.
**Opened:** 2026-08-28
**Kind:** Remediation of existing project files. **Not a code change** — nothing in any repo
needs fixing for this.
**Origin:** the confirmed downstream half of
[`aperture-construction-duplication.md`](aperture-construction-duplication.md)
([#59](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/59)).

## What happened

`HBPH - Set Aperture Psi-Installs` gave every aperture its own uuid-suffixed window
construction. `PHX` dedupes window types by identifier
(`from_HBJSON/create_assemblies.py:509`, `if hb_win_const.identifier not in _project.window_types`),
and those identifiers were unique per aperture — so PHX collapsed nothing. The inflated list
passed straight through into the PHPP and WUFI-Passive window-type tables.

On project 2310 that was **939 window types in place of 79**, none of the 860 extras carrying
distinct data.

## Affected range

| | |
|---|---|
| Introduced | `b2c322b` (2026-08-03), first released in **HB-PH v1.25.2** |
| Fixed | PR [#60](https://github.com/PH-Tools/honeybee_grasshopper_ph/pull/60), released in **v1.33.0** (2026-08-26) |
| **Affected** | **v1.25.2 → v1.32.x**, and only models where `HBPH - Set Aperture Psi-Installs` was actually used |

A model exported in that window that never ran the component is unaffected — the component is
the only thing that created the duplicates.

## Why it matters

The energy results are not necessarily wrong: the 860 extras are near-identical, so the
computed U-values and losses should agree. The damage is to the **submission documents** — a
PHPP or WUFI window-type table with 939 rows in place of 79 is not reviewable, and a certifier
reading it cannot tell the model is sound. Anything already submitted in that state is worth
knowing about before the next review round.

## What to do

1. **Scope it.** Which projects were exported to PHPP/WUFI between 2026-08-03 and 2026-08-26
   using `Set Aperture Psi-Installs`? 2310 (AEA Emerson Place) is confirmed affected.
2. **Check each.** Open the PHPP `Windows` worksheet or the WUFI window-type list and compare
   the row count against the number of distinct window types the model actually has.
3. **Remediate** by re-exporting from HB-PH ≥ v1.33.0. No model edits are needed — the same
   Rhino definition now produces the collapsed list.
4. **Flag to the certifier** only where an affected table was already submitted.

## Verification that the fix holds

Recorded in [`aperture-construction-duplication.md`](aperture-construction-duplication.md)
§"Verification result": 948 apertures over 79 types now produce exactly 79 constructions,
with no cross-contamination between apertures carrying different psi values.

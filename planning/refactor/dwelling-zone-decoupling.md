# Plan: Decouple "Dwelling" from `Room.zone` (GH components)

**Status:** Code changes implemented (2026-07-21). Remaining: manual component retirement
(§8), install to `ladybug_tools/`, and the 2613 re-run.
**Date:** 2026-07-21
**Author:** Ed May + Claude
**Kind:** Cross-repo refactor. This repo holds the **root cause** — the only two references
to `Room.zone` in the entire toolkit both live here.

**Companion docs (same slug in each repo):**
- `honeybee_ph/planning/refactor/dwelling-zone-decoupling.md` — **primary**; owns the shared
  helper, the full evidence trail, and the design decision. Read it first.
- `PHX/planning/refactor/dwelling-zone-decoupling.md` — downstream consumer

**Blocked on:** `honeybee_ph` **and** `PHX` landing first. Order (decided 2026-07-21):

```
1. honeybee_ph  →  deploy/install  →  2. PHX  →  deploy/install  →  3. honeybee_grasshopper_ph (this repo)
```

This repo lands **last**: PHX validates the shared helper against golden `NumberUnits`
values while these components are still untouched, so any defect found here is unambiguously
a component defect, not a helper defect. Each repo must be installed before the next begins
(see §4 — the install step is what makes a change visible in Rhino).

---

## 1. Problem

`HBPH - Set Dwelling` stamps the dwelling name onto `honeybee.room.Room.zone`, and
`HBPH - Set Residential Program` reads it back to group Rooms into dwellings. That worked
while `Room.zone` was inert. It no longer is: current `honeybee-energy` reads `Room.zone` as
a real EnergyPlus instruction and merges every Room sharing a value into **one thermal
Zone** containing multiple `Space` objects.

So tagging a house's six floor-Rooms as one *dwelling* now also merges them into one
*thermal zone* — one air node, one HVAC system — which is a physics change nobody requested.

Observed on 2613 Ayers (E+ 25.1 / hbjson 2.1.2): 1 `Zone` + 6 `Space` objects in the IDF,
and **1** `ZoneHVAC:IdealLoadsAirSystem` where the model authored six — five silently
dropped in translation. `HB Validate Model` flags it: *"The model has the following invalid
zones served by different HVAC systems."* The same definition under E+ 23.2 / hbjson 1.58.6
(2514 MESH) produced six Zones correctly. See the primary doc §2 for the full trail.

### The two references

| File | Line | Direction |
|---|---|---|
| `honeybee_ph_rhino/gh_compo_io/program/set_dwelling.py` | 113 | `dup_room.zone = dwelling_name` — **write** |
| `honeybee_ph_rhino/gh_compo_io/program/set_res_program.py` | 79 | `room_groups[hb_room.zone]` — **read** |

A full sweep of this repo and `honeybee_REVIVE_grasshopper` — all `.py`, both `.ghx`
installers, and all 138 compiled `.ghuser` (decompressed; see primary doc §2 for the
double-DEFLATE format note, a naive grep false-negatives on every one) — found **no other
reference**. `honeybee_REVIVE_grasshopper` has zero.

---

## 2. Two findings that shape the fix

### 2.1 Two parallel residential paths, for two different destinations

| Component | Backend | `_num_dwellings` source | Destination |
|---|---|---|---|
| `HBPH - Set Residential Program` | `GHCompo_CreatePHProgramSingleFamilyHome` | **grouped by `Room.zone`** | E+ attributes for hourly sim (REVIVE) |
| `HBPH - Add Process Equipment` | `GHCompo_AddProcessEquip` | direct user input | WUFI / PHPP static export |

Only the first reads `zone`. Both are live; they are not redundant with each other.

`Set Residential Program` ships in **two** user objects (both instantiating the same backend
class) — see §8, where the older duplicate is retired.

### 2.2 On 2613 specifically, `Set Dwelling`'s only surviving effect was the damage

Forensics on `2613_Ayers_Home_260720.hbjson`:

- All six Rooms share one `ProgramType` — `rv2024_Residence_Resilience`, applied by
  `HB-REVIVE - Set Resiliency Program`.
- **No room-level `people` object on any Room** (`people = None` throughout).
- **Zero `HBPH_SFH_*` load objects** — `Set Residential Program` left no trace.
- The REVIVE program's own People carries a fresh `PhDwellings(num_dwellings=0)`, not the
  object `Set Dwelling` built.

So on this model the REVIVE program assignment **replaced** whatever People/`PhDwellings`
`Set Dwelling` attached. Its dwelling identity is gone from the final model entirely —
and `Room.zone` is the **only surviving artifact of that component**, which is precisely the
one that collapsed the thermal zoning.

This does not narrow the fix (the `zone` read path is live in the REVIVE prep workflow and
must still be corrected), but it explains why 2613's *loads* were fine while its *zoning* was
not, and it is a clean illustration of why dwelling identity does not belong on `zone`.

### 2.3 REVIVE components are fully insulated

Both dwelling-aware REVIVE components take totals as explicit inputs —
`_total_number_dwellings` / `_total_icfa` / `_total_number_bedrooms` on
`HB-REVIVE - Create REVIVE Residential Program`, and `_total_num_dwelling_units` on
`HB-REVIVE - Set Resiliency Program`. No grouping, no `zone`, no `PhDwellings` traversal.

Consequence: on 2613 the REVIVE **loads were correct**; only the thermal zoning was wrong.
No REVIVE component needs to change.

---

## 3. Changes

### 3.1 `set_dwelling.py` — stop writing `Room.zone`

Delete line 113 (`dup_room.zone = dwelling_name`).

With `zone` unset, `Room.zone` falls back to `Room.identifier`
(`honeybee/room.py`: `if self._zone is None: return self._identifier`), yielding one E+ Zone
per Room, one `IdealAirSystem` per Zone, and a model that validates.

Dwelling identity is unaffected — the component already builds a `PhDwellings` object at
lines 101-102 and attaches it to every Room's `People` at line 120. That has always been the
real carrier; the `zone` write was redundant.

**Do not** replace it with an explicit `dup_room.zone = dup_room.identifier`. That would
clobber any deliberate upstream zone grouping (e.g. a user's own `HB Set Zone`). Leaving
`_zone` as `None` preserves the distinction between "unset" and "deliberately set".

### 3.2 `set_res_program.py` — group by dwelling identity

Replace `_group_rooms_by_dwellings()` (lines 74-81) with a call to the shared helper:

```python
from honeybee_energy_ph.dwellings import group_rooms_by_dwelling
```

Delete the local implementation and the now-unused `defaultdict` import if nothing else
needs it. Keep the call site in `run()` (line 465) unchanged in shape.

The helper's `PhDwellings.default()` guard is what preserves correct behavior for Rooms that
never went through *Set Dwelling* — see primary doc §4.1.

### 3.3 `set_res_occupancy.py` — group by dwelling identity (added 2026-07-21)

**Found during implementation:** there were **four** implementations of dwelling grouping,
not three. `set_res_occupancy.py:66` had its own `_group_rooms_by_dwellings()`. The earlier
sweep missed it because it greps clean for `.zone` — it already grouped by
`dwellings.identifier`, i.e. the *correct* mechanism, but without the default-singleton or
`None` guards.

Replaced with `group_rooms_by_dwelling()`. The consequence depends on component order:

| Scenario | Before | After |
|---|---|---|
| MF, `Set Dwelling` first (the documented MF order) | correct | **identical** |
| SFH, `Set Dwelling` first | correct | **identical** |
| SFH, `Set Occupancy` first (un-tagged Rooms) | all Rooms pooled into one group | each Room groups alone |
| MF, `Set Occupancy` first (wrong order) | **all apartments pooled into one** | each Room alone — wrong, but not silently merged |

Only the un-tagged case changes. **Total model occupancy is identical in every case** —
`set_people_per_m2()` spreads a group's total PH-occupancy over that group's total floor
area, so pooling only moves occupants between Rooms, never adds or removes them.

Why the change is a correction rather than a regression: pooling gave every Room in the
group the same `people_per_area`, so a crawlspace entered with **0** people still received
occupants. That was invisible while `Room.zone` merged everything into one E+ Zone — E+
summed the loads into a single air node either way. Now that each Room is its own Zone
(§3.1), the distribution drives per-zone results directly. It is the mechanism behind the
2613 anomaly: `0.0222 ppl/m²` applied uniformly across 876 m², crawlspace included.

Worked example (6 Rooms, 25 m² each; 3 people entered on each of two Rooms):

| Room | input ppl | pooled (before) | per-Room (after) |
|---|---|---|---|
| 00_CRAWLSPACE | 0.0 | 1.000 | **0.000** |
| 01_SOUTH | 3.0 | 1.000 | **3.000** |
| 02_SOUTH | 3.0 | 1.000 | **3.000** |
| _(3 others @ 0.0)_ | 0.0 | 1.000 each | **0.000** each |
| **TOTAL** | 6.0 | 6.000 | 6.000 |

**Accepted risk:** every existing SFH model that ran `Set Occupancy` before `Set Dwelling`
will see its occupancy *distribution* shift. Whole-building totals are unchanged, but
per-zone hourly results will move. Decided acceptable (Ed, 2026-07-21) because the new
behavior honors the per-Room inputs the component documents.

Backend-only — no `.ghuser` change (see §4). An optional docstring clarification that
`_num_people` is genuinely per-Room can be folded into the next manual GH session.

### 3.4 Do NOT add an `HB Set Zone` workaround

Rejected. Bolting `HB Set Zone` downstream leaves the components authoring a knowingly
invalid model and relies on every user remembering the fix. The components should not lie
about thermal structure in the first place.

### 3.5 Deferred: `_merge_zones_` input

Not in scope. For large Phius MF work, one Zone per *dwelling unit* is a legitimate runtime
optimization — but it must be an explicit opt-in that **also** consolidates the HVAC (the
current failure mode is precisely that zones merged while HVAC did not). Revisit only if MF
runtimes actually hurt.

---

## 4. Deployment model — no `.ghuser` rebuild required

**This refactor requires no manual Grasshopper work.** Establishing that took some digging,
so it is recorded here.

### How a component actually resolves

A `.ghuser` embeds only the component **front-end** script, which is a pure delegator. The
whole body of `HBPH - Set Dwelling` (mirrored in plain text at
`honeybee_grasshopper_ph/src/HBPH - Set Dwelling.py`) is:

```python
from honeybee_ph_rhino import gh_compo_io          # package __init__ re-exports
...
gh_compo_interface = gh_compo_io.GHCompo_SetDwelling(IGH, _num_dwellings_, _hb_rooms)
hb_rooms_ = gh_compo_interface.run()
```

All logic lives in the backend package `honeybee_ph_rhino/gh_compo_io/`, imported at runtime.
Both changes in §3 are backend-only and alter **no** component input, output, name, or
version message. The `.ghuser` files therefore do not change.

Confirmed by the sweep: none of the 122 extracted `.ghuser` scripts contain a `.zone`
reference — the attribute is touched only in the backend.

### Where the backend actually loads from

Editing the Dropbox repo does **not** affect Rhino. The runtime imports from:

```
/Users/em/ladybug_tools/python/lib/python3.10/site-packages/honeybee_ph_rhino/
```

These are real installed directories (not symlinks to the repo) — `honeybee_ph-1.33.28.dist-info`.
**So there is an install/sync step between editing and testing.** This was missing from the
first draft of this plan; it is the step that makes changes visible in Grasshopper.

### `.ghuser` round-trip, for reference

`.ghuser` files can only be authored *in* Grasshopper. The repo copies under
`honeybee_grasshopper_ph/user_objects/` are **distribution artifacts**; the production
versions live in the live Rhino UserObjects folder (108 HBPH components):

```
~/Library/Application Support/McNeel/Rhinoceros/8.0/Plug-ins/Grasshopper (b45a29b1-…)/UserObjects/honeybee_grasshopper_ph/
```

`src/__HBPH__Util_Update_GHCompos.py` is run *inside* Grasshopper to collect them: it
instantiates every live component onto the canvas, copies the `.ghuser` files into the repo,
and writes each component's `obj.Code` to `src/*.py`. That `src/` mirror is the readable
source of truth for front-end code — 96 files, and the reason a plain `.py` grep was
sufficient all along.

**Only needed if a component's inputs/outputs change.** Not the case here.

---

## 5. Verification

No unit tests are possible here: `ph_gh_component_io.gh_io` raises
`ImportError: Failed to import System` outside .NET (verified — the import is unguarded), so
these modules cannot be imported by CPython pytest. **This is the reason the grouping logic
moves to `honeybee_energy_ph`** — see primary doc §4.5, where it does get real coverage.

Verification here is end-to-end:

1. **Install** the updated `honeybee_ph` + `honeybee_ph_rhino` into
   `ladybug_tools/python/lib/python3.10/site-packages/` and restart Rhino. Nothing below
   tests anything until this is done.
2. **PHX smoke test** — `PHX/tests/_source_gh/hbph_test_models.gh`. Confirm `NumberUnits` in
   the emitted WUFI XML is **unchanged** for both an SFH case and an MF case. This is the
   critical regression gate: if dwelling grouping breaks, unit counts move.
3. **SFH regression via `HBPH - Set Residential Program`** (not the `Add Process Equipment`
   path): a 6-Room house must still resolve to **one** dwelling — same iCFA, occupancy, and
   appliance loads as before the change.
4. **Rerun 2613 Ayers REVIVE** and confirm:
   - `HB Validate Model` → clean
   - `eplusout.sql` `Zones` table → **6** rows, not 1
   - `in.idf` → **6** `ZoneHVAC:IdealLoadsAirSystem`, **0** `Space` objects
   - `summer_heat_index.html` / `winter_ventilation.html` → 6 series, not 1

### Reference commands

```bash
sqlite3 eplusout.sql "SELECT ZoneIndex, ZoneName FROM Zones;"
grep -c "^ZoneHVAC:IdealLoadsAirSystem," in.idf
grep -c "^Space," in.idf
```

### 5.5 Result: fix proven via the real honeybee-energy IDF writer (2026-07-21)

Six Rooms built exactly as `HBPH - Set Dwelling` builds them (shared `PhDwellings`), then
translated with `model.to.idf()`:

| | E+ `Zone` objects | `Space` objects | distinct IdealAirSystems | dwelling groups |
|---|---|---|---|---|
| OLD (`Room.zone` written) | **1** | **6** | 1 | 1 |
| NEW (`Room.zone` not written) | **6** | **0** | 6 | 1 |

The OLD row reproduces the 2613 model exactly (1 Zone + 6 Spaces), confirming the diagnosis
end-to-end. The NEW row is the repaired state, with dwelling identity intact.

Caveat: the standalone test Model emits `0` `ZoneHVAC:IdealLoadsAirSystem` in both IDFs — a
bare Model with no setpoints does not write ideal-loads objects. The meaningful signal is
the six distinct room-level systems, which the merged case collapsed to one.

---

## 6. Definition of Done

- [x] `honeybee_ph` helper shipped and importable — **honeybee-ph 1.33.30**
- [x] `PHX` landed and released — **PHX 1.56.63**
- [x] `requirements.txt` bumped: `honeybee-ph>=1.33.30`, `PHX>=1.56.63`
      (`hbph_installer.ghx` carries its own pins — those are updated by GitHub Actions on
      release, so pre-release drift between the two files is expected, not a gap.)
- [x] `set_dwelling.py` — `Room.zone` write removed (+ comment explaining why it must not return)
- [x] `set_res_program.py` delegates to the shared helper; unused `defaultdict` import dropped
- [x] `set_res_occupancy.py` delegates to the shared helper (§3.3, option 2)
- [x] All four dwelling-grouping implementations consolidated onto one tested function
- [x] Verified 2.7-safe (no f-strings / annotations), `py_compile` OK, `black` + `ruff` clean
- [x] End-to-end proof via the real honeybee-energy IDF writer (§5.5)
- [ ] `HBPH - Create Program - Single Family Home` retired (manual GH step, Ed — §8)
- [ ] Updated packages **installed** to `ladybug_tools/.../site-packages/`, Rhino restarted
- [ ] PHX smoke test: `NumberUnits` unchanged, SFH + MF
- [ ] 2613 REVIVE rerun clean per §5.4
- [ ] `HBPH - Create Program - Single Family Home` retired per §8 (manual GH step, Ed)
- [ ] `context/` updated to state that `Room.zone` is not a Honeybee-PH tagging surface
- [ ] Row updated in `planning/STATUS.md`
- [ ] On completion: fold into `context/`, move to `planning/archive/dwelling-zone-decoupling/`

No `.ghuser` rebuild for the `set_dwelling` / `set_res_program` changes — see §4. The only
manual Grasshopper work is the component retirement in §8.

---

## 7. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| SFH grouping breaks → per-Room iCFA/occupancy instead of per-house | **High** | §5.3 regression; helper's default-singleton guard |
| **Testing the repo instead of the install** — edits invisible in Rhino, "no change" misread as "no effect" | **High** | §4; install + restart before any GH verification |
| Users' saved definitions carry stale `zone` in old `.hbjson` | Low | GH regenerates every solve; only affects re-opened archives |
| Existing Phius-Residential models on the new toolchain are already wrong | **High** | Sweep active projects' `.hbjson` for Rooms sharing a `zone`; re-run affected models |

---

## 8. Adjacent issue folded into scope: the duplicate SFH component

`HBPH - Create Program - Single Family Home` and `HBPH - Set Residential Program` are
near-identical duplicates:

- both instantiate the **same** backend class, `GHCompo_CreatePHProgramSingleFamilyHome`
- identical docstrings, identical `_hb_rooms` input, identical `hb_rooms_` output
- dated `EM January 27, 2025` vs `EM January 28, 2025`

The Jan-27 `Create Program - Single Family Home` is the **older, superseded** one. It also
carries a **stale import**: its front-end does
`from honeybee_ph_rhino.gh_compo_io.program import create_single_family as gh_compo_io`, but
`create_single_family.py` does not exist. That line sits inside the `if DEV:` block, so it is
dormant at `dev=False` and only raises when dev mode is enabled.

**Decision (2026-07-21):** retire `HBPH - Create Program - Single Family Home`; keep
`HBPH - Set Residential Program` as canonical. **Ed removes the old component manually in
Grasshopper.** Repo-side follow-up: drop its `.ghuser` and `src/*.py` from distribution and
de-register it, following the existing `gh_compo_io/program/_deprecated_/` convention.

Note this component is **not** redundant with `HBPH - Add Process Equipment` — see §2.1.
They serve different destinations (hourly E+ sim vs static WUFI/PHPP export) and both stay.

### `.ghuser` handoff convention

Where a change genuinely requires Grasshopper (component removal, IO changes, docstring
edits), the edits are **written up here and handed to Ed to apply manually in Grasshopper**,
then collected via `src/__HBPH__Util_Update_GHCompos.py`. Claude does not author `.ghuser`
files. For this refactor the only such item is the component retirement above; the
`set_dwelling` / `set_res_program` changes are backend-only and need no GH work.

---

## 9. Non-issue, recorded to stop it being re-raised

An earlier draft claimed `shw/create_heater.py` and `shw/create_system.py` contain f-strings
that would break IronPython 2.7. **That was wrong** — a naive `grep 'f"'` false-matched the
`f"` inside `loss_coeff")` and `diff",`. A correct word-boundary check
(`grep -rnE '(^|[^A-Za-z0-9_])f["'"'"']'`) finds **zero** f-strings and **zero** return
annotations anywhere in `honeybee_ph_rhino/gh_compo_io/`.

The only py3 syntax in the package is in `honeybee_ph_rhino/scripts/run_openph_with_hbjson_file.py`,
which is a standalone CLI script invoked by subprocess under CPython — never imported by a GH
component. It is correct as-is.

**The IronPython 2.7 constraint is intact and unviolated. Nothing to clean up here.**

---

## 10. Blast radius beyond this refactor

Any Phius-Residential model built with *HBPH - Set Dwelling* on hbjson ≥ 2.x / E+ ≥ 24.x has
merged thermal zones and dropped HVAC systems. This is not REVIVE-specific — it affects
normal E+ runs too. Worth a sweep of active project `.hbjson` files:

```python
import json
d = json.load(open(path))
zones = {r.get("zone") for r in d["rooms"]}
# len(zones) < len(d["rooms"])  ->  affected
```

PHPP/WUFI/METr outputs are **not** affected — PHX never reads `Room.zone` (see the PHX
companion doc).

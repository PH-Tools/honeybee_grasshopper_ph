# Already-exported models carry inflated window-type tables

**Status:** Remediation complete (2026-08-26) — all four phases done. Awaiting only:
(a) Ed's confirmation of which .mwp went to the certifier for Round 5, and (b) merge of the
PHX guard branch (`fix/phpp-components-stale-rows`, [PHX #99](https://github.com/PH-Tools/PHX/issues/99)).
Code defect itself fixed in v1.33.0. Archive this packet once (a) and (b) close.
**Opened:** 2026-08-28
**Kind:** Remediation of existing project files, plus one optional PHX hardening change
(Phase 4). Nothing in this repo needs code changes.
**Origin:** the confirmed downstream half of
[`aperture-construction-duplication.md`](../archive/aperture-construction-duplication.md)
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

## Scoping result (2026-08-26) — full-Dropbox scan

A read-only scan of every `.hbjson` under `~/Dropbox` (excluding `bldgtyp-00` repo fixtures;
422 files parsed) flagged **only project 2310**. The other projects active in the window
(2524 Linde, 2615 Tano Rd, 2613 Ayers, 2242 Arverne D, 2611 Whippoorwill, 2616 39 15th St)
all show construction-count == distinct display-name count.

**Detectors** (both confirmed against 2310's known-good and known-bad files):

- *HBJSON:* window-construction count > distinct `display_name` count, plus identifiers
  matching the uuid arithmetic (`<con_id>_<con_id>_<hex8>_<hex8>`).
- *WUFI XML:* `grep -c '<WindowType index='` against the model's expected type count.
- *WUFI .mwp (binary):* `strings <file> | grep -cE '_[0-9a-f]{8}_[0-9a-f]{8}$'` — 939 hits on
  the one affected file, 0 on every clean file. Works despite the proprietary format because
  construction identifiers are stored as plain strings.

**Affected artifacts — the complete set, all in `2310 {AEA} Emerson Place/13_WUFI/`:**

| artifact | count | state |
|---|---|---|
| `_hbjson/…_260811.hbjson`, `…_260812.hbjson`, `…_260812_2.hbjson` | 3 | 939 window constructions / 79 names |
| `_xml/…_260811*.xml` (7), `…_260812_8_12_*.xml` (11), `…_260812_2_8_12_12_45_8.xml` (1) | 19 | 939 WUFI window types |
| `5 Round/…_260811.mwp` | 1 | 939 signature hits |

**Everything else is clean**, including: `_xml/…_260812.xml` and `…_260812_2.xml` (79 types —
exported from the clean machine the same day), `…_260812_3*` (158), `…_260814*` (158),
`…_260817*` (170), `5 Round/…_260812.mwp`, `…_260812_2.mwp`, `…_260817.mwp` (0 hits each),
and the current root-level `…_260818.mwp` and `…_260826.mwp` (0 hits each). The buggy window
on this project was effectively 2026-08-11 through the morning of 2026-08-12.

**Erratum to the archived evidence table** (`archive/aperture-construction-duplication.md`):
on disk today, `…_260812_2.hbjson` (14.1 MB, mtime 13:44) is a *buggy* twin of
`…_260812.hbjson` — the clean 79-construction comparator is `…_260812_3.hbjson` (12.5 MB,
21:04). The `_2` hbjson was evidently overwritten by a buggy-machine export after the A/B was
recorded. (The *`.mwp`* named `_260812_2` is clean — the name collision is coincidental.)

**Consequence: no re-export is needed.** Clean exports already exist and post-date the buggy
ones. The one open question only Ed can answer: **which .mwp went to the certifier for
Round 5?** If it was `260811.mwp`, flag it and supply the clean 260817+ model at the next
round; anything else and nothing inflated ever left the office.

## Cautions — how remediation itself could cause new problems

1. **Never re-export into a PHPP workbook that previously received the inflated list.**
   `PHX/PHPP/sheet_io/io_components.py` `write_glazings()`/`write_frames()` write from the
   section's first entry row and never clear below the written rows — 79 types over a
   939-row table leaves ~860 stale frame/glazing rows and the sheet stays unreviewable.
   Export into a fresh workbook, or clear the Components glazing/frame sections (and Windows
   rows) first. Phase 4 adds a guard for this in PHX.
2. **Auto-clearing is just as dangerous as not clearing.** Users legitimately hand-add
   frame/glazing rows below the PHX-written block during cert rounds. Any PHX-side clearing
   must be opt-in, never default — otherwise a re-export silently destroys manual work.
3. **WUFI window-type counts legitimately double post-fix.** The PHX per-edge psi-install
   synthesis emits psi-variants at WUFI/METr export time: 2310's clean exports show 158
   (= 2 × 79) and 170 (= 2 × 85) types. Expected by design — do not read it as a recurrence.
4. **A ≥ v1.33.0 re-export is not a like-for-like diff against a v1.25.x export.** The range
   also carries the Phius-MF `reference_quantity` fix (#69), the IHG-type input changes
   (#67/#68), and the `Space.from_room` rework (#61) — diff old vs new output before handing
   a "windows-only" change narrative to a certifier.
5. **Do not move or rename any file in the 2310 folders.** Round 5 is live; markers only.

## Remediation phases

Branch: `fix/bug59-field-remediation` (this repo, docs + scanner). Phase 4 gets its own
branch in `PHX`. Phases 1-3 touch no repo code; Phase 4 is the only code change and follows
the spec → codex build → Claude review model.

### Phase 1 — Durable detector script — ✅ DONE (2026-08-26)

The session scanner proved the detectors; make it re-runnable and self-documenting.

- [x] Added `planning/bugs/scan_inflated_window_types.py` (PEP 723 header, `uv run`, CPython —
  repo tooling, not deployed Rhino code, so the IronPython rules do not apply). Scans a tree
  for `.hbjson` (construction-count + uuid-signature detector), `.xml` (ElementTree walk of
  `WindowType/Name`, gated on a `<WUFIplusProject>` header sniff), and `.mwp` (ASCII-run
  signature) files. Default root `~/Dropbox`; `--root`, `--all`, `--exclude` flags; exit 1
  when anything is flagged. Excluded subtrees are pruned during the walk, not filtered after.
- [x] Verified: reproduces exactly the affected-artifact table above — 2665 files scanned,
  **23 AFFECTED** (3 hbjson + 19 xml + 1 mwp), 1953 clean, 640 non-WUFI xml skipped, 49
  unreadable (non-JSON OpenStudio `.hbjson` artifacts, labeled rather than silently skipped).
  Four-angle cleanup review applied (ElementTree over regex, walk pruning, single print loop);
  re-run after refactor produced the identical 23.

### Phase 2 — Quarantine markers in the 2310 project folder — ✅ DONE (2026-08-26)

Non-destructive. One marker file, no moves, no renames (Caution 5).

- [x] Wrote `~/Dropbox/bldgtyp/2310 {AEA} Emerson Place/13_WUFI/_BUG59-affected-files.md`
  listing the 23 affected files by folder: do not build the next round from these; use
  `…_260817` or later; energy results near-identical but the table is not reviewable. Written
  in the client-facing register (no em-dashes, plain sentences); includes the two handoff
  notes (post-fix type-count doubling is expected; the Round-5 submission question).
- [x] Verified: file exists, lists all 23 artifacts (3 hbjson + 19 xml + 1 mwp), names the
  clean replacements (`…_260817`+, current `…_260818.mwp` / `…_260826.mwp`).

### Phase 3 — Documentation corrections — ✅ DONE except final status flip (2026-08-26)

- [x] Appended the dated correction note to
  `planning/archive/aperture-construction-duplication.md` §Evidence (original table left as
  recorded; on-disk clean comparator is `…_260812_3.hbjson`).
- [x] Updated `planning/STATUS.md` and `planning/bugs/README.md` rows: scoped, single
  project, remediation underway; remaining items named.
- [x] Also repaired the archive-move link rot: both archived docs' references to this file
  now point at `../bugs/…` (they broke when the packet moved to `archive/`).
- [ ] Flip this doc's Status line to "Remediation complete — awaiting Ed's confirmation of
  the Round 5 submission vintage" once Phase 4 is done.
- [x] Verify: links resolve, statuses consistent across the three documents.

### Phase 4 — PHX guard against stale Components rows — ✅ DONE (2026-08-26)

Repo: `PHX`, branch `fix/phpp-components-stale-rows` (commit `1422eda` + STATUS row).
Tracked as [PHX #99](https://github.com/PH-Tools/PHX/issues/99). Spec by Claude, built by
codex/gpt-5.5, reviewed line-by-line by Claude (shape attribute names and row-model column
lists verified against `shape_model.py` / `component_frame.py` / `component_vent.py`).

- [x] The three writers block-read the section tail after writing (with the xlwings-#1924
  length-guard + per-cell fallback) and warn once per section via `xl.output`, naming
  worksheet, section, and stale rows.
- [x] Keyword-only `clear_stale: bool = False` blanks only the input columns each section's
  row model writes, batched by contiguous row/column groups; formula columns never touched.
  Not plumbed into `PHPPConnection`.
- [x] Tests: `tests/test_PHPP/test_sheet_io/test_io_components_stale_rows.py` — real
  `EN_10_6` shape + fake-XL framework; warn/clear/clean-sheet cases for all three sections.
- [x] Verified: full PHX suite green (1086 passed, 3 skipped) including the
  `tests/test_xl_replay` golden-state invariant; black clean.
- Known limitation (accepted): detection ends at `section_last_entry_row`, which is
  contiguous-fill based — a stale block separated from the written block by hand-cleared
  rows is not seen. The actual hazard (a shrinking export leaves a contiguous tail) is
  fully covered.

## Out of scope (recorded, not planned)

- An export-time inflation warning in `PHX/from_HBJSON/create_assemblies.py` (window-type
  count ≫ distinct display names). The GH-side mechanism that caused inflation is deleted;
  a heuristic warning would mostly fire on false positives. Revisit only if the pattern
  recurs from another source.
- Deleting or archiving the 23 affected files. Ed's call, after Round 5 closes.

## Verification that the fix holds

Recorded in
[`aperture-construction-duplication.md`](../archive/aperture-construction-duplication.md)
§"Verification result": 948 apertures over 79 types now produce exactly 79 constructions,
with no cross-contamination between apertures carrying different psi values.

# Refactor: Aperture-level Psi-Install — GH components

**Status:** **Effectively complete (2026-08-28).** Code shipped and released; the
follow-on PHN client shipped too. One confirmatory check is outstanding — see below.
Upstream merged: honeybee_ph PR #87, PHX PR #80. GH components merged in PR #60,
released in v1.33.0.
**Follow-on — DONE (2026-08-28).** The PHN per-edge client shipped:
`HBPH+ - PH-Nav Get Apertures` now parses route 3's `installs` block and emits an
`install_types_` collection (`honeybee_grasshopper_ph_plus` PR #10, archived at
`honeybee_grasshopper_ph_plus/planning/archive/phn-psi-install-per-edge/`). Consuming
it required teaching **this** repo's `HBPH - Set Aperture Psi-Installs` a keyed-
collection input alongside its DataTree (PR #71) — branch-index matching cannot
express per-window values against a flat aperture list. Confirmed end-to-end through
a METr export placing Psi=0 on mulled edges.
**Remaining: none.** Steps 1-3 of §4 DONE 2026-08-12. Release-pin bumps DONE
(`requirements.txt` pins honeybee-ph>=1.33.56, PHX>=1.56.95 — both past the PR-#87 /
PR-#80 releases). #59 and honeybee_ph #51 both CLOSED. §4 step 4's construction-count
check was run 2026-08-28 at 2310's scale against the current component — 948 apertures
over 79 types produced exactly **79** constructions, with no cross-contamination
between apertures carrying different psi values and stable identifiers across repeated
runs. Evidence in `aperture-construction-duplication.md` §"Verification result".
A literal 2310 re-export remains available as confirmation but is not load-bearing:
`duplicate_aperture_construction()` is absent from the codebase.
**One field consequence is tracked separately** and is NOT part of this refactor:
models exported with v1.25.2 - v1.32.x carry inflated window-type tables into
PHPP/WUFI — `exported-models-inflated-window-types/exported-models-inflated-window-types.md`.
**Date:** 2026-08-12
**Author:** Ed May + Claude
**Kind:** Cross-repo refactor. This repo holds the user-facing components **and the root cause
of bug #59** — the per-aperture construction-duplication mechanism, which this refactor deletes.
**Resolves:** [#59](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/59)
(`aperture-construction-duplication.md`) — by removal of the mechanism, not by patching it.

**Companion docs (same slug in each repo):**
- `honeybee_ph/planning/archive/aperture-psi-install/` — **primary** (complete, archived): data model, resolver, issue #51
- `PHX/planning/archive/aperture-psi-install/` — (complete, archived) PHPP per-row write, WUFI/METr variant synthesis
- `ph-navigator-v2/planning/features_v1.1/aperture-psi-install/upstream-alignment.md`
- `honeybee_grasshopper_ph_plus/planning/archive/phn-psi-install-per-edge/` — (complete, archived) the PHN per-edge client and this repo's keyed-collection input

---

## 1. Summary of the upstream design

Ψ-install becomes its own type: `PhApertureInstallType` (name + Ψ value + source note),
assigned per-edge (top/right/bottom/left) on `AperturePhProperties`. `None` = inherit the
construction frame element's value. Window constructions are never duplicated for psi-install
again — PHX handles the WUFI/METr type-splitting at export time.

## 2. Component inventory — what changes

### 2.1 NEW: `HBPH - Create Aperture Install Type`

Worker: `honeybee_ph_rhino/gh_compo_io/apertures/win_create_install_type.py`.
Inputs: `_display_name`, `_psi_install` (unit-aware string, `W/mK` default — reuse the
`ph_units` parse/convert pattern from the existing psi components), `_source` (optional note).
Output: `PhApertureInstallType`. Registry entry in `_component_info_.py` (hard rule 2).

### 2.2 REWRITE: `HBPH - Set Aperture Psi-Installs`

Worker: `honeybee_ph_rhino/gh_compo_io/apertures/win_set_psi_install_values.py`.

Today (v1.25.2+): duplicates the aperture, **duplicates the whole window construction** with a
uuid-suffixed identifier (`duplicate_aperture_construction()`, `:81-111`), duplicates the PH
frame, and mutates `psi_install` on the copy. This is bug #59: constructions grow with aperture
count (939 vs 79 on project 2310).

After: the component duplicates the aperture and sets the per-edge install-type slots on
`aperture.properties.ph`. **It never touches the construction.**

- Inputs: `_apertures` (tree), `_install_types` (tree; per-branch list of up to four values in
  t/r/b/l order, following the existing branch/element fallback pattern).
- Accept either `PhApertureInstallType` objects **or** bare numbers/strings: bare values are
  auto-wrapped into anonymous install types with **content-keyed** identifiers (e.g.
  `PhApertureInstallType_0.0400` after unit-normalization) so repeated runs and repeated values
  are stable and dedupe downstream. No uuids anywhere.
- `duplicate_aperture_construction()` and its `clean_and_id_ep_string` identifier arithmetic
  are **deleted**. The isolation that `b2c322b` fixed (shared-construction mutation) is
  preserved structurally: the component no longer mutates any shared object — it only writes
  aperture-instance properties on a duplicated aperture.
- Keep helpers pure/importable (no `Grasshopper` imports needed for the logic once construction
  handling is gone) — the worker logic worth testing lives upstream in `honeybee_ph` anyway
  (hard rule 6: no tests in this repo).

### 2.3 KEEP: `HBPH - Set HB-Construction Psi-Installs`

`win_set_hb_const_psi_install_values.py` — stays as the **type-default** path. It duplicates
only the constructions the user explicitly passes (one output per input — non-proliferating)
and sets frame-element `psi_install`. No structural change; update the component description
to say "sets the construction-level *default*; per-window conditions use the aperture-level
component".

### 2.4 KEEP: `HBPH - Create PH Window Frame Element`

`win_create_frame_element.py` — unchanged. `psi_install` remains a frame-element attribute
(the type default), default 0.04 W/mK. No new flag (issue #51's `psi_install_enabled` is
deliberately not implemented — a zero-Ψ value is the "off" state; see primary doc §8 (now archived)).

### 2.5 Housekeeping

- Registry entries + `.ghuser` regeneration via `src/__HBPH__Util_Update_GHCompos.py`
  (hard rule 3), commit regenerated `src/*.py` + `user_objects/*.ghuser`.
- IronPython 2.7 rules throughout (hard rule 1).
- `requirements.txt` pins updated by the release orchestrator, not by hand (hard rule 4).

## 3. Bug #59 closure

This refactor is the fix. When it ships:

- Re-run the §Verification checks in `aperture-construction-duplication.md` — in
  particular the 2310 end-to-end: 939 apertures ⇒ **79** window constructions and 79
  `EnergyWindowMaterialSimpleGlazSys`, identifiers stable across repeated exports, original
  constructions never mutated.
- The bug doc's "proposed correction" (content-keyed construction dedup inside the component)
  is **superseded** — the component no longer creates constructions at all. **Decided
  2026-08-12 (Ed): no interim/stopgap patch** — user base is small and updates slowly; go
  straight to the full refactor. #59 stays open until this ships.
- Mark #59 and the bug doc resolved, noting the resolution mechanism differs from the one
  originally proposed.

## 4. Ed's manual canvas steps (the only remaining work)

The Python side is complete, including pre-drafted canvas wrapper code. In Rhino/Grasshopper:

1. **New component** `HBPH - Create Aperture Install Type`: add a GHPython component, three
   inputs (`_display_name` str, `_psi_install` str, `_source` str; all item-access), one
   output `install_type_`. Paste the pre-drafted code from
   `honeybee_grasshopper_ph/src/HBPH - Create Aperture Install Type.py`.
2. **Edit component** `HBPH - Set Aperture Psi-Installs`: rename input
   `_psi_installs_w_mk` → `_install_types` (tree-access, no type hint) and paste the updated
   code from `honeybee_grasshopper_ph/src/HBPH - Set Aperture Psi-Installs.py`.
   (Note: an un-edited old component keeps working — bare psi values are auto-wrapped into
   anonymous Install Types — but the input name/description should be updated.)
3. Run `src/__HBPH__Util_Update_GHCompos.py` on the canvas; commit the regenerated
   `src/*.py` + `user_objects/*.ghuser`.
4. After the release orchestrator bumps `requirements.txt` (needs honeybee-ph ≥ the PR-#87
   release and PHX ≥ the PR-#80 release): re-export project 2310 and verify **79** window
   constructions / 79 `EnergyWindowMaterialSimpleGlazSys` against 939 apertures, stable
   identifiers across repeated exports (bug doc §Verification).
5. Close [#59](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/59) (mechanism
   deleted) and [honeybee_ph #51](https://github.com/PH-Tools/honeybee_ph/issues/51)
   (auto-closed by PR #87 — confirm), noting the Install-Type resolution in each.

## 5. User-facing model (docs/canvas copy)

Three orthogonal things, three components:

| Concept | Set by | Granularity |
|---|---|---|
| Frame element `psi_install` | Create Frame Element / Set HB-Construction Psi-Installs | window type (default) |
| Install Type | Create Aperture Install Type | project library (named condition) |
| Per-edge assignment | Set Aperture Psi-Installs | aperture instance, t/r/b/l |

Typical patterns: uniform project ⇒ set the type default, done. "All A1 in wall-type B get
0.08, all A1 in wall-type C get 0.05" ⇒ two install types, assign by selection. Buried jamb /
party-wall edge ⇒ assign a zero-Ψ install type to that edge.

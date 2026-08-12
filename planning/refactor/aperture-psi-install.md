# Refactor: Aperture-level Psi-Install — GH components

**Status:** Planned — design agreed 2026-08-12; not implemented. Blocked on `honeybee_ph`
shipping `PhApertureInstallType` + the aperture slots + resolver (the primary), and the
pinned release reaching `requirements.txt`.
**Date:** 2026-08-12
**Author:** Ed May + Claude
**Kind:** Cross-repo refactor. This repo holds the user-facing components **and the root cause
of bug #59** — the per-aperture construction-duplication mechanism, which this refactor deletes.
**Resolves:** [#59](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/59)
(`bugs/aperture-construction-duplication.md`) — by removal of the mechanism, not by patching it.

**Companion docs (same slug in each repo):**
- `honeybee_ph/planning/refactor/aperture-psi-install.md` — **primary**: data model, resolver, issue #51
- `PHX/planning/refactor/aperture-psi-install.md` — PHPP per-row write, WUFI/METr variant synthesis
- `ph-navigator-v2/planning/features_v1.1/aperture-psi-install/upstream-alignment.md`

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
deliberately not implemented — a zero-Ψ value is the "off" state; see primary doc §8).

### 2.5 Housekeeping

- Registry entries + `.ghuser` regeneration via `src/__HBPH__Util_Update_GHCompos.py`
  (hard rule 3), commit regenerated `src/*.py` + `user_objects/*.ghuser`.
- IronPython 2.7 rules throughout (hard rule 1).
- `requirements.txt` pins updated by the release orchestrator, not by hand (hard rule 4).

## 3. Bug #59 closure

This refactor is the fix. When it ships:

- Re-run the §Verification checks in `bugs/aperture-construction-duplication.md` — in
  particular the 2310 end-to-end: 939 apertures ⇒ **79** window constructions and 79
  `EnergyWindowMaterialSimpleGlazSys`, identifiers stable across repeated exports, original
  constructions never mutated.
- The bug doc's "proposed correction" (content-keyed construction dedup inside the component)
  is **superseded** — the component no longer creates constructions at all. **Decided
  2026-08-12 (Ed): no interim/stopgap patch** — user base is small and updates slowly; go
  straight to the full refactor. #59 stays open until this ships.
- Mark #59 and the bug doc resolved, noting the resolution mechanism differs from the one
  originally proposed.

## 4. User-facing model (docs/canvas copy)

Three orthogonal things, three components:

| Concept | Set by | Granularity |
|---|---|---|
| Frame element `psi_install` | Create Frame Element / Set HB-Construction Psi-Installs | window type (default) |
| Install Type | Create Aperture Install Type | project library (named condition) |
| Per-edge assignment | Set Aperture Psi-Installs | aperture instance, t/r/b/l |

Typical patterns: uniform project ⇒ set the type default, done. "All A1 in wall-type B get
0.08, all A1 in wall-type C get 0.05" ⇒ two install types, assign by selection. Buried jamb /
party-wall edge ⇒ assign a zero-Ψ install type to that edge.

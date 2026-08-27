# Planning Status

Master index of tracked planning work in honeybee_grasshopper_ph.

_Last updated: 2026-08-28_

## Active / current work

| Item | Kind | Status | Issue | Pointer |
|------|------|--------|-------|---------|
| Phius MF custom MEL/Lighting export `reference_quantity = 2` | Bug fix (cross-repo; **fix landed here**, packet owned by `honeybee_ph`) | **Merged** (2026-08-25, PR #69) — the six MF MEL/lighting builders now construct from `ph_default_equip[...]["PHIUS"]` so `reference_quantity = 5`. Remaining: canvas re-export confirming `<ReferenceQuantity>5</ReferenceQuantity>` in the WUFI XML and `"refQ": 5` in the METr JSON, then release. See the packet §10 for the open WUFI import question | [#76](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/76) | [`honeybee_ph/planning/archive/phius-mf-custom-load-reference-quantity/`](https://github.com/PH-Tools/honeybee_ph/blob/main/planning/archive/phius-mf-custom-load-reference-quantity/README.md) |
| Set Occupancy list padding | Bug fix | **Requested** — reproduced; not implemented | [#73](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/73) | issue-only (full evidence in #73) |
| Decouple "Dwelling" from `Room.zone` | Refactor (cross-repo) | **Code implemented** — remaining: manual component retirement, `ladybug_tools` install, 2613 re-run | [#74](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/74) | [`refactor/dwelling-zone-decoupling.md`](refactor/dwelling-zone-decoupling.md) |
| PH-Tools website consolidation | Plan (cross-repo) | Planning | [#75](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/75) | [`features/website-consolidation.md`](features/website-consolidation.md) |

## Completed / archived work

| Item | Kind | Status | Pointer |
|------|------|--------|---------|
| Already-exported models carry inflated window-type tables | Field remediation + PHX hardening | **Complete** (2026-08-27) — only 2310 affected (23 artifacts, Aug 11-12); no re-export needed (clean exports post-dated the buggy ones). Detector script + quarantine marker + doc corrections merged (PR #72); PHX Components stale-row guard merged (PHX PR #100, closes PHX #99). Phius Round-5 submission handling stays with Ed | [`archive/exported-models-inflated-window-types/`](archive/exported-models-inflated-window-types/exported-models-inflated-window-types.md) |
| Aperture-level Psi-Install (Install Types) | Refactor (cross-repo) | **Complete** (2026-08-28) — released v1.33.0; PHN per-edge client and the keyed-collection input followed (#71). Construction-count check verified at 2310 scale | [`archive/aperture-psi-install.md`](archive/aperture-psi-install.md) |
| Per-aperture window construction duplication (#59) | Bug fix | **Resolved** (2026-08-28) — mechanism deleted rather than patched; 948 apertures / 79 types now yield 79 constructions. Field impact tracked separately (see Active) | [`archive/aperture-construction-duplication.md`](archive/aperture-construction-duplication.md) |
| Consume PHN per-edge Psi-Install data | Feature (in `honeybee_grasshopper_ph_plus`) | **Complete** (2026-08-28) — HBPH+ PR #10; consuming it added the keyed-collection input here (PR #71). Confirmed via METr | [`HBPH+ archive/phn-psi-install-per-edge/`](https://github.com/PH-Tools/honeybee_grasshopper_ph_plus/tree/main/planning/archive/phn-psi-install-per-edge) |
| Re-point default-space creation at upstream honeybee-ph factory | Refactor (cross-repo) | **Complete** — released v1.28.1 with generated `honeybee-ph>=1.33.36` pin; meter, foot, multi-floor, host, and round-trip canvas checks pass | [`archive/space-from-room-factory/`](archive/space-from-room-factory/README.md) |

## Cross-repo work

`aperture-psi-install` spans four repos. This repo holds the user-facing components and the
root cause of bug #59 (`duplicate_aperture_construction()`), which the refactor deletes.
Blocked on the `honeybee_ph` primary shipping and its pinned release.

| Repo | Doc | Role |
|------|-----|------|
| `honeybee_ph` | `planning/archive/aperture-psi-install/` | Primary — **complete, archived** (v1.33.33) |
| `PHX` | `planning/archive/aperture-psi-install/` | **Complete, archived** (v1.56.73) — PHPP per-row write; WUFI/METr variant synthesis |
| `honeybee_grasshopper_ph` | [`archive/aperture-psi-install.md`](archive/aperture-psi-install.md) | **Complete, archived** (v1.33.0) — components; deleted the bug-#59 mechanism |
| `ph-navigator-v2` | `planning/features_v1.1/aperture-psi-install/upstream-alignment.md` | Phase-07 GH-client mapping |
| `honeybee_grasshopper_ph_plus` | `planning/archive/phn-psi-install-per-edge/` | **Complete, archived** (2026-08-28) — the PHN per-edge client |

`dwelling-zone-decoupling` spans three repos. **This repo holds the root cause** — the only
two references to `Room.zone` in the whole toolkit (`set_dwelling.py:113`,
`set_res_program.py:79`). Blocked on `honeybee_ph` shipping the shared helper.

| Repo | Doc | Role |
|------|-----|------|
| `honeybee_ph` | `planning/refactor/dwelling-zone-decoupling.md` | Primary — shared helper + tests |
| `honeybee_grasshopper_ph` | [`dwelling-zone-decoupling.md`](dwelling-zone-decoupling.md) | Root cause — the two `Room.zone` references |
| `PHX` | `planning/refactor/dwelling-zone-decoupling.md` | Downstream consumer — clearance + dedup |

`space-from-room-factory` spans two repos. The `honeybee_ph` **primary** builds the SDK-level
default-space factory (pure ladybug-geometry) and ships first; this repo then rewrites
`space_create_from_hb_rooms.py` as a thin wrapper. The shared `make_spaces/` helpers remain
for their other detailed-space consumers. The common single-floor canvas behavior stays
stable; Room hosting and one-volume-per-floor behavior are intentional upstream corrections.

| Repo | Doc | Role |
|------|-----|------|
| `honeybee_ph` | `planning/archive/space-from-room-factory/` | Primary — **complete, archived; released v1.33.36** |
| `honeybee_grasshopper_ph` | [`archive/space-from-room-factory/`](archive/space-from-room-factory/README.md) | **Complete, archived; released v1.28.1** with generated `honeybee-ph>=1.33.36` pin |

## Update rule

When an item reaches `Complete`, fold its outcome into the relevant `context/` doc, then move it to `archive/<slug>/` and add a row to `archive/README.md`.

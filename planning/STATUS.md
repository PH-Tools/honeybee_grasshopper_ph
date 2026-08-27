# Planning Status

Master index of tracked planning work in honeybee_grasshopper_ph.

_Last updated: 2026-08-25_

## Active / current work

| Item | Kind | Status | Pointer |
|------|------|--------|---------|
| Consume PHN per-edge Psi-Install data | Feature (in `honeybee_grasshopper_ph_plus`) | **Complete** (2026-08-28) — shipped as HBPH+ PR #10; consuming it added a keyed-collection input to this repo's `Set Aperture Psi-Installs` (PR #71). Confirmed via METr | [`archive/phn-psi-install-per-edge/`](https://github.com/PH-Tools/honeybee_grasshopper_ph_plus/tree/main/planning/archive/phn-psi-install-per-edge) |
| Aperture-level Psi-Install (Install Types) | Refactor (cross-repo) | **Effectively complete** (2026-08-28) — canvas work, .ghuser regeneration and release pins all done; #59 / #51 closed. Only the confirmatory 2310 re-export check is left, and the duplication mechanism it tests for no longer exists in the code | [`refactor/aperture-psi-install.md`](refactor/aperture-psi-install.md) |
| Per-aperture window construction duplication | Bug fix | **Fix implemented** (2026-08-12) — `duplicate_aperture_construction()` deleted in the refactor; #59 closes after Ed's canvas step + 2310 verification | [`bugs/aperture-construction-duplication.md`](bugs/aperture-construction-duplication.md) |
| Phius MF custom MEL/Lighting export `reference_quantity = 2` | Bug fix (cross-repo; **fix landed here**, packet owned by `honeybee_ph`) | **Merged** (2026-08-25, PR #69) — the six MF MEL/lighting builders now construct from `ph_default_equip[...]["PHIUS"]` so `reference_quantity = 5`. Remaining: canvas re-export confirming `<ReferenceQuantity>5</ReferenceQuantity>` in the WUFI XML and `"refQ": 5` in the METr JSON, then release. See the packet §10 for the open WUFI import question | [`honeybee_ph/planning/archive/phius-mf-custom-load-reference-quantity/`](https://github.com/PH-Tools/honeybee_ph/blob/main/planning/archive/phius-mf-custom-load-reference-quantity/README.md) |
| Set Occupancy list padding | Bug fix | **Requested** — reproduced; not implemented | [`occupancy-list-padding.md`](occupancy-list-padding.md) |
| Decouple "Dwelling" from `Room.zone` | Refactor (cross-repo) | **Code implemented** — remaining: manual component retirement, `ladybug_tools` install, 2613 re-run | [`dwelling-zone-decoupling.md`](dwelling-zone-decoupling.md) |
| PH-Tools website consolidation | Plan (cross-repo) | Planning | [`website-consolidation.md`](website-consolidation.md) |

## Completed / archived work

| Item | Kind | Status | Pointer |
|------|------|--------|---------|
| Re-point default-space creation at upstream honeybee-ph factory | Refactor (cross-repo) | **Complete** — released v1.28.1 with generated `honeybee-ph>=1.33.36` pin; meter, foot, multi-floor, host, and round-trip canvas checks pass | [`archive/space-from-room-factory/`](archive/space-from-room-factory/README.md) |

## Cross-repo work

`aperture-psi-install` spans four repos. This repo holds the user-facing components and the
root cause of bug #59 (`duplicate_aperture_construction()`), which the refactor deletes.
Blocked on the `honeybee_ph` primary shipping and its pinned release.

| Repo | Doc | Role |
|------|-----|------|
| `honeybee_ph` | `planning/archive/aperture-psi-install/` | Primary — **complete, archived** (v1.33.33) |
| `PHX` | `planning/archive/aperture-psi-install/` | **Complete, archived** (v1.56.73) — PHPP per-row write; WUFI/METr variant synthesis |
| `honeybee_grasshopper_ph` | [`refactor/aperture-psi-install.md`](refactor/aperture-psi-install.md) | Components; deletes the bug-#59 mechanism |
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

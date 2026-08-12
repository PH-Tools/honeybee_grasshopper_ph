# Planning Status

Master index of tracked planning work in honeybee_grasshopper_ph.

_Last updated: 2026-08-12_

## Active / current work

| Item | Kind | Status | Pointer |
|------|------|--------|---------|
| Aperture-level Psi-Install (Install Types) | Refactor (cross-repo) | **Code implemented** (2026-08-12) — remaining: Ed's canvas/.ghuser work, release-pin bumps, 2310 re-export check (doc §4) | [`refactor/aperture-psi-install.md`](refactor/aperture-psi-install.md) |
| Per-aperture window construction duplication | Bug fix | **Fix implemented** (2026-08-12) — `duplicate_aperture_construction()` deleted in the refactor; #59 closes after Ed's canvas step + 2310 verification | [`bugs/aperture-construction-duplication.md`](bugs/aperture-construction-duplication.md) |
| Set Occupancy list padding | Bug fix | **Requested** — reproduced; not implemented | [`occupancy-list-padding.md`](occupancy-list-padding.md) |
| Decouple "Dwelling" from `Room.zone` | Refactor (cross-repo) | **Code implemented** — remaining: manual component retirement, `ladybug_tools` install, 2613 re-run | [`dwelling-zone-decoupling.md`](dwelling-zone-decoupling.md) |
| PH-Tools website consolidation | Plan (cross-repo) | Planning | [`website-consolidation.md`](website-consolidation.md) |

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

`dwelling-zone-decoupling` spans three repos. **This repo holds the root cause** — the only
two references to `Room.zone` in the whole toolkit (`set_dwelling.py:113`,
`set_res_program.py:79`). Blocked on `honeybee_ph` shipping the shared helper.

| Repo | Doc | Role |
|------|-----|------|
| `honeybee_ph` | `planning/refactor/dwelling-zone-decoupling.md` | Primary — shared helper + tests |
| `honeybee_grasshopper_ph` | [`dwelling-zone-decoupling.md`](dwelling-zone-decoupling.md) | Root cause — the two `Room.zone` references |
| `PHX` | `planning/refactor/dwelling-zone-decoupling.md` | Downstream consumer — clearance + dedup |

## Update rule

When an item reaches `Complete`, fold its outcome into the relevant `context/` doc, then move it to `archive/<slug>/` and add a row to `archive/README.md`.

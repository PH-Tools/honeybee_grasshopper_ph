# Planning Status

Master index of tracked planning work in honeybee_grasshopper_ph.

_Last updated: 2026-07-21_

## Active / current work

| Item | Kind | Status | Pointer |
|------|------|--------|---------|
| Decouple "Dwelling" from `Room.zone` | Refactor (cross-repo) | **Code implemented** — remaining: manual component retirement, `ladybug_tools` install, 2613 re-run | [`dwelling-zone-decoupling.md`](dwelling-zone-decoupling.md) |
| PH-Tools website consolidation | Plan (cross-repo) | Planning | [`website-consolidation.md`](website-consolidation.md) |

## Cross-repo work

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

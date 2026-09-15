# Planning Status

Master index of tracked planning work in honeybee_grasshopper_ph.

_Last updated: 2026-09-15_

## Active / current work

| Item | Kind | Status | Issue | Pointer |
|------|------|--------|-------|---------|
| Phius MF custom MEL/Lighting export `reference_quantity = 2` | Bug fix (cross-repo; **fix landed here**, packet owned by `honeybee_ph`) | **Merged** (2026-08-25, PR #69) — the six MF MEL/lighting builders now construct from `ph_default_equip[...]["PHIUS"]` so `reference_quantity = 5`. Remaining: canvas re-export confirming `<ReferenceQuantity>5</ReferenceQuantity>` in the WUFI XML and `"refQ": 5` in the METr JSON, then release. See the packet §10 for the open WUFI import question | [#76](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/76) | [`honeybee_ph/planning/archive/phius-mf-custom-load-reference-quantity/`](https://github.com/PH-Tools/honeybee_ph/blob/main/planning/archive/phius-mf-custom-load-reference-quantity/README.md) |
| Remove deprecated 'Add PH Equipment' + 'Phius MF Res Calculator' | Refactor (upstream `honeybee_ph` #79 step 1 released 1.33.65) | **Released** (2026-09-12, v1.40.0; PR #87) — both dead components, their workers, registry entries, and the MF calc `.ghuser` deleted; `_deprecated_/` package gone; canvas export check passed, issue closed. Remaining: the v1.40.0 notes are auto-generated and do not yet name the replacement components | [#84](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/84) | issue-only (spec in #84) |
| Create Elec Equip: document the `quantity` input | Docs (cross-repo follow-up) | **Implemented on branch** `fix/quantity-input-description-98` — the input description now states the default (1) and that `energy_demand` is per-unit. The pin half of the issue is **not** hand-edited: `requirements.txt` is owned by the release orchestrator, which picks up `honeybee-ph` 1.33.67 / `PHX` 1.57.1 on the next release run | [#98](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/98) | issue-only (spec in #98) |
| Set Occupancy list padding | Bug fix | **Requested** — reproduced; not implemented | [#73](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/73) | issue-only (full evidence in #73) |
| Decouple "Dwelling" from `Room.zone` | Refactor (cross-repo) | **Code implemented** — remaining: manual component retirement, `ladybug_tools` install, 2613 re-run | [#74](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/74) | [`refactor/dwelling-zone-decoupling.md`](refactor/dwelling-zone-decoupling.md) |
| PH-Tools website consolidation | Plan (cross-repo) | Planning | [#75](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/75) | [`features/website-consolidation.md`](features/website-consolidation.md) |

## Completed / archived work

| Item | Kind | Status | Pointer |
|------|------|--------|---------|
| PH Additional Zone: PHPP v10 reduction-factor inputs | Feature (upstream `honeybee_ph` #122) | **Complete** — released v1.39.0 (2026-09-12, PR #85); five optional factor inputs, `.ghuser` rebuilt. The four load/cooling factors take effect in PHPP/WUFI only once `PHX` #65 lands (tracked there) | issue-only ([#78](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/78)) |
| Bldg Segment `mechanical_cooling_` input | Feature (cross-repo, part 3 of `honeybee_ph` #110; contributor PR) | **Complete** — released v1.40.0 (2026-09-12, PR #77); blank/None normalizes to False; `.ghuser` regenerated | issue-only ([PR #77](https://github.com/PH-Tools/honeybee_grasshopper_ph/pull/77); upstream [`honeybee_ph` #110](https://github.com/PH-Tools/honeybee_ph/issues/110)) |
| Create PH Equipment ignores a boolean `False` input (#96) | Bug fix | **Complete** (2026-09-15) — merged PR #97; `_normalize_input_value` applies boolean attributes by value. Canvas-verified: `False` injected, text `"false"`, and the Boolean Toggle all write `in_conditioned_space: false` to the HBJSON. Found during the #94 canvas check | issue-only ([#96](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/96)) |
| Create Elec Equip writes the string "None" into numeric equipment fields (#94) | Bug fix | **Complete** (2026-09-15) — released v1.41.0 (PR #95); canvas-verified: the text `"None"` is skipped, numeric text coerces. Source of the production string unresolved (the float hint blocks it on the canvas). Follow-up #96 | [`archive/create-elec-equip-none-string.md`](archive/create-elec-equip-none-string.md) |
| Foundation: PHPP 10 Ground inputs (#79) | Feature (upstream `honeybee_ph` #123 / `PHX` #121, #122) | **Complete** (2026-09-12) — released v1.38.0 (PR #80); `.ghuser` rebuilt to 14 input nodes; default corrections in the Release notes. Same release first pins `PH-units` in the installer (PR #81) | [`archive/foundation-ground-inputs/`](archive/foundation-ground-inputs/README.md) |
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

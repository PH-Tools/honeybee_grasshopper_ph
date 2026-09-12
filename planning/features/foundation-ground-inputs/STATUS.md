---
DATE: 2026-09-12
STATUS: In progress
AUTHOR: Ed May / Claude
ISSUE: https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/79
---

# Status

Branch: `feat/foundation-ground-inputs-79`

| Phase | Title | Status |
|-------|-------|--------|
| 1 | Worker inputs | Implemented on branch |
| 2 | Canvas verification and UserObject | In progress |
| 3 | PR and release | Scoped |

**Next step:** Phase 2, step 1 (confirm deployed packages), then the canvas walkthrough with Ed.

## Decisions

- **D1. `wind_shield_factor` uses `Component.NewFloatHint()` with no target unit.** `run()` converts a
  value only when the input has a target unit (`foundations_create.py`, `if user_input and
  target_unit`). A string hint with no unit would set the attribute to the string `"0.1"`. This matches
  `basement_ventilation_ach`. `wind_velocity_at_10m_m_s` keeps the string hint with target unit `M/S`.
- **D2. Empty-input handling stays as is.** An unconnected input reads as `None` and `if user_input:`
  skips it, so the upstream default survives; the issue's "do not write 0" criterion already holds. A
  typed `0` is skipped too (wind velocity `0` stays `4.0`). Not changed here: switching to
  `is not None` would also make a typed `0` on `perim_insulation_position` resolve to `3-VERTICAL`
  (`CustomEnum` 1-based index, `0 - 1 = -1`). Follow-up candidate.
- **D3. No committed test.** This repo keeps no tests, and `honeybee_ph/tests` has none for
  `honeybee_ph_rhino` workers. The worker is not importable in CPython (module-level
  `Component.NewStrHint()` after a swallowed `GhPython` import). Verification is an uncommitted scratch
  check with stubbed GH modules (Phase 1) plus canvas checks (Phase 2).
- **D4. No version bump, no hand-edited pin.** Component `Message` is `RELEASE_VERSION`; pins are
  written by the release orchestrator. The wrapper `src/HBPH - Create Foundation.py` builds inputs at
  runtime, so it does not change. The `.ghuser` needs a rebuild only if the saved component has fewer
  input nodes than the largest group now needs (index 13, so 14 nodes). Phase 2 checks the count.
- **D5. Release notes.** The release body is auto-generated from PR titles. The four default
  corrections go in the PR description, then into the GitHub Release body after the orchestrator runs.

## Verification log

- **Phase 1 (2026-09-12):** eight inputs added. CI gate clean (`black --check`, `isort --check-only`).
  Scratch check with stubbed GH modules, 0 failures: group keys and names, units and hints
  (`wind_shield_factor` float, no unit), every input name is a class attribute, heated basement
  unchanged; unconnected inputs keep `0.0` / `4.0` / `0.05`; `"12 ft2"` to 1.11484 m2, `"10 mph"` to
  4.4704 m/s, shield factor arrives as float `0.1`; `to_dict` / `PhFoundationFactory.from_dict` round
  trip equal for all three classes. IronPython 2.7 by inspection: no f-strings or annotations.
- **Phase 2, step 1 (2026-09-12):** Rhino's `ladybug_tools` site-packages has the new worker but a
  stale `honeybee_ph` (dist-info 1.33.56; `foundations.py` lacks the fields). The upstream merges did not
  pass through the fsdeploy Edit hook. Content differs in 4 honeybee_ph-repo files and 11 PHX files.
  Full `--sync-repo` not used: it would also delete empty Rhino-only `cli/` and `constructions/` dirs.

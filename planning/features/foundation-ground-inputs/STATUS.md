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
- **Phase 2, step 1 re-check (2026-09-12, after Ed's update):** Rhino has `honeybee_ph` 1.33.64 and PHX
  1.56.107 (latest PyPI); no content difference against the local repos for the five honeybee_ph packages
  or PHX. The update installed the Honeybee-PH v1.37.0 release, which overwrote the branch worker; the
  branch `foundations_create.py` was copied back and matches. `ph_units` is still 1.5.35 (missing
  PH_units #6, a CPython dataclass-shim fix; no effect on the canvas). Installed Create Foundation
  `.ghuser` is byte-identical to the repo copy.
- **Phase 2, step 2 (2026-09-12):** a fresh component with `_type=2` shows 12 input nodes, all names
  correct through `basement_ventilation_ach`. Below the 14 needed, so the `.ghuser` gets 2 more nodes.
  The update util copies `.ghuser` files from the installed `UserObjects/honeybee_grasshopper_ph/`
  folder into the repo (it does not export from the canvas), so the rebuilt User Object is saved there
  first. Pre-change installed `.ghuser` backed up (sha1 `f3f58e67`).
- **Phase 2, step 3 (2026-09-12):** two nodes added on the canvas (14 total). Node names match the issue
  for `_type` 2 (12, 13 interior wall), 4 (9 to 12, node 13 `-`), 3 (9, 10, then `-`), and 1 (unchanged
  heated-basement inputs, 7 to 13 `-`). `wind_shield_factor` tooltip reads `(Type hint: float)`.
- **Phase 2, steps 4 and 5 (2026-09-12):** User Object saved over the installed
  `honeybee_grasshopper_ph/HBPH - Create Foundation.ghuser` (sha1 `909ca8f3`, 6308 bytes; was
  `f3f58e67`, 4151). Metadata unchanged: Name, NickName, Category `HB-PH`, SubCategory `01 | Model`,
  Exposure primary. Decoded: 14 `InputParam` entries (was 12); embedded wrapper code identical to
  `src/HBPH - Create Foundation.py`. Update util copied it into the repo; no `src/*.py` changed, and every
  other installed `.ghuser` is byte-identical to the repo.

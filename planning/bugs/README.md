# planning/bugs/ — reproduced defects awaiting a fix

One file per defect, flat by slug. A doc lands here once the defect is **reproduced and root-caused** — a
suspicion belongs in an issue, not here. Each doc must carry enough evidence that the next agent can go
straight to the fix without re-deriving the diagnosis.

This README is the index — scan or grep it instead of opening every file.

| Item | Component | Status | Issue | Doc |
|------|-----------|--------|-------|-----|
| Already-exported models carry inflated window-type tables | (no component — field remediation) | **Scoped, remediation underway** (2026-08-26) — only 2310 affected (23 artifacts, Aug 11-12); detector script (`scan_inflated_window_types.py`) + quarantine marker done; remaining: PHX stale-row guard, Round-5 submission confirmation | [#59](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/59) | [`exported-models-inflated-window-types.md`](exported-models-inflated-window-types.md) |
| ~~Per-aperture window construction duplication~~ | `HBPH - Set Aperture Psi-Installs` | **Resolved 2026-08-28** — archived | [#59](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/59) | [`../archive/aperture-construction-duplication.md`](../archive/aperture-construction-duplication.md) |

## Conventions

- **Flat by slug:** `planning/bugs/<slug>.md`. Do not nest by date or by area.
- **Index here:** every defect gets one row above.
- Required sections: defect, evidence, root cause, proposed correction, verification.
- Record what was **ruled out**, with the evidence that ruled it out. Half the cost of a defect like this is
  the second engineer re-investigating a dead end.
- When fixed: fold the outcome into `context/`, then move the file to `planning/archive/<slug>/` and add a
  row to `planning/archive/README.md`.

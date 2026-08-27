# planning/archive/ — completed & superseded work

Finished feature folders (and single-file plans) folded back into `context/`, kept for history. Move an item here (unchanged) when its work is `Complete` or `Superseded`; keep the flat `<slug>` name so it stays findable by name.

This README is the index — scan or grep it instead of guessing dates.

| Item | Kind | Completed | Summary | Folder |
|------|------|-----------|---------|--------|
| Aperture-level Psi-Install (Install Types) | Refactor (cross-repo) | 2026-08-28 | `PhApertureInstallType` per-edge on the Aperture; deletes the bug-#59 construction-duplication mechanism. Released v1.33.0; PHN per-edge client and keyed-collection input followed in #71 | [`aperture-psi-install.md`](aperture-psi-install.md) |
| Per-aperture window construction duplication (#59) | Bug | 2026-08-28 | 939 constructions for 79 types. Resolved by removing the mechanism, not patching it; verified at 2310 scale. Field impact on already-exported models tracked in `bugs/exported-models-inflated-window-types.md` | [`aperture-construction-duplication.md`](aperture-construction-duplication.md) |
| Re-point default-space creation at upstream honeybee-ph factory | Refactor (cross-repo) | 2026-08-14 | Delegated default Space construction to `Space.from_room`; released v1.28.1 with generated upstream pin; meter, foot, multi-floor, host, and round-trip canvas checks pass. | [`space-from-room-factory/`](space-from-room-factory/README.md) |

## Conventions

- **Flat by slug:** `planning/archive/<slug>/`. Do not nest by date.
- **Index here:** every archived item gets one row above (completed date is a column).
- **If this ever gets long** (dozens+), bucket by year — `planning/archive/2026/<slug>/` — never by day.
- Canonical outcomes live in `context/`; this folder is history.

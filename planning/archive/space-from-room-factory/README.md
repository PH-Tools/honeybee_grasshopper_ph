# Refactor: Re-point default-space creation at the upstream honeybee-ph factory

**Status:** Complete · Released in `honeybee_grasshopper_ph` v1.28.1;
generated dependency pins and live Rhino verification complete · 2026-08-14
**Author:** Ed May + Claude
**Kind:** Cross-repo refactor (downstream side). The **primary** is
`honeybee_ph/planning/archive/space-from-room-factory/` — the new SDK-level
`Space.from_room()` factory built on pure ladybug-geometry
(`Polyface3D.from_offset_face` for extrusion). This doc covers only the
GH-side consumption.

**Companion docs (same slug in each repo):**
- `honeybee_ph/planning/archive/space-from-room-factory/` — primary: factory,
  tests, release evidence, and the live verification definition.

---

## WHAT

The upstream factory shipped in `honeybee-ph==1.33.36`. This repo consumes it
as follows:

1. **Rewrite the worker** `honeybee_ph_rhino/gh_compo_io/space_create_from_hb_rooms.py`
   (`GHCompo_CreatePHSpacesFromHBRooms`) to delegate space *construction* to
   the upstream factory. What remains GH-side is exactly the Rhino-specific
   shell:
   - room duplication (`hb_room.duplicate()`) and iteration over the input list;
   - **document-unit conversion** of the 2.5 m default height
     (`ph_units.converter` + `ladybug_rhino.units_abbreviation`) from meters
     into the Rhino/Room model units. The upstream factory performs no unit
     conversion; `avg_ceiling_height` must use the Room geometry's coordinate
     units;
   - IGH routing for unit-conversion failures and upstream validation errors.
2. **Retain `make_spaces/` for its remaining detailed-space consumers.** The
   import audit confirms `space_create_spc.py`, `space_add_spc.py`, and the
   detailed Add/Create Spaces script components still use all four helpers.
   The default-space wrapper no longer imports them, but none is orphaned and
   no helper is deleted in this refactor. The upstream v1 contract preserves
   one floor/volume per source floor face and intentionally does not merge
   coplanar faces.
3. **The common single-floor canvas case remains stable.** Same component,
   same inputs/outputs, same default 2.5 m height, and same
   `"{room}_default_space"` naming. Two upstream contract corrections are
   intentional: the Space host is now the Honeybee Room (not
   `RoomPhProperties`), and a multi-floor Room now produces one floor/volume
   per source Floor face rather than combining every segment into one volume.
   No-floor diagnostics also use the upstream validation message. Verify the
   common single-floor outputs plus these host/multi-floor contracts.
4. **Pin bump:** the release orchestrator raises the `honeybee_ph` minimum to
   the published factory release; `requirements.txt`, `RELEASE_VERSION`, and
   `hbph_installer.ghx` are not hand-edited.

### Constraints

- Registry rules apply as usual (`_component_info_.py`) if any component
  signature changes — expected: none.
- IronPython 2.7 syntax throughout.
- Primary release: `honeybee-ph==1.33.36`, published and installed in both
  this repo's `.venv` and `/Users/em/ladybug_tools/python` before verification.

## Implementation evidence

- `GHCompo_CreatePHSpacesFromHBRooms.add_default_space()` delegates construction
  to `Space.from_room()` and retains only duplication, unit conversion,
  attachment, and IGH error routing.
- Headless worker smoke passes for meter and foot documents: the source Room
  remains unchanged, the output has one `Room_1_default_space`, and the volume
  heights are `2.5 m` and `8.2020997375 ft` respectively.
- A Room with no Floor faces raises the upstream `ValueError` and records the
  same message through `IGH.error()`; unit-conversion failures are routed the
  same way before Room iteration.
- Black, Ruff, the Python-2-compatible parser check, and `git diff --check`
  pass for the worker.
- Component signature is unchanged, so registry/source/user-object regeneration
  is not required.
- Wrapper commit `edc6990` merged in PR #61 (`9d2ae2a`). Release workflow
  31819524996 completed successfully and published
  `honeybee_grasshopper_ph` v1.28.1 (`062402f`). The generated
  `requirements.txt` and `hbph_installer.ghx` both require
  `honeybee-ph>=1.33.36`.
- Live Rhino/Grasshopper verification passes with the archived primary
  `manual-test.ghx` definition:
  - meter single-floor: one Space/volume/segment, 20.0 m2 floor and weighted
    floor area, 50.0 m3 volume, and 2.5 m height;
  - foot single-floor: one Space/volume/segment, 215.278 ft2 floor and weighted
    floor area, 1765.739 ft3 volume, and 8.2021 ft height;
  - foot multi-floor: one Space with two ordered volumes/segments, 12.0 ft2
    floor and weighted floor area, 98.4252 ft3 volume, and two 8.2021 ft
    heights.
- All live cases preserve `Space.host is output_room` and Room-dict round-trip
  host rebinding. No component warnings/errors were observed.

## WHY

The logic that assembles a default PH `Space` from a Honeybee Room (floor
faces → segments → floor → extruded volume → space) is pure model logic, but
it currently lives only in this repo, threaded through `IGH` for extrusion
and merging. That placement forced the ph-modeler web-app POC (2026-08) to
re-derive the whole assembly by hand in CPython — and every future non-Rhino
consumer (PH-Navigator, scripts, tests) pays the same tax. The geometry
operations delegated to Rhino have pure ladybug-geometry equivalents, so the
coupling is historical, not necessary.

Upstreaming also makes the contract real: today the GH component and the POC
disagree on the `Space` host type and on merge behavior, and both "work".
One tested upstream factory defines the truth; this repo keeps what is
genuinely Rhino's — units, canvas IO, user geometry input — and nothing else.
Net effect here: `space_create_from_hb_rooms.py` shrinks to an upstream-backed
adapter, while the shared detailed-space helpers remain for their other live
consumers. One more piece of PH model knowledge stops being Grasshopper-only.

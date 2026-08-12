# Per-aperture window construction duplication

**Status:** Requested — root-caused and reproduced against a real model; not implemented.
**Resolution path (2026-08-12):** superseded by the cross-repo `aperture-psi-install` refactor
([`planning/refactor/aperture-psi-install.md`](../refactor/aperture-psi-install.md)), which deletes
`duplicate_aperture_construction()` entirely. Decided 2026-08-12 (Ed): no interim patch —
proceed straight to the full refactor; the content-keyed correction below is kept for the record only.
**Issue:** [#59](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/59)
**Opened:** 2026-08-12
**Component:** `HBPH - Set Aperture Psi-Installs`
**File:** `honeybee_ph_rhino/gh_compo_io/apertures/win_set_psi_install_values.py`
**Introduced:** `b2c322b` (2026-08-03) — *"fix(gh): stop mutating shared window construction in Set Aperture
Psi-Installs"*. First release containing it: **Honeybee-PH v1.25.2**.

## Defect

`duplicate_aperture_construction()` gives **every aperture its own window construction**, with an identifier
made unique by `clean_and_id_ep_string()` (which appends a fresh `uuid4()[:8]`). Two apertures that resolve
to byte-identical frames, glazing, and psi-install values still emit two separate constructions, because the
identifier is keyed on **aperture identity** rather than on **construction content**.

Nothing downstream can collapse them: Honeybee de-duplicates constructions by identifier, and the identifiers
are unique by construction. The HBJSON `properties.energy.constructions` array therefore grows linearly with
aperture count instead of with the number of distinct window types.

## Evidence

Project 2310 (AEA Emerson Place), same Rhino definition, same geometry, two machines:

| | HB-PH ≥ v1.25.2 | HB-PH ≤ v1.25.1 |
|---|---|---|
| export | `2310 Emerson Place_260811.hbjson` | `2310 Emerson Place_260812_2.hbjson` |
| file size | 14.1 MB | 11.3 MB |
| apertures | 939 | 939 |
| **window constructions** | **939** | **79** |
| distinct `display_name`s | 79 | 79 |
| `EnergyWindowMaterialSimpleGlazSys` | 939 | 79 |
| base window types | 21 | 21 |

Aperture counts per named type are identical across the two files (all 79 diffed, zero mismatches), and the
PH properties — frame elements, psi-glazing, psi-install, glazing U/g — are identical. Only the construction
object count differs. In this model **every** `psi_install` is 0.10 W/mK on all 20 frame profiles, so not one
of the 860 extra constructions carries distinct data.

## Root cause

`win_set_psi_install_values.py:81-111`:

```python
def duplicate_aperture_construction(_aperture):
    """Give an aperture its own window construction and identifier."""
    ...
    aperture_suffix = _aperture.identifier

    if isinstance(construction, WindowConstructionShade):
        dup_construction = construction.duplicate()
        dup_window_construction = construction.window_construction.duplicate()
        dup_window_construction.identifier = clean_and_id_ep_string(
            "{}_{}".format(construction.window_construction.identifier, aperture_suffix))
        dup_window_construction.lock()
        dup_construction._window_construction = dup_window_construction
    elif isinstance(construction, WindowConstruction):
        dup_construction = construction.duplicate()
    ...
    dup_construction.identifier = clean_and_id_ep_string(
        "{}_{}".format(construction.identifier, aperture_suffix))
```

The identifier arithmetic is directly visible in the exported file:

```
aperture.identifier     = W4.A_C0_R0_a1789218
construction.identifier = W4.A_C0_R0
emitted identifier      = W4.A_C0_R0_W4.A_C0_R0_a1789218_49914505
                          └─ con id ─┘└─── aperture id ───┘└ uuid ┘
```

`clean_and_id_ep_string()` is called twice per aperture — once for the `WindowConstructionShade` wrapper and
once for the nested `WindowConstruction` — which is why the two carry the same prefix but different trailing
hashes (`..._a1789218_49914505` vs `..._a1789218_<other>`). The nested-construction id is only reachable
through the private `_window_construction` attribute; Honeybee exposes no public setter (noted in the source).

## Do not regress the reason this code exists

`b2c322b` fixed a real defect and must not simply be reverted. Before it, the component reached through
`ap_prop_energy.construction` and mutated `ph_frame` on the **shared** construction in place. Every aperture
pointing at `W4.A_C0_R0` ended up with whichever psi-install branch was processed last — silent
cross-contamination between apertures, with no warning and no visible symptom in the HBJSON.

The correct fix keeps that isolation and removes only the *spurious* uniqueness.

## Ruled out

- **Ladybug Tools / honeybee-energy / honeybee-core.** The two machines also differed in LBT version
  (1.10.41 vs 1.10.51), which is what first drew suspicion. Diffing that range: `honeybee_energy/properties/`
  is untouched — nothing changed in how apertures hold or assign constructions. The honeybee-energy delta is
  the gbXML translator build-out (`writer.py` +1420 lines), construction unit conversion, People CO₂ rate, a
  subprocess simulation runner, and a `constructionset.prioritized_abridged` fix. In honeybee-core,
  `clean_and_id_ep_string()` is byte-identical across the range; the additions (`clean_xml_tag_string()`, the
  DOE-2 illegal-name guard, `rename_*_by_attribute()`, `face_edges()`) are all opt-in and none run by default.
  LBT version correlates with the symptom on these two machines but is not causal.
- **`honeybee_grasshopper_ph_plus`, `PHX`, `PH-Navigator V1`.** The identifiers are written before any of
  these run; the arithmetic above matches this component's source exactly.

**Caveat on the A/B:** the two machines differ by more than the HB-PH version. The v1.25.1 export carries
`properties.ref` blocks on its materials (`honeybee_ref`) and the v1.25.2 export does not, so `honeybee_ref`
is installed on one machine and not the other. Confirm the HB-PH version on each machine directly rather than
inferring it from LBT version.

## Proposed correction

Two changes, both in `duplicate_aperture_construction()` and its caller:

1. **Fast path — do nothing when nothing changes.** If the psi-install values resolved for this aperture
   already equal those on its current construction, return the aperture untouched. No duplicate, no new
   identifier. For a model like 2310, where all psi-installs are uniform, this alone restores the pre-v1.25.2
   output byte-for-byte.

2. **Content-keyed identifiers with reuse.** When the values *do* differ, derive the new identifier
   deterministically from the base construction identifier plus the resolved psi-install tuple, using
   `clean_ep_string()` (no uuid), and cache constructions by that key for the duration of the component run so
   apertures resolving to the same key share one object:

   ```python
   psi_key = hashlib.sha256("|".join("{:.4f}".format(v) for v in psi_values).encode("utf-8")).hexdigest()[:8]
   new_id = clean_ep_string("{}_psi{}".format(construction.identifier, psi_key))
   ```

   A readable key (`_psi0.1000-0.1000-0.1000-0.1000`) is easier to debug in PHPP/WUFI but risks the 100-char
   `valid_ep_string` ceiling on long base names — the hash is the safer default. `PhWindowFrame` always has
   exactly four elements, so the tuple length is fixed.

Preserve in both paths: `display_name` stays the human-readable type name (this is why the broken file still
showed only 79 display names); the nested `WindowConstruction` gets the same content-keyed treatment as its
shade wrapper; `lock()` is still called after mutation.

Note that `run()` mutates `ph_frame` **after** duplication (`win_set_psi_install_values.py:202-213`). With a
shared cached construction this stays correct only because apertures sharing a key write identical values —
keep that invariant explicit in a comment, or move the frame mutation to construction-creation time.

## Verification

This repo has no test suite (`CLAUDE.md` hard rule 6 — the worker suite lives in `honeybee_ph`). The
identifier-building logic should be extracted into a pure helper with no Grasshopper imports so it can be
tested upstream; today `duplicate_aperture_construction()` sits in a module that imports `Grasshopper`,
`System`, and `GH_Path` at module scope and cannot be imported outside Rhino.

- N apertures sharing one window type and one psi-install branch produce **exactly one** construction.
- Two apertures with the same base construction but *different* psi-install values produce **two**
  constructions, and neither one's frame values leak into the other — the original regression from `b2c322b`.
- Identifiers are stable across repeated runs of the same definition: exporting twice without editing the
  model yields identical construction identifiers (this is what `clean_and_id_ep_string` breaks today).
- The original construction passed into the component is not mutated.
- End-to-end on 2310: re-export from an HB-PH build carrying the fix and confirm **79** window constructions
  and 79 `EnergyWindowMaterialSimpleGlazSys` entries against 939 apertures, with per-type aperture counts
  unchanged from `2310 Emerson Place_260812_2.hbjson`.

## Downstream impact

The inflated construction list propagates through `PHX` into the PHPP and WUFI-Passive window-type tables,
where 939 near-identical entries appear in place of 79. Worth confirming whether `PHX` collapses them on
serialization or passes them straight through — if the latter, any model exported from HB-PH ≥ v1.25.2 that
used this component needs re-checking before certification submission.

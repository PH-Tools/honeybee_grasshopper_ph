# Set Occupancy list padding

**Status:** Requested — reproduced, not implemented
**Issue:** [#73](https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/73)
**Opened:** 2026-08-06
**Component:** `HBPH - Set Occupancy`
**File:** `honeybee_ph_rhino/gh_compo_io/program/set_res_occupancy.py`

## Defect

`GHCompo_SetResOccupancy.number_people` pads a short `_num_people` list by repeating its last
value. Against six Rooms, `[2, 1, 1]` becomes an effective total of 7 occupants rather than the
user-entered total of 4. Unspecified Rooms should receive zero occupants; repeating the last
nonzero value creates people the user did not enter.

The padding count is independently wrong:

```python
self._number_people += [self._number_people[-1]] * (self.max_input_length - 1)
```

It adds `max_input_length - 1` items instead of
`max_input_length - len(self._number_people)`. Any starting list longer than one element is
over-padded. `izip()` hides the excess today, but the property returns the wrong-length list and
mutates the component input in place.

`number_bedrooms` uses the same count expression and should be audited in the same change. Its
fill-value contract needs an explicit decision; the occupancy defect only establishes that
missing `_num_people` values must be zero.

## Proposed correction

- Return a padded copy; do not mutate the incoming Grasshopper list.
- Pad `_num_people` with `0.0` to exactly `max_input_length`.
- Decide and document whether missing `_num_bedrooms` values are zero-filled or intentionally
  repeat the last supplied value, then use `max_input_length - len(values)`.

## Verification

- Six Rooms plus `_num_people=[2, 1, 1]` yields `[2, 1, 1, 0, 0, 0]` and total `4`.
- A one-item list, a partially populated list, and a full-length list all return exactly six
  values.
- Reading either property twice is idempotent and does not mutate the original input list.
- The existing single-value Grasshopper workflow retains its explicitly chosen behavior.

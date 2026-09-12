---
DATE: 2026-09-12
STATUS: In progress
AUTHOR: Ed May / Claude
ISSUE: https://github.com/PH-Tools/honeybee_grasshopper_ph/issues/79
---

# Foundation: PHPP 10 Ground inputs

Expose the eight PHPP 10 `Ground` fields that `honeybee_ph` 1.33.64 added to the foundation classes on
the `HBPH - Create Foundation` component.

The behavior contract (field list, indexes, descriptions, acceptance criteria) is issue #79. This
packet holds the decisions and the phase plan the work executes from.

**Read order:** [`STATUS.md`](STATUS.md), then [`PLAN.md`](PLAN.md).

## Upstream (all merged and released 2026-09-12)

| Repo | Item | Release |
|------|------|---------|
| `honeybee_ph` | #111, merged in #123: fields + four default corrections | 1.33.64 |
| `PHX` | #120 Part A (#121): model fields; Part B (#122): `Ground` writer | 1.56.105+ (requires `honeybee-ph>=1.33.64`) |
| `PH_units` | `M/S` already supported | n/a |

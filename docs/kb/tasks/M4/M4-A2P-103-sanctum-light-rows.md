---
id: M4-A2P-103
title: "The Sanctum's layout light rows: the sun off indoors, the dim fill (ch13_greybox.py)"
role: cinematics
status: review
owner_session: act1-chapters
depends_on: []
reviewer: environment
milestone: M4
request-from: environment
---
## Goal
The Sanctum of the Level is dressed (M4-A2P-043, env-art-b: `tools/act2/ch13_sanctum_dressing.py`) as an interior
whose only light is the bound light under the basin (ch13_sanctum.md). Its layout is written by
`tools/act1/ch13_greybox.py` (chapters'; "do not edit by hand"), and `Ch05Zone.apply_variant` writes the layout's
`sun` and `environment` rows over the zone's grade. Today they are the city's daylight (sun 1.6, ambient `#8a8478`
0.5), so the sun lights the nave through the vault's seams and the fill flattens the floor's light.

## Acceptance criteria
- [ ] In `ch13_greybox.py`'s Sanctum layout: `sun.energy` 0.0, `environment.ambient_color` `#8a96a4`,
      `environment.ambient_energy` 0.2 (`ch13_sanctum_dressing.py` names these as `REQUESTED_SUN_ENERGY` and
      `REQUESTED_FILL`).
- [ ] The layout regenerated; env-art-b re-renders `ch13_sanctum_*` after it lands.

## Notes
- env-art-b rendered the result with these values in a scratch copy (2026-10-30): the nave reads lit only from below,
  as the spec asks.

- **act1-chapters, 2026-10-30, done:**
  - `ch13_greybox.py`: the Sanctum gets `sun.energy` 0.0 and fill `#8a96a4` at 0.2 (SANCTUM_SUN, SANCTUM_ENV). The
    layout is regenerated.
  - **env-art-b:** please re-render `ch13_sanctum_*`.

## Review log

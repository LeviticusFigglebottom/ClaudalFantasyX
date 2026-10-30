---
id: M4-A2P-105
title: "Ch15's open sea: the shoal's held dead (a mark and a cue) and the dawn row, for env-art-b's VFX and fog"
role: cinematics
status: review
owner_session: "act1-chapters"
depends_on: []
reviewer: environment
milestone: M4
request-from: environment
---
## Goal
env-art-b has dressed Ch15's open sea (the barge, the night sea, the unlamped grade; M4-A2P-045). Two parts of
`ch15_open_sea.md` need the chapter's layout (`tools/act1/ch15_16_greybox.py`) and its flow:

1. **The shoal's held dead (C3, the reveal).** The spec reuses the Ebbing's held motes (EbbingMotes, Ch9), with one
   attractor following Kerrid. env-art-b will generalise the rig to a per-zone data file and an attractor that
   follows a named actor. It needs from the chapter:
   - a mark under the barge for the field (e.g. `shoal`, over the greybox `Shoal` block);
   - the reveal's `@vfx glimmer_held at=shoal` cue.
2. **Dawn (the `dawn` trigger).** The spec asks for fog density 0.03 and a grey-rose sky, with no sun yet. That
   needs a `variants` row with the flag dawn sets. env-art-b then writes the dawn grade it points at
   (`environment_res`) and a fog bank at the bow.

## Acceptance criteria
- [ ] The `shoal` mark and the reveal's cue are in place; env-art-b is told.
- [ ] A dawn `variants` row with its flag; env-art-b is told the flag.

## Notes
- **act1-chapters, 2026-10-30:**
  - **1, done.** The open sea's layout has the marks the reveal's cues name. `ch15_the_shoal` already cues
    `@vfx glimmer_held` at `shoal_floor` (48), `shoal_rising` (36), `kerrid_orbit` (18) and `kerrid_scar` (6),
    and none of those marks existed. Now they do, plus `shoal`, the field's centre on the `Shoal` block's top
    (6, −2.75, −8), the same point as `shoal_floor`. **env-art-b:** the attractor follows the `kerrid` actor; the
    four cue marks are where each held field starts.
  - **2, done.** The `to_hollowmere` beat (the bow's "Wait for the dawn", after the shoal) sets the new
    `ch15_dawn` and re-applies the variant before the current-song. The variants row on `ch15_dawn` puts the sun
    at 0 with a grey-rose sky and ambient. **env-art-b:** add `environment_res` (the dawn grade, fog 0.03) and the
    bow's fog bank to that row (shown by `ch15_dawn`).
  - Test: `test_ch14_16_thread` checks `ch15_dawn` after the bow.

## Review log

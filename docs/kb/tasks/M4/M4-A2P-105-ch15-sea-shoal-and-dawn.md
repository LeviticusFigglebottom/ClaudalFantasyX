---
id: M4-A2P-105
title: "Ch15's open sea: the shoal's held dead (a mark and a cue) and the dawn row, for env-art-b's VFX and fog"
role: cinematics
status: todo
owner_session: ""
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

## Review log

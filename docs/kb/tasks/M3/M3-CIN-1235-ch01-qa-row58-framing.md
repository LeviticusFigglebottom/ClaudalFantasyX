---
id: M3-CIN-1235
title: "PC GPU QA pass 3, row 58 (slice-polish, Ch1): the Hullgnaw's rise, the net pen and O07 frame nothing they name"
role: cinematics
status: review
owner_session: slice-polish (claude/m2-slice)
depends_on: []
milestone: M3
request-from: lead
---
## Goal
The Lead's QA pass 3 (origin/gpu/act1-qa-3), row 58: `ch01_hullgnaw_rises` and `ch01_net_pen` were nearly black with no
Hullgnaw and no Child in frame, and O07's camera was pressed against the hull. Fix them, self-render the stills, and
log MERGE-READY.

## Acceptance criteria
- [x] ch01_hullgnaw_rises: the Hullgnaw is on stage (a hidden layout actor with the creature's own model, shown by
      the chapter beat's `show_block` before the scene; `@anim hullgnaw intro` plays its rise) and rises up through
      the net-pen deck at the centre of O16, in front of Rhen. Viewed (lavapipe): it reads as a dark mass with its
      cyan glow at the centre of the frame.
- [x] ch01_net_pen: P01, over Rhen's shoulder onto the pen; the children (the Child speaks) are in frame, and the
      camera is released after Rhen's last line. Viewed.
- [x] ch01_bark_outer_mooring: O07 looks square at the Seventh Terrace's name-board on her stern (1.5 s insert),
      which ends before Sadi's answer. The shot holds the insert (`hold_cue: camera O07`). Viewed: the board fills
      the frame.

## Notes
- The shot rig gains `show` (stage actors to show first, as the chapter beat's show_block does).
- The Hullgnaw in the storm light is dark on lavapipe; PC-QUEUE: check its emissive read on the GPU.

## Review log

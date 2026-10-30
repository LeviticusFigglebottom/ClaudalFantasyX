---
id: M3-C09-1209
title: Ch9 greybox to final, ch09/corrow_night on the Corrow kit's fallen wall (the strand, the mole, the road)
role: cinematics
status: review
owner_session: act1-chapters (claude/act1-chapters)
depends_on: [M3-C08-1202, M3-ENV-04B, M3-C09-02]
milestone: M3
reviewer: qa
request-from: ""
---
## Goal
Move Ch9's flat greybox Corrow night into Ch8's kit frame, in the wall's fallen state (M3-ENV-04B).

## Acceptance criteria
- [x] `tools/act1/ch09_corrow_night.py`: the layout moved once (`--relayout`); the dressing and collision derived from
      Ch8's (the fallen wall always; the strand of the drowned as sunk shingle banks from the Brine Shoals kit; the
      landing at the breach; a bridge to Ch8's mole and its ramp up to the walk, where Liss waits at her cut hoist; the
      coast road as the walk east of the wall-gate; the lake at the eaves behind the wall, Kerrid on the broken stair;
      Iskarra's set 1700 m east).
- [x] The dawn variant swaps to the day grade (`environment_res`, now in Ch05Zone's variants too).
- [x] `test_ch09_thread` 7/0; `test_ch09_corrow_walkable` (the strand, the way to Liss, the road, every mark).
- [x] Shots `ch09_corrow_strand`, `ch09_corrow_road` rendered on the PC, viewed, approved. Baselines approved by the Lead's gates (big13 1fa92b81 / a4410fd9; tracks never write baselines, TRACK-RULES).

## Notes
- Greybox kept visible: the landing and the raft, the rocks (fallen Watchers on them), the shroud rows, the lamps,
  the lake, the hoist coil, the milestone, the mole, Iskarra's set (M3-ENV-1203 and a strand request when viewed).

## Review log
- 2026-10-29 act1-chapters: to review (every criterion met; the stand-ins listed in Notes wait on their own requests).

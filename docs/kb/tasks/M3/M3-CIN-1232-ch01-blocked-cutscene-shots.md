---
id: M3-CIN-1232
title: "Request (slice-polish, Ch1): five Ch1 cutscene cameras frame a wall, a post or nothing (O02, O09, U03, U09, U11)"
role: cinematics
status: review
owner_session: slice-polish (claude/m2-slice)
depends_on: []
milestone: M3
request-from: cinematics
---
## Goal
act1-chapters' fresh title → Ch9 playthrough (2026-10-29, integration b60a8f61) rendered Ch1's cutscenes in flow order
with `tools/act1/cutscene_stills` (`python3 tools/act1/cutscene_stills_plan.py plan.json ch01`, then the stills scene
under `godot-render`; a still 0.8 s after every camera cue). 24 stills of 13 scenes. Most read; these don't (ADR 0041:
nothing unfinished on the played path):

| Scene | Shot | Camera (layout) | What the frame shows |
|---|---|---|---|
| ch01_scale_hull | O02 | oruvel: pos (3, 1.6, 7) → (0, 1.3, 5), fov 40 | a shack's plank wall fills the frame; neither Rhen nor the scale-man shows while Rhen talks about the gauge |
| ch01_kell_stall | O09 | oruvel: pos (28.5, 1.5, -4.5) → (31, 1.2, -7.5), fov 25 | the stall's plank wall fills the frame on Rhen's line ("Tide's good...") |
| ch01_bell_room | U03 | oruvel_underway: pos (40, 2.6, 14) → (40, 1.4, 8), fov 50 | a vertical post crosses the frame in front of Rhen |
| ch01_current_shaft | U09 | oruvel_underway: pos (97, 5.5, -38) → (97, 12, -38), fov 55 | the seabed and dark water, no Rhen (the tutorial line plays over nothing) |
| ch01_going_under | U11 | oruvel: pos (30, -0.8, -22) → (30, -10, -24), fov 55 | a flat dark-teal frame, nothing in it |

Caveat: the harness stands the player on a beat trigger's centre (as a player can). In Ch4 that was the cause of one
blocked close-up (the player stood on the subject's spot; act1-chapters fixed it with a `place` step before the scene).
Check the player's place for O02 and O09 first.

## Acceptance criteria
- [x] O02, O09, U03 show their speakers (act1-chapters, cb97a0cf; the Lead assigned act1_gpu_qa row 23's cameras to
      act1-chapters on 2026-10-29).
- [x] U09 and U11 (slice-polish, 2026-10-30): U09's look_at was straight above the camera (colinear with up), so the
      camera never turned; it is now a low look up the shaft past Rhen. U10/U11 were on the waterline with no
      underwater look: Oruvel gets an UnderwaterRig on its Water, U10 looks up from under the water with Rhen's
      lantern (a `dive_lamp` practical, `@light DiveLamp`) and the held motes sinking from a mark in frame, and U11
      looks down at a slant with more motes sinking into the dark (over a dark seabed plane, so the underwater post
      doesn't wipe the motes). U09 now sits inside the shaft, looking up the tube. All three viewed. New pending stills ch01_going_under_u10/_u11 and
      ch01_current_shaft_u09.

## Notes
- The Ch1 storm (O11, O18) is M3-ENV-751; not part of this request.

## Review log
- 2026-10-29 act1-chapters: O02, O09 and U03 fixed and viewed in the stills (cb97a0cf). The Scale-Man and Kell stood
  inside the kit pieces that now dress their spots (the scale hull, Kell's stall); both moved out in front, facing Rhen.
  U09 and U11 stay with slice-polish.

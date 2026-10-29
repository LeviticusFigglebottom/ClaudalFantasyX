---
id: M3-HER-1155
title: "Cutscene A: after Rhen stands, four lines stay on H05, a low shot framed for him lying down, so they play on empty sky"
role: cinematics
status: todo
owner_session: ""
reviewer: qa
depends_on: []
milestone: M3
request-from: qa
---
## Goal
The big14 GPU playtest (docs/kb/qa/gate-runs/big14/README.md, sheet walk_p03, frames newgame_27–30) shows four
lines framed on empty sky: "I'm Asha. That's Toma…", "Toma Okeru,", "To Asha. Who is very glad…", "Later. You're
shaking.". An orange blur at the top edge of newgame_27 is Rhen's hair.

Cause: `ch02_girl_on_the_beach.dlg` cuts to `@camera H05 blend=0.0` (line 84) before `@anim rhen take_hand asha` and
`@anim rhen rise_to_stand` (lines 90–91), and the next camera cue is H01 at line 105. H05 (haluna.tscn
`Shot_cut_H05`) stands at (-0.85, 0.44, 8), 0.44 m off the sand and about 1 m from him, looking at (0.2, 0.88, 7.79).
That framing suits him lying or kneeling. Once he stands, his head is at about 1.7 m, out of the top of the frame,
and the lines that follow play on sky.

Also (the PC's real-GPU QA, row 21, on lead/gate-ft-beach): "the camera starts below the waterline, looking up
through the surface". H05 stands at y 0.44 in the shallows. When the tide (weathering_tide.gd's
`hymn_water_level`) is above that, the low shot is under the water. Keep H05 above the highest water the beach sees
at that time of day.

## Acceptance criteria
- [ ] After `@anim rhen rise_to_stand`, cut to a shot that frames him standing with Asha and Toma (H06 or a new
      one) for lines ch02_beach_029–034.
- [ ] H05 stays above the water surface at the beach's tide for Cutscene A.
- [ ] Self-render the cutscene. No line plays on a frame without a face in it.

## Notes
Filed by integration-qa (big14 item 5). The rest of item 5, "Rhen is not on screen at the start", turned out to be
Asha standing between the trailing field camera and Rhen. HeroFieldParty now keeps followers off the camera's line
to the leader (sight_clear_m).

## Review log

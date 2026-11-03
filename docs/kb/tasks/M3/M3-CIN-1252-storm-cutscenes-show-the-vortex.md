---
id: M3-CIN-1252
title: "FAST-TRACK (11-03 playtest): the storm cutscenes show the Undertow's vortex (Ch1's Rising, Ch8's B07)"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice)"
depends_on: [M3-C01-100]
reviewer: art
milestone: M3
---
## Goal
The human's playtest: "the seagull/storm scene doesn't show the actual vortex". Ch1's Rising (O11) showed the
Undertow only as a dark tower on the horizon, and Ch8's B07 held its long silent beat on the people on the beacon
gallery (F08), with the storm out of frame. Both scenes now show the vortex itself, using the zone's real Undertow
(UndertowStorm, the M3-C01-100 horizon storm; Coilspire's kit storm), not a slab.

## Acceptance criteria
- [x] Ch1 `ch01_the_rising`: O11 (the wall stands up), then **O11E**, a cut to the storm's eye from high above
  (the spiral arms, the eye, the held light sinking down the throat), then back to O11 for Rhen's line.
- [x] Ch8 `ch08_storm_against_wind`: the long beat opens on **F08W** (the wall from the gallery, over the sea),
  cuts to **F08E** (straight down the eye: the maelstrom and its foam rings, cyan rents, a bolt), and only then
  finds the people (F08).
- [x] `@storm view|off [look=]` (CutsceneStorm, sequencer.json `storm`): during a storm shot the Undertow's clock
  runs (the vortex turns; Oruvel holds it still), the zone fog thins (a storm zone's spray fog greyed the throat
  out at 20 km), the sun lights the storm's top, and a bolt strikes on the side facing the camera. `off`, or the
  scene's end, restores all of it.
- [x] Music checked: both scenes already play the storm's own cues (`undertow_rising`: G octatonic, low brass,
  a limping pulse, "never a heroic one"; B07 holds silence). No audio request needed.
- [x] Self-rendered and viewed (lavapipe): ch01_rising_eye, ch08_storm_wall_f08w, ch08_storm_eye_f08e (new shots,
  `pending_baseline`).

## Notes
- Coordination: act1-chapters owns the storm FIGHTS' arenas (and Coilspire's layout and Ch8's dialogue). This
  task adds only the F08W/F08E shot rows and B07's opening cues, under the Lead's FAST-TRACK assignment.
  battle-presentation and audio own the fights' backdrop and music.
- For Rendering (not blocking): at a steep angle down the eye, the maelstrom disc's near rim shows dark ribbed
  arcs (ch08_storm_eye_f08e, either side of the throat). Worth a look on the GPU.

## Review log

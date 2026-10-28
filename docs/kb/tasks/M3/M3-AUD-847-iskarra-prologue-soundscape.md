---
id: M3-AUD-847
title: "The Iskarra prologue soundscape: the vigil's murmur in the bed, and Rhen's lamp crackling at the lamp"
role: audio
status: review
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
reviewer: cinematics
depends_on: [M3-AUD-817]
milestone: M3
request-from: lead
---
## Goal
The Lead (10-27, 21:42): env-art is re-dressing Iskarra (M3-ENV-724). Give the prologue its room tone, the vigil's
murmur, the distant sea and wind, and the lamp's crackle.

## Acceptance criteria
- [x] The room tone, the distant sea and the wind were already in `iskarra_dusk`: the towers' wind and ceramic
      singing, the water's laps and swells, far drips, and the far sea (M3-AUD-817).
- [x] The vigil's murmur: a new `vigil` bus in prologue_ambience.py. It plays the villagers' murmur (life_sfx.py),
      low-passed and set back, about three times a loop, about 15 dB under the wind while one speaks. The bed is
      re-rendered at −26.05 LUFS with seam ×0.59 and is byte-identical on re-render, at 0.41 MiB (its budget is 0.6).
- [x] The lamp's crackle: cutscene_foley.py `cs_lamp_crackle_1..4`, an oil wick's spits and the flame's breath at
      −30 LUFS. CutsceneAudio's `lamps` makes every Light3D on a stage that `lamps.match` names (the prologue's
      `LanternLight` under Rhen) crackle at the lamp at random gaps while it is lit. data_check validates it.
- [x] Tests: test_cutscene_audio covers a lit lamp crackling at the lamp, a dark one staying silent, a freed one being
      dropped, and the real prologue stage's LanternLight being watched. `--filter=cutscene_audio` 8/0, `audio`
      165/0, `cutscene` 69/0.
- [ ] Once env-art's re-dress lands: if it adds lamps or braziers, add their light names to `lamps.match`.

## Review log

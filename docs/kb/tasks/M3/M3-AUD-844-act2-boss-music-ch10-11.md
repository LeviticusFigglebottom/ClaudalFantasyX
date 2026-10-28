---
id: M3-AUD-844
title: "Act II boss music, Ch10-11: mangrove_drowner and lamp_engine (two stems each)"
role: audio
status: blocked
owner_session: "audio worktree agent"
reviewer: design
depends_on: [M3-AUD-839]
milestone: M3
request-from: lead
blocked-by: ADR 0041
---
## Goal
Write two of the six Act II boss cues in docs/kb/audio/act2_finals.md: the Mangrove Drowner (Ch10, phase 2
`uprooted`) and the Lamp Engine (Ch11, phase 2 `opened`). Each is a two-stem boss loop modelled on
`assets_src/music/cinder_matron.py`: stem 1 is the first phase, and stem 2 joins at the phase change. Both stems share
one gain and one limiter curve computed on the full stack, have equal lengths and LOOPSTART 0, and put the seam in a
quiet eighth. The audio is rendered with `render_all.py --act2` and is not committed until Git LFS is live
(ADR 0039).

## Acceptance criteria
- [x] `assets_src/music/act2/mangrove_drowner.py`: G Aeolian (with the spawn's Ab and the D chord's F#), 12/8 at
      62 dotted quarters a minute (Ossa Fen's bar), 20 bars. 1-2 the roots | 3-10 A | 11-12 breakdown (the moan, the
      big draw) | 13-16 B | 17-20 A'. Stem 1 (rooted): the fen pipe theme with a darker pipe an octave below, the
      haul bass, frame and big drums, gourds, the draw, the spawn's moan, a dark pad, and drips. Stem 2 (uprooted):
      six root-knocks a bar (the walk), a high breath flute counter-line, low strings, the rising water, splinters,
      a second drum line, and a sub surge. 77.42 s. p1 810,633 bytes, p2 990,061 bytes. Stack -16.07 LUFS, true
      peak -1.32 dBTP (decoded). Stem 1 alone -18.17 LUFS / -1.13 dBTP, stem 2 alone -20.09. Seam jump x0.23 / x0.39,
      flux x0.22 / x0.19. Both renders identical.
- [x] `assets_src/music/act2/lamp_engine.py`: C minor, 4/4 at 116 BPM (twice Lowlight's 58: the engine's stroke on
      the 1 and the 3), 36 bars. 1-4 the machine starts | 5-12 A | 13-20 B (opens on Lowlight's bound call) | 21-24
      breakdown | 25-32 A' | 33-36 the turn, ending on stem 2's lift. Stem 1 (the housing): a hard low flute theme
      with brass kettle-gong strikes, the escapement ticks and the engine's stroke, ring 1 in dotted eighths, a
      driving 3+3+2 bass, drums, the shears' snip, a dark pad, and the twelve lamps' steady tone. Stem 2 (the core):
      a glass counter-line, then the lift (G4-B4-C5-D5 | Eb5-F5-G5, rising, bars 35-36), the bound dead humming,
      rings 2 and 3 freed, off-sixteenth ticks, a second drum line, low strings, a sub surge, and the core's steady
      light. No held tone swells or beats.
      74.48 s. p1 898,457 bytes, p2 852,910 bytes. Stack -16.05 LUFS, true peak -1.60 dBTP (decoded). Stem 1
      alone -18.08 LUFS / -2.07 dBTP, stem 2 alone -20.28. Seam jump x0.44 / x0.50, flux x0.16 / x0.47. Both renders
      identical.
- [x] Rows in `render_all.py` `ACT2_FINALS`. Nothing under assets/audio/music/act2/ is committed.
      `test_act2_finals` and `validate_data` pass.
- [ ] The Lead adds the music.json and PROVENANCE rows and the `.import` files in the LFS commit (below). The
      battle.encounters rows wait for the Ch10/Ch11 encounters.

## Intended music.json rows
```json
"mangrove_drowner": {
  "stems": [
    "res://assets/audio/music/act2/mangrove_drowner_p1.ogg",
    "res://assets/audio/music/act2/mangrove_drowner_p2.ogg"
  ],
  "start_stems": [0],
  "_note": "Ch10 boss (M3-AUD-844); phase `uprooted` -> stems_on [1] over 3 s"
},
"lamp_engine": {
  "stems": [
    "res://assets/audio/music/act2/lamp_engine_p1.ogg",
    "res://assets/audio/music/act2/lamp_engine_p2.ogg"
  ],
  "start_stems": [0],
  "_note": "Ch11 boss (M3-AUD-844); phase `opened` -> stems_on [1] over 2 s"
}
```
and under `battle.phases`:
```json
"uprooted": {"stems_on": [1], "sec": 3.0, "_note": "M3-AUD-844: the Mangrove Drowner rises on its roots: the walk, the flute and the rising water over 3 s"},
"opened": {"stems_on": [1], "sec": 2.0, "_note": "M3-AUD-844: the Lamp Engine's housing opens (its 2.0 s phase_change): the glass, the dead and the freed rings over 2 s"}
```

## Review log

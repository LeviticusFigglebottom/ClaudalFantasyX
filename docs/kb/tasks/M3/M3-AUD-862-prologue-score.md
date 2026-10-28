---
id: M3-AUD-862
title: "The prologue's score: `prologue_dusk`, an intro that scores the dusk plaza and a quiet loop (ADR 0041)"
role: audio
status: review
owner_session: "audio worktree agent"
reviewer: design
depends_on: [M3-AUD-861]
milestone: M3
request-from: lead
---
## Goal
The prologue is the first scene after the title, and today only its room tone (the `iskarra_dusk` bed) plays
under it. ADR 0041 puts Act I at final quality, so the scene needs its score. The cue is the Hush's first statement
after the title. Ch9's `iskarra_vigil` will later echo it darker.

`prologue_dusk` (`assets_src/music/prologue_dusk.py`) is an intro that scores `prologue_dead_city.dlg` as timed,
followed by a quiet seamless loop. The loop can hold under the line if the player lingers, and the scene's fade-out
and the router's fade take it away.
- MEL_A (hush_theme_v2.py, imported, never retyped) is played in its own register on a single breath flute over a
  low string drone on A. The line splits the phrase. The first half plays while Rhen crosses and ends on its rising
  G as the lantern catches. The lantern brings the cue's first chord (F major seventh), its first warmth.
- Under the line, the 300 Hz to 3 kHz band is left to the voice. Only the drone, the warmth's low F and a glass
  halo play. When the glimmer rises, three rising glass figures (twelve motes) play, and MEL_A's second half
  answers over Dm, Am/C, Esus and E, a half close left open.
- There is no choir and there are no words, samples, recordings or AI audio. Every note is original (SPEC §2).

## Timeline (s)
| t | Scene (.dlg) | Music |
|---|---|---|
| 0–4.5 | `@fade in 3.0`, `@wait 1.5` | the drone on A breathes in |
| 3.0 | | MEL_A's first half, the flute alone |
| 4.5–11.5 | Rhen walks to Asha (the 7 s camera blend), `@wait 1.0` | the phrase continues |
| 12.4 | | the first half's last note, the rising G |
| 12.5–13.9 | `@light LanternLight on 1.4` | the first chord (Fmaj7) blooms, the halo enters; the chord has died away by 14.5 |
| 14.5–19.5 | the narrator's line (about 5 s of VO) | the hollow: the drone, the low F, the halo |
| 19.5 | `@vfx glimmer_lift` | three rising glass figures |
| 19.8–29.3 | `@wait 4.0`, `@fade out 2.5` (23.5–26.0) | MEL_A's second half; the last E is held from 27.3 |
| 30.5 | | **LOOPSTART**: the 24 s loop (the drone, the halo, rising figures at loop 3.0 and 12.5 s) |

Key A minor, 3/4, 72 BPM with rubato (the answer moves at 75 and slows into its last bar). The loop is unmetred.

## Acceptance criteria
- [x] `assets/lfs/audio/music/prologue_dusk.ogg` and its `.loop.json` (ADR 0173) are rendered by the
      `render_all.py` job added after `act1_final_ambience`. The job is
      `python3 tools/audio/render_all.py --only prologue_dusk --determinism`.
- [x] The cue is an intro plus a loop. The file is 54.50 s (2,403,450 samples). The intro is 30.5 s, so
      LOOPSTART = 1,345,050, and the loop is 24.0 s, so LOOPLENGTH = 1,058,400. The Vorbis LOOPSTART and LOOPLENGTH
      tags match the sidecar.
- [x] Stereo Vorbis q3, 462,822 bytes.
- [x] Integrated loudness is −16.00 LUFS over the whole file. The intro measures −13.8 and the loop −22.1 (a quiet
      plaza). Momentary max is −11.29 LUFS, and true peak is −2.57 dBTP.
- [x] The seam jump is x0.20 and the flux x0.52. The intro-to-loop splice residual is −182 dB (the bed is built
      periodic and tiled back from LOOPSTART).
- [x] Deterministic: the second render is byte-identical. The ogg's sha256 starts `81aa7dfa2c6e` and the sidecar's
      `faf00e5841e5`.
- [x] The voice's band (300 Hz–3 kHz) under the line (14.6–19.5 s) is 21.0 dB under the same band during MEL_A's
      first half. In the loop it is 22.5 dB under.
- [x] `validate_data` reports 0 errors. test_audio_data, test_act2_finals, test_music_markers and
      test_act1_audio_audit pass.
- [ ] The main session lands the audio in Git LFS, byte-checked against this render. It also adds the PROVENANCE
      row and the music.json rows below.

## Intended music.json rows
```json
{
  "cues": {
    "prologue_dusk": {"file": "res://assets/lfs/audio/music/prologue_dusk.ogg", "_note": "the prologue (prologue_dead_city.dlg; M3-AUD-862): MEL_A in its own register on a breath flute over a drone on A, split by the narrator's line (the 300 Hz-3 kHz band left clear under it); a 30.5 s intro timed to the scene, then a quiet 24 s loop; plays over the iskarra_dusk bed; Git LFS"}
  },
  "zones": [
    {"scene": "res://game/levels/prologue/prologue.tscn", "music": "prologue_dusk", "_note": "M3-AUD-862: the prologue, the first music after the title; the scene's fade-out and the router's fade take it away"}
  ]
}
```

## Review log

---
id: M2-AUD-03
title: The slice's three final music cues: Haluna by day, battle v2 with the Drownbell, the Hush / cutscene family
role: audio
status: doing
owner_session: "audio (claude/audio)"
depends_on: [M2-AUD-02]
milestone: M2
request-from: lead
---
## Goal
SPEC §10 M2: "three final music cues". The beat sheet (vertical_slice.md §6) names the slice's cues. Self-synthesized, original melodies only (SPEC §2), built on the M1-AUD-02 prototypes and their listening notes. "Final" is the human's verdict (§16 Q3).

## Acceptance criteria
- [ ] (a) `haluna_village`, the town loop by day, and `haluna_night`, its stripped-back night bed (B11).
- [ ] (b) `battle_standard` v2, and `drownbell` as two synchronized stems (phase 1: the bell toll on the downbeat; phase 2 adds low strings and a rising-water swell), switched live on the Flood phase.
- [ ] (c) the Hush family: `hush_first_verse` (Cutscene B, B09, a vocalise-like solo line over a drone, the piano entering on *mir*; plus the B12 piano coda), `haluna_dawn` (Cutscene A), and the `ilun_summon` sting.
- [ ] Loop points (tags, sidecars, .import), −16 LUFS ± 0.5, ≤ −1 dBTP, the file-size budget, import settings; byte-reproducible renders; PROVENANCE rows.
- [ ] listening_notes.md entries the human can judge each cue by.

## Notes

## Notes
- 2026-10-24 audio (claude/audio). Every cue is original (each source's docstring says what the material is) and
  synthesized in-repo; nobody has listened yet. listening_notes.md "M2: the slice's three final cues" asks the
  human the specific questions; the human's verdict decides "final" (SPEC §16 Q3).
  - **(a)** `haluna_village` (75 s loop, 6/8, D pentatonic; flute tune that never lands on D, interlocking
    metallophones, plucked lute through a wooden body, bass, frame drums, gongs) and `haluna_night` (83.5 s loop, the
    same tune slower, flute and drone). Shared material: `assets_src/music/haluna_theme.py`. music.json: Haluna's
    zone row plays the village, and the night after `ch03_drownbell_defeated`; both `resume` after a battle.
  - **(b)** `battle_standard_v2` (v1's composition re-orchestrated: no modelled guitar, no VA lead; metallophone
    stabs, muted plucks, a hard-blown flute twin lead; 3 s intro + 72 s loop) is now the default battle cue (v1 kept
    for A/B). `drownbell`: two synchronized stems (72.7 s loop, C Phrygian, 132 BPM): stem 1 is built on a tower
    bell (new `tools/audio/synth/bells.py`) tolling on the downbeat; stem 2 (low strings, rising water, a sub
    surge, a second drum, a glass line) fades in over 4 s on the Flood phase (music.json battle.phases.flood;
    BattleAudio). Both stems share one gain and one limiter gain curve from the full stack
    (`synth.mixer.limit_gain`), so they sum exactly to the mastered mix.
  - **(c)** `hush_first_verse` (Cutscene B: the Hush's first phrase on a vocalise-like instrument, a breath flute
    through an open-"ah" formant filter, over an A drone; the piano enters on *mir* at 0:28; 80 s), `hush_coda`
    (B12, piano alone, 39 s; end_card's zone row), `haluna_dawn` (Cutscene A: piano and low metallophone between
    D major and B minor, 148 s), `ilun_summon` (a 6 s sting on the Music bus when Ilun is called; battle_sfx.json
    `vowbound_stings`). The sequencer finds the cutscene cues by name in `music_dir`, so its stand-ins no longer
    apply.
  - Loudness: every cue −16 ± 0.1 LUFS integrated, true peak ≤ −1.6 dBTP (the boss stack −16.0; stem 1 alone about
    −18); checked by `render_all.py` (M2_CUES) and `tools/tests/test_audio_loudness.py`. Loops: tags, sidecars,
    .import synced, `test_audio_loops.gd`.
  - Bus balance: each cue's bus gains were set from measured bus loudness (comments above each `render()`).

## Review log

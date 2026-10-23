---
id: M1-AUD-02
title: Three prototype cues plus the §16 Q3 quality check with the human
role: audio
status: review
owner_session: "audio-stream-2"
depends_on: [M1-AUD-01]
milestone: M1
request-from: ""
reviewer: lead
---
## Goal
SPEC §14: escalate early if quality fails.

## Acceptance criteria
- [x] Hush theme, standard battle, temple ambience
- [ ] Samples shown to the human at the end of M1 (brief ready: docs/kb/audio/listening_notes.md)

## Notes
Delivered 2026-10-22 by audio-stream-2.

- Instruments upgraded first, per the M1 top-3 list. The new `synth/grand.py` piano
  has a hammer model, unison strings, two-stage decay, half pedal, a modal soundboard
  and sympathetic resonance. `synth/performance.py` adds rubato, voicing, melody lead
  and a humanized pedal. `ModFDNReverb` replaces the ringing 8-line FDN. Before/after
  numbers are in docs/kb/audio/pipeline.md: the reverb tail went from 15.9 dB to 8.9 dB
  spectral p99/median (ideal is 8.5), and piano decays are now in the physical range in
  all registers (the old model missed in 4 of 6).
- Cues:
  - `hush_theme_v2.ogg`: 69.4 s, −16.1 LUFS, −1.6 dBTP.
  - `battle_standard.ogg`: 3 s intro + 72 s loop, −16.1 LUFS, −1.9 dBTP.
  - `temple_trial.ogg`: 80 s loop, −16.0 LUFS, −3.2 dBTP.
  - Together they are 2.66 MiB. Renders are deterministic.
- Loops carry LOOPSTART/LOOPLENGTH Vorbis comments and `.loop.json` sidecars, which are
  synced into the `.import` files. `tests/unit/test_audio_loops.gd` checks them.
- Self-assessment: Hush 40–50 %, battle 25–35 %, temple 45–55 % of commercial. Weakest
  elements: the distorted guitar (battle) and the synthetic Cantor voice (temple).
  **Nobody has listened yet.** The human's §16 Q3 answer is the remaining criterion.
- No handoff file was written: this session was limited to the audio paths. The Lead
  may want to add one.

## Review log

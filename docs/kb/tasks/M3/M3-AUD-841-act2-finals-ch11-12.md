---
id: M3-AUD-841
title: "Act II finals: lowlight, keth_pass, quellan (Ch11-12 zone loops from the sketches)"
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
Grow three Act II sketches (M3-AUD-804) into their finals, per docs/kb/audio/act2_finals.md: `lowlight` (Ch11),
`keth_pass` and `quellan` (Ch12). Each final keeps its sketch's mode, meter, tempo, palette and themes (it loads the
sketch module and its material; the sketch file and its committed output are untouched), and becomes a 2-3 minute
seamless loop with developed sections. Sources in `assets_src/music/act2/`, rows in render_all.py `ACT2_FINALS`;
the audio stays uncommitted until Git LFS is live (ADR 0039).

## Acceptance criteria
- [x] `assets_src/music/act2/lowlight.py`: C minor, 4/4, 58 BPM, 36 bars. I 1-4 | A 5-8 | B 9-12 | C (the binding)
      13-20 | A' 21-24 | B' 25-28 | D 29-32 | coda 33-36 with the engine's stall. Measured: 148.97 s, 1,389,947 bytes, -15.99 LUFS,
      momentary max -11.68, TP -3.01 dBTP, seam jump x0.72, flux x0.34, renders identical.
- [x] `assets_src/music/act2/keth_pass.py`: E minor, 6/8, 46 dotted quarters a minute, 48 bars. I 1-4 | A 5-12 |
      B 13-16 | A' 17-24 | C (the echo) 25-32 | B' 33-36 | A'' 37-44 | I' 45-48. Measured: 125.22 s, 1,600,272 bytes, -16.05 LUFS, momentary
      max -11.25, TP -2.01 dBTP, seam jump x0.50, flux x0.41, renders identical.
- [x] `assets_src/music/act2/quellan.py`: F major, 4/4, 92 BPM, 48 bars. I 1-4 | A 5-12 | B 13-16 | A' 17-24 |
      C (the weaving-room) 25-32 | B' 33-36 | A'' 37-44 | I' 45-48. Measured: 125.22 s, 1,343,378 bytes, -16.02 LUFS, momentary max
      -12.53, TP -1.47 dBTP, seam jump x0.01, flux x0.64, renders identical.
- [x] Each renders with `python3 tools/audio/render_all.py --act2 --only act2/<cue> --determinism`: Vorbis q3 stereo,
      under 3 MB, -16 LUFS +- 0.5, true peak <= -1 dBTP, the seam clean, the two renders identical.
- [x] Nothing under `assets/audio/music/act2/` is committed (tools/tests/test_act2_finals.py passes);
      `validate_data` passes.
- [ ] Design review; the human's listening verdict (the sketches' verdicts, when they come, apply to these too).

## Review log

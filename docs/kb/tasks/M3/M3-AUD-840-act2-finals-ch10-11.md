---
id: M3-AUD-840
title: "Act II zone finals, Ch10-11: ossa_fen, reedhollow, sunken_vey"
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
Grow the three M3-AUD-804 sketches for Ch10-11 (`ossa_fen`, `reedhollow`, `sunken_vey`, about 60 s each) into
their finals (act2_finals.md): 2-3 minute seamless loops with developed sections. Each keeps its sketch's mode,
meter, tempo, palette and themes, and imports the sketch's material instead of retyping it. The sketches stay
byte-identical. Sources land now. The audio lands with Git LFS (ADR 0039), so no `.ogg`/`.loop.json` is committed.

## Acceptance criteria
- [x] `assets_src/music/act2/ossa_fen.py`: G Dorian, 4/4 at 62, 40 bars. Form: 1-4 channels | 5-12 A (pipe) |
      13-16 B (flute) | 17-24 C, the sway a fourth up, pipe and flute trading, high E natural | 25-28 stillness |
      29-36 A' with a flute counter-line | 37-40 B' with the pipe's echo. **154.84 s, 2,108,823 bytes (q2, as
      the sketch), -16.07 LUFS, TP -2.81 dBTP, seam jump x2.61 / flux x1.17, deterministic.**
- [x] `assets_src/music/act2/reedhollow.py`: the Kirru mode on A, 5/4 (3+2) at 78, 40 bars. Form: 1-4 roost |
      5-10 A | 11-14 B (clutch) | 15-22 C, overlapping whistlers on F#m/B, the harp's second figure | 23-28 A' in
      stretto | 29-34 B', the clutch rising one step further, to G# | 35-38 roost thinning, the head (37) |
      39-40 backs turned. **153.85 s, 1,584,084 bytes (q3), -15.97 LUFS, TP -1.79 dBTP, seam jump x0.35 / flux
      x0.42, deterministic.** The clutch line is kept separate in `CLUTCH_LINES` and `add_clutch`, so it can be
      swapped for the Letting's first cell (act3_plan.md §4 Q2) once that motif exists.
- [x] `assets_src/music/act2/sunken_vey.py`: E-flat Dorian, 3/4 at 46, 40 bars. Form: 1-4 galleries | 5-15 the
      song (as the sketch) | 16 silence | 17-24 C, the cell turned upward, the low glass falling against it,
      resting on C natural | 25-28 the deep (third bell) | 29-36 A'' fully doubled | 37-39 last phrase | 40 silence.
      **156.52 s, 976,636 bytes (q3), -15.99 LUFS, TP -4.52 dBTP, seam jump x0.87 / flux x0.36, deterministic.**
- [x] `tools/audio/render_all.py` `ACT2_FINALS`: one row per cue. `render_all.py --act2 --determinism` gives
      "identical" for all six files. `test_act2_finals` and `validate_data` pass when the uncommitted renders
      aren't on disk (with the renders on disk, the validator flags their missing PROVENANCE rows, which land
      with LFS).
- [ ] Lead: act2_finals.md's Measured column, music.json, PROVENANCE and `.import` rows once LFS is live.

## Review log

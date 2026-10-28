---
id: M3-AUD-843
title: "Act II zone finals, Ch15-16: unlamped, pale_rim, drowned_choir"
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
Grow three Act II sketches (M3-AUD-805) into finals (docs/kb/audio/act2_finals.md): 2-3 minute seamless loops with
developed sections. Each keeps its sketch's mode, meter, tempo, palette and themes, and imports the sketch's material
rather than retyping it. The sketches and their committed output stay as they are. The audio is rendered with
`render_all.py --act2` and is not committed until Git LFS is live (ADR 0039).

## Acceptance criteria
- [x] `assets_src/music/act2/unlamped.py`: E-flat minor, 4/4, 51 BPM, 33 bars. A+B (1-13, the sketch whole) | 14 |
      C over the shoal (15-22: Cb Abm Cb Fb Abm Cb Bb Bb, the flute climbs to Gb5 and is left on D5) | lull
      (23-24) | A' (25-28, motes answer the vigil) | B' (29-32) | 33 = bar 1. 155.29 s, 1,740,086 bytes,
      -16.04 LUFS integrated, momentary max -11.60, true peak -3.28 dBTP, seam jump x1.25, flux x0.64, identical
      on a second render.
- [x] `assets_src/music/act2/pale_rim.py`: E (no third for most of the loop), 4/4, 51 BPM, 33 bars. A (1-13, the
      sketch whole) | 14-15 | C, the white noon (16-22: the glare, the floor on B, the four ahead draw away, near and
      far flutes trade the calls) | 23-26 | A' (27-29, the third call held on G# and falling to the low E) | 30-33
      = bar 1. 155.29 s, 1,679,140 bytes, -16.03 LUFS, momentary max -10.15, true peak -3.82 dBTP, seam jump
      x1.42, flux x0.40, identical.
- [x] `assets_src/music/act2/drowned_choir.py`: A minor, 3/4, 47 BPM, 40 bars. 1-4 the deep | A, MEL_A hummed
      (5-12) | B, the sketch's open vowels and the Cantor's cell (13-16) | A2, MEL_B hummed with the tenors on INNER
      (17-24) | C, the stones on open vowels and the Cantor singing MEL_C (25-30) | the F-E close (31-32) | the
      cell once more (33-36) | 37-40 = bar 1. Words are never sung. 153.19 s, 828,955 bytes, -16.00 LUFS,
      momentary max -8.92, true peak -1.74 dBTP, seam jump x0.59, flux x0.66, identical.
- [x] Each loads its sketch (and the Hush through the sketch) with importlib and leaves the sketch file untouched.
      The rows are in `render_all.py` `ACT2_FINALS`. Nothing under assets/audio/music/act2/ is committed.
      `test_act2_finals` and `validate_data` pass.
- [ ] The Lead adds music.json and PROVENANCE rows and the `.import` files, in the LFS commit.

## Review log

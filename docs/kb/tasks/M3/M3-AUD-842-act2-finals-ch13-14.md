---
id: M3-AUD-842
title: "Act II finals, Ch13-14: ansedra, lamp_archive, peace_wedding"
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
Grow the three Ch13-14 Act II sketches (M3-AUD-805) into their finals (act2_finals.md): 2-3 minute seamless loops
with developed sections, each keeping its sketch's mode, meter, tempo, palette and themes, importing the sketch's
material (the sketch files and their committed output stay byte-identical). The audio waits for Git LFS (ADR 0039):
sources and render_all rows land now, the .ogg and .loop.json files are not committed.

## Acceptance criteria
- [x] `assets_src/music/act2/ansedra.py`: C major, 4/4, 63 BPM, 40 bars. Form: 1-2 intro | 3-10 A court tune | 11-14 B
      motif on glass | 15-16 close | 17-24 C barge song (new) | 25-28 B' motif hummed, glass on the C# only |
      29-36 A' two flutes | 37-40 close via Dbmaj7. Measured: 152.38 s,
      1,650,877 bytes, -16.01 LUFS, momentary max -13.26, TP -3.64 dBTP, seam jump x0.66, flux x0.54, identical.
- [x] `assets_src/music/act2/lamp_archive.py`: D minor, 3/4, 59 BPM, 45 bars. Form: 1-2 ledger | 3-6 A Hush broken off
      | 7-11 canon | 12-14 kept/spent | 15-16 ledger | 17-24 C the roll (new) | 25-28 C' left hand | 29-30 ledger |
      31-35 canon reversed | 36-39 sighs climbing (new) | 40-41 ledger | 42-45 Sefir's motif resolving. Measured:
      137.29 s, 1,246,070 bytes, -16.07 LUFS, momentary max -7.97, TP -1.61 dBTP, seam jump x1.03, flux x0.50,
      identical.
- [x] `assets_src/music/act2/peace_wedding.py`: G major, 3/4, 88 BPM, 64 bars. Form: 1-2 dance | 3-10 A | 11-16 A half
      + close | 17-24 C couple's tune (new) | 25-32 C' zither + flute descant (new) | 33-40 A2 two flutes |
      41-42 dance | 43-46 B, gong begins | 47-50 motif hummed | 51-58 D decline (new), gong on | 59-64 A'.
      Measured: 130.91 s, 1,416,422 bytes, -16.03 LUFS, momentary max -12.29, TP -1.65 dBTP, seam jump x0.73,
      flux x0.47, identical.
- [x] Each imports its sketch with importlib (and V.finish from act2_voices), never edits it; Vorbis q3 stereo, under
      3 MB, -16 LUFS +-0.5, true peak <= -1 dBTP, deterministic (render_all --act2 --determinism: identical).
- [x] render_all.py `ACT2_FINALS`: one row per cue. test_act2_finals and validate_data pass; nothing under
      assets/audio/music/act2/ is tracked.
- [ ] Lead: music.json, PROVENANCE rows, act2_finals.md's Measured column and the .import files with the LFS commit.

## Review log

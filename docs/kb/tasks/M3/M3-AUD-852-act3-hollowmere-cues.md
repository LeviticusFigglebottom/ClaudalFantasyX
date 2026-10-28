---
id: M3-AUD-852
title: "Act III, Ch17: compose hollowmere (the flotilla's zone loop) and dace_ledger (the reading bed)"
role: audio
status: blocked
owner_session: "audio worktree agent"
reviewer: design
depends_on: [M3-AUD-836]
milestone: M3
request-from: lead
blocked-by: ADR 0041
---
## Goal
The first two Act III cues from act3_plan.md §2, for Ch17 "Hollowmere": the Saltwright flotilla's zone loop, and
the through-composed bed under Rhen reading Dace's ledger. Both state Dace's current-song from motifs.py
(CURRENT_SONG, imported, never retyped); `dace_ledger` also imports Ysolde's line (ysolde_theme.py LINE) for its
second half. They render through `tools/audio/render_all.py --act3` into `assets/audio/music/act3/`, which stays
uncommitted until Git LFS is live (ADR 0039).

## Acceptance criteria
- [x] `assets_src/music/act3/hollowmere.py`: D dorian, 3/4 at 76 BPM (CURRENT_SONG_BPM), 57 bars, a 135.00 s
      seamless loop (LOOPSTART 0, LOOPLENGTH 5953500; `downbeat_offset_s` 0.197). Three wrights' mallets on hulls
      and a caulking iron, rope creaks on the swell, the sea and laps, a D-A drone, a string pad, a deck-bass, a
      wright's whistle with CURRENT_SONG fragments and a far whistler, and a low string's lament in the B section
      (bars 21-32, the work thinned to one knock: Liss's father's silence).
      Measured: 1,618,722 bytes, −16.03 LUFS integrated, true peak −1.85 dBTP, seam jump ×1.46, flux ×0.55,
      Vorbis loop tags match the sidecar, `--determinism` identical.
- [x] `assets_src/music/act3/dace_ledger.py`: through-composed, 90.0 s, not looped. A low D pedal and bowed low
      strings, the current-song in five fragments an octave down at a reading pace (none reaches home), Ysolde's
      line three octaves up from 46 s (her bars 1-4, then 5-7, left unfinished), and the last fragment ("sound again,
      and home to D") breaking off on C at 80.3 s with every layer; silent from about 83 s (the blank page).
      The reading band is left light: everything low-passed under ~320 Hz or high-passed over ~2.8 kHz, plus a
      −9 dB cut at 1 kHz on the master; 300 Hz–3 kHz is 0.8 % of the master's spectral energy.
      Measured: 496,557 bytes, −16.04 LUFS integrated, true peak −2.74 dBTP, `--determinism` identical.
- [x] Both rows appended to `ACT3_FINALS` in tools/audio/render_all.py; `python3 -m unittest
      tools/tests/test_act2_finals.py` passes; nothing under `assets/audio/music/act3/` is committed.
- [ ] Design's review (listening): the mallets' level against the whistle in hollowmere's A sections, and whether
      dace_ledger's break at 80.3 s lines up with the ledger's last page in the Ch17 staging (the cue's length can
      move with `T_BREAK`).
- [ ] When LFS is live: the music.json rows below, the PROVENANCE.md rows, and the renders committed (the Lead).

## Intended music.json rows (not yet added: the files are not committed)
```json
    "hollowmere": {
      "file": "res://assets/audio/music/act3/hollowmere.ogg",
      "resume": true,
      "_note": "Ch17, the Hollowmere flotilla and Dace's dry-dock (M3-AUD-852): Saltwright work music, a 135 s loop; the current-song in the wright's whistle"
    },
    "dace_ledger": {
      "file": "res://assets/audio/music/act3/dace_ledger.ogg",
      "_note": "Ch17, Rhen reads Dace's ledger (M3-AUD-852): a 90 s through-composed bed for reading; the 300 Hz-3 kHz band is left light; it breaks off at 80.3 s and ends in silence"
    }
```

## Review log

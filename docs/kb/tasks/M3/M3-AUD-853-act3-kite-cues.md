---
id: M3-AUD-853
title: "Act III: the Kite's cues (the_kite, the Ch18 hub loop; kite_maiden_flight, the first lift-off)"
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
Two of act3_plan.md §2's Ch18 rows. `the_kite` is the hub loop for the Saltwright airship (`ch18/kite`): the
maiden flight, **the world opens** (SPEC §6.6). It is the only open, airborne cue in the game: wind, sail, rigging,
a lifted major, the star-path at last flying home, and Liss's theme in a B section because she flies it. It is lifted
but not triumphant, since the sea below glows with the dead. `kite_maiden_flight` is the first lift-off. It rises
out of Hollowmere's world (D dorian, a Saltwright whistle) into the_kite's A section and ends where the loop can
take over.

## Acceptance criteria
- [x] `assets_src/music/act3/the_kite.py` renders `assets/audio/music/act3/the_kite.ogg` and `.loop.json`. It is
      in D major, 4/4 at 108 BPM, 64 bars, **142.22 s**, a seamless loop (LOOPSTART 0, LOOPLENGTH 6272000; the file
      starts a sixteenth before bar 1). Form: deck 1-4 | A, the star-path, 5-20 | B, Liss's theme, 21-36 | C, the
      sea below, 37-44 | A' 45-60 | deck 61-64. Measured: **1,844,892 bytes**, **-16.05 LUFS** integrated,
      **-1.55 dBTP**, seam jump **x0.75**, flux **x0.74**, Vorbis tags match the sidecar, determinism identical.
- [x] `assets_src/music/act3/kite_maiden_flight.py` renders `assets/audio/music/act3/kite_maiden_flight.ogg`
      (through-composed). It moves from D dorian at 76 BPM to D major at 108 BPM and ends on the_kite's A chord.
      Measured: **46.86 s**, **578,673 bytes**, **-16.04 LUFS** integrated, **-2.27 dBTP**, determinism identical.
- [x] Every tune that recurs is loaded, never retyped. The star-path is haluna_dawn.py `RH_CELL`, with its harmony
      from `LH` bars 5-12. Liss's theme is liss_theme.py `T_A`, `T_A2`, `T_B`, `CHORDS`, `VOICING`, with
      `cittern_body`, `WHEEL` and `paddle`. Dace's current-song is motifs.py `CURRENT_SONG[0]`. The maiden flight
      loads the_kite.py for its A section, voices and voicings. Everything else is original (SPEC §2): no samples,
      recordings or generated audio.
- [x] Both rows are in render_all.py `ACT3_FINALS`. Nothing under `assets/audio/music/act3/` is committed (LFS is
      not live); `python3 -m unittest tools/tests/test_act2_finals.py` passes.
- [ ] Design's review. Does the_kite read as the hub's open, airborne bed and stay lifted but not triumphant?
      Does the maiden flight's lift land with the scene's take-off beat? The lift (C to C# in the whistle, over A)
      falls at about 8.3 s and the star-path enters at 17.4 s.
- [ ] Lead: add the music.json rows below once LFS is live and `ch18/kite` exists.

Intended music.json rows (not added here, since music.json is owned elsewhere and the files are LFS-pending):

```json
    "the_kite": {
      "file": "res://assets/audio/music/act3/the_kite.ogg",
      "resume": true,
      "_note": "Ch18, the Kite (the hub): the star-path flying home, Liss's theme in B, the sea's glow in C; a 142.2 s loop (M3-AUD-853); zone row ch18/kite once it exists"
    },
    "kite_maiden_flight": {
      "file": "res://assets/audio/music/act3/kite_maiden_flight.ogg",
      "_note": "Ch18, the maiden flight's lift-off: from Hollowmere's D dorian whistle (the current-song) into the_kite's A; 46.9 s, through-composed, ends on the A chord so the_kite's bar 1 follows (M3-AUD-853); the sequencer plays it by name, then the_kite"
    }
```

## Review log

---
id: M3-AUD-11
title: Act I route themes: the Brightwater ferry crossing (Ch4) and the Brine Shoals (Ch6)
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio; worktree agents)"
depends_on: [M2-AUD-03]
milestone: M3
request-from: lead
---
## Goal
act_outline.md Ch4: the dawn ferry across Brightwater strait, the drifting drowned trader, Ysolde boarding cold and correct; Ch6: the Brine Shoals, a route of wrecks and mud-flats where the Order's raid burns a Saltwright camp.

## Acceptance criteria
- [x] Two original field loops (−16 LUFS, seamless), distinct from saltgrass_causeway; cue rows; listening notes.

## Notes
- `assets_src/music/brightwater_ferry.py` -> `assets/audio/music/brightwater_ferry.ogg` (+ sidecar, .import). E-flat
  Lydian, 9/8 at 52 dotted quarters, 22 bars, 76.15 s loop. A high breath flute over a hull pad, a rolling rigging
  pluck and a sea swell (one per bar). Ysolde is a damped metallophone playing two even strikes a bar against the
  threes, on the grid (bars 11-14). The derelict is Cb / Ab minor with a dark ship's bell rung off the beat
  (bars 15-18). Decoded: -16.03 LUFS, TP -2.50 dBTP, 974 141 bytes, seam flux x1.64.
- `assets_src/music/brine_shoals.py` -> `assets/audio/music/brine_shoals.ogg` (+ sidecar, .import). C# minor, 5/4
  (3+2) at 66 BPM, 16 bars, 72.73 s loop. A salvage lute with tremolo on long notes, over a muted bass, a low pad and
  mud steps on a large frame drum. The smoke is D over C# (Neapolitan), a large gong and ember crackle (bars 11-14).
  Each lute pitch is evened by `voicing()`, because the body's modes made F#4 ring 10 LU over the median. Decoded:
  -16.04 LUFS, TP -1.56 dBTP, 740 001 bytes, seam flux x2.84 (under the 3x gate, so no downbeat offset; the
  `DOWNBEAT_OFFSET_S` hook is in both files if it is ever needed).
- Bus gains were set from measured bus loudness and confirmed on a re-render (each file's comment above `render()`).
  `--determinism` gives identical output for both files.
- Registered in render_all JOBS and M2_CUES. Cue rows go in music.json `cues` (resume: true; no zone rows until
  `ch04/brightwater_ferry` and `ch06/brine_shoals` exist), LOOPING_CUES, and listening_notes "M3: Act I routes".

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.

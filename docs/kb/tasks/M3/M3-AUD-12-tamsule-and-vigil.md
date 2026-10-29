---
id: M3-AUD-12
title: Tamsule port (Ch7) and the Iskarra vigil act break (end of Ch9)
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio; worktree agents)"
depends_on: [M2-AUD-03]
milestone: M3
request-from: lead
---
## Goal
act_outline.md Ch7: Tamsule, the port of the Tamsule Bell (Reefball), busy and glimmer-lit; Ch9's act break: a Rhen voice-over at the Iskarra vigil (a bed for VO, sparse, leaving room for the voice).

## Acceptance criteria
- [x] Tamsule: an original town loop. The vigil: a through-composed bed (~90 s) under a voice-over, with the voice's frequency range left clear. −16 LUFS; cue rows; listening notes.

## Notes
- `assets_src/music/tamsule.py` -> `music/tamsule.ogg` + `.loop.json`: a 70.0 s seamless loop, 7/8 (2+2+3) in A
  dorian, a quaver every 0.25 s (sidecar bpm 240 counts quavers, bar_beats 7). A hammered dulcimer (three-string
  courses, rolled long notes) over a running lute, bass, frame drums (jingles in A'), glimmer-lamp hum, glass, rigging
  tinks, and the Tamsule Bell (tidecup_match's A2 bell, dark 0.35). B (bars 21-28) is Oruvel's side waiting: the
  Tidecup song's first phrase (our own) re-barred into 7/8 over a heartbeat. Decoded: -16.03 LUFS, TP -1.66 dBTP,
  0.74 MiB (q3.5); seam jump x0.14, flux x0.52. Bar 1 starts 0.625 s into the file (`downbeat_offset_s`): with the
  downbeat (or any quaver onset) on the wrap, render_all's seam flux measured 6-7x the median.
- `assets_src/music/iskarra_vigil.py` -> `music/iskarra_vigil.ogg`: 93.0 s, through-composed, for Rhen's VO. Lows
  under 300 Hz (an A drone, deep water, the Hush's MEL_A two octaves down on dark low strings, three low-passed
  piano octaves), highs over 2.6 kHz (rising glass motes, a halo, the Hush's first cell in the glass once), plus a
  -9 dB cut at 1 kHz (Q 0.45) on the master. Decoded: -16.03 LUFS, TP -2.68 dBTP, 0.52 MiB (q3); the 300 Hz-3 kHz
  band measures -39.9 LUFS against the cue's -16.0 (about 24 LU down).
- Bus gains for both set from measured bus loudness (planned levels in the comment above each `render()`), re-rendered
  and confirmed. `render_all --only tamsule|iskarra_vigil --determinism`: identical. Godot import done, the tamsule
  loop settings synced (beat_count 0); cue rows `tamsule` (resume) and `iskarra_vigil` (no zone rows yet);
  `tamsule` in LOOPING_CUES; listening notes "M3: Tamsule and the Iskarra vigil".
- Checks: validate_data, taskboard --check, test_audio_data, Godot `--filter=audio` (51 run, 0 failed),
  test_audio_loudness (OK).

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.

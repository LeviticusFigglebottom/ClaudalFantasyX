---
id: M3-AUD-823
title: "Act I's `@music` ids: eight point at cues already composed, and the rest are tracked until they land"
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio, session_01Wmj8xaLtwcqiS3qwC6PciW)"
depends_on: [M3-AUD-818]
milestone: M3
request-from: audio
---
## Goal
Act I's scripts call `@music <id>` with ids the Act I cues were never named by. Eight scenes have their cue already
(composed in M3-AUD-04, 10, 11, 12 and 19) under another name, so they played nothing.

## Acceptance criteria
- [x] music.json alias rows, each the original's row with a note: `oruvel_raft` → oruvel, `oruvel_underway` →
      lamp_diver, `haluna_wake` → pilgrims_wake, `brightwater_crossing` → brightwater_ferry, `pemakar_terraces` →
      terraces_of_ash, `ashcrown_trial` → ashcrown, `tamsule_port` → tamsule, `coilspire_flues` → coilspire (this
      replaces the sequencer's temple_trial stand-in).
- [x] tools/tests/test_cutscene_sfx_files.py checks every `@music` id against music.json and the sequencer's
      stand-ins. Its MUSIC_TODO lists the cues still being composed (M3-AUD-819 to 822) and may only shrink.

## Notes
- No new files, so no size cost. `undertow_reach` and `corrow_day` keep their sequencer stand-ins (the boss stems and
  corrow_seawall), which are the right music for those scenes.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.

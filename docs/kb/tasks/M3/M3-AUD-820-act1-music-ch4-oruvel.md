---
id: M3-AUD-820
title: "Act I music: Ch4's hearer_hum, ysolde_theme, name_board_home, the_long_way_round; Ch7's oruvel_theme and tavi_kell"
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio, session_01Wmj8xaLtwcqiS3qwC6PciW; composed by a worktree agent)"
depends_on: [M3-AUD-823]
milestone: M3
request-from: lead
---
## Goal
act1-chapters' M3-C04-05 and M3-C07-06: six `@music` cues the scripts call that didn't exist.

## Acceptance criteria
- [x] `the_long_way_round` (80 s, F major, one note per syllable of the sung lyric; flute stand-in for the village's
      voices). Its markers in seconds, for Cinematics' `@wait music=`: ch04_shell_012 2.20, _013 13.25, _014 25.08,
      _015 35.79, verse_repeat 47.28, _021 57.99, tag 69.16, end 78.18.
- [x] `hearer_hum` (61 s loop), `ysolde_theme` (61 s loop), `name_board_home` (58 s; the star-path is haluna_dawn's
      RH_CELL, imported, not retyped), `oruvel_theme` (Oruvel's tune on one flute, a tone up in A to sit on the
      Bell's hum), `tavi_kell` (33 s solo piano; two notes of Oruvel's tune, never finished).
- [x] Every cue at −16 LUFS ±0.2 with TP ≤ −1.5; deterministic; PROVENANCE; listening notes. 3.2 MiB in all.

## Notes
- For Cinematics: name_board_home and tavi_kell enter 1.2–1.5 s in, after the scripts' 2 s fades.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.

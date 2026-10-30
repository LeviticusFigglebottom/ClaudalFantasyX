---
id: M3-AUD-819
title: "Act I music: Ch1's rhen_current_hum, going_under, undertow_rising (also Ch8); Ch9's corrow_night and dawn_road"
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio, session_01Wmj8xaLtwcqiS3qwC6PciW; composed by a worktree agent)"
depends_on: [M3-AUD-818, M3-AUD-823]
milestone: M3
request-from: lead
---
## Goal
act1-chapters' Ch1 brief and M3-C09-06: the scripts' missing Ch1 and Ch9 cues. Dace's current-song is defined in
motifs.py, and every statement of it uses those notes.

## Acceptance criteria
- [x] `rhen_current_hum`: 15 s, phrase 1 of CURRENT_SONG hummed by Rhen.
- [x] `going_under`: 30 s, the roar falling away, then the whole song far down on the vocalise.
- [x] `undertow_rising`: two stems, a 17.6 s intro (Oruvel's tune stopping mid-phrase) and a 70 s octatonic loop
      with low brass. The second stem is the run's pulse.
- [x] `corrow_night`: a 61 s loop, corrow_seawall's tune slowed over the surf and the Order's hum broken far off.
      It is ch09/corrow_night's zone music.
- [x] `dawn_road`: a 62 s loop on the causeway's walking pulse, slower and older.
- [x] All −16 LUFS ±0.1, deterministic; PROVENANCE; listening notes. 3.2 MiB in all.

## Notes (for act1-chapters / Cinematics)
- **ch01_going_under.dlg cuts the song after phrase 1.** U11 holds `@wait 6.0`, then fades the music, but the
  song's last note lands at 22.9 s. To end on it as the beats doc asks, U11 needs about `@wait 17.4`.
- **The run's pulse (C1-13)** needs a trigger to bring stem 2 in. Ch8 plays stem 1 only, and hears the Oruvel intro
  too: say if Ch8 should skip it (a second cue id or a start offset).

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.

---
id: M3-AUD-828
title: "Act I's zones and bosses play their music: zone rows, encounter rows and the Matron's Pour"
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio, session_01Wmj8xaLtwcqiS3qwC6PciW)"
depends_on: [M3-AUD-827]
milestone: M3
request-from: audio
---
## Goal
The Act I cues' notes said "no zone row until the scene exists" and "no encounter row until the fight exists". The
scenes and encounters have landed, so walking into those zones and starting those fights played no cue of their own.

## Acceptance criteria
- [x] music.json zone rows: ch01 oruvel and oruvel_underway, ch04 haluna_wake (haluna_night, per act1_ch04.md §6)
      and brightwater_ferry, ch05 pemakar and ashcrown, ch06 brine_shoals, ch07 tamsule and tamsule_bell_galleries.
- [x] battle.encounters: ch04_spar_wraith, ch05_cinder_matron, ch06_inquisitor. battle.phases: `pour` brings in the
      Cinder Matron's second stem over 3 s.
- [x] validate_data 0/0; `--filter=audio` passes.

## Notes
- Still to add when its cue lands: ch09 corrow_night (M3-AUD-819). The Ch8 zones and the Undertow's Reach
  encounter are on claude/act1-chapters, not yet here.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.

---
id: M3-AUD-814
title: "FAST-TRACK: villagers' chat and work, gulls, crabs and fish heard in the field (LifeAudio)"
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio, session_01Wmj8xaLtwcqiS3qwC6PciW)"
depends_on: [M3-AUD-802]
milestone: M3
request-from: lead
---
## Goal
The human's playtest ("parts look primitive"): creatures' villagers chat and work, and its wildlife wheels, scuttles
and darts, all in silence. Give them near, positional sound, by listening only (ADR 0031).

## Acceptance criteria
- [x] 44 original synthesized one-shots (assets_src/sfx/life_sfx.py): 12 murmur turns (low and high voices, wordless),
      work foley for the net-mender, the sweeper, the stall and the bowl, near gull calls and takeoffs, crab
      scuttles and fish darts. Deterministic, PROVENANCE rows, 0.6 MiB.
- [x] LifeAudio (game/audio/life_audio.gd) and game/data/audio/life.json: a chat turn murmurs once at its start in
      the speaker's voice; work sounds at the work point every 2.5–5.5 s; a flock calls every 5–13 s and a gull
      taking off claps off; a bolting crab scuttles (0.6 s cooldown per beach); a startled shoal darts. Only within
      30 m of the camera. Never writes what it reads.
- [x] Hooks `pending` until claude/creatures merges (FieldNpc, WildlifeLayer); every member name was checked against
      that branch. data_check validates life.json.
- [x] tests/unit/test_life_audio.gd (stand-ins, 9 tests).

## Notes
- 2026-10-27 audio: two reads are private fields until creatures adds public ones (M3-AUD-815): FieldNpc
  `_chat_speaker` and WildlifeShoal `_startle`. LifeAudio prefers `chat_speaking()` and `startled()` the moment
  they exist, so no audio change is needed then.
- When claude/creatures merges into the integration branch: drop the two `pending` flags in life.json and re-run
  validate_data and `--filter=life`.
- Listen-for notes are in docs/kb/audio/listening_notes.md, "M3: village and wildlife life".

- 2026-10-27 audio, M3-AUD-826 (a follow-up): **villagers' steps.** Each FieldNpc gets its own FootstepAudio
  (footsteps.json with life.json `villager.steps` over it: −9 dB, a 0.45 m stride, cloth but no hero gear, distance
  steps only), advanced only within `hear_m`. test_a_villager_walking_its_route_steps_quietly_without_hero_gear.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.

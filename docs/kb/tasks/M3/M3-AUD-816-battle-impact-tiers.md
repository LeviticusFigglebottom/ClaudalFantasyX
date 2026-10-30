---
id: M3-AUD-816
title: "FAST-TRACK: battle impact tiers and the KO slow-mo, heard (BattleImpact, M3-BPR-401)"
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio, session_01Wmj8xaLtwcqiS3qwC6PciW)"
depends_on: [M3-AUD-803]
milestone: M3
request-from: lead
---
## Goal
The human's playtest: battles looked primitive. Battle-presentation's M3-BPR-401 gave blows hit-stop, shake by
damage and a KO slow-mo, and emits `BattleImpact.landed(target_id, strength, stop_sec)` and
`slowmo_planned(from_sec, sec, factor)` for audio. Give that weight a sound.

## Acceptance criteria
- [x] 10 synthesized layers (assets_src/sfx/impact_sfx.py): medium, heavy and crushing impacts, mostly under
      300 Hz and quieter than the element hit they support (−24, −21 and −19 against the −18 hits), plus the KO
      slow-mo swell (air drawn in and down, a sub swell and one muffled heartbeat).
- [x] ImpactAudio (game/audio/impact_audio.gd), impact_audio.json: tier by strength (0.25, 0.55, 0.85; a light blow
      adds nothing). A hit-stop ducks Music −6 dB for its length plus 0.12 s. The swell plays at the slow-mo's
      start (plan time over the choreography's speed) and Music ducks −9 dB through the slowed time.
- [x] Reduced audio keeps only the heavy tier and the swell.
- [x] Hook `pending` until claude/battle-presentation merges. Checked against that branch: with pending off,
      validate_data passes the class and both signal names.
- [x] tests/unit/test_impact_audio.gd (6 tests); data_check validates tiers, rows and ducks.

## Notes
- 2026-10-27 audio: when claude/battle-presentation merges, drop `pending` in impact_audio.json. The impact plays
  flat on Combat, since the sub layers don't localise. test_battle_ko_once now uses battle-presentation's exact
  lines for the wickfry case, so that merge has no conflict.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.

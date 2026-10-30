---
id: M3-AUD-825
title: "The Ashcrown strike trial heard: the catch, the run along the veins, the landing (AshcrownTrial)"
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio, session_01Wmj8xaLtwcqiS3qwC6PciW)"
depends_on: [M2-AUD-01]
milestone: M3
request-from: audio
---
## Goal
act1-chapters' M3-C05-04 asks audio to "hook the trial's sounds (a run along the veins, the landing) to
AshcrownTrial's `ran` and `landed` signals on the zone root". The trial (Ch5 B08) was silent.

## Acceptance criteria
- [x] 12 synthesized files (assets_src/sfx/ashcrown_sfx.py), on ashcrown.py's copper and ash palette: the catch,
      the studs going dark, the fade, the vein run, grounding and the seal, the landing, gates, plates, the alcove.
- [x] AshcrownAudio (game/audio/ashcrown_audio.gd; the director attaches it to Ch05AshcrownZone, like
      ShrineAudio): listens to the zone's AshcrownTrial, plays a release's run by its outcome, and sounds at
      Greybox/Bowl_<tier> or Greybox/<gate> when the zone has the node. ashcrown_sfx.json is validated by data_check.
- [x] tests/unit/test_ashcrown_audio.gd (3, one on the real zone); `--filter=audio` passes.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.

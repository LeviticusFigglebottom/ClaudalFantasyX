---
id: M3-AUD-801
title: Switch the field and Reefball hooks live: WaterSphereRig, the pending zone beds and voices whose scenes and speakers have landed
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
big7 brought the Reefball sphere rig and more of m2-slice's scenes and speakers.

## Acceptance criteria
- [x] Each pending flag whose class, scene or speaker now exists comes off, validate_data stays 0/0, tests cover the real classes.

## Notes
- 2026-10-24 audio (claude/audio), after big7:
  - **Live:** the WaterSphereRig hook (reefball_hooks.json). The real rig's `radius_m()` matches. Its only scene is
    `_tests/reefball/reefball_test.tscn`; `test_water_sphere` stays leak-free.
  - **Live:** music.json battle `ch01_hullgnaw` → `hullgnaw` (the encounter landed).
  - **Still pending:** the six m2-slice zone beds (their scenes are not on this branch yet), the 17 m2-slice voices
    (their speakers are not here yet), ReefballMatch, ReefballBall and ReefballGoal (no minigame yet), and the zone
    and encounter rows of the other Act I cues (their scenes and encounters are not here yet).
- Tests: tests/unit/test_audio_live_hooks.gd (the real rig is heard: class match, radius, murmur in and out; the
  Hullgnaw mapping). Two runs, no "still in use".

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.

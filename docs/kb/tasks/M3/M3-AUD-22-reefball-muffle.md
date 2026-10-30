---
id: M3-AUD-22
title: Reefball: underwater muffling inside the sphere
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
M3-AUD-17 hears goals and the crowd; inside the water sphere the world should be heard through water.

## Acceptance criteria
- [x] A ramped low-pass on the world/crowd buses while the listener is inside the sphere (data-driven, mix.json); tests.

## Notes
- 2026-10-24 audio (claude/audio): `game/audio/bus_muffle.gd` (BusMuffle, on the director) and mix.json `muffle`
  (World, Ambience, Combat, SFX; 700 Hz; 0.35 s; Music left out). ReefballAudio's `muffle` block
  (reefball_hooks.json) turns `underwater` on while the ear (the camera, else the `player` group) is inside a sphere,
  with the swimmers' wall band. It goes live with gpu/m3-rnd-01-reefball's WaterSphereRig (the hook is pending).
- Also fixed: an intermittent "4 resources still in use at exit" from the reefball tests. The game's autoload heard
  the stand-ins, and the director test started real crowd beds. Stand-ins are now named after entering the tree, and
  the director test records its beds.
- Tests: test_reefball_audio.gd (+2: the ear in and out, the band, the sphere going; the low-pass ramp and switch-off,
  Music untouched); MuffleTest. Checks: validate_data, test_audio_data, Godot `--filter=reefball` (6/0, 4 runs leak-free),
  `--filter=audio`.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.

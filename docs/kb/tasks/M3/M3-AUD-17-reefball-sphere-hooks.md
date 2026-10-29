---
id: M3-AUD-17
title: Reefball crowd and water-sphere sound wired to the gpu/m3-rnd-01-reefball sphere
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio; worktree agents)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
M3-AUD-06 rendered the Reefball sounds; gpu/m3-rnd-01-reefball builds the water sphere.

## Acceptance criteria
- [x] A listener for the sphere (entry, exit, swim, ball contacts) and the crowd beds' crossfade, by class/signal names in data; tests with stand-ins.

## Notes
- `game/audio/reefball_audio.gd` (ReefballAudio) + `game/data/audio/reefball_hooks.json`. The director builds,
  configures and steps it; `_on_node_added` gains two lines before the UI branch. Matching is by script global
  class (or base, or `audio_class` meta); signals are connected by name with has_signal guards, any arity.
- gpu/m3-rnd-01-reefball has only `WaterSphereRig` (a render rig: `radius_m()`, no signals; no ball, goals or
  match). So entry/exit/strokes come from positions: Node3Ds in the `reefball_swimmer` / `player` groups against
  the rig's centre and radius (0.3 m hysteresis, a stroke per 1.6 m, jumps over 4 m not swum). Its arrival brings
  the murmur; its leaving silences the stands (the zone's other beds stay).
- ReefballMatch / ReefballBall / ReefballGoal hooks are pending guesses (kickoff, contacts at the ball, goal +
  cheer/groan, whistles, `naming_rite_started` silences the beds in 0.8 s and the murmur returns after 12 s).
- data_check `reefball_hook_errors` + test; `tests/unit/test_reefball_audio.gd` (4 tests, stand-ins, including the
  director's bound listener). `-- --filter=audio`: 59 run, 0 failed. Docs: audio_runtime.md "Reefball".
- Once that branch merges: drop `pending` on WaterSphereRig; put the arena's swimmers in group `reefball_swimmer`;
  rename the match/ball/goal hooks to the minigame's real classes and signals when it lands.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.

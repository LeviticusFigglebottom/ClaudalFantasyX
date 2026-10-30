---
id: M3-AUD-824
title: "Reefball's sounds on the real ReefballMatch (M3-RBL-01), and the scoring ring's bell"
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio, session_01Wmj8xaLtwcqiS3qwC6PciW)"
depends_on: [M3-AUD-17]
milestone: M3
request-from: audio
---
## Goal
reefball_hooks.json was written before the minigame existed, so it guessed `ReefballMatch`, `ReefballBall` and
`ReefballGoal` and their signals. The engine has landed (game/minigames/reefball/): one headless ReefballMatch with
`contact_started`, `action_resolved(result)`, `float_scored(side, score)` and `match_finished(outcome, score)`.
There are no ball or goal nodes. Ch7's brief also asks for `float_ring_bell`.

## Acceptance criteria
- [x] The ReefballMatch hook is bound to the real signals. The action's row comes from the result's action (rise
      → push, dive → swim, pass → kick, loft → shot), a failed one adds a gasp, and the holder's turn is a catch. A
      float scored plays the score and the ring's bell, with a cheer for the player's side (`player_side`) or a
      groan. A win or a loss adds a cheer or a groan before the end whistle. The two guessed hooks are gone.
- [x] ReefballAudio: `holder_property` watches the node that holds a headless match (it may arrive before its
      match); `by` picks sub-actions from a signal argument, a Dictionary key, or a comparison with the object's
      property. data_check validates `by`.
- [x] `reefball_float_ring_bell`, synthesized (reefball_sfx.py), at −18 LUFS like the other world SFX.
- [x] tests/unit/test_reefball_audio.gd drives the real match through a holder; the crowd and argument mechanics
      keep their tests on a local table. `--filter=reefball` 55/0, `--filter=audio` 147/0.

## Notes
- No scene holds a match yet: the Tidecup's arena and UI are another track's. Whatever node holds it as `match`
  will be heard with no audio change. If its property has another name, change `holder_property`.
- The kick-off whistle and the naming rite are now the scenes' own (`ch07_naming.dlg` and its `@sfx`).

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.

---
id: M2-BPR-11
title: "Playtest fix: a felled foe's KO replayed on every later move, and its faint ghost stayed"
role: combat
status: review
owner_session: battle-presentation (session_014EcW9e5tEmjDi5S2HmCECd)
depends_on: [M2-BPR-01]
milestone: M2
request-from: lead
reviewer: lead
---
## Goal
The human's playtest on the integration branch (07781cba): a defeated enemy's greyed-out body stayed after the kill
and replayed its death animation on every later move. Fix it at the root: the KO plays once, the fallen foe fades
and is removed, and later beats skip it. Also check whether any presentation path plays one action twice.

## Acceptance criteria
- [x] Root cause found and fixed: BattleStage.refresh_ko calls `set_stone(false)` on every fighter after every
      action, and `CreatureActor.set_frozen(false)` called `AnimationPlayer.play()` whenever the player was idle,
      which restarts a finished KO clip. set_frozen now ignores a repeat and resumes only a clip Petrify paused.
- [x] A fallen foe fades out and is hidden (`battle_sandbox.json` `foe_ko_alpha` 0); the party keeps `ko_alpha`.
- [x] Regression test `tests/unit/test_battle_ko_once.gd`: fell one foe, three more actions, the KO clip started
      exactly once and the foe is hidden; for a creature model and a primitive stand-in; revive and Petrify still
      work. The test fails without the fix (2 KO starts).
- [x] "Enemies act twice", presentation side: one plan per `action_resolved` (a new action finishes the old one);
      the VFX connect to the contact beat or `action_resolved`, never both; placeholder clips skip creatures; no
      creature has a `ready` clip that would read as a second move. The replayed KO itself (a fallen foe moving on
      every later turn) is the likely source of that report. The engine side is the Lead's combat agent's.

## Notes
- Files: game/creatures/creature_actor.gd (creatures' file: set_frozen, the fade's hide), game/battle/scene/
  fighter_stand_in.gd, game/battle/scene/battle_stage.gd, game/data/ui/battle_sandbox.json, the test, the doc.

## Review log

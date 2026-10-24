---
id: M2-CRE-03
title: "Battle integration: enemies.json model field, the creature actor on the stage, validator and tests"
role: character
status: review
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: art
depends_on: [M2-CRE-02]
milestone: M2
request-from: lead
---
## Goal
An enemies.json `model` field that the battle stage turns into the actor scene (built on M2-UI-07's FighterStandIn "scene" hook), with clips played on attack, cast, hit, KO and phase change, falling back to the primitive. BattleVfx/BattleBossVfx anchors still land on the rim, polyps and toll. validate_data.py checks the field. Tests.

## Acceptance criteria
- [x] See Goal; the notes record what shipped.

## Notes

- 2026-10-24: enemies.json `model` (reef_crab, lantern_eel, gull_harrier, drownbell, spawn_polyp) → CreatureModels → BattleStage.stand_in_spec `scene` (the UI track's M2-UI-07 hook, cherry-picked verbatim) plus creatures.json `stand_in`; CreatureActor plays clips from game/data/creatures/creatures.json; BattleActorMotion (attached in BattleStage.spawn, battle_controller.gd untouched) drives action, hit, phase and breakable-part clips from the engine's signals; KO and Petrify reach the actor through refresh_ko. The spec height (battle_sandbox.json) still places damage numbers and the BattleVfx/BattleBossVfx anchors (rim 0.29 m on the bell, chest on the polyps, the toll at the feet): checked in drownbell_flood. tools/validate_creatures.py (called by validate_data.py). tests/unit/test_creature_actor.gd (13 tests, including a live sandbox battle and a live Drownbell fight that breaks the rim and floods the bell). Coverage within the baseline (battle 99.95%).

## Review log

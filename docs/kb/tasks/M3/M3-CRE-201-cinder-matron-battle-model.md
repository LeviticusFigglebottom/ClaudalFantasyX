---
id: M3-CRE-201
title: "enemies.json: give cinder_matron its battle `model` so the Crust presentation shows in play"
role: character
status: done
owner_session: "creatures (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY)"
depends_on: [M3-CRE-04]
milestone: M3
request-from: ui
---
## Goal
`game/creatures/cinder_matron/cinder_matron_battle.tscn` exists, but the `cinder_matron` row in
`game/data/battle/enemies.json` has no `"model"`. So in a real fight she is a primitive stand-in. M3-C05-07's Crust
hook (`BattlePartCues`, `part_cues.cinder_matron` in `game/data/ui/battle_sandbox.json`) then has no Crust part to
show or hide. Its tests add the model to `CreatureModels.models()` only while they run.

## Acceptance criteria
- [x] `cinder_matron` names her model (already on the integration branch: enemies.json `model` res://game/creatures/cinder_matron/cinder_matron_battle.tscn), as the other creature rows do (`"model"` → `CreatureModels`).
- [x] The Ch5 boss shots (if any) are re-approved after viewing (battle_boss_intro_matron is in the creatures RENDER-REQUEST of 2026-10-27).
- [x] `tests/unit/test_battle_part_cues.gd` still passes (6/0, 2026-10-27). It can then drop its temporary model registration (UI will
      do that once this lands).

## Review log
- 2026-10-27, creatures: closed; the model line had landed with m2-slice's Act I `model` lines (big8). UI can drop the test's temporary registration.

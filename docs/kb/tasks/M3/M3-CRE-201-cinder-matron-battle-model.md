---
id: M3-CRE-201
title: "enemies.json: give cinder_matron its battle `model` so the Crust presentation shows in play"
role: character
status: todo
owner_session: ""
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
- [ ] `cinder_matron` names her model, as the other creature rows do (`"model"` → `CreatureModels`).
- [ ] The Ch5 boss shots (if any) are re-approved after viewing.
- [ ] `tests/unit/test_battle_part_cues.gd` still passes. It can then drop its temporary model registration (UI will
      do that once this lands).

## Review log

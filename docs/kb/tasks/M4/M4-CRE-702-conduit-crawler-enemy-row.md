---
id: M4-CRE-702
title: "The conduit crawler's enemies.json row (its model, clips and portrait are built)"
role: combat
status: review
owner_session: "claude/creatures"
depends_on: [M4-A2P-022]
reviewer: character
milestone: M4
request-from: character
---
## Goal
Add `conduit_crawler`'s enemies.json row as part of M4-A2P-022: the repairing add with its `crawler_mend`, on the Lamp
Engine's `ch11_lamp_engine`. Its row has `"model": "res://game/creatures/conduit_crawler/conduit_crawler_battle.tscn"`.
The creatures track built it from the beat sheet and act2_roster: a salt-glass dome on six jointed brass legs, its bound light dim inside, a brush and a wiper on its fore-arms (LORE_CONDUIT_CRAWLER).
That covers the mesh, the jointed legs (563eda19), the clips (idle, attack, cast, hit, ko and its mend), the portrait,
the creatures.json row and the review shot. Once the row lands, the creatures track checks it in the arena the same hour.

## Acceptance criteria
- [x] `conduit_crawler` in game/data/battle/enemies.json with `name_key`/`lore_key` (ENEMY_/LORE_CONDUIT_CRAWLER,
      M4-A2P-009) and the `model` key above.
- [x] validate_data and `--filter=battle` green.

## Notes
- Filed by claude/creatures on the Lead's direction (2026-10-30, 14:28): ask act1-chapters for the row.
- 2026-10-30 (claude/creatures): the row landed with M4-A2P-022 (fc316eda4, on the integration branch at efe7fb10d) with
  the `model` key. Wired up: creatures.json `clip_by_skill` maps `brush_jab` to attack (the brush arm jabs),
  `crawler_mend` to cast (it relights the part) and `crawler_tend` to idle_b (it tends and pays the party no mind), with
  their contact times. Godot creature 159/0. As played in `ch11_lamp_engine`, a dark slab of the arena covers the
  enemy half of the frame, so the crawlers and the engine barely read. That is the arena's or battle presentation's
  framing, reported to the Lead. Ready for review by **character**.

## Review log

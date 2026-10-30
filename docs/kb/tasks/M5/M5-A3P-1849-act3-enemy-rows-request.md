---
id: M5-A3P-1849
title: "Request: enemies.json rows and encounters for the creatures lane's Act III regulars"
role: combat
status: todo
owner_session: ""
depends_on: []
milestone: M5
reviewer: character
request-from: character
---
## Goal
The creatures lane has built the Act III regulars from the Act III bestiary (docs/kb/art/creatures/act3_roster.md,
"Reconciled with the Act III beat sheets"), each with a creatures.json row, clips and a portrait. None has an
enemies.json row yet, so none can be fought or listed in the bestiary. Each row's `model` is the battle scene below; the
creature row is found by that scene (`CreatureModels.creature_for_scene`).

| Chapter | Creature | Model scene | Notes |
|---|---|---|---|
| 19 | `wick_crawler` | `res://game/creatures/wick_crawler/wick_crawler_battle.tscn` | act3/wick_crawler.md |
| 19 | `chain_lamp` | `res://game/creatures/chain_lamp/chain_lamp_battle.tscn` | act3/chain_lamp.md (weak point `shackle`) |
| 19 | `spire_moth` | `res://game/creatures/spire_moth/spire_moth_battle.tscn` | act3/spire_moth.md (the flue moth's seam) |
| 19 | conduit crawler, Act III | `res://game/creatures/conduit_crawler/conduit_crawler_battle.tscn` | a new enemy id (e.g. `spire_conduit_crawler`), the cheapest regular; same model and creatures.json row (act2/conduit_crawler.md, "Act III use") |
| 20 | `held_shoal` | `res://game/creatures/held_shoal/held_shoal_battle.tscn` | act3/held_shoal.md (`idle_turned` for its untargetable phase) |
| 20 | `drowned_lantern` | `res://game/creatures/drowned_lantern/drowned_lantern_battle.tscn` | act3/drowned_lantern.md (weak point the globe's seam) |
| 17 | `deep_scuttler` | `res://game/creatures/deep_scuttler/deep_scuttler_battle.tscn` | optional, the outer moorings (x3 per the roster default) |
| 17 | `hull_rasp` | `res://game/creatures/hull_rasp/hull_rasp_battle.tscn` | optional, a single foe that rewards breaking its part first |

## Acceptance criteria
- [ ] An enemies.json row per creature (`act: 3`, localization keys, stats, skills, AI), with `model` set as above.
- [ ] Their encounters in the Ch17, Ch19 and Ch20 zones, per the roster.

## Review log

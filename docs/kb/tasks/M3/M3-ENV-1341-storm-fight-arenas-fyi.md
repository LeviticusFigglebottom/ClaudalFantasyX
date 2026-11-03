---
id: M3-ENV-1341
title: "FYI/offer: the storm fights' arena variant is applied battle-side (BattleStorm); bake a storm grade if wanted"
role: environment
status: todo
owner_session: ""
depends_on: [M3-BPR-451]
milestone: M3
request-from: combat
---
## Goal
The human's playtest (11-03) item 4: the storm fights used the normal backdrop. battle-presentation's BattleStorm
(M3-BPR-451) turns the arena into its storm variant at spawn without touching the arena scenes: oruvel_raft_morning
(ch01_scuttlers, ch01_hullgnaw) takes the Oruvel storm environment; coilspire_headland_path, coilspire_tier_landing
and seawall_stairhead_storm/hoist get their sky shader's storm params; all get rain, wind and the Undertow behind.

## For env-art-b and act1-chapters
- act1-chapters: confirm the fight list in game/data/vfx/battle/storm_fights.json `fights` (add any storm fight I
  missed by request; ch06_ridge_gulls is calm, so it is left out).
- env-art-b: if a storm arena wants its own art-directed grade, write it as an Environment .tres and name it in that
  look's `environment_res` (or ask me to).

## Review log

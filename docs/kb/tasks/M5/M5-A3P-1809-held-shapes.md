---
id: M5-A3P-1809
title: "Ch20: the held shapes, the memory layers' townsfolk as held light (crowd silhouettes per layer)"
role: character
status: blocked
blocked-by: "the Ch20 zones (U01–U04) and their locations.json ids don't exist yet (environment / world track)"
owner_session: ""
depends_on: []
milestone: M5
reviewer: character
---
## Goal
ADR 0207, Act III bestiary (docs/kb/art/creatures/act3_roster.md, Ch20 "held shapes"): "held shapes buying and
selling", the remembered townsfolk as held light in the memory layers (U01 market, U02 terrace, U03 kitchen, U04
Reefball crowd). Crowd bodies in the silhouette mode (VillagerLayer `silhouette`, M3-HER-1142) in `glimmer_held`, no
faces or tints, posed in the layer's activity (the market's work clips, the Reefball crowd's roar). A crowd-generator
pass per layer, no new mesh. The Reefball layer needs 30+, so a cheap MultiMesh path for distant rows.

## Acceptance criteria
- [ ] Per layer: a villagers zone file of silhouette rows in the layer's activity, validated.
- [ ] U04: a MultiMesh path for distant rows (one draw call per body), within the hitch bar.
- [ ] Tests (tools test_npc; Godot villager/crowd) and a review shot per layer, viewed.

## Review log

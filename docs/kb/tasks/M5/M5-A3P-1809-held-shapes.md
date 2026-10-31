---
id: M5-A3P-1809
title: "Ch20: the held shapes, the memory layers' townsfolk as held light (crowd silhouettes per layer)"
role: character
status: doing
blocked-by: "the per-layer rows wait on the Ch20 zones (U01–U04) and their location ids (environment / world track)"
owner_session: "creatures (claude/creatures)"
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
- [x] U04: a MultiMesh path for distant rows: CrowdFar (flipbook poses, one draw call per body and pose), with the crowd clip `cheer`. Threaded by default: worst frame 48 ms, in after 1.05 s on the review stage (5.3 s on the main thread before).
- [ ] Tests (tools test_npc; Godot villager/crowd) and a review shot per layer, viewed.

## Review log
- 2026-10-31 creatures: the unblocked part is built: CrowdFar (game/world/npc/crowd_far.gd; docs/kb/tech/field_npc.md "Distant crowds"), the crowd `cheer` clip (adult library, `extra`), review stage `held_shapes_reefball` (32 held shapes, viewed), tests test_crowd_far 3/0, crowd 24/0, tools test_npc OK. Blender: the adult library rebuilds identical; crowd_man_medium_b's mesh, texture and brow drift is pre-existing (same 6 diffs without this change). The per-layer rows wait on the zones.
- 2026-10-31 creatures: CrowdFar builds off the main thread (threaded actor loads, pose on the main thread, skin on the WorkerThreadPool). Worst frame 48 ms, crowd in after 1.05 s (4 cores, headless). `threaded = false` for the review shot. test_crowd_far 4/0 (a threaded build matches the one at once), crowd 25/0.

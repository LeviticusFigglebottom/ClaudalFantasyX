---
id: M5-A3P-1807
title: "Ch19: the conduit crawler's Act III use on the Lamp Spire (the built model, a creatures.json level/palette row)"
role: character
status: review
owner_session: "creatures (claude/creatures)"
depends_on: []
milestone: M5
reviewer: character
---
## Goal
ADR 0207 (the human's directive, 2026-10-30): Act III production in the creatures lane, from the Act III bestiary
(docs/kb/art/creatures/act3_roster.md, "Reconciled with the Act III beat sheets"). `conduit_crawler`: real mesh, rig, clips and
portrait at the Act I bar (procedural and reproducible, byte-identical Blender build, PROVENANCE rows, ADR 0204 world
rules, banned_terms), a creatures.json row, the clip audit passing, and a review shot.

## Acceptance criteria
- [x] Built from source (assets_src/creatures/conduit_crawler/), verified byte-identical, with PROVENANCE rows.
- [x] creatures.json row, clips (idle, idle_b, attack, hit, hit_b, ko and its own), the clip audit clean.
- [x] Portrait and a review shot, viewed.
- [x] Tests (tools test_creatures; Godot creature filter).

## Review log
- 2026-10-30 creatures: reused as built (same model and creatures.json row; the enemies.json row is requested from Combat in M5-A3P-1849). Brought to the Act I bar: planted feet and no brush drag, so the clip audit is clean; byte-identical, tools tests OK, Godot creature filter 160/0, portrait re-rendered, shot viewed. The shot differs from its baseline by the earlier leg rework (563eda19e) as well; the shots session recaptures it.

---
id: M5-A3P-1803
title: "Ch20: the held shoal, a school of held light (act3/held_shoal.md)"
role: character
status: todo
owner_session: ""
depends_on: []
milestone: M5
reviewer: character
---
## Goal
ADR 0207 (the human's directive, 2026-10-30): Act III production in the creatures lane, from the Act III bestiary
(docs/kb/art/creatures/act3_roster.md, "Reconciled with the Act III beat sheets"). `held_shoal`: real mesh, rig, clips and
portrait at the Act I bar (procedural and reproducible, byte-identical Blender build, PROVENANCE rows, ADR 0204 world
rules, banned_terms), a creatures.json row, the clip audit passing, and a review shot.

## Acceptance criteria
- [ ] Built from source (assets_src/creatures/held_shoal/), verified byte-identical, with PROVENANCE rows.
- [ ] creatures.json row, clips (idle, idle_b, attack, hit, hit_b, ko and its own), the clip audit clean.
- [ ] Portrait and a review shot, viewed.
- [ ] Tests (tools test_creatures; Godot creature filter).

## Review log

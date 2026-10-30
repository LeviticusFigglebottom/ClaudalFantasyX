---
id: M5-A3P-1806
title: "Ch17: the hull rasp, a hullgnaw variant boring the flotilla's keels (act3_roster.md, reconciled)"
role: character
status: review
owner_session: "creatures (claude/creatures)"
depends_on: []
milestone: M5
reviewer: character
---
## Goal
ADR 0207 (the human's directive, 2026-10-30): Act III production in the creatures lane, from the Act III bestiary
(docs/kb/art/creatures/act3_roster.md, "Reconciled with the Act III beat sheets"). `hull_rasp`: real mesh, rig, clips and
portrait at the Act I bar (procedural and reproducible, byte-identical Blender build, PROVENANCE rows, ADR 0204 world
rules, banned_terms), a creatures.json row, the clip audit passing, and a review shot.

## Acceptance criteria
- [x] Built from source (assets_src/creatures/hull_rasp/), verified byte-identical, with PROVENANCE rows.
- [x] creatures.json row, clips (idle, idle_b, attack, hit, hit_b, ko and its own), the clip audit clean.
- [x] Portrait and a review shot, viewed.
- [x] Tests (tools test_creatures; Godot creature filter).

## Done (2026-10-30)
As built: act3_roster.md "As built". Verified byte-identical; tools test_creatures OK; Godot creature 160/0; shot and
portrait viewed. For Combat: an enemies.json row (the hullgnaw's skills, scaled) and the Ch17 moorings encounter
(`hull_rasp` alone, per the roster's default).

## Review log

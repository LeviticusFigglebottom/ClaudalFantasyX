---
id: M5-A3P-1805
title: "Ch17: the deep scuttler, the Act I scuttler grown darker on the outer moorings (act3_roster.md, reconciled)"
role: character
status: review
owner_session: "creatures (claude/creatures)"
depends_on: []
milestone: M5
reviewer: character
---
## Goal
ADR 0207 (the human's directive, 2026-10-30): Act III production in the creatures lane, from the Act III bestiary
(docs/kb/art/creatures/act3_roster.md, "Reconciled with the Act III beat sheets"). `deep_scuttler`: real mesh, rig, clips and
portrait at the Act I bar (procedural and reproducible, byte-identical Blender build, PROVENANCE rows, ADR 0204 world
rules, banned_terms), a creatures.json row, the clip audit passing, and a review shot.

## Acceptance criteria
- [x] Built from source (assets_src/creatures/deep_scuttler/), verified byte-identical, with PROVENANCE rows.
- [x] creatures.json row, clips (idle, idle_b, attack, hit, hit_b, ko and its own), the clip audit clean.
- [x] Portrait and a review shot, viewed.
- [x] Tests (tools test_creatures; Godot creature filter).

## Done (2026-10-30)
As built: act3_roster.md "As built". Verified byte-identical (2 outputs); tools test_creatures OK; Godot creature 160/0;
the shot viewed (the wounds tuned to small, sharp openings after the first render showed none, the second patches).
For Combat: an enemies.json row and the Ch17 outer moorings encounter (`deep_scuttler` x3, per the roster's default).

## Review log

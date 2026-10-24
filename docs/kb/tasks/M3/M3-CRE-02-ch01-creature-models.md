---
id: M3-CRE-02
title: "Ch1 creature models: Hullgnaw, wickfry, tower limpet, oil slug"
role: character
status: review
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: art
depends_on: [M3-CRE-01]
milestone: M3
request-from: lead
---
## Goal
The four Ch1 creatures from docs/kb/art/creatures/act1/ through the creature pipeline (docs/kb/art/creatures/pipeline.md):
build, materials, battle scene, creatures.json row, job, provenance, a review shot. `"model"` goes on their enemies.json
rows once m2-slice adds them (M3-C01-02).

## Acceptance criteria
- [x] hullgnaw (first pass: 5.4k triangles, 17 bones, the five clips; review shot creature_hullgnaw)
- [x] wickfry (first pass: 44 glass shrimp on their own bones, 7k triangles, 46 bones; the cloud fists on attack, rings on cast, falls on KO)
- [x] tower_limpet (first pass: 8.5k triangles, 3 bones, the five clips; review shot creature_tower_limpet)
- [x] oil_slug (first pass: 4.2k triangles, 9 bones, the five clips; review shot creature_oil_slug)

## Notes
- 2026-10-24: all four have first passes, each with a creatures.json row, a byte-identical job, PROVENANCE rows and a review shot (`creature_<id>`). None has an enemies.json row yet: m2-slice adds the rows (M3-C01-02), and the `model` line goes on them then. Battle stand-in specs (height, hover) also come with those rows: build heights are Hullgnaw 3.0 m, wickfry a cloud centred at 1.0 m, tower limpet 0.55 m, oil slug 0.3 m.

## Review log

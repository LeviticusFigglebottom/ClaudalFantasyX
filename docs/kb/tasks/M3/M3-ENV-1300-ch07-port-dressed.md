---
id: M3-ENV-1300
title: Ch7's port (ch07/tamsule) dressed with env-art's port pieces, its river water, the Bell at z -75
role: environment
status: review
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC)"
depends_on: []
milestone: M3
reviewer: cinematics
---
## Goal
ADR 0041: `ch07/tamsule` was the last undressed Ch7 zone (act1-chapters waited on env-art's port kit, M3-C07-04).
Dress it from env-art's port preview (`port_preview.pieces()`), keep the greybox as the walk (ADR 0200), and make
the river water instead of a floor 1 m down.

## Acceptance criteria
- [x] `tools/act1/ch07_tamsule_port_dressing.py` writes `tamsule_dressing.json` and `tamsule_collision.json` (rails
  on every open deck edge); the zone's Water, riverbed and Tide; the galleries' Ch7 noon sun and grade.
- [x] The Bell's mark and T08/T09 look at the kit's ring at (0, -1.6, -75) (`--relayout`, once).
- [x] `test_ch07_port_walkable` (routes, people on decks, rails); `--filter=ch07` and the cutscene-walk audit green.
- [x] Shots `ch07_tamsule_mouth`, `_market`, `_gantry` self-rendered and viewed (no baselines written).

## Notes
- Liss and Kerrid still show as capsules: no field body yet (characters / hero-integration), not kit.

## Review log

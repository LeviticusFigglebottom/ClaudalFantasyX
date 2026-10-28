---
id: M3-ENV-1303
title: Ch5 Ashcrown (ch05/ashcrown) on env-art's Ashcrown kit, its trial on the top four tiers, its steep flights walked (M3-C05-1215)
role: environment
status: review
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC)"
depends_on: [M3-ARC-1216]
milestone: M3
reviewer: cinematics
---
## Goal
The last fully greybox Act I zone. act1-chapters' M3-C05-1215 was blocked on the kit's 48° and 60° flights;
hero-integration's steep-stair traversal (M3-ARC-1216, ADR 0193, `claude/hero-integration` @ bccce923) unblocks it.

## Plan
- The kit's frame is the zone's: the pilgrims' causeway (B07: StairFoot at its foot, the Tenders' gate at its head),
  the forecourt, the flying stair (HeroStairs) to the crown (tier 6, y 42: the pavilion, the catch-spire, t1), the
  trial down tiers 5, 4, 3 (t2..t4) by the vein stairs, the anvil hall (the court: the anvil, the Matron's alcove, the
  chamber door, the hall door to the sea as the arch).
- Story pieces from the kit's `b_trial.py` (built), Pemakar's graves for the Tenders' graves.
- The view lights the bowl pieces and turns the gate pieces (ZoneKitDressing followers).
- Collision from the kit (treads, ambulatories, hall), flights as HeroStairs rows, walk tests, shots A01–A08.

## Notes (2026-10-28, env-art-b)
- Done as planned, plus the day arenas (`assets_src/environments/kits/ashcrown/b_arenas.py`: `ashcrown_forecourt_day`,
  `ashcrown_anvil_court`) and request M3-BPR-1305 to repoint the Ch5 encounters onto them.
- `--relayout` moved every story point into the kit's frame; act1-chapters should re-read the layout's marks before
  editing B07–B10 staging. The zone map's POIs and bounds follow (`game/data/ui/zone_maps.json`). The map still draws
  only the layout's blocks, and the floors now live in `ashcrown_collision.json`, so the map is sparse (a UI request is
  noted in the live log).
- Tests: `--filter=ashcrown` 22/0, `cutscene_walks` 1/0, `battle_arenas` 10/0, `hero_stairs` 7/0, `zone_kit` 10/0.
  Self-rendered: ch05_ashcrown_{causeway,forecourt,crown,tiers,court}, battle_arena_ashcrown_{forecourt_day,anvil_court}.

## Review log

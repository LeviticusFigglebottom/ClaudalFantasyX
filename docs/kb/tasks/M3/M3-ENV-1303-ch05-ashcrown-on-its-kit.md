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
- 2026-10-29 cinematics (act1-chapters): viewed in a flow-order stills pass (`tools/act1/cutscene_stills`, every Ch5
  Ashcrown scene). The kit reads: the causeway, the gate's arch, the crown pavilion and catch-spire (A04), the anvil
  hall with the Matron's alcove (A07, A08), the chamber door (A10). Story cameras re-staged on my side after the
  relayout (A02 aimed 20 m off the party; A11 stood behind Kahre's heart looking out at the void; A12 tilted into the
  ceiling), plus Kahre's own body behind the shut door for A11 and `chamber_in` in front of the door. Hand edits in
  `ashcrown_layout.json` (shots A02/A11/A12, marks `chamber_in`, `kahre_bound_at`, actor `kahre`): keep them if you
  re-run `--relayout`. Field POIs still to re-check (act1-chapters). Verdict: approved for the kit.

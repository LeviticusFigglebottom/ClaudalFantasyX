---
id: M3-ENV-1303
title: Ch5 Ashcrown (ch05/ashcrown) on env-art's Ashcrown kit, its trial on the top four tiers, its steep flights walked (M3-C05-1215)
role: environment
status: doing
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

## Review log

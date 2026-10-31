---
id: M5-A3P-1402
title: "Ch20 Undertow: the rest landing (R1, R2: a landing between the layers)"
role: environment
status: review
owner_session: "claude/env-art"
depends_on: [M5-A3P-1400]
reviewer: art
milestone: M5
request-from: lead
---
## Goal
act3_ch20's two rests, R1 ("the party, fewer lights") and R2 ("the Vowbound menu, one name left"), and the chapters'
M5-A3P-1011 ("the two rests") need a place between the floors: a small island landing, not a remembered room. Add
`memory_landing` to undertow_layers.py:
- a small fragment of Iskarra's flags (r 3.5) with its hanging root;
- a curved stone bench for the party;
- a short held-light post, one steady cyan lamp. The rest is quieter than the rooms.

The well the Kite drops down (U00) can use `heart_eyewall` (undertow_heart.py) scaled down. That's for the chapters'
staging; no new piece.

## Acceptance criteria
- [x] `memory_landing` built within 4k / 300 triangles, with glb, import, PROVENANCE row and manifest row; the
      undertow_layers.md table updated.
- [x] Viewed; the floor is flat at y 0 where the party stands; tests extended.

**Done (env-art, 2026-10-31):**
- memory_landing: 1754 / 274 triangles, with glb, import, PROVENANCE row and manifest row.
- It hangs in the undertow_cage arena at (-14, 16, -46).
- Viewed at a walker's eye and from away.
- test_undertow_layers checks that the floor is flat round the middle and the light is held only.

## Review log

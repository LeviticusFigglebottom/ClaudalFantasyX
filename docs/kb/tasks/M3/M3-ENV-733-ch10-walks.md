---
id: M3-ENV-733
title: "Ch10's walks: Ossa Fen's root-walks, Reedhollow's reed causeway and platforms, the clutch's stone, and the greybox swap map"
role: environment
status: blocked
blocked-by: ADR 0041
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-718]
milestone: M3
reviewer: cinematics
---
## Goal
The Lead's backlog item 4 (10-28): Act II zone kits for act1-chapters' Ch10–12 greybox. The Ch10 greybox
(M4-C10-02, on claude/act1-chapters) walks on 3.6 m root-walks and reed causeways, and the fen kit (M3-ENV-718) had
no walkable pieces for them.

## Acceptance criteria
- [x] `reedhollow.py`: `root_walk_6m`, `reed_causeway_6m`, `reed_platform_6m` and `clutch_stone`. The walking tops
  are level at y 0 and the rails stand at the greybox's z ±2.0, 0.5 m high (`tools/tests/test_reedhollow.py`, 3).
- [x] ossa_fen.md §4: the block-to-piece swap map for both Ch10 zones.
- [x] The pieces are in the Act II kit-row preview (shot `kitrow_fen_reedhollow_walks`).
- [ ] The render viewed; the swap itself is act1-chapters' (it owns `game/levels/ch10/**`).

## Notes
- **2026-10-28 (env-art):** built. Ch11 and Ch12 are covered by the Lowlight, Sunken Vey and Keth kits; the gaps
  there are small and listed in the live log.

- **2026-10-28 (env-art): paused by ADR 0041** (Act I at final quality first; later-act work stops). The work stays committed and pushed as is; nothing is reverted. Resume when the human lifts the pause.

## Review log

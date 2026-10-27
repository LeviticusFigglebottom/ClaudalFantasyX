---
id: M3-ENV-712
title: "Corrow: carve the Watcher heads' backs (from the parapet walk they read as smooth barrels)"
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-04, M3-ENV-04B]
milestone: M3
reviewer: rendering
---
## Goal
act1-chapters' PC render `ch09_corrow_road` (gpu/render-act1-chapters-77a6a77) walks the parapet road, where the
camera sees the backs of the 140 parapet heads. Each back was a smooth squircle with faint course joints, so the
row read as primitive barrels: the human's "parts look primitive". The faces seen from the sea are unchanged.

## Acceptance criteria
- [x] `cw_watchers._carved_back` (LOD0) carves the back of `watcher_head`, `_b`, `_fallen` and `_cracked`:
  - staggered laterite blocks, 0.7 m long, with vertical joints, each block a little proud or sunk;
  - heavy vertical hair locks above the neck, and a headband running round to the ears;
  - carved ears on both sides;
  - the crown domes 0.12 m, so it reads as a skull, not a barrel's lid.
  The height stays inside the 2.45 m ± 0.1 m contract.
- [x] Budgets: LOD0 8000 → 10500 (`watcher_head`) and 9000 → 11000 (broken heads), for 41 back columns instead of
      21. LOD1 is unchanged (304–412 triangles), so the 140-head row only pays this on the few heads near the
      camera.
- [x] `test_corrow_kit` OK; Godot `--filter=corrow` 8/0. Full Corrow rebuild: only the four heads changed.
- [ ] PC renders of the shots that frame the heads, viewed and approved; act1-chapters re-checks `ch09_corrow_road`.

## Review log

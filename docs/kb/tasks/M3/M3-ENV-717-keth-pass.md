---
id: M3-ENV-717
title: "Keth Pass (Ch12): sheet, kit and the Avalanche Ram arena"
role: environment
status: blocked
blocked-by: ADR 0041
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: []
milestone: M3
reviewer: rendering
---
## Goal
The Lead's queue item 4: the Act II places that the creatures track's Ch10–12 bosses need. Sheet first, then the kit.

## Acceptance criteria
- [x] The design sheet: `docs/kb/art/environments/keth_pass.md`.
- [x] The kit's arena pieces (`haluna/keth.py`) and the arena `keth_seep_terrace` for the Avalanche Ram, to the
      battle contract: `test_battle_arenas` passes for it (floor and camera line); `test_arenas`, `test_fog_lamps` OK.
- [x] The zone kit's remaining pieces for Keth Pass: `keth_road_switchback`, `keth_scree_slope`, `woolback_trough` (2026-10-27). Quellan and Cloudloom: sheet §5 and `cloudloom_hall`, `keth_curtain`, `quellan_house`, `woven_awning` (2026-10-27).
- [ ] PC renders viewed and approved.

- **2026-10-27 (env-art): rework after the PC render gpu/render-env-art-95be611, which was not approved.**
  - **What failed.** The wall read as stretched white pillows, and the seeps as pale-blue ribbons.
  - **Wall.** Its blocks are now crisp (r 0.05, a deeper joint) and set proud or back of each other.
  - **Material.** `kit_keth_lit_ceramic` is a weathered grey (#AEB1AB, paint 0.5, cavity 0.55).
  - **Seeps.** Threads a third of the old width, with `kit_keth_seep` at alpha 0.35 and emission 0.7.
  - **Still a capsule.** The Avalanche Ram stand-in is a capsule until Character's model lands.

- **2026-10-28 (env-art): paused by ADR 0041** (Act I at final quality first; later-act work stops). The work stays committed and pushed as is; nothing is reverted. Resume when the human lifts the pause.

## Review log

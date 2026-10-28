---
id: M3-ENV-734
title: "Ch12: Quellan's inn and well, Hesk's dais, and the greybox swap map"
role: environment
status: blocked
blocked-by: ADR 0041
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-717]
milestone: M3
reviewer: cinematics
---
## Goal
The Lead's backlog item 4 (10-28): Act II zone kits for act1-chapters' Ch10–12 greybox (on claude/act1-chapters).

## Acceptance criteria
- [x] `keth.py`: `quellan_inn`, `quellan_well` and `hesk_dais`. The dry-stone walls are now `_dry_stone_walls`, and `quellan_house` is byte-identical.
- [x] `tools/tests/test_keth.py` (3): every Keth piece's budget (the kit had no test), the inn's open door and banner, the dais height.
- [x] keth_pass.md §6: the swap map for the Keth Pass, Quellan and Cloudloom greyboxes.
- [x] In the Act II kit rows (shot `kitrow_quellan_inn_well_dais`).
- [ ] The render viewed; the swap is act1-chapters' (`game/levels/ch12/**`).

## Notes
- **2026-10-28 (env-art):** built.

- **2026-10-28 (env-art): paused by ADR 0041** (Act I at final quality first; later-act work stops). The work stays committed and pushed as is; nothing is reverted. Resume when the human lifts the pause.

## Review log

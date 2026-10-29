---
id: M3-ENV-721
title: "Ansedra (Ch13–14): sheet, kit and the Warden's escape arena"
role: environment
status: blocked
blocked-by: ADR 0041
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: []
milestone: M3
reviewer: rendering
---
## Goal
The Lead's queue item 4, for the act outline's Act II zones past Ch12: Ansedra, the holy city (Ch13–14), and the
Ch14 boss (Warden Malcor Venn on the Conclave's pursuit barge). The sheet comes first, then the kit.

## Acceptance criteria
- [x] The design sheet: `docs/kb/art/environments/ansedra.md`.
- [x] `bowl_dome`, `ansedra_far_domes`, `pursuit_barge`, `lut_ch14_wedding`, and the arena `ansedra_lagoon_escape`
      built to the battle contract.
- [x] The zone pieces: `lacquer_hall`, `lacquer_court_ground`, `sanctum_basin`, `archive_stacks` (ansedra.md §1, with composition notes; placement is act1-chapters's).
- [ ] PC renders viewed and approved.

## Notes
- **2026-10-27 (env-art):** the Warden's arena.
  - **Pieces.** `ansedra.py` (`bowl_dome`, `ansedra_far_domes`, `_lit`, `pursuit_barge`), with two materials
    (`kit_lacquer_black`, `kit_window_lit`).
  - **Grade.** `lut_ch14_wedding`, a new `zone_lut.py` grade. The colour script's −4° hue turn on the reds is left to
    Rendering's LUT tool.
  - **Arena.** `ansedra_lagoon_escape`, on the bridal barge.
  - **Preview.** `preview_ansedra_lagoon_escape.tscn` (a stand-in for the Warden). Shot
    `battle_arena_ansedra_lagoon_escape`.
  - **Tests.** `tools/tests/test_ansedra.py` (6).
  - **For act1/combat:** set the Ch14 Venn encounter's arena to `ansedra_lagoon_escape` when it exists.

- **2026-10-28 (env-art): paused by ADR 0041** (Act I at final quality first; later-act work stops). The work stays committed and pushed as is; nothing is reverted. Resume when the human lifts the pause.

## Review log

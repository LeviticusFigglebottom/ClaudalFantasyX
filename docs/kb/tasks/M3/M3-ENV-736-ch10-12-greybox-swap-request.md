---
id: M3-ENV-736
title: "Swap the Ch10–12 greyboxes onto env-art's kits (request to act1-chapters)"
role: cinematics
status: blocked
blocked-by: ADR 0041
owner_session: ""
depends_on: [M3-ENV-733, M3-ENV-734, M3-ENV-735]
milestone: M4
request-from: environment
reviewer: environment
---
## Goal
act1-chapters' Ch10–12 greyboxes (M4-C10-02, M4-C11-02, M4-C12-02, on claude/act1-chapters) can take env-art's
Haluna-kit pieces now. Every block id has a piece; the maps are:
- Ossa Fen and Reedhollow: ossa_fen.md §4;
- Lowlight and the Sunken Vey: lowlight.md §5;
- Keth Pass, Quellan and Cloudloom: keth_pass.md §6.

The walkable strips are level at y 0 and as wide as the greybox's (3.6 m, rails 0.5 m at z ±2.0), so the spawns,
marks and triggers keep their places.

## Acceptance criteria
- [ ] Each zone's blocks swapped per the map, when the beat sheet (M4-C1x-01) names its shots (or sooner).
- [ ] The zone grades: `lut_ch10_fen` (ossa_fen.md §0), `ch11`, `ch12`. The arenas' LUTs are in
      `assets/environments/arenas/` until zone copies are cut.
- [ ] Ask env-art (a task, `role: environment`) for anything the map leaves out.

## Notes
- 2026-10-28 (env-art): filed after the Lead's backlog item 4. The kit pieces render in the Act II kit-row preview
  (M3-ENV-732) so they can be reviewed before the swap.

- **2026-10-28 (env-art): paused by ADR 0041** (Act I at final quality first; later-act work stops). The work stays committed and pushed as is; nothing is reverted. Resume when the human lifts the pause.

## Review log

---
id: M4-A2P-043
title: "Ansedra, the Sanctum and the Lamp Archive dressed, lit and walkable at final quality (the hero zone)"
role: environment
status: review
owner_session: env-art-b
depends_on: [M4-A2P-047]
reviewer: rendering
milestone: M4
request-from: lead
---
## Goal
Place the built kit (M3-ENV-721) in the city, the Sanctum and the Archive; Ansedra is the act's hero zone (SPEC §7.4: bespoke hero meshes on top of the kit). The still mirror lagoon and basin use M4-A2P-047.

## Acceptance criteria
- [ ] As M4-A2P-040, for Ch13; a swap map in ansedra.md first.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch13.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.
- 2026-10-30: started by env-art-b under ADR 0205 (Act II per track once its Act I rows are closed).
- 2026-10-30 (env-art-b): all three zones dressed in their greybox frames, so no story point moved:
  - Ansedra: `tools/act2/ch13_ansedra_dressing.py`, the still mirror, the ch13 grade.
  - The Sanctum: `ch13_sanctum_dressing.py`, the bound light only. Its layout light rows are requested of chapters
    in M4-A2P-103.
  - The Lamp Archive: `ch13_archive_dressing.py`, grey clerestory daylight.
  - 15 pieces in `haluna/ansedra.py`. Shots `ch13_ansedra_*`, `ch13_sanctum_*`, `ch13_archive_*`. Tests
    `test_ansedra_dressing.gd`, `test_sanctum_dressing.gd`, `test_lamp_archive_dressing.gd` and
    `tools/tests/test_ch13_*_dressing.py`.
  - Open for later: the Archive's day-by-day light variants (C6), and the mooring barges' hull (Narrative's call in
    the spec).
  - Reviewer: rendering, on the PC: the still mirror's SSR and the upward-lit vault.

- 2026-10-30 (env-art): **built**, `tools/act2/ch13_ansedra_dressing.py`. Ansedra's walks and buildings and the two
  interiors are built from the greybox (`ansedra_zones.py`; ansedra.md's revision line is the swap map), with the
  kit's domes and skyline round them. lut_ch13_still. env-art's previews (`game/levels/_tests/ch13_zones/`) were
  viewed at thirty cameras. Tests: `tools/tests/test_ch13_ansedra_dressing.py`. The mount is chapters'
  (M4-A2P-0431); the mirror water mode is rendering's (M4-A2P-047).

## Review log

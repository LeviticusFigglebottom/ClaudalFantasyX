---
id: M4-A2P-043
title: "Ansedra, the Sanctum and the Lamp Archive dressed, lit and walkable at final quality (the hero zone)"
role: environment
status: doing
owner_session: "env-art (claude/env-art, 2026-10-30)"
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

- 2026-10-30 (env-art): **built**, `tools/act2/ch13_ansedra_dressing.py`. Ansedra's walks and buildings and the two
  interiors are built from the greybox (`ansedra_zones.py`; ansedra.md's revision line is the swap map), with the
  kit's domes and skyline round them. lut_ch13_still. env-art's previews (`game/levels/_tests/ch13_zones/`) were
  viewed at thirty cameras. Tests: `tools/tests/test_ch13_ansedra_dressing.py`. The mount is chapters'
  (M4-A2P-0431); the mirror water mode is rendering's (M4-A2P-047).

## Review log

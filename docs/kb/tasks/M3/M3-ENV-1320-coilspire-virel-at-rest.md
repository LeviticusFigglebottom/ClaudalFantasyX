---
id: M3-ENV-1320
title: Coilspire's crown chamber shows Virel's model at rest, not the greybox block (Act I inventory, M3-HER-1141)
role: environment
status: review
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC)"
depends_on: []
milestone: M3
reviewer: creatures-b
---
## Notes (2026-10-28, env-art-b)
- creatures-b's `assets/creatures/virel/virel.glb` is now in the tree. `tools/act1/ch08_coilspire_dressing.py` places
  it on the Virel block's foot (B06 F07, held still: a dressing piece, so no idle plays), with its own slot materials.
  It follows the block, and the greybox keeps nothing now.
- `--filter=` ch08 23/0, zone_kit 12/0. Viewed in the chamber from three scratch cameras: the sailcloth coils, the
  seams' teal and the brass key read. ch08_coilspire_storm and _hall are unchanged (Virel is out of frame).
- For creatures-b: in the chamber it hangs in its battle pose. A coiled rest pose ("coiled the height of the
  chamber") would match F07 better, if one is planned.

- **env-art-b, 2026-10-29 (the Lead's decision, big18 gate):** Coilspire showed Virel twice, this still dressing piece
  and act1-chapters' ZoneCast `virel` actor on her coil (M3-CRE-700), which owns her state after the binding. The
  dressing piece is removed (`ch08_coilspire_dressing.py`); there was no separate coil or plinth piece under her. Viewed
  on a trial merge with act1-chapters @ 72254f9f, from F07 and F06: one Virel before the binding, none after.

## Review log

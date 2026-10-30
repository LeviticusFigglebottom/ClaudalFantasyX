---
id: M4-A2P-042
title: "Keth Pass, Quellan and Cloudloom dressed, lit and walkable at final quality"
role: environment
status: doing
owner_session: "env-art (claude/env-art, 2026-10-30)"
depends_on: []
reviewer: rendering
milestone: M4
request-from: lead
---
## Goal
Place the built kit (M3-ENV-717, 734) per keth_pass.md §6: the switchbacks and pass-cords, Quellan's street, inn and well, Cloudloom's open-roofed hall with thousands of instanced keth and their noon shadows, weather snow and wind.

## Acceptance criteria
- [ ] As M4-A2P-040, for Ch12; nothing frozen in the temple (ADR 0015).
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch12.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

- 2026-10-30 (env-art): **built**, `tools/act2/ch12_keth_dressing.py`. Each zone's ground and stone are built from
  the greybox (`keth_zones.py`), with the kit placed round them. env-art's previews (`game/levels/_tests/ch12_zones/`)
  were viewed at thirty cameras. Tests: `tools/tests/test_ch12_keth_dressing.py`. The mount is chapters'
  (M4-A2P-0421). Weather snow and wind are rendering's.

## Review log

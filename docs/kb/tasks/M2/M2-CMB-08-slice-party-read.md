---
id: M2-CMB-08
title: The slice party can Read (SPEC §6.1); the bestiary fills in the slice
role: combat
status: review
owner_session: worktree-agent-aa4303cb02313a538
reviewer: lead
depends_on: [M1-CMB-03]
milestone: M2
request-from: "lead"
---
## Goal
Only Ysolde knows `read`, and she is not in the vertical slice (Rhen, Asha, Toma). So the slice never shows the Read panel or fills a bestiary page from a Read.

## Acceptance criteria
- [x] One slice hero has Read, decided from the design docs and put in data.
- [x] Tests: the slice party Reads each tideline foe (crab, eel, harrier) and the bestiary logs it.
- [x] `sim.py --check` still passes.

## Notes (worktree-agent-aa4303cb02313a538)
- **Rhen knows Read** (`characters.json`, last in his skill list). Reasons in battle_ctb.md § Read: he reads currents and appraises salvage for a living, he is in every slice fight, and a skill cannot be unequipped away. Ysolde keeps it. No equipment category grants skills, so an accessory would have needed a new engine feature.
- Tests: `tests/unit/test_battle_slice_read_bestiary.gd`: only Rhen of the slice three reads; he reads every `ch02_tideline` and `sandbox_reef` foe and each is logged; a live tideline Read lands in `Game.state.bestiary`.
- `sim.py --check` passes and the report is byte-identical (the policies never choose a non-damaging Read).

## Review log

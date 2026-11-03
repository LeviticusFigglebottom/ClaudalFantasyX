# Live log: combat-systems environment

**Session:** `session_01F3vrUN933kFk8vhen4Tm2X` (cloud) · **Branch:** `claude/combat-systems` (from `claude/undertow-lead-handoff-ze8rrn` @ 920ebd32) · **Role:** combat (rules and data) · **Lead:** `session_018aiGwGLGkxsnMnu8VfCu1m`

I own the battle RULES and DATA: the headless engine (`game/battle/*.gd`), items, abilities, encounter balance numbers, the balance sim (`tools/balance/sim.py --check`), and field-usable abilities and items. VFX are battle-presentation's; menu screens are ui-menus'. Path claims are in `docs/kb/ownership.md` (the "Combat systems" row).

## Queue (the human's playtest FAST-TRACKs, 2026-11-03, in order)
1. A REVIVE item in the Act I economy (in battle and in the field).
2. After a WON fight, KO'd members come back at 1 HP.
3. Spells castable OUTSIDE combat (`field_usable`), with an API for ui-menus.
4. The solo Ch1 Hullgnaw is a little too hard: sim-tune it.
5. Then: combat rows in `docs/kb/qa/act1_gpu_qa.md` (newest on origin/gpu/act1-qa-7) and the inventory.

## Log (newest first)

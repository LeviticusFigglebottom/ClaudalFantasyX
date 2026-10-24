---
id: M2-FP-12
title: The Drownbell at slice quality (standing boss read-out, retry loop)
role: combat
status: done
reviewer: ui
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M2-FP-06, M2-FP-05]
milestone: M2
request-from: lead
---
## Goal
M2-FP-06 follow-up from the m2-slice standing queue. The Drownbell's mechanics work, but they show only in transient floats (which don't appear at all when damage numbers are off) and in one timeline chip suffix. Pillar 4 says the player always knows what the boss is building toward and what answers it. Bring the fight's read-out and its defeat/retry loop to vertical-slice quality without touching the balance.

## Acceptance criteria
- [x] A standing boss read-out (`BattleBossStatus`), shown for as long as a boss with mechanics is on the field: the boss and phase name, the telegraphed skill with its turns left, the weak point's progress, and the field with how many are bound to it. It is independent of the damage-numbers setting, and its layout comes from battle_hud.json.
- [x] Strings through loc keys; the opening phase's name and the field's name come from enemies.json.
- [x] The phase change is announced even with damage numbers off.
- [x] Defeat → Fight again restarts the Drownbell at phase 1 with Call Ilun still known, and the read-out resets.
- [x] Tests; `sim.py --check` unchanged (no balance data touched).

## Notes (m2-slice, 2026-10-24)
- Filed as M2-FP-11 and renumbered to FP-12: the integration branch's M2-FP-11 (zone-sun bias and FlowRouting) took that id first. Commits 331e9c2 and 09db8b2 say FP-11.
- `game/battle/scene/battle_boss_status.gd` (`BattleBossStatus`), built and refreshed by `BattleBossHud`. Layout: `battle_hud.json` `boss_status` (top left, under the target info). Data: enemies.json `phase_name_key` and `field_name_key` on the bell. Loc: `HUD_BOSS_CHARGE_NEXT_FMT`, `HUD_BOSS_CHARGE_IN_FMT`, `HUD_BOSS_FIELD_FMT`, `PHASE_DROWNBELL_TOLL`, `FIELD_DROWNBELL_FLOOD`. Docs: battle_ctb.md, "Status strip".
- **A lavapipe render found a second clarity bug.** The toll chip read "The Drown…", because "The Drownbell · The Toll" ran past the chip, so the telegraphed turn couldn't be told from the bell's other turns. A committed turn's chip now names its skill alone ("The Toll"); the glyph and the foe colour still say whose turn it is. This is a one-line change in UI's `timeline_chip.gd`, so **UI reviews it**.
- The phase change is announced by the phase's help-line prompt (already independent of damage numbers) and by the strip's title.
- No balance data changed. `sim.py --check` passes: Drownbell naive 0.0%, role_answer 77.6%, smart 85.2%.
- Tests: `tests/unit/test_battle_boss_status.gd` (5: the read-out, the countdown and rim with damage numbers off, the toll chip text, the flood and its polyps, no read-out without a boss, Fight again restarting the bell at the Toll with Call Ilun known).
- Not here (the PC's M2-RND-04): the bell's 3D telegraph VFX, the flood rise, the seaward death motes.

## Review log
- 2026-10-24 review-sweep-Q (ui): **approve.** `BattleBossStatus` takes its layout from battle_hud.json `boss_status` and doesn't depend on the damage-numbers setting. The phase and field names come from enemies.json (`phase_name_key`, `field_name_key`), and all five new loc keys exist, with no duplicates. Fight again restarts at the Toll with Call Ilun known (tested). UI accepts the timeline_chip change: a committed turn's chip names its skill alone ('The Toll'), and its glyph and colour still say whose turn it is. That serves pillar 4 better than a truncated 'The Drown…'. The sim moved from 79.7/89.6 to 77.6/85.2 only through the Swell merges; no balance data changed.

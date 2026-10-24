---
id: M2-CMB-02
title: Swell second-life loop (design): a masher with Swell still wins 32%
role: combat
status: done
owner_session: "worktree-agent-a64f55e43791c2ef3"
depends_on: [M2-NIT-03]
milestone: M2
request-from: "lead"
reviewer: progression
---
## Goal
M2-NIT-03 cut Shallows Verse to power 4; the masher-with-Swell rate fell from 37.9% to 32.1%. Lead decision: accept that for now, with a 35% decision line. The residual is structural: Ballast fills when Asha is nearly down, so any party heal is a second life for her.

## Acceptance criteria
- [x] Prototype both fixes from the M2-NIT-03 handoff in the sim: (a) a Verse targeting every ally but the singer (a new target kind); (b) Asha's default mode fills from her allies' hurt (a per-hero default). Pick the one that keeps Swell exciting and brings naive_swell to 25% or below
- [x] Bands and the ease ceilings hold; the formulas trio rule; the docs (battle_ctb.md, balance_report tuning log)

## Notes (combat, worktree-agent-a64f55e43791c2ef3)
- **Picked (a): Shallows Verse targets `all_other_allies`**, every living active ally but the singer, at power 4. naive_swell is 23.8% at good (19.8 at miss, 26.1 at perfect), and 39.1% on tier-1. Every band and both ease ceilings hold at miss, good and perfect.
- **Rejected (b): a per-hero Tether default for Asha.** It is a rate cliff. At 60 and at 100 her gauge never fills in a sandbox fight. At 120 the masher is 25.7%, and the loop moves to Rhen. It would also have touched saves, unlock counting and the M2-UI-01 menu.
- Sweeps and reasoning: balance_report.md tuning log, "2026-10-23 M2-CMB-02". Summary: battle_ctb.md § Swell. The masher's decision lines are now 25% and 45% (balance_targets.md).
- **Cost:** careful players see the Verse about 0.09 times a fight, down from 0.34 to 0.41. The gauge waits until someone else is hurt, and it carries. A playtest should judge it. If it is too rare, the lever is the fill (for example a per-hero default to Wake), not the target.
- **Reviewer focus:**
  - the tuning-log entry;
  - `BattleEngine._valid_targets` and `_hit_set`;
  - `BattleMenus.skill_candidates`, `swell_rows` and `group_label`;
  - the one controller line (`_show_pick`'s `group_label`).

## Review log
- 2026-10-24 review-sweep-O (progression): **approve.** Option (a) removes the loop rather than moving it, and the numbers reproduce.
  - **Re-run:** `tools/balance/sim.py --seeds 1000 --check` with the report in scratch, so the repo is untouched, gives rc 0. `naive_swell` is **23.8%** on `sandbox_reef` and **39.1%** on `sandbox_reef_tier1`, exactly as recorded, under the 25% and 45% lines. Every band holds: naive 10.9 / 25.1, role_answer 97.1 / 98.4, smart 100 / 100 with the mean-turn ease floors met. Drownbell is pending (not authored on this branch).
  - **What I read:** fb49cc0, ef096bb and b1fdfdd. These cover:
    - battle_engine.gd `living_other_allies_of`, `_hit_set` and `_valid_targets` (the actor is filtered out for `all_other_allies`);
    - battle_menus.gd `skill_candidates`, `swell_rows` (greyed with nobody else standing), `group_label` and `_target_text`;
    - the one controller line, sim_policy.gd and validate_data's skill-only target;
    - the two loc keys, and the formulas trio (formulas.md row, test_formulas.gd pin, formulas.gd unchanged, so the rule holds).
  - **Other `all_allies` switches:** I grepped them all. enemy_ai.gd uses selectors, not skill targets. ItemBattleAction has its own target set. `begins_with("all_")` in the controller and menus covers the new kind. Nothing is missed.
  - **Checks:** Godot `--filter=` battle 307/0 failed, swell 124/0 (includes test_battle_swell_others.gd). gdlint and gdformat are clean.
  - **Note for the Lead (no task):** the cost is that careful players see the Verse about 0.09 times a fight. A playtest should judge whether that is too rare, and the task already names the lever (the fill, not the target).

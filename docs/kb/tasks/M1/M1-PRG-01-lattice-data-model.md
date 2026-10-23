---
id: M1-PRG-01
title: Lattice data model, editor tool, and first section
role: progression
status: done
owner_session: progression-stream-1
reviewer: combat
depends_on: [M1-CMB-00]
milestone: M1
request-from: ""
---
## Goal
SPEC §6.4 board as data plus tools/lattice_editor/.

## Acceptance criteria
- [x] Board JSON (nodes, edges, type, value) with a validator
- [x] Movement and Facet activation logic, headless and tested
- [x] Applies stat nodes onto BattleCombatant base stats

## Notes
The 3D presentation is M2.

Delivered (see `docs/kb/design/lattice.md`):
- `game/data/progression/facets.json` (rules plus six Facet types) and `lattice_standard.json`, generated from `tools/lattice_editor/sections/standard.lat`. The first section has 87 nodes, 94 edges, and three hero petals with cross-over bridges.
- `game/progression/`: LatticeBoard, LatticeRules, FacetInventory, LatticeTraveler, LatticeProgress (`apply_to(BattleCombatant)`), and ProgressionFormulas.
- Movement points come from battle XP. The formulas are in `formulas.md § Progression`. Moving costs 1, or 0 onto any node someone has activated.
- 13 new skills in `skills.json` with loc keys. Existing rows are unchanged.
- Validator: `check_progression` in `tools/validate_data.py`. Tests are in `tools/tests/test_lattice_*.py` and `tests/unit/test_lattice_*.gd`.
- Save version 2 adds `GameStateData.lattice`, with a v1→v2 migration.

For Combat review:
- Check the new skill rows and numbers. Challenge depends on Provoke, which comes in M1-CMB-02.
- Check the Progression formulas (§12.3 pair).
- Hook-up still to do: build party combatants with `LatticeProgress.apply_to()` in BattleEngine (`_make_party_member`) or in the sandbox glue. Feed `xp_awards()` into `award_battle()`. Neither is done here, because `game/battle/` is out of scope for this task.

## Review log
- **2026-10-22, Combat (ui-combat-stream-1), SPEC §12.3 pair: approve with one fix.**
  Checked the 13 new `skills.json` rows, the board's stat totals per petal, and `ProgressionFormulas` against the battle formulas. The hook-up is done in M1-CMB-01: `BattleEngine.party_modifier = progress.apply_to` builds party fighters with their Lattice gains, and the sandbox victory feeds `xp_awards()` into `award_battle()` (105 XP → 3 movement points, asserted in `tests/unit/test_battle_controller.gd`).
  1. **Fix (Progression): Shield Wall is uncastable.** It costs 14 MP; Toma has 12 MP base, his petal has no MP node, and the only MP he can reach is `mp+6` on the Asha bridge *behind its L1 gate*. Either drop it to 10 MP or put an `mp+` node in Toma's L2 pocket before it.
  2. **Tune: Breakwater is a trap.** Damage is linear in power, so the fair comparison is power per rank: Attack 8/R3 = 2.67, Breakwater 10/R5 = 2.0, and it costs 10 MP. Suggest power 14 (2.8/rank) or R4 with power 11.
  3. **Watch: Kick Off** (5/R1 = 5.0 per rank) is the best tempo in the game, and with Slipstream's self-Haste it doubles again. It is Rhen's niche and MP gates it (24 MP = 3 casts), so it's fine for M1. M1-CMB-05's simulator should report it.
  4. **Watch: agility is the strongest Lattice stat.** Rhen's petal totals AGI +12 (22 → 34), so `base_delay` drops 58 → 40 (31% shorter delays, about 45% more turns). Asha's MAG +12 lifts Mend 230 → 350. Both are deliberate niche growth; re-run the sandbox bands at a full petal in M1-CMB-05.
  5. **Note for M1-CMB-02 and bosses:** Sunder and Shell Breaker apply permanent (−1) Breaks at 100%. Bosses will need resistances.
  6. **Question (ADR, Combat + Progression):** `level` sits in the damage and heal formulas (`stat + level`), but it is not a Lattice stat and nothing raises it, so it is a constant 5. Decide before M2 enemy tuning whether level exists at all.
  Fine as-is: Undercut (6/R3, delay 1, 6 MP) is a fair Attack sidegrade. Lantern Flare and Stilling Bell at 70% are good (`lure_glow` is `magic: true`, so Silence answers the eel). Chorus Mend trades MP for tempo against three Mends (103 vs 77 HP per rank). Challenge waits on Provoke (the validator warns). The LP thresholds and the XP credit rule fit together: rotating reserves shares XP at no time cost, by design.
- 2026-10-23 lead: closing on Combat's approval; Shield Wall MP 14→10 applied. The open question about hero level was resolved by ADR 0012.

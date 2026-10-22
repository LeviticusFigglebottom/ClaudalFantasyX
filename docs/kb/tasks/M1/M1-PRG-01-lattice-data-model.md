---
id: M1-PRG-01
title: Lattice data model, editor tool, and first section
role: progression
status: review
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

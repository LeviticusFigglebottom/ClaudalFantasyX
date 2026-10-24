---
id: M2-CMB-04
title: Vowbound battle rules in the engine (the call replaces the party; Ilun from Asha)
role: combat
status: review
owner_session: "worktree-agent-a8a3feee9300b5a1b"
depends_on: [M2-CMB-03]
milestone: M2
request-from: "lead"
reviewer: design
---
## Goal
SPEC §6.3: when called, a Vowbound replaces the whole party, with its own HP, abilities and Swell, and grows with Asha's stats. The slice needs one (Ilun, for the Drownbell's phase 2, vertical_slice.md §5). claude/first-playable ships a stand-in skill (ADR 0024/0026, *Call Ilun*) until the system exists. This task builds the headless engine rules and Ilun's data, with tests and a balance probe. It does not wire the Drownbell (the m2-slice track owns that) or the HUD (M2-UI-05).

## Acceptance criteria
- [x] `BattleVowbound` (Node-free, no random rolls): the call, refusals, the stood-down party, dismissal, a fall that is no defeat, victory handing the field back, and its own Swell and finisher
- [x] Stats from the caller: `Formulas.vowbound_stat`, with formulas.md, formulas.gd and test_formulas.gd changed together
- [x] Data: `game/data/battle/vowbound.json` (Ilun), three skills rows, four loc keys, and a validator with Python tests
- [x] Tests: `tests/unit/test_battle_vowbound.gd`; the battle and formulas filters are green; coverage holds
- [x] `sim.py --check` passes (its per-seed runs are byte-identical: no suite calls a Vowbound yet), plus a balance probe of a masher calling Ilun
- [x] ADR 0027 (the call's cost and the turn rules), and battle_ctb.md § Vowbound

## Notes (combat, worktree-agent-a8a3feee9300b5a1b)
- **The rules** (battle_ctb.md § Vowbound, ADR 0027):
  - **The call.** On the caller's own turn, the whole active party stands down and the Vowbound takes the turn. The call costs the caller a rank-`call_rank` delay (3) when the party returns, while the others keep their ticks.
  - **Dismissal** spends the Vowbound's turn.
  - **A fall is no defeat.** The party returns, and that Vowbound is gone for the battle.
  - **Victory while it is out** gives the field back to the party first.
  - **Refused while it is out:** swap, escape and items.
- **Ilun** (from Asha at level 5): 360 HP, DEF 20, MDF 28, MAG 22, AGI 11. His skills are Brine Lash, Tidal Ward and Attack, and his finisher is Floodnet. He absorbs water and is weak to lightning.
- **Balance probe** (scratch, not committed; 1000 seeds, sandbox, no gear): a masher wins 8.7%, and 38.9% when it calls Ilun at once. A free call was worth 20 points by itself, even with a 1 HP Ilun, which is why the call costs the caller's rank. 38.9% is above the 25% Swell masher line. That is proposed on purpose, for review, as a once-a-battle rescue.
- **The banned term.** The data field is `caller`; the usual class word is on `tools/banned_terms.txt`.
- **Engine footprint:** 723 → 756 lines. The changes are a `vowbound` var, `summon()`, `dismiss()`, `_recall()`, `_field_changed()`, and one-line hooks in `escape`, `find`, `_check_outcome`, `_finish` and `_swap_indices`. None of them touches a region claude/first-playable edits; a trial `git merge-tree` was clean except for the known `.uid` add/add.
- **Gates:** battle 319, vowbound 14 and formulas 30 (all green); coverage battle 99.95% with 1213 tests passing; tools unittest 457 OK; `sim.py --check` passes with byte-identical runs; validate_data, taskboard, gdlint and gdformat clean.
- **Reviewer focus:** the turn rules (ADR 0027), the 38.9% masher number and the proposed 40% line, and whether Silence should block the call.

## Review log

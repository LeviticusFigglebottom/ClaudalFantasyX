---
id: M2-CMB-04
title: Vowbound battle rules in the engine (the call replaces the party; Ilun from Asha)
role: combat
status: done
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
- 2026-10-24 review-sweep-P (design): **approve with fixes.** ADR 0027 is **accepted** with three amendments, recorded in the ADR. Fixes are filed as M2-CMB-05 (engine and data) and M2-FP-17 (the Drownbell with the real call).
  - **Verified.**
    - `BattleVowbound` is `extends RefCounted`, with no Node and no rolls. It only reads its JSON, like the other data loaders.
    - Every rule in battle_ctb.md § Vowbound is in the code: the stand-down, the call_rank offset for the caller and kept ticks for the others, dismissal spending the turn, a fall recalling the party in `_check_outcome`, `_finish` recalling before the outcome, and swap, escape and items refused.
    - The formulas trio changed together.
    - Re-run here: `--filter=vowbound` 14/0, `formulas` 30/0, `battle` 357/0. Coverage is battle 99.95%.
  - **SPEC §6.3.** It complies on "replaces the whole party", "its own HP, abilities and Swell" and "grows with Asha's stats". The cinematic and item-taught growth are rightly listed as not decided.
  - **IP.** `tools/banned_terms.txt` bans `summoner`, and neither the data nor the loc rows use it (`caller` is in the data). `summon` as a verb and an API name is the SPEC's own word, so that is fine.
  - **The call cost (rank 3): right.** Option 3 (MP or a gauge) would tax careful players, not mashers. The probe isolates the cost properly: the 1 HP call goes from 20 to 8 points.
  - **Silence blocking the call: right, keep it.** The call is a verse (vowbound.md: each Vowbound teaches a verse), and throat_honey is in the Haluna shop, so the player has the counter. Pillar 4: the refusal reason `silenced` must show on the greyed command (M2-UI-05).
  - **38.9% against the proposed 40% line: accepted as a provisional ceiling**, sandbox with no gear, masher plus an immediate call. It is not a band yet. Ilun falls in 99.6% of those runs, so he is a rescue, not a second party. The binding line is set once the sim models the call (M2-CMB-05), and it is checked per encounter.
  - **Wording.** "Once-a-battle rescue" overstates it. A dismissed Ilun can be called again, so it is really **one HP pool per battle**. Reword it in M2-CMB-05.
  - **Water: yes, a real risk.** It is a stall rather than a win button, and it breaks the slice's beat:
    - The Drownbell **and** its polyps absorb water, so Brine Lash and Floodnet both *heal* them. Ilun's Attack (STR 7) does about nothing into DEF 30, so Ilun cannot hurt the bell at all.
    - Every flood-phase attack but Hood Slam is water (`flood_surge` and `undertow_surge`), and Ilun absorbs water, so the flood heals him.
    - His gauge fills only from HP he loses, so Floodnet never comes.
    - **Result:** called in the flood, Ilun is near-immortal and harmless. The party hides out of reach with its statuses frozen, the flood never clears, and `TUT_DROWNBELL_FLOOD` ("Call on Ilun") leads nowhere.
    - **Ruling:** the tide he drinks becomes the net. Amendment A1: absorbed HP fills the Vowbound's gauge. A2: Floodnet becomes non-elemental (the net binds) and carries `clears_field: flood`. Brine Lash stays water, because Read teaches you not to lash an absorber.
  - **Exploit (A3).** The call never runs the caller's `_end_turn`: no Poison or Regen tick, no status countdown, no Doom count, no `turns_taken` and no `turn_ended`. A Doomed or Poisoned Asha skips a tick each time she calls. The call is the caller's action, so the caller's end-of-turn effects apply at the moment of the call; only her `next_time` waits for the return.

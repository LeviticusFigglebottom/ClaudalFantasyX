---
id: M4-A2P-1200
title: "Ch14's two fights (ch14_water_steps, ch14_malcor_venn) and the Lacquer Court's flow beats"
role: combat
status: review
owner_session: "act1-chapters (claude/act1-chapters)"
depends_on: [M4-A2P-114, M4-A2P-023]
reviewer: design
milestone: M4
request-from: cinematics
---
## Goal
The rest of M4-A2P-114 (§1 rows 15–19). act1-chapters wired Ch10–Ch13 there; Ch14 needs its fights first.
- **Encounters** per docs/kb/plan/act2/chapters/ch14.md §4:
  - `ch14_water_steps`: the set piece on the court's water-steps (scripted; arena lacquer_court_steps).
  - `ch14_malcor_venn`: the boss, two phases (arena ansedra_lagoon_escape). In phase 1 the bound `flat_engine` part
    slows the timeline, and only Liss can break it (BattleParts `answered_by`, M4-A2P-023). In phase 2 he boards
    (`when_down`).
  - Also: `malcor_venn`'s enemies.json row, its sim suite and band (docs/kb/plan/act2/bosses/malcor_venn.md).
- **Flow** (ch14.json, the Lacquer Court; zone triggers in tools/act1/ch14_greybox.py):
  - A `dais` touch trigger at `vows`: play `ch14_the_vows`, then battle `ch14_water_steps` (victory_flag
    `ch14_steps_held`, return_spawn Barge).
  - An arrive row: play `ch14_first_ripple`, then battle `ch14_malcor_venn` (victory_flag `ch14_venn_beaten`, which
    must be declared).
  - On return: play `ch14_left_standing`, then the existing `escape` go.
- **Thread:** test_ch14_16_thread plays them in order, and qa_known.json `"unraised"` drops the five Ch14 rows. This
  needs M3-UI-1242's `"chapter"` on the court's rows, or the guard reading it. Until then, Ch13's thread checks them.

## Acceptance criteria
- [ ] Both encounters resolve (test_act1_encounters_resolve), and the boss's sim suite is in band.
- [ ] ch14.json plays §1's order, and test_qa_threads has no Ch14 `unraised` row left.

## Notes (act1-chapters, 2026-10-30)
- **ch14_water_steps:** Ch8's stair-hold schema.
  - Merel's knife is a party ward (`cut_the_line`); four lines win it.
  - The court (a tide entry) reinforces Court Stillguard, up to two on the field.
  - Their `seize_the_line` grabs at the knife: three ranks of delay, or a blow on Kerrid when he covers it.
  - Kerrid is locked in, with a lent `hold_the_steps`; everyone has `stand_fast` so a turn with no foe never stalls.
  - Suite `set_piece`: naive 48.4, role 87.8, smart 100 (500 seeds).
- **ch14_malcor_venn:** the flat-engine plus Venn.
  - The engine is `answered_by` Liss (locked in). It pulses Slow every third turn and breaks at 50% (its `broken`
    phase, which creatures.json plays).
  - Venn boards at 50% or on the engine's fall (`when_down`), and yields at 15%.
  - New in BattleParts: `leaves_with`. The engine withdraws with him, so his yield wins the fight, and it can't stall
    when Liss is down.
  - Role answer: Ysolde (low mdef). Suite: naive 0.4, role 75, smart 100 at 40 turns (500 seeds).
- **ch16_abiding_guard:** `abiding_first` and two `abiding_guard`s.
  - The guards close ranks (a short Protect on all), and `leaves_with` the first.
  - The storm wakes at 50%. The first yields at 25%, which is the hand-over.
  - Role answers: Toma for the first, Kerrid for the guards. Suite: naive 0.8, role 71, smart 100 at 41 turns.
  - Gaps: the sheet's turn-6 phase clock (phases have no turn trigger yet) and its `storm_rising` field rules (no
    phase field here).
- **The court flow (ch14.json):**
  - The `dais` touch plays `ch14_the_vows`, then the water-steps.
  - The return plays `ch14_first_ripple`, then Venn.
  - The next return plays `ch14_left_standing`.
  - The barge is gated on `ch14_complete`.
  - test_ch13_thread plays it all, and qa_known `unraised` is empty.
- **Asks:**
  - Effects for the 13 foe skills: M4-A2P-1201 (battle-presentation).
  - The people's sounds: the three are `"silent"` in creature_voices (audio).

## Review log

---
id: M4-A2P-1200
title: "Ch14's two fights (ch14_water_steps, ch14_malcor_venn) and the Lacquer Court's flow beats"
role: combat
status: todo
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

## Review log

---
id: M2-CMB-03
title: Split battle_engine.gd under the lint cap (no behaviour change)
role: combat
status: done
owner_session: "worktree-agent-a8a3feee9300b5a1b"
depends_on: []
milestone: M2
request-from: "lead"
reviewer: lead
---
## Goal
`game/battle/battle_engine.gd` was at 976 of gdlint's 1000-line cap, and claude/first-playable adds about 25 more lines to it (the Drownbell's BossMechanics hooks). Extract cohesive helpers into new RefCounted classes so the engine has room again, with no behaviour change.

## Acceptance criteria
- [x] The engine is at 800 lines or fewer
- [x] Every test is unchanged and green
- [x] `python3 tools/balance/sim.py --check` passes
- [x] Coverage does not drop (`python3 tools/coverage/run_coverage.py`)
- [x] battle_controller.gd only if the split is low-risk (it is not: see Notes)

## Notes (combat, worktree-agent-a8a3feee9300b5a1b)
- **battle_engine.gd: 976 → 723 lines.** Four new static, Node-free helpers in `game/battle/`:

  | Class | What moved | Lines |
  |---|---|---|
  | `BattleHits` | `_resolve_on` (one skill on one target: damage, heal, Read, inflicted statuses, delay), `_roll_on_hit`, `_variance` | 108 |
  | `BattleItemUse` | `use_item`'s body, `item_defeats_party`, `preview_item`, `_valid_item_targets`, `_resolve_item_on`, `_rejoin_time` | 142 |
  | `BattleAutoTurn` | `basic_attack`, `_auto_pool` (Berserk and Confuse) | 41 |
  | `BattleSpoils` | `xp_awards`, `currency_award`, `_roll_drops` | 52 |

- **The public API is unchanged.** Every public name stays on `BattleEngine` as a one-line wrapper (`use_item`, `item_defeats_party`, `preview_item`, `basic_attack`, `xp_awards`, `currency_award`; `drop_awards` and `credited_ids` as before). The engine still owns the turn flow: `BattleItemUse.use` gets the engine's `_end_turn` as a Callable, so the emit and turn-end order is the same as before.
- **The RNG order is unchanged.** Each helper draws on `engine.rng` in the old order. This is proven, not argued: the simulator's per-seed `balance_runs.csv` (10,000 seeded battles) and `balance_summary.csv` are **byte-identical** between the base commit (run on an untouched `git archive` copy) and this branch.
- **Merge-friendly with claude/first-playable.** Nothing moved from the regions that branch edits (signals and vars, `setup`, `preview`, `run_enemy_turn`, `_checked`, `_execute`'s loop tail, `swap`, `_end_turn`, `_rebuild_roster`, `_make_party_member`). The only edit near one of them is the `_resolve_on` call in `_execute`, three unchanged lines above that branch's `BossMechanics.after_action` line.
- **battle_controller.gd not split.** claude/first-playable already moves the controller's id helpers out (`BattleIds`) and edits it in nine places. Any extraction here would conflict with those hunks, so it is not low-risk. That branch has the controller at 986 lines (and the engine at exactly 1000, so this split is what makes its merge fit); split it after the merge, on the integration branch.
- **Reviewer focus:** `BattleItemUse.use` (the Callable turn end), `BattleHits.resolve` against the old `_resolve_on`, and that the engine's wrappers keep their doc comments.

## Review log
- 2026-10-24 review-sweep-P (lead): **approve.** I diffed 183a2bf hunk by hunk, and there is no behaviour change.
  - **RNG order.** `BattleHits.resolve` is the old `_resolve_on` line for line: the same draws in the same order (hit, crit, variance, on-hit strikes, then inflicts). The only reshaping is that the inflict loop moved into `_inflict`, which runs at the same point. `_roll_on_hit` and `_variance` take the engine's `rng`, so no second generator exists.
  - **Turn flow.** `BattleItemUse.use` keeps the old order: fail checks, hits, `consume`, `action_resolved.emit`, then the engine's `_end_turn` through the Callable. `_finish` still rolls drops before `battle_finished` is emitted. `BattleAutoTurn.pool` still makes its one Confuse roll on `engine.rng` (`living_other_allies_of` is the old `erase(actor)`).
  - **No Node deps.** The four helpers are `extends RefCounted` and static, with no Node, scene or Game reference.
  - **Wrappers.** Every public name stays on the engine as a one-line wrapper, and the doc comments are kept or shortened with a pointer. The commit touches no test.
  - **Re-run here.** `--filter=battle` gives 357/0, and gdlint on `game/battle` is clean. `run_coverage.py` gives battle 99.95% (2126/2127) and progression 96.52%, within the baseline.
  - **Not re-run.** The byte-identical sim claim is heavy, so I did not re-run it; the diff review backs it up.
  - **Size.** The engine is now 784 lines after the first-playable merge: still under the 800 target, with room below the cap.

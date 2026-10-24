---
id: M2-BPR-05
title: Battle intro and outro: encounter stinger, opening banner, victory pose and return
role: combat
status: doing
owner_session: battle-presentation (claude/battle-presentation)
depends_on: [M2-BPR-01]
milestone: M2
request-from: lead
---
## Goal
An original encounter transition into battle, the opening banner's timing, and the victory pose and the return to the field.

## Acceptance criteria
- [x] Original transition (not the inspiring game's)
- [x] Opening banner timing in data
- [ ] Victory pose (clip or procedural) before the result panel
- [ ] Tests

## Notes
- Battle-presentation track standing queue (Lead, 2026-10-24). Listen-only presentation: the engine stays headless (CLAUDE.md §3).
- 2026-10-24, part 1 done (worktree subagent): the encounter stinger and the opening banner's timing. `BattleStinger` (game/flow/battle_stinger.gd) plays a tide line of dark water rising from the bottom edge (battle_tideline.gdshader, 0.75 s, data in game/data/flow/battle_transition.json) in the field before the router's fade, awaited by `BattleRequest.submit`. Reduced motion gives a plain cross-fade. The router and ADR 0029 budgets are unchanged. The opening banner now waits, holding the battle, until the router's fade has lifted (`reveal_wait_max_sec` cap in battle_hud.json). Tests: tests/unit/test_battle_stinger.gd (11). Docs: docs/kb/tech/battle_presentation.md § Encounter transition.
- Part 2 still to do: the victory pose before the result panel and the return to the field, on top of BattleChoreo. The Tests box is ticked when that part ships its own tests.

## Review log

---
id: M3-UI-1240
title: "Request: a rooted marker on the hero's HUD row and the hit float (the root crab's Root Drag)"
role: ui
status: todo
owner_session: ""
depends_on: [M4-A2P-020]
milestone: M4
request-from: combat
---
## Goal
M4-A2P-020 adds **rooted**. It is a skill effect, not a status, so SPEC §6.8's 21 statuses and their glyphs are
unchanged.
- A skill row's `root_turns` sets `BattleCombatant.rooted_turns` on the hit hero. The hit dictionary carries `rooted`.
- While `rooted_turns > 0`, `engine.swap_refusal()` returns `BattleEngine.FAIL_ROOTED`, and the swap help line reads
  "{name} can't leave the line: held by the roots." (`HUD_SWAP_ROOTED`; done in `BattleMenus.swap_lock_text`).
- It counts down at the end of each of the hero's own turns.

**Pillar 4:** the player should see the hold before opening the swap menu.

## Acceptance criteria
- [ ] A small marker on the rooted hero's HUD row (or portrait) with the turns left (read `rooted_turns`). Our own
      vector shape, not a status glyph.
- [ ] The hit float shows the root when `rooted` is on the hit.
- [ ] A HUD test.

## Review log

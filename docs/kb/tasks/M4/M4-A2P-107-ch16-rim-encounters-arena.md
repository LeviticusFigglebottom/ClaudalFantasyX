---
id: M4-A2P-107
title: "Ch16's rim encounters fight in pale_rim_shallows (name the arena on their rows)"
role: combat
status: todo
owner_session: ""
depends_on: []
reviewer: environment
milestone: M4
request-from: environment (env-art-b)
---
## Goal
ch16.md's encounter table gives `ch16_rim_skates` and `ch16_rim_crawlers` the arena **`pale_rim_shallows`**
(the gap was env-art-b's). It now exists on `claude/env-art-b`:
- `assets/environments/arenas/pale_rim_shallows/pale_rim_shallows.tscn`, written by
  `assets_src/environments/kits/haluna/rim_arenas.py` from the Pale Rim's own dressing, water and grade.
- Its id is registered in `game/data/battle/arenas.json`'s `scenes` (appended after `lacquer_court_steps`).
- It has a preview, `game/levels/_tests/battle_arenas/preview_pale_rim_shallows.tscn`, and a shot,
  `battle_arena_pale_rim_shallows`.

The encounter rows in `game/data/battle/encounters.json` are combat's, so env-art-b hasn't edited them.

## Acceptance criteria
- [ ] `ch16_rim_skates` and `ch16_rim_crawlers` carry `"arena": "pale_rim_shallows"`.
- [ ] `tests/integration/test_act1_encounters_resolve.gd` drops the two ids from `ACT2_NO_ARENA_YET` and passes.

## Review log

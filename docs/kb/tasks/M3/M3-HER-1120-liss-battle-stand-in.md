---
id: M3-HER-1120
title: "Liss in battle on her real model: her battle_sandbox stand_in row (request to ui-menus)"
role: ui
status: review
owner_session: "claude/ui (ui-menus)"
reviewer: combat
depends_on: [M2-HER-1103]
milestone: M3
request-from: combat
---
## Goal
Liss is an Act I party member (the chapter files put her in Ch6–Ch9 parties). Characters built her model with the
full clip contract (claude/characters: idle, ready, attack, cast, item, read, defend, finisher, hit, dodge, ko,
victory, revive). The hero track has her battle wrapper ready (`game/hero_motion/battle/liss_battle_actor.tscn`;
HeroBattleActor loads `assets/characters/liss/liss_lod1.glb` by path). Until that model reaches the branch, it shows
her stand-in capsule. battle_sandbox.json has no `liss` row yet, so she'd be a default primitive.

## Acceptance criteria
- [ ] `game/data/ui/battle_sandbox.json` `stand_ins` gets
      `"liss": {"shape": "capsule", "color": "#7A8F6A", "radius": 0.27, "height": 1.62, "tint": "#7A8F6A",
      "scene": "res://game/hero_motion/battle/liss_battle_actor.tscn", "yaw_deg": -90.0}`
      (colour and size are yours to pick: they're the capsule's until her model lands).
- [ ] The battle filter stays green.

## Notes
- Checked on a scratch worktree with her assets (2026-10-27): the pop guard over all 26 battle changes is clean, her
  revive included; her field walk is 0.97 m/s and run 2.19 m/s (hero_motion.json, already on claude/hero-integration).

## Notes
- 2026-10-28: done on claude/hero-integration by integration-qa on the Lead's word (ADR 0041; the party's capsules
  are now integration-qa's, M3-HER-1149), as Ysolde's row was on the FAST-TRACK. The row points at
  game/hero_motion/battle/liss_battle_actor.tscn. Liss shows her model once claude/characters' liss_lod1.glb merges;
  until then the wrapper draws its own stand-in. ui-menus: nothing to do; keep the row when you merge.

## Review log
- 2026-10-28, ui-menus: done on claude/ui (the 20:25 queue). Liss's `battle_sandbox.json` row names `liss_battle_actor.tscn` (yaw -90), and `tests/unit/test_battle_party_stand_ins.gd` checks every hero with a wrapper is shown through it. The big13 merge (e010d0f1) kept the row; her wrapper is on the merged tree.

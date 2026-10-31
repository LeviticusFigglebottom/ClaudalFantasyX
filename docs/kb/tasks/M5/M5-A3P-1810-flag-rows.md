---
id: M5-A3P-1810
title: "VillagerLayer flag rows: a row shown while a flag is set (`flag`) or until it is (`not_flag`)"
role: character
status: review
owner_session: "creatures (claude/creatures)"
depends_on: []
milestone: M5
reviewer: tech
---
## Goal
The Act III revisits change the towns' crowds (act3_roster.md Ch18: Haluna's "Backs to the Water", Reedhollow's
farewell-tide again on `ch17_complete`). VillagerLayer needs rows that appear or go when a story flag lands, so a
zone can swap a crowd person's row for a changed one.

## Acceptance criteria
- [x] `flag` / `not_flag` on a villagers row: shown only while / until the flag is set (Game.get_flag, checked each
  tick); combined with `shown` (day/night). A hidden villager is stopped and not ticked.
- [x] validate_npc.py: both name declared flags; a `flag` row is a variant of its crowd person's own row (it doesn't
  count as their second zone row).
- [x] Tests: Godot `test_flag_rows_swap_when_the_flag_is_set` (villager 49/0, crowd 21/0); tools test_npc.

## Review log
- 2026-10-30 creatures: built and tested. The Ch18 rows that use it are M5-A3P-1811 (blocked on the Act III flags).

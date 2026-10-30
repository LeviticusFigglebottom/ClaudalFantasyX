---
id: M2-HER-1128
title: "Request (slice-polish): the first-playable thread test skips B02 (Neme's table) after the tideline win"
role: qa
status: review
owner_session: "integration-qa (claude/hero-integration)"
reviewer: cinematics
depends_on: []
milestone: M2
request-from: qa
---
## Goal
The integration-qa thread guard (tests/integration/test_qa_threads.gd, M3-HER-1121) now also checks that each story
thread raises every flag its main objectives wait on (objectives.json, the progress spine). On the slice's thread
(tests/integration/test_fp_thread.gd), one is never raised: **ch02_ate_at_nemes**.

This is not a game softlock. HalunaStory.begin() plays B02 (`after_battle_scene_id`, ch02_nemes_table, which sets the
flag) on the first arrival after the tideline win, and test_haluna_slice_beats covers it. But the thread reloads
Haluna with `_load_zone()` and never calls `begin()` after the battle. So the slice's playthrough skips Neme's table,
and the save at the shrine happens with the objective line still on "to Neme's".

## Acceptance criteria
- [x] After `_win_battle(&"ch02_tideline")`, the thread arrives at Haluna as the game does (story.begin()), B02 plays,
      and `ch02_ate_at_nemes` is set before the shrine save.
- [x] Remove `ch02_ate_at_nemes` from tests/integration/qa_known.json "unraised". `--filter=qa_threads` stays green.

## Notes
- 2026-10-29 integration-qa: after the tideline win, the thread places Rhen at BattleReturn and calls
  `story.begin()`, as the game's arrival does. B02 plays, and `ch02_ate_at_nemes` is set and asserted before the
  shrine save. qa_known.json's `unraised` is empty now. `--filter=fp_thread` 2/0, `--filter=qa_threads` 1/0. The
  reviewer is slice-polish (cinematics), since test_fp_thread is theirs; integration-qa wrote the fix, so it
  can't review it.

## Review log

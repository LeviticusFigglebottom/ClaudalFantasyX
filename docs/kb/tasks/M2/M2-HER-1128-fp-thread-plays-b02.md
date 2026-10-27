---
id: M2-HER-1128
title: "Request (slice-polish): the first-playable thread test skips B02 (Neme's table) after the tideline win"
role: qa
status: todo
owner_session: ""
reviewer: qa
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
- [ ] After `_win_battle(&"ch02_tideline")`, the thread arrives at Haluna as the game does (story.begin()), B02 plays,
      and `ch02_ate_at_nemes` is set before the shrine save.
- [ ] Remove `ch02_ate_at_nemes` from tests/integration/qa_known.json "unraised". `--filter=qa_threads` stays green.

## Review log

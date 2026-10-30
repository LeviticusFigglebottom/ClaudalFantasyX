---
id: M4-A2P-1014
title: "Request (portraits, M4-A2P-081): the Ullari woman has a model but no baked portrait; test_dialogue_box is red"
role: ui
status: todo
owner_session: ""
depends_on: [M4-A2P-053, M4-A2P-081]
reviewer: character
milestone: M4
request-from: narrative
---
## Goal
Found while running the `dialogue` Godot tests for the Act II voice pass (claude/act2-plan, after merging the
integration branch at big28). M4-A2P-053 landed `ullari_woman_stage.tscn`, so
`test_dialogue_box.gd::test_every_act2_speaker_with_a_model_has_a_portrait` now expects
`DialogueBox.portrait_for(&"ullari_woman") == &"ullari_woman"` and gets `""`. Speakers.json still points her at
`portrait_villager_placeholder`. The other 86 dialogue tests pass. No story change is involved: the speaker id and
her seven Ch12 lines are unchanged.

## Acceptance criteria
- [ ] Bake the Ullari woman's portrait the way M4-A2P-081 baked Merel, Tobin and the clerk, and register it.
- [ ] Or, if her stage isn't final yet, say so here and the Lead decides whether the test waits.
- [ ] `godot --headless --path . res://tests/run_tests.tscn -- --filter=dialogue` is green.

## Review log

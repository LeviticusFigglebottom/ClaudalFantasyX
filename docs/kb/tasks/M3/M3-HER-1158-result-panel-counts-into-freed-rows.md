---
id: M3-HER-1158
title: "FAST-TRACK: BattleResultPanel's count tween writes into freed rows (930 'Trying to cast a freed object' per fight in a real-frame run)"
role: ui
status: review
owner_session: "ui (claude/ui, 503b99839)"
reviewer: qa
depends_on: []
milestone: M3
request-from: qa
priority: high
---
## Goal
This is the human's error class, "Trying to cast a freed object", new since big15. integration-qa's real-frame
battle entry probe (`tools/dev/battle_entry_probe.tscn -- --chapters=3`, on big15 merged) logs
`SCRIPT ERROR: Trying to cast a freed object. at BattleResultPanel._set_count (battle_result_panel.gd:266)` 930
times in one run of the Ch3 fights.

Cause:
- `FieldBattle._show_result()` calls `super()`, which shows the result and starts the open tween. Its tween_methods
  count EXP, lume and drops into each row's Label through `_set_count(value, c)`.
- It then calls `hud.result.show_result(...)` again with the field's own choices. `show_result` `queue_free`s the
  old rows and clears `_counters`, but never kills the previous `_open_tween`.
- The old tween keeps calling `_set_count` with the old rows' dictionaries every frame until its count ends, and
  `c["label"] as Label` casts a freed Label each time.

Patch (two lines and a guard):
```gdscript
# show_result(), before the old rows are freed:
	if _open_tween != null and _open_tween.is_valid():
		_open_tween.kill()

func _set_count(value: float, c: Dictionary) -> void:
	var label: Variant = c["label"]
	if not is_instance_valid(label):  # checked before the cast: casting a freed object is a script error
		return
	(label as Label).text = _count_text(c, roundi(value))
```

## Acceptance criteria
- [x] A re-shown result panel kills the previous open tween; `_set_count` checks the label before casting.
- [x] `godot --headless --path . res://tools/dev/battle_entry_probe.tscn -- --chapters=3` logs no
      battle_result_panel error.

## Notes
Owner: UI + Combat (`game/ui/**`); battle-presentation (M3-BPR-415, 2b0a5ffbe) edits this panel today. Filed rather
than fixed because it's another track's file. tools/freed_cast_lint.py doesn't see this shape (a cast inside a
tween callback with no is_instance_valid at all); a lint for "a tween_method bound to a node that can be freed"
would need the call graph.

## Review log
- 2026-10-29 integration-qa (the filer): fixed by ui in 503b99839 ("a count-up never writes into freed rows", act1_gpu_qa
  row 33): `_set_count` returns when the row's label is gone, and test_battle_result_motion covers it. It's in big17.
  Moved to review. Verified on lead/gate-big17: `open()` kills the previous open tween (lines 83-84),
  `_set_count` checks the label, and `battle_entry_probe -- --chapters=3` logs 0 battle_result_panel errors (big15:
  ~930). Reviewer: ui, to close.

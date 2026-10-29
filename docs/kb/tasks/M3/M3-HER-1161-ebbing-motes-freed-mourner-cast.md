---
id: M3-HER-1161
title: "Request: EbbingMotes casts a freed mourner (SCRIPT ERROR every frame once a mourner actor is freed)"
role: rendering
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: qa
---
## Goal
`game/vfx/ebbing/ebbing_motes.gd` (M3-C09-03, env-art-b), around line 168 in the mourner pass:

```gdscript
var node := row["node"] as Node3D
if not is_instance_valid(node):
```

It casts before checking validity. Once a mourner actor is freed (the Ebbing scene ends, the zone reloads at dawn, or
`tools/act1/cutscene_stills` frees each scene), every frame raises "Trying to cast a freed object". It's the same
class as the human's playtest report that M3-HER-1149 swept. `tools/freed_cast_lint.py` found it. It turned
big16's and big17's tool suites red (test_freed_cast_lint), and now holds a KNOWN row pointing at this task.

The fix (3 lines):

```gdscript
var held: Variant = row["node"]
if not is_instance_valid(held):
	_mourners.erase(id)
	continue
var node := held as Node3D
```

## Acceptance criteria
- [ ] The validity check comes before the cast.
- [ ] Remove this task's KNOWN row from `tools/freed_cast_lint.py`. `python3 tools/freed_cast_lint.py` then shows
      0 hits for the file, and tools.tests.test_freed_cast_lint stays green.
- [ ] A test in tests/unit/test_ebbing_motes.gd that frees a mourner and steps the motes, with no script error.

## Notes
- Filed by integration-qa, 2026-10-29, from big17's gate (the tool suite's 4 reds). The KNOWN row is on
  claude/hero-integration.

## Review log

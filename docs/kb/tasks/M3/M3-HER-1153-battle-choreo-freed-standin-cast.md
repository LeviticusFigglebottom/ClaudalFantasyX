---
id: M3-HER-1153
title: "BattleChoreo casts a leaving stand-in before its is_instance_valid check (a 'Trying to cast a freed object' in battle)"
role: ui
status: todo
owner_session: ""
reviewer: qa
depends_on: []
milestone: M3
request-from: qa
---
## Goal
In `game/battle/scene/battle_choreo.gd:801`, `var f := e["node"] as FighterStandIn` runs before
`if not is_instance_valid(f)`. A leaving stand-in that's already freed (the stage rebuilt, a fight torn down while
one is still walking off) is a script error on the cast, which is the human's "Trying to cast a freed object".

## Acceptance criteria
- [ ] Check `e["node"]` with `is_instance_valid` before the cast. The row is still dropped.
- [ ] Remove this task's KNOWN row from `tools/freed_cast_lint.py`.

## Notes
Found by integration-qa's freed-cast lint. Filed rather than fixed because `game/battle/scene/**` belongs to
UI + Combat (battle-presentation edits it today).

## Review log

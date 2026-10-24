---
id: M2-FP-28
title: Ch1 tutorial lines name their bindings by action, so they follow rebinding and the last device
role: cinematics
status: todo
owner_session: ""
depends_on: []
milestone: M2
request-from: ui
---
## Goal
The input parity audit (M2-UI-26) found two Ch1 tutorial lines that write their keys out in the text,
so they are wrong after a rebind and never switch to the pad's names:
- `game/data/dialogue/ch01/ch01_tut_shutter.dlg` (`ch01_tut_003`): "Hold F, or the left face button, to open the shutter."
- `DLG_CH01_TUT_001` ("Walk with the left stick, or W, A, S and D. Turn the camera with the right stick, or Q and R.").

The dialogue box now fills `{action}` names in every line (`InputNames.fill`, the tip card's rule): the
action's first key, or its first pad button once the pad was the last device used.

## Acceptance criteria
- [ ] `ch01_tut_003` reads e.g. "Hold {field_lantern_shutter} to open the shutter. ..." (the action from `game/data/flow/ch01_field.json`).
- [ ] `ch01_tut_001` names its actions the same way (or describes them without keys if a stick has no single name).
- [ ] `tools/dlgc.py` regenerated `game/data/loc/dialogue.csv`; `dlgc --check` clean.

## Notes
- m2-slice owns `game/data/dialogue/ch01/**` (ownership.md), so this is a request rather than a UI edit.
- Unknown `{names}` stay as written, so the hook changes no current line.

## Review log

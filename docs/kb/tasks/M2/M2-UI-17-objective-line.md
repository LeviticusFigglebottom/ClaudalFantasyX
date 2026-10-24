---
id: M2-UI-17
title: The on-screen objective line (on change, on demand, and in the field menu)
role: ui
status: doing
owner_session: "claude/ui"
depends_on: [M2-UI-16]
milestone: M2
request-from: lead
---
## Goal
Show the current objective without clutter: briefly when it changes, on demand (a remappable button), and always in the field menu. Hidden in cutscenes, conversations and battle.

## Acceptance criteria
- [ ] `ObjectiveHud` in the field (one attach line in FieldController, the precedent of M2-UI-04): a small panel top-left that slides in on change, holds, and fades; reduced motion fades without sliding; follows text size and palette.
- [ ] A new action `field_objective` (keyboard Tab, pad Select/Back), remappable on the Controls page.
- [ ] Hidden while the field controller does not accept input (cutscenes, dialogue) and never in battle.
- [ ] The field menu shows the objective on its root.
- [ ] Tests and a shot.

## Review log

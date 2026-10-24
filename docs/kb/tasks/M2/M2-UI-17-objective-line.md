---
id: M2-UI-17
title: The on-screen objective line (on change, on demand, and in the field menu)
role: ui
status: review
reviewer: lead
owner_session: "claude/ui"
depends_on: [M2-UI-16]
milestone: M2
request-from: lead
---
## Goal
Show the current objective without clutter: briefly when it changes, on demand (a remappable button), and always in the field menu. Hidden in cutscenes, conversations and battle.

## Acceptance criteria
- [x] `ObjectiveHud` in the field (one attach line in FieldController, the precedent of M2-UI-04): a small panel top-left that slides in on change, holds, and fades; reduced motion fades without sliding; follows text size and palette.
- [x] A new action `field_objective` (keyboard Tab, pad Select/Back), remappable on the Controls page.
- [x] Hidden while the field controller does not accept input (cutscenes, dialogue) and never in battle.
- [x] The field menu shows the objective on its root.
- [x] Tests and a shot.

## Notes
ObjectiveHud attached in FieldController; field_objective action (Tab / pad Back) remappable on Controls; gated on accepts_input and tree pause; the field menu root shows the objective (Objective block, right column, hidden with no map); test_objective_hud.gd, test_zone_map.gd; shot field_objective_line. Fix: the line wraps and the panel grows (a trimming Label asked for no height).

## Review log

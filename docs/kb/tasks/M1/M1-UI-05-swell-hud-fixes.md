---
id: M1-UI-05
title: Swell HUD and validator fixes (review-sweep-I on CMB-04)
role: ui
status: todo
owner_session: ""
depends_on: [M1-CMB-04]
milestone: M1
request-from: "combat"
---
## Goal
From the review-sweep-I entries (file:line references there).

## Acceptance criteria
- [ ] The Lamp Ring advances on clamped or fixed-step time so one long frame cannot skip a beat (battle_controller.gd ~:251-253, ~:702)
- [ ] The full-gauge gold frame is distinguishable from the fill (contrast check; hud_gauge.gd ~:59-60)
- [ ] validate_data checks that each timing window fits inside its beat (~:1598)
- [ ] The ring help text does not hard-code the beat count (strings.csv ~:421)

## Review log

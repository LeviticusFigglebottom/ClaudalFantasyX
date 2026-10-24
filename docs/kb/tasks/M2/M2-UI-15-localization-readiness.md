---
id: M2-UI-15
title: Localization readiness: a pseudo-locale render test and a no-hardcoded-string check
role: ui
status: todo
owner_session: "claude/ui"
depends_on: [M2-UI-09]
milestone: M2
request-from: lead
---
## Goal
SPEC M7 needs a localization-ready string table. Prove the UI survives longer and accented translations, and keep player-facing strings on loc keys.

## Acceptance criteria
- [ ] A pseudo-locale (`xx`, generated from strings.csv by a tool: accented letters, about 35% longer, wrapped in brackets) is loaded in tests. Every menu (field menu, bestiary, settings pages, title, battle HUD pages, shop and inn) is built under it, and each Label's text fits its rect or is set to wrap or ellipsize, with no silent overflow.
- [ ] A tools unittest scans game/ui and game/battle/scene for player-facing literals (`.text = "..."`, `tr()` on a non-key, `set_help("...")`) and fails on any not on an allow-list.
- [ ] The fixes the two checks find.

## Review log

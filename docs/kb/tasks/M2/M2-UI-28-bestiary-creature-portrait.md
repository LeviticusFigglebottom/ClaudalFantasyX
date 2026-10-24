---
id: M2-UI-28
title: "Bestiary page and Read panel: show the creature's live portrait (CreaturePortrait)"
role: ui
status: doing
owner_session: "claude/ui"
reviewer: character
depends_on: [M2-CRE-10]
milestone: M2
request-from: character
---
## Goal
The creatures track (claude/creatures) ships `game/creatures/creature_portrait.tscn` (`CreaturePortrait`): a live 3D
portrait of an enemy's battle model in its own small world with a transparent background. Put it on the bestiary
page (`game/ui/bestiary/`) and, if it fits, the Read panel (`game/ui/battle/read_panel.gd` / `enemy_page_view.gd`).

## Acceptance criteria
- [ ] The bestiary page shows the selected entry's portrait: instance the scene, call `show_enemy(id)`; when it
      returns false (no model yet) the page keeps its current layout.
- [ ] A never-read entry shows the portrait as a silhouette or not at all (UI's call; the portrait has no
      silhouette mode yet: ask character if you want one).
- [ ] The bestiary shots (`bestiary_menu`, and the field menu's if it shows the page) re-approved after viewing.

## Notes
- Renumbered at the Lead's big7 merge (2026-10-24): filed by creatures as M2-UI-16, which collided with claude/ui's M2-UI-16 (objective system, filed later but already merged and referenced). M2-UI-26 is the next id free across all branches. Older handoffs still say M2-UI-16.
- API: `show_enemy(id: StringName) -> bool`, `clear()`, `has_creature()`. Framing, clip and time come from
  `game/data/creatures/creatures.json` `portrait` (defaults, per-creature overrides). Default size 256×256; the
  container stretches its viewport, so size it in the layout.
- Cost: one SubViewport rendering a ~5–20k-triangle model. Disable it (`clear()`) when the page closes.
- Review shot of all portraits: `creature_portraits` (claude/creatures).

- **Renumbered again (Lead merge, big8, 2026-10-24):** big7's M2-UI-26 collided with claude/ui's M2-UI-26 (input parity audit, ADR 0036). Now M2-UI-28, the next id free across all branches.

## Review log

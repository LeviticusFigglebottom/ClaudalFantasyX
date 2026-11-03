---
id: M3-UI-1250
title: "FAST-TRACK (playtest 11-03): every status says how to identify it and how to remove it"
role: ui
status: review
owner_session: claude/ui (ui-menus, session_01F3vrUMk5AsY8FMR6bL35TW)
depends_on: []
reviewer: combat
milestone: M3
request-from: lead
---
## Goal
The human's playtest FAST-TRACK 3 (TRACK-RULES 11-03): status effects must be explained. ui-menus owns the explanations;
battle-presentation owns the on-body visuals.

## Acceptance criteria
- [x] A status help panel (`StatusHelpPanel`) with each status's glyph, name, blessing/affliction, what it does, how
  long it lasts, whether it outlasts the battle, and what removes it (items, abilities, a save shrine's rest, wearing
  off, its own way). Reachable with the new remappable **status help** key (H / pad Back, `status_help.json`) from
  the battle command menu (the acting hero), target picking (the fighter under the cursor), the Read panel (the
  foe; its hint names the key), and the field Status page (the hero; its help line names the key).
- [x] All words come from the game's tables (`StatusHelpModel`): statuses.json durations and descriptions,
  items.json `cure` effects (battle-only items marked), party skills' `cleanses` (heroes, Lattice nodes, and a
  Vowbound's only once bound), party_rest.json carried statuses and shrine cures. A new cure in game/data shows with
  no UI edit.
- [x] A first-time card (`StatusTipCard`) the first time each status lands on the party, at the party's next
  command, holding the battle; its help key opens the panel on that status. Once per save (`status_<id>_met`), off
  with the Accessibility tips setting, never in fixtures or captures.
- [x] A Codex "Afflictions" section: one entry per status, opened as it is met, its page the whole help.
- [x] Hover (tooltip) or long press (callout) on a status chip in the party panel and the target info shows its one
  line.
- [x] Tests: tests/unit/test_status_help.gd (13). Shots: battle_status_help, battle_status_tip (pending baselines).

## Notes
- The glyphs are the HUD's own `StatusGlyph` set (one shape per status). When battle-presentation's on-body icon set
  lands, the panel takes it by swapping the glyph class only.
- Cure data: everything needed is already in game/data. combat-systems: if a status gains a cure (a field spell, a
  new item), add it to the data and the panel follows.

## Review log

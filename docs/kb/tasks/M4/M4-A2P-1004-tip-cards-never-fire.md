---
id: M4-A2P-1004
title: "Request: three first-time tips never fire, and the tips start a chapter late (tutorial_tips)"
role: ui
status: todo
owner_session: ""
depends_on: []
reviewer: narrative
milestone: M4
request-from: narrative
---
## Goal
To ui-menus (`game/data/ui/tutorial_tips.json`, `game/ui/field/tutorial_tips.gd`, `tip_card.gd`). This comes from the
Lead's Act I tutorial clarity pass (pillar 4). Each finding was traced in code and data.

| # | Sev | Where | Problem | Suggested fix |
|---|---|---|---|---|
| F1 | **high** | `tutorial_tips.json` `field_menu` (`on: flag`, `when: ch02_tideline_won`). `menu_save` and `swell` require it | **None of the three ever shows.** `ch02_tideline_won` is set inside the battle scene (`field_battle.gd:87`), where no tip card exists. The card hears flags only while it's alive (`tip_card.gd:54,145`). On the field's reload only `field_ready` tips are checked (`:78-80`). So `tut_field_menu_seen` is never set, and the chain dies | `"on": "field_ready", "requires": ["ch01_wickfry_won"]` (the zone reloads after Ch1's first scripted fight), or let a reload re-check `flag` tips whose `when` is already set |
| F5 | med | `objective` (`requires: ch02_met_asha`) | Since ADR 0042, New Game starts in Ch1. Ch1 has objectives, maps, the menu and Rhen's Swell, but no tip explains them until Ch2 | `"on": "flag", "when": "ch01_saw_bell_room"`. A Ch1 `field_ready` fires during the fade-in, before `ch01_started` is set (`zone_story.gd:271`) |
| F8 | low | `tutorial_tips.gd:47-50` | Only placed shrine objects get the `shrine` tag. The layout-trigger shrines (Ch6, Ch7, Ch8) are tagged `save_shrine`, so a player who skipped Haluna's shrine never sees the tip | Also add `shrine` when the payload has `save_shrine` |

**Wording, optional (yours to take):** the tip bodies say "errand", "gear" and "In a deal", which no menu label uses
(the labels are Objective, Equip, Buy and Sell). Matching them would help once F1 makes the menu tips appear.

## Acceptance criteria
- [ ] F1: a new game sees the field-menu, menu-save and Swell tips.
- [ ] F5 and F8 fixed, or answered here with a reason.

## Review log

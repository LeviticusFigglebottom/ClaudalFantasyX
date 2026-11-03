---
id: M3-UI-1253
title: "FAST-TRACK (playtest 11-03): the revive item in the field Items page raises a fallen hero"
role: ui
status: doing
owner_session: claude/ui (ui-menus, session_01F3vrUMk5AsY8FMR6bL35TW)
depends_on: []
milestone: M3
request-from: lead
---
## Goal
FAST-TRACK 5 (UI half): the revive item, used from the field Items page on a fallen hero, raises them. combat-systems
owns the item (an original name; the battle `revive` effect).

## Acceptance criteria
- [ ] The Items page offers any `"field": true` item whose battle effect is `revive` on a fallen hero only, with its
  preview, and refuses it on a standing one in words.
- [ ] A fallen hero shows as fallen on the target list and the party cards.
- [ ] Tests over the shipped revive item(s), so a new one from combat-systems needs no UI change.

## Notes
- Already in place before this task: `relighting_wick` (items.json, `revive` 25 %, field: true) works from the Items
  page (test_items_menu `test_a_revive_raises_the_fallen_and_a_cure_clears_a_carried_status`). This task checks the
  whole path against combat-systems' new item once it lands, and fills any gap.

## Review log

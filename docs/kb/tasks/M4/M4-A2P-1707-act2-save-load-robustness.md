---
id: M4-A2P-1707
title: "Act II save and load robustness in the mounted Ch10-Ch13: Continue restores the seven, the flags, the zone and the spawn"
role: ui
status: review
owner_session: claude/ui (ui-menus)
depends_on: []
reviewer: qa
milestone: M4
request-from: lead
---
## Goal
The Act II counterpart of M4-A2P-1705, in the mounted Ch10-Ch13.

## Acceptance criteria
- [x] Every enterable Ch10-Ch13 location (11): a chapter autosave with the seven (three in the line, four in reserve)
      and Act II's flags, then Continue from the title. Chapter, location, party and reserve, flags, bag, money and play
      time come back, and the party enters that location's scene at a named spawn
      (test_continue_every_act1_zone::test_every_act2_location_continues_where_it_was_saved).
- [x] The shrine round trip (test_qa_save_shrines) runs over every zone: green.
- [x] Found: no Ch10-Ch13 zone has a save shrine or rest point yet. Requested from the chapters as M4-A2P-1706.

## Review log

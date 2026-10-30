---
id: M4-A2P-1705
title: "Save and load robustness: save in every Act I zone, Continue from the title; party, flags, zone and spawn restore"
role: ui
status: review
owner_session: claude/ui (ui-menus)
depends_on: []
reviewer: qa
milestone: M4
request-from: lead
---
## Goal
Save in every Act I zone (and mid-cutscene where allowed), load from the title, and check that the party, flags, zone
and spawn all restore.

## Acceptance criteria
- [x] Every enterable Act I location (17, the prologue to Ch9): a chapter autosave, then Continue as the title does.
      Chapter, location, party and reserve, flags, bag, money and play time come back. WorldReturn enters that
      location's scene at a named spawn (tests/integration/test_continue_every_act1_zone.gd).
- [x] Shrine saves in every zone round-trip (existing test_qa_save_shrines). The autosave waits out a cutscene and
      saves its end (existing test_autosave_deferred).
- [x] Found and fixed: a chapter autosave continued at the last shrine, a chapter back (ADR 0121).

## Notes
- 2026-10-30 ui-menus: the fix is SaveSystem.autosave_state() (ADR 0121). The new test fails on the old code (16 of 17
  locations entered the last shrine's zone) and passes now.

## Review log

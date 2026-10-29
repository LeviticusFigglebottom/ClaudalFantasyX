---
id: M3-ARC-02
title: Debug chapter select (F8): start a fresh game at Ch1 or any built Act I chapter
role: architect
status: done
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M3-ARC-01]
reviewer: qa
milestone: M3
request-from: lead
---
## Goal
The Lead asked for this on 2026-10-24, along with the end card's `next_location` switch (M3-C04-04). The M2 review build ends at the title after B11, so testers need a debug-only way into each Act I chapter without editing data.

## Acceptance criteria
- [x] F8 in the debug overlay (debug builds only, like F1–F12) lists one start per chapter: Ch1, then each built chapter in story order.
- [x] Enter on a start does all of this:
  - begins a fresh game (`Game.new_game`);
  - sets the story-so-far flags, which are what earlier chapters leave set on a straight playthrough;
  - sets the chapter and the party;
  - goes to the chapter's location and spawn. The chapter's own zone story then takes over.
- [x] The data is `game/data/debug/chapter_select.json`. `tools/chapter_flow_check.py`, through validate_data, checks:
  - the location, and the spawn on greybox zones;
  - the chapter number;
  - the heroes;
  - that the flags are declared;
  - that the ids are unique.
- [x] Tests:
  - `tests/unit/test_debug_overlay.gd`: two tests, the starts are in order and F8 starts Ch4;
  - `tools/tests/test_chapter_flow.py`: `ChapterSelectTest`.

## Notes
- **Ch8 isn't built yet.** Its start goes in once M3-CMB-01 lands and Ch8 has a zone.
- **The flags are a judgement call.** Each chapter's lists are its main completion flags, not every optional flag. Its zone sets its own party on arrival anyway.

## Review log
- 2026-10-28, integration-qa (qa reviewer, also holding the architect seat): **accepted.** chapter_select.json now
  lists Ch1–Ch9 in story order, Ch8 included (Mole). tools/tests/test_chapter_flow OK, debug_overlay 14/0 on
  claude/hero-integration (big15 merged).
  - **Caveat, not this task's:** the Ch4 start uses `ch04/haluna_wake` NemeDoor, which stands 7.8 m above the ground
    (M3-HER-1154, act1-chapters' data), so F8 → Ch4 drops the party through the map until that patch lands.

---
id: M3-ARC-01
title: Data-driven chapter flow for Act I (generalise HalunaStory and first_playable.json; ADR 0035)
role: architect
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: []
reviewer: lead
milestone: M3
request-from: lead
---
## Goal
Lead 2026-10-24 12:00 (the human authorised M3 in parallel with the M2 review; m2-slice owns Act I gameplay and narrative). The slice's flow is bespoke: `HalunaStory` and `FirstVerseScene` read hand-named sections of `first_playable.json`. Act I adds six chapters, each with several zones, and they need one shared way to say:
- what plays on arrival, by flag;
- which triggers start which dialogue, battle or scene;
- where a battle returns to;
- how a chapter hands off to the next.

All of it in data, validated, and headless-testable. The slice must keep working unchanged: the Haluna and shrine tests pass, and its shots don't move.

## Acceptance criteria
- [x] ADR 0035 records the design.
- [x] A chapter registry and a per-zone story schema under `game/data/flow/`, checked by `validate_data` (flags declared, dialogue ids exist, scenes and spawns exist).
- [x] A reusable `ZoneStory` node that plays a zone's story from that data, with arrival beats, triggers, battles with victory and escape returns, hand-offs through `FlowRouting`, and night or variant hooks.
- [x] A test chapter with two zones drives it end to end in an integration test.
- [x] The prologue's hand-off: it stays `first_playable.json` `prologue.next_location`, which is already data. M3-C01-02 repoints it to Ch1, and no registry code is needed (ADR 0035).
- [x] The slice is unchanged: `test_fp_thread` and the Haluna tests pass.

## Notes
- 2026-10-24 m2-slice, **done, for review by lead.**
  - **ADR 0035** and the reference doc `docs/kb/tech/chapter_flow.md`, which has the how-to and the schemas.
  - **`ZoneStory`** (`game/flow/zone_story.gd`): arrive, beats, barks, overheard barks and party. The steps are play, place, set, party, zone, beat, if_event, battle, go and scene.
  - **`ChapterRegistry`** reads `game/data/flow/chapters.json`, which is empty until the first chapter lands.
  - **`GreyboxZone`** (`game/world/zone/greybox_zone.gd`) builds a playable zone from a layout JSON; its defaults are in `game/data/world/greybox_defaults.json`.
  - **Validation:** `tools/chapter_flow_check.py`, run by `validate_data`, checks the chapter files and layouts. `scene_spawns` now reads a greybox zone's spawns from its layout.
  - **Fixture:** `game/levels/_tests/zone_story/`, two zones and a test chapter.
  - **Tests:** `tests/integration/test_zone_story.gd` (7) and `tools/tests/test_chapter_flow.py` (8).
  - **The slice is untouched:** HalunaStory and first_playable.json are unchanged.

## Review log

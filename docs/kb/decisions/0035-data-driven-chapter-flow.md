# 0035 — Data-driven chapter flow and greybox zones for Act I

- **Status:** accepted
- **Date:** 2026-10-24
- **Roles affected:** cinematics, narrative, environment, combat, qa
- **Author role:** architect (m2-slice, M3-ARC-01)

## Context
The vertical slice's flow is hand-built. `HalunaStory` and `FirstVerseScene` read named sections of `first_playable.json` (`haluna`, `first_verse`, `shell_shrine`), and every beat is a code path.

M3 adds Ch1, Ch4–6, Ch8 and Ch9, which is about a dozen zones, plus Ch7's story. They're built in parallel by several agents. That needs:
- one shared way to say what plays where;
- checks that data written by many hands names real flags, dialogue, encounters, locations and spawns;
- greybox levels quick enough to author that the story can be played before env-art's kits exist (SPEC §5.4: data-driven; ADR 0007).

## Options
1. **A story script per zone in GDScript,** like HalunaStory. It's flexible, but every chapter re-solves the same problems, and nothing outside the code can check it.
2. **A general state machine or visual scripting.** It's more power than Act I needs, it's harder to review, and it's a new tool to build.
3. **Data steps for each zone, played by one node,** with greybox zones built from a layout file. Both are validated together.

## Decision
Option 3.
- **ZoneStory** (`game/flow/zone_story.gd`) plays a zone's block of a chapter file. It has:
  - `arrive` rows (`{when, steps}`; the first one that holds runs on arrival);
  - `beats` (run by a trigger or interactable whose payload is `{"beat": id}`);
  - `barks` swaps by flag;
  - overheard barks, as in the slice;
  - a `party` filled on arrival.
- **Steps:** `play`, `place`, `set`, `party`, `zone` (a call on the zone root), `beat`, `if_event`, and the three steps that end a run: `battle` (returns to the zone), `go` and `scene`. Every hand-off goes through `FlowRouting` (M2-FP-09) or `BattleRequest`.
- **ChapterRegistry** (`game/flow/chapter_registry.gd`) finds a zone's block in the chapter files that `game/data/flow/chapters.json` lists.
- **GreyboxZone** (`game/world/zone/greybox_zone.gd`) is a zone root built from a layout file: blocks, spawns, marks, stand-in actors, fixed shots, triggers, a sun and an environment, the player, the camera and the stage. A zone scene is just that root plus `location_id` and `layout_path`. Env-art's kit replaces the blocks later; the story data doesn't change.
- **Validation:** `tools/chapter_flow_check.py`, run by `validate_data`, checks every chapter file and the layout of every zone it names. That covers flags, compiled dialogue, encounters, heroes, locations, spawns in the target zone, trigger beats, and hand-offs coming last. `validate_data.scene_spawns` reads a greybox zone's spawns from its layout.
- **The slice is unchanged.** Haluna, the Shell Shrine and the first verse keep their own scripts and `first_playable.json`. The prologue's hand-off stays `first_playable.json` `prologue.next_location`, which Ch1 repoints. Moving Haluna to ZoneStory is optional later work, not part of M3.

## Consequences
- **Easier:**
  - A chapter is JSON, `.dlg` and a layout, all reviewable in a diff and caught by CI when they name something that doesn't exist.
  - Parallel chapter work touches separate files; `chapters.json` gets one appended line per chapter.
- **Harder:**
  - Anything the steps can't express (a puzzle, a set-piece's wave meter) needs zone-root code or a new step kind.
  - A new step kind needs the ADR noted, the checker updated, and a test in `tests/integration/test_zone_story.gd`.
- **Watch:**
  - Two story systems exist until Haluna moves. New chapters must use ZoneStory, not copy HalunaStory.
  - Greybox layouts don't collide like real kit pieces (no step-up). Check that each route can be walked when the kit swaps in (cf. M2-FP-24).

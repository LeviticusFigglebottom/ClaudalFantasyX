---
id: M2-FP-25
title: B06 Saltgrass Causeway: the slice's one route between Haluna and the Shell Shrine
role: cinematics
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M3-ARC-01]
reviewer: narrative
milestone: M2
request-from: lead
---
## Goal
The Lead's 2026-10-24 13:09 intro audit found this M2-review BLOCKER; it goes ahead of M3. SPEC's M2 asks for "one route", but `first_playable.json` goes straight from `haluna.ending_scene` to `shell_shrine.tscn`. Build `ch03/saltgrass_causeway` from vertical_slice.md B06 and haluna.md C01–C07:
- a greybox zone (GreyboxZone and ZoneStory), with env-art's route kit swapping in later;
- the camera rails C01–C07, with C02 the default side-on rail;
- the three marker-post banters, at C04, C03 and C05;
- a route encounter table (reef crabs, lantern eels, and the gull harrier's flier lesson at C07), using encounters.json;
- the Lit Age ring's teal glint;
- the hand-offs Haluna → causeway → shrine.

## Acceptance criteria
- [x] The causeway zone, with its location row, spawns, camera volumes and rails (C01–C07).
- [x] Three banters (`.dlg`, overheard), about 90 words, with flags declared.
- [x] Field random encounters (data-driven, seeded, Light Step aware) and the scripted harrier lesson.
- [x] Haluna's causeway head goes to the causeway, and the causeway's far end goes to the Shell Shrine.
- [x] A headless thread test covers it, and `test_fp_thread` still passes.

## Notes
- 2026-10-24 m2-slice, **done, for review by narrative.**
  - **The zone:** `ch03/saltgrass_causeway` is a GreyboxZone at `game/levels/ch03/saltgrass_causeway/` (layout JSON plus a root-only scene), with its story in `game/data/flow/chapters/ch03.json` (ADR 0035).
  - **Getting there:** Haluna's "Go now" travels there (`haluna.ending_location` and `ending_spawn`, `HalunaStory.KEY_GO`), so the location is recorded. The islet steps go to `ch03/shell_shrine` at `Entry`.
  - **Camera:** C02 is the default side-on dolly rail; C01 and C03–C07 are beat frames from haluna.md's lenses. GreyboxZone `camera_volumes` is new: fixed, pan_follow and dolly, with rails.
  - **Banters:** three overheard barks (posts at C04, tidepool at C03, ring at C05), 90 words in all. They play once each, and their flags are declared.
  - **Fights:**
    - The gull harrier at C07 is a scripted strip fight, `ch03_causeway_harrier`, with the `TUT_FLIER_RHEN` prompt. A win sets `ch03_harrier_won`; an escape steps back to `BeforeHarrier`.
    - After it, random `ch03_causeway_shore` fights every 25–45 m (`FieldEncounters`, new: seeded, a weighted table, aware of Light Step's `encounter_rate_pct`, returning to where Rhen stood).
    - Both are in the Ch1–Ch3 regular band at 1000 seeds (balance_targets.md has the numbers, including the foe-order finding).
  - **The Lit Age ring's glint** is an emissive block.
  - **Tests:**
    - `test_fp_thread`: causeway head → causeway → harrier → random fight → shrine.
    - `test_zone_story` (the volumes, the encounters, Light Step, the return point).
    - `test_chapter_flow` (the checker).
  - **Next:** env-art's route kit replaces the blocks.

## Review log

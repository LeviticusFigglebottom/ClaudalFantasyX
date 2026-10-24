---
id: M2-FP-25
title: B06 Saltgrass Causeway: the slice's one route between Haluna and the Shell Shrine
role: cinematics
status: doing
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
- [ ] The causeway zone, with its location row, spawns, camera volumes and rails (C01–C07).
- [ ] Three banters (`.dlg`, overheard), about 90 words, with flags declared.
- [ ] Field random encounters (data-driven, seeded, Light Step aware) and the scripted harrier lesson.
- [ ] Haluna's causeway head goes to the causeway, and the causeway's far end goes to the Shell Shrine.
- [ ] A headless thread test covers it, and `test_fp_thread` still passes.

## Notes

## Review log

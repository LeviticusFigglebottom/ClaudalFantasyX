# Gate big27 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ e605c9f4 (Merge lead/gate-big26).

## Pinned heads (merged --no-ff, in order; the Lead's priority first)
- claude/ui @ 2742662e
- claude/hero-integration @ ec64658d
- claude/act2-plan @ 0b05a631
- claude/env-art-b @ 0cfb0eb8
- claude/env-art @ 92b180e9
- claude/creatures @ b09e9b40
- claude/audio @ 08a244b1
- claude/act1-chapters @ fb22ae65
- claude/characters @ 7e3d9202
- claude/m2-slice @ 61fc9729
- claude/creatures-b @ 98b31c5f
- claude/battle-presentation @ bdc5ef22
- claude/act2-plan @ ccab6f4c
- claude/audio @ 11e8703a
- claude/env-art-b @ b8bc4d70

The Lead's list is all in: ui 95f51b98 (victory-screen preload), integration-qa ec64658d (MERGE-READY "take it into the
next batch": the resident field restores the zone's EventBus connections and shrine registrations on re-attach),
act2-plan 9be20122 (read-through tasks), env-art-b c6dec98b (the 40 .import fixes), env-art's Prologue pass, creatures
d91a783f and cbcd5b5c, and audio's Lamptongue doc. I didn't find a separate "scripted-fight resident return" commit on
claude/hero-integration; it gets merged the moment it posts.

## Resolutions
- audio: `game/data/dialogue/compiled/ch14_first_ripple.json` and `ch16_the_choir.json` (generated) conflicted. Both
  .dlg sources merged clean, so I regenerated with `tools/dlgc.py` (328 scenes, 0 errors; dlgc --check clean).
- PROVENANCE: removed the rows for assets/creatures/{avalanche_ram,rime_urchin}/materials/ice.tres (the owners
  removed the files and rows, per ADR 0015). The union merge had re-added them.
- **Task id clashes (M4-A2P):** the id that reached integration first keeps it.
  - 115: env-art-b's Quellan eye-height request (on integration) keeps it; act2-plan's read-through Prologue–Ch3 → **118**.
  - 116: the Lowlight arena request (on integration) keeps it; act2-plan's read-through Ch4–Ch9 → **119**;
    env-art-b's Pale Rim exit request → **121**.
  - 117: act1-chapters' Ch14 fights and court flow (17:34:56) keeps it; act2-plan's Brine Shoals vendor (17:35:17) → **120**.
  - Each moved file got a gate note, and the cross-references between them were updated. The owners' live logs still use the old ids.
  - LEAD-ASK: the M4-A2P counter is being raced by four roles (three clashes in two batches). Could each role draw
    from its own range, or check `taskboard --check` against the integration branch before filing?

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1056 files) · no conflict
markers · no new duplicate PROVENANCE rows, loc keys or shot ids.

GATE-BUILT @ b7b09c5e

## Fast gate
- Selected: 54 test files (plus test_aspect_layouts, to re-check the routed red).
- Lane A (mine): 27; lane B (GATE-HELPER): 27, in `gate-big27-lanes-b.txt` @ 66ae0cc2.
- LEAD-ANSWERED (18:04): per-track M4-A2P ranges (TRACK-RULES "FROM 2026-10-30 18:05"). The moved tasks are now in
  their filers' ranges: act2-plan's read-throughs and Brine Shoals vendor are **M4-A2P-1000, 1001, 1002** (were 115,
  116, 117), and env-art-b's Pale Rim exit request is **M4-A2P-1500** (was 116). Gate notes and cross-references updated.
- ui @ 33a57693 merged (≥ 43fa81ab; the commits after 2742662e are live-log only). The 4:3 Read fix was already in
  through 2742662e: **test_aspect_layouts 18/0** in lane A.

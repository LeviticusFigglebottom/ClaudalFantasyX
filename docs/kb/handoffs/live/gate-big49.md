# Gate big49 (fast gate, ADR 0205)

Base: **lead/gate-big48 @ 9f9f5011** (not merged yet). Merge big48 first; big49 then adds only the commits below.

## Pinned heads (merged with --no-ff in this order)
1. claude/audio @ d7b5bcec: **big47's routed red fixed**, M3-AUD-865 the storm beds import looping (storm_gale, storm_wall). Log: MERGE-READY @ d3052411.
2. claude/ui @ f136fa1f: **big47's routed reds fixed** (status help's UI sound hooks for the panel and tip card, audit notes for the controller and
   chip; test_status_names allows Ch4's beat). Log: MERGE-READY @ c71894a7.
3. claude/m2-slice @ 029bba8a: beat audit (the last three frame-timed cutscene shots hold their line), Act III M5-A3P-1203/1701/1704/1707 (the
   Ending's last stops, the credits' beach-rite vignette, Ch18's seen flags, the Ch17 ledger page). Log: held-timing shots self-rendered and viewed.
4. claude/env-art-b @ b10d44fd: **FAST-TRACK follow-up**, Corrow's storm sea takes no sun glint (slice-polish's W20). Log: MERGE-READY.
5. claude/act1-chapters @ 05b7d427: M4-A2P-071..075 taken; the Act II break at the Prologue's plaza (LEAD-ANSWERED); ch16_act_break_vigil
   shot (pending). Log: MERGE-READY.

## Conflicts
- game/data/ui/credits.json (ui's M5-A3P-1700 sections vs slice-polish's vignette): ui's sections and layout kept, with slice-polish's
  `beach_rite` vignette scene (`res://game/flow/ending_beach_rite.tscn`) and `next_scene` (post_credits.tscn). Both scenes exist.
- PROVENANCE, loc and shots.json by merge_union. test_hero_walk_cycle.gd.uid: the same uid on every branch.

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1139 files) · manifest valid (812 shots, no duplicate
id) · no duplicate loc keys · no new duplicate PROVENANCE rows · no conflict markers · no gate-run images.

GATE-BUILT @ ff9eefd2

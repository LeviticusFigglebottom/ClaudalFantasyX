# Gate big31 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ 7c4c6de1 (Merge lead/gate-big30).

## Pinned heads (merged --no-ff, in order)
- claude/creatures @ 100f767f
- claude/hero-integration @ cbbbc34b
- claude/env-art @ 07f876e9
- claude/act1-chapters @ f243dec2
- claude/env-art-b @ 9a85e089
- claude/act2-plan @ 00314a8d
- claude/audio @ 1ad6cfc9
- claude/characters @ 418bc13f
- claude/m2-slice @ 4d5c9ed0
- claude/creatures-b @ c095cfec
- claude/battle-presentation @ b417e390
- claude/env-art @ 82c7033c

creatures' M3-HER-1168 (the threaded villager build: the Drownbell/Haluna reveal) isn't posted yet; per the Lead it goes
in the moment it posts, even mid-batch. A watcher is on claude/creatures. If it lands while lanes run, it is merged
between runs, followed by a fresh import and a re-gate of its tests. creatures' 2be4ee1f (the test_villager_routines fix)
is in.

## Resolutions
- act2-plan: compiled ch11_drowned_galleries.json and ch11_nhoa.json (generated) regenerated with tools/dlgc.py from the
  cleanly merged .dlg sources.
- battle-presentation: `tools/vfx/readability_sheet.gd.uid`: theirs. big30's gate had committed an import-written uid for
  the owner's script; the owner's own uid wins.

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1063 files) ·
test_gdignore_imports OK · no conflict markers · no new duplicate PROVENANCE rows, loc keys or shot ids.

GATE-BUILT @ 3a1ad626

## Fast gate
- Selected: 43 test files (plus test_villager_routines and test_qa_capsules, to re-check routed reds).
- Lane A (mine): 22; lane B (GATE-HELPER): 21, in `gate-big31-lanes-b.txt` @ 6a695535.

## Results so far
- Lane A (mine, 22 files): 21 green. **test_villager_routines is green** (creatures' 2be4ee1f fixed big29's routed red).
  - test_qa_capsules 3/1: unchanged (act1-chapters' new Ch14/Ch16 foes have no bodies). Still routed: **act1-chapters**.
- Lane B (GATE-HELPER, 21 files @ 6a695535, arrived 21:14): all green.

## Mid-batch (the Lead, 21:25): M3-HER-1168 and others, merged after lane A finished
  - claude/creatures @ e0b9afb5
  - claude/act1-chapters @ df9183f9
  - claude/creatures-b @ 3fa26392
  - claude/audio @ 61de113f
  - claude/ui @ f88dcab9
  - claude/env-art @ 6e00a323
- creatures @ e0b9afb5 carries **445d5888 M3-HER-1168**: VillagerLayer loads its actors on worker threads under the fade, so
  Haluna's held reveal drops from 1.85 s to 0.2 s. act1-chapters' 6047d9d2 (the Act II balance pass) is in.
- All clean. Checks: validate_data 0/0 · taskboard clean · dlgc clean · gdlint and gdformat clean (1064) · gdignore OK ·
  no new duplicate PROVENANCE rows.
- Re-gate on a fresh import: the 28 test files these merges touch, plus every villager/crowd/haluna/scene_router/resident_loads
  test (the Lead's list) and test_qa_capsules.
- Re-gate (28 files, fresh import): import check clean · boot 0 ERROR lines · log check 0 · 27 green. Every
  villager, crowd, haluna, scene_router and resident_loads test is green with M3-HER-1168 in. The red is test_qa_capsules
  (routed, as above).
- Tools suite (-j 2, 211 units; it overlapped the mid-batch merges, so the audits were re-run on the final tree):
  - Now green: test_hero_clips, test_zone_map_pois and **test_villagers** (the long-known red is gone).
  - test_act1_audio_audit and test_battle_vfx_coverage (cut_the_line, court_reinforce, court_wait): unchanged since big30.
    Still routed: **act1-chapters**.
  - test_rig_integrity (Asha, Liss, Pell, Rhen, Ysolde, Stillguards A/C/D/E, and now **Sefir**): still routed:
    **characters** (classified by failing pose in big30, not probed).
  - Known: test_palette_check, test_screenshots.

GATE-FAST-DONE @ 47561982 (merge-approved: no batch-caused red). M3-HER-1168 is in. Routed: act1-chapters
(test_qa_capsules, test_act1_audio_audit, test_battle_vfx_coverage); characters (test_rig_integrity). Known: test_palette_check,
test_screenshots.

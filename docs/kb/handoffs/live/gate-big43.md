# Gate big43 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ 6980e847 (Merge lead/gate-big42).

## Pinned heads
- claude/characters @ b48c6325: row 56 skirt polish, WIP (a5698164: the reduced hem swing eased in over starts and out over stops; b48c6325: in the
  locomotion clips the staff keeps clear of the full swing's cloth). The only head with new commits; no other branch moved since big42.
- A watcher is on claude/characters for the polish's MERGE-READY. It is merged between test runs, then a fresh import and a re-gate.

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1107 files) · test_gdignore_imports OK · no conflict
markers · no new duplicate PROVENANCE rows.

GATE-BUILT @ a6c072dc

## Fast gate
- Selected: 1 test files (plus test_hero_stage, to re-check big42's routed red).
- Lane A (mine): 1; lane B (GATE-HELPER): 0, in `gate-big43-lanes-b.txt` @ 43f4c49b.

## Mid-batch: characters @ fe54e656 (row 56 polish, cloud pass 6)
- 26534a86 (the outer hem's leg share 0.5, faded out at the centre) and fe54e656 (the hem trail and the back's full swing fade across the panels):
  sources only (`build_asha.py`, `hero_clips.py`); the rebuilt libraries aren't committed. Not marked MERGE-READY (its last is @ a480b2cb); taken
  because the Lead asked for the polish when it posted. Note: characters' head carries a2bc108d (act2-plan's old Ch17) only as history, through
  integration's big42 merge of act2-plan's clean lane; the merge changes just those 2 files.

## Fast-gate results
- Import and boot clean; log check 0; `Parameter "t" is null`: not seen.
- test_hero_stage 11/1 on both trees (Asha's walk skirt helper bones 17° off the baked clips): characters', as in big42. The polish doesn't rebuild the clips.
- Tools suite (on the final tree for characters' tests): **test_hero_locomotion is green now, and so is test_rig_integrity Asha**. test_hero_clips is
  red again (the committed libraries don't rebuild from the polished hero_clips.py). Routed: **characters** (rebuild and commit Asha's library and
  helper bones). The rest is the standing list: test_b_arenas (env-art-b), test_cutscene_sfx_files' sequencer check (audio), test_creatures
  (creatures-b), test_freed_cast_lint (audio), test_status_names (ui). Known: test_palette_check, test_screenshots.

GATE-FAST-DONE @ 8d876020 (merge-approved: no batch-caused red). In: row 56 polish sources. Routed: characters (test_hero_stage,
test_hero_clips; rebuild the outputs), and the standing list.

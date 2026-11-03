# Gate big45 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ 974ef09b (Merge lead/gate-big44).

## Pinned heads
- claude/battle-presentation @ 5aabaf53 (live log: the three Ch6 ridge fights clean).
- claude/characters @ c02add20: **row 56, the panel-bone skirt** (a35fe528: the panels driven by both thighs with pendulum lag in the locomotion
  clips, neighbours within 20°, the underskirt one tube; c02add20: the thigh hug kept above mid-thigh). 094ffc75: test_hero_stage samples a story
  walk and a battle clip. Its log isn't marked MERGE-READY (still @ a480b2cb); taken per the Lead, 09:04 (cloud-qa confirms the trousers look and the
  pinch are gone). The notch fix follows. Note: both commits say "rebuilding"; whether the outputs are committed shows in the tests.

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1107 files) · test_gdignore_imports OK · no conflict
markers · no new duplicate PROVENANCE rows.

GATE-BUILT @ 88b258b5

## Fast gate
- Selected: 1 test files (plus test_hero_stage).
- Lane A (mine): 1; lane B (GATE-HELPER): 0, in `gate-big45-lanes-b.txt` @ 3fc847a9.

## Fast-gate results
- Import and boot clean; log check 0; `Parameter "t" is null`: not seen.
- **test_hero_stage** 11/1: now `asha attack DEF-armpit.R: 38.8°` (094ffc75 makes the test sample a story walk and a battle clip). Tools:
  **test_hero_clips** red (the committed libraries don't rebuild from the reworked hero_clips.py) and **test_rig_integrity Asha** red. All three are
  characters' row 56 rework in progress: both commits say "rebuilding", and the rebuilt outputs aren't committed. Routed: **characters** (commit
  the rebuilt asha.glb, LOD and library, then recheck the helper bones).
- The rest is the standing routed list: test_b_arenas (env-art-b), test_cutscene_sfx_files' sequencer check and test_freed_cast_lint (audio),
  test_creatures (creatures-b), test_status_names (ui). Known: test_palette_check, test_screenshots.

GATE-FAST-DONE @ f6723271 (merge-approved under the standing rule: every red is branch content). In: row 56's panel-bone skirt sources,
per the Lead. Its rebuilt outputs and the notch fix follow from characters.

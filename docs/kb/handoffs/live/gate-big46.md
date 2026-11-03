# Gate big46 (fast gate, ADR 0205)

Integration base: claude/undertow-lead-handoff-ze8rrn @ e2411fb0 (big45 @ c972ea42 plus the 11-03 Lead docs).

## Pinned heads
- claude/characters @ 5e9cb380: **row 56, the notch fix** that big45 said would follow (979a5482: back to the a35fe528 look the Lead approved,
  fe54e656's skirt sources and the committed GLB; in the locomotion clips the back panels keep within 12° of their neighbours and a derived panel's
  hem within 5° of its knee, so the back cloth never folds over (the white notch at profile 0 and 11); Asha's library rebuilt and committed;
  5e9cb380: test_hero_stage samples Asha's offer_hand). Not marked MERGE-READY (its log is still @ a480b2cb); taken as the follow-up big45 named.
- No other head moved since big45 (every other track is an ancestor of the integration branch; the 11-03 tracks haven't pushed yet).
  claude/combat-systems doesn't exist on origin yet.

## Conflicts
None (clean merge, 11 files).

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1107 files) · no conflict markers · no gate-run images.

GATE-BUILT @ d75aeefc

## Fast gate
- Selected: the Godot tests filtered to `hero` (the batch touches Asha's clips, `hero_helper_bones.gd`, `helper_bones.json` and
  `test_hero_stage.gd`; `--filter=asha` selects no file), plus the whole tools suite (221 units). No GATE-HELPER lane this batch.
- XDG_DATA_HOME and logs under the gate session's scratch dir; HYMN_STEP_TIMEOUT=10800.

## Fast-gate results
- Import clean (godot_log_check import: 0; only the first-pass `*.en.translation` load notices); boot smoke 0 ERROR lines; `Parameter "t" is
  null`: not seen.
- **Godot `--filter=hero`: 116 run, 0 failed.** test_hero_stage is **green** (big42–45: 11/1, the skirt helper bones off the baked clips), and
  test_hero_cutscene_snaps and test_hero_cutscene_motion pass.
- **Tools suite: 221 units, 2104 tests.** test_hero_clips, test_hero_locomotion and test_rig_integrity Asha are **green** (big45 had test_hero_clips
  and Asha's rig red). Reds:
  - the standing routed list, unchanged: test_b_arenas (env-art-b, `ashcrown_anvil_court`), test_cutscene_sfx_files' sequencer check and
    test_freed_cast_lint (audio), test_creatures (creatures-b), test_status_names (ui). Known: test_palette_check, test_screenshots.
  - test_dialogue_clarity and test_direction_holds: **this container, not the batch.** Both decode audio that's an unfetched LFS pointer here
    (`assets/lfs/audio/ambience/oruvel_raft.ogg`, `assets/audio/music/act2/reedhollow.ogg`; ffmpeg exit 187). The batch touches no audio.
- Note for this gate container: LFS objects aren't fetched (lfs.github.com is blocked), so the import rewrites the pointer `.ogg.import` files;
  those rewrites aren't committed.

GATE-FAST-DONE (merge-approved under the standing rule: no batch-caused red). In: row 56's notch fix with Asha's rebuilt library; it turns
big45's three characters reds green.

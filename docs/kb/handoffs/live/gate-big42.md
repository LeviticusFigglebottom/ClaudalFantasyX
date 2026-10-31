# Gate big42 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ 89c4aaf2 (Merge lead/gate-big41).

## Pinned heads (merged --no-ff, in order)
- claude/characters @ fccc3a1b
- claude/hero-integration @ 885cf12a
- claude/act1-chapters @ b2ea5941
- claude/battle-presentation @ 8513fc63
- claude/act2-plan @ 7356f1f0

- characters @ fccc3a1b: **row 56, the last Act I art row**: Asha rebuilt with the outer hem on the legs, her library and the run sheet (viewed).
- **act2-plan is back in** as its clean lane, fbe737f5 on 2f9cf3af, per the Lead's 06:23 ruling: Act III scripts (.dlg), loc and objective text
  only, with no chapter flow, level, qa_known or flag change (a dry run had 0 conflicts). It puts the Act III music and SFX cues on
  `test_cutscene_sfx_files`' MUSIC_TODO and SFX_TODO sets with its M5-A3P-1002..1016 request ids (that file is audio's; noted for audio).
- env-art-b: no new commits since big41 (row 84 isn't posted).

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean (1107 files) · test_gdignore_imports OK · no conflict
markers · no new duplicate PROVENANCE rows or loc keys.

GATE-BUILT @ 44625c6d

## Fast gate
- Selected: 12 test files.
- Lane A (mine): 6; lane B (GATE-HELPER): 6, in `gate-big42-lanes-b.txt` @ 64e308db.

## Fast-gate results
- Import and boot clean; log check 0; `Parameter "t" is null`: not seen.
- Lane B (GATE-HELPER, 6 files @ 64e308db, arrived 06:54): all green.
- Lane A (mine, 6 files): 5 green.
  - **test_hero_stage** 11/1 (`test_helper_bones_match_the_baked_clips`: asha walk DEF-skirt_0.001 17.1°, skirt_0.002 17.1°, skirt_4.001 5.9°).
    Red on claude/characters @ fccc3a1b alone (probed): row 56's rebuilt clips and helper_bones.json disagree. Routed: **characters**.
- Tools suite (221 units):
  - **Now green: test_hero_clips** (characters' library) and test_villagers (since big41).
  - test_rig_integrity Asha: red again with row 56's rebuild. Routed: **characters**.
  - test_cutscene_sfx_files: act2-plan's MUSIC_TODO and SFX_TODO clear two of the three checks. `test_every_music_cue_plays_as_the_sequencer_finds_it`
    still lists the Act III music (credits_suite, dace_ledger, ending_dock and others); that check doesn't read the TODO sets. Routed:
    **audio** (its test, with act2-plan's requests).
  - Still routed: test_b_arenas (env-art-b, the Ashcrown arena), test_status_names (ui), test_freed_cast_lint (audio), test_creatures
    (creatures-b), test_hero_locomotion (characters). Known: test_palette_check, test_screenshots.

GATE-FAST-DONE @ 5a341a19 (merge-approved: no batch-caused red). In: **row 56, the last Act I art row**, and act2-plan's clean lane
(Act III scripts, loc and objectives). Routed: characters (test_hero_stage, rig Asha, locomotion), audio (cutscene music check, freed_cast), env-art-b
(b_arenas), ui, creatures-b.

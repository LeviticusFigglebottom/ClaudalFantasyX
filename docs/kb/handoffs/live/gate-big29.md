# Gate big29 (fast gate, ADR 0205)

Integration base: claude/new-session-mj8c3c @ c646c3a8 (Merge lead/gate-big28).

## Pinned heads (merged --no-ff, in order)
- claude/env-art @ d3ee3aea
- claude/env-art-b @ 4ec6f92e
- claude/act2-plan @ 7887051c
- claude/ui @ cf79e115
- claude/creatures @ 1533ffbf
- claude/hero-integration @ 022223dc
- claude/audio @ 2d315058
- claude/characters @ 6960efe9
- claude/creatures-b @ 4743abd7
- claude/env-art @ bd7cfcb1

The Lead's list: env-art dadb6930 (the Ch2/Ch3 beauty pass; its newer head bd7cfcb1 adds a Ch4 in-progress log line)
and env-art-b d364a561 (the Pemakar/Ashcrown/Coilspire beauty pass) are in, along with the newest act2-plan, ui (Act II tips),
creatures and integration-qa. slice-polish, act1-chapters, m2-slice and battle-presentation have no new commits; slice-polish's
M4-A2P-115 fixes will be taken when they post.

## Resolutions
- None needed: every merge was clean (ownership.md and append-only files through merge_union).

## Build checks
validate_data 0/0 · taskboard --check clean · dlgc --check clean · gdlint and gdformat clean · test_gdignore_imports OK ·
no conflict markers · no new duplicate PROVENANCE rows, loc keys or shot ids.

GATE-BUILT @ 8c47d977

## Fast gate
- Selected: 44 test files.
- Lane A (mine): 22; lane B (GATE-HELPER): 22, in `gate-big29-lanes-b.txt` @ 43af4e0c.

## Fast-gate results
- Import check clean · boot 0 ERROR lines · log check 0.
- Lane A (mine, 22 files): all green.
- Lane B (GATE-HELPER, 22 files @ 43af4e0c, arrived 19:34): 21 green.
  - **test_cutscene_face_per_actor** 2/1 (`test_his_shipped_pose_table_is_characters`): the shipped
    game/data/cutscene/sefir_face_poses.json differs from characters' source
    game/levels/_tests/characters/sefir/sefir_face_poses.json in `sad` and `tender`. characters' dd590bd7 (M4-A2P-055,
    Sefir in person) changed the source without syncing the shipped copy; the same mismatch is on claude/characters
    alone. Branch content. Routed: **characters** (copy the source into the shipped table, as the test asks).
- Per the Lead (19:45), merged after lanes A and B:
  - claude/audio @ 590e3ceb
  - claude/act2-plan @ f69bdcfb
  - claude/creatures @ 3c681f8d
  - claude/ui @ b084899d
  - claude/m2-slice @ c0ef15b4
  - claude/env-art @ 7d2197e6
  - claude/characters @ eb04c076
  - claude/battle-presentation @ 004f4dae
  These include slice-polish's 5a935953 (A1–A8 Act I story fixes; on claude/m2-slice), audio 3d9476ea, act2-plan's
  emotional-beats pass, creatures' Oruvel and Pemakar vignettes, and ui's newest. All clean (an import-written
  test_prop_audio.gd.uid was removed so audio's committed one wins). Checks: validate_data 0/0 · taskboard clean ·
  dlgc clean · gdlint clean · test_gdignore_imports OK · no new duplicate rows, keys or shot ids.
  Re-gate: a fresh import plus the 66 test files these merges touch, run by me. characters' newer head doesn't sync
  Sefir's shipped poses yet (still routed).

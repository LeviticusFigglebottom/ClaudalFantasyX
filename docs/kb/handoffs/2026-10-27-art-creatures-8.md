# Handoff: creatures track (art), 2026-10-27, base clips under the floor (worktree agent)

Branch `worktree-agent-ab04148130b2b3dd6`, launched by the creatures Lead (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY).
Not pushed. The Lead merges it and records the claim.

## Done
- **M3-CRE-631**, to review (art). The before/after numbers are in
  docs/kb/tasks/M3/M3-CRE-631-base-clips-under-the-floor.md.
  - **New `assets_src/creatures/common/grounding.py`** (creature_kit.py untouched). It poses the mesh at every baked
    frame as the export does, and turns or lifts listed limbs by the least amount that keeps them on the floor.
  - **Reef crab** (and the wallcrab, wreck crab and root crab):
    - every clip stays at or above y 0, with a new KO in which it settles on its plastron, knees up;
    - the weak-point mask peaks at 1.0 (was 0.16), a small closed mark;
    - 7,928 triangles (was 8,648), from a coarser plastron.
  - **Tide crawler** (and the rim crawler): every clip stays at or above y 0, with a new KO that collapses 0.22 m.
  - **Slag tortoise** (and the scree crawler): flat soles at y 0, legs lifted where the shell would press them through
    the floor, and a KO that tucks the legs in and rises 4 cm.
  - **Test:** tools/tests/test_creatures.py `GroundedClipsTest` skins every frame from the GLB (about 3 s).
  - **Verify:** every one of the 42 creature jobs prints identical, the 8 rebuilt and the 34 untouched.

## In progress
- Nothing. The renders wait for the PC.

## Exact next step
1. Merge the branch.
2. RENDER-REQUEST on the PC:
   - `creature_reef_crab`, `creature_reef_crab_attack`, `creature_wallcrab`, `creature_wreck_crab`, `creature_root_crab`;
   - `creature_tide_crawler`, `creature_rim_crawler`, `creature_slag_tortoise`, `creature_scree_crawler`;
   - the `battle_choreo_*` shots.
3. View them, re-approve the baselines, and fill the task's Review log.

## Known issues
- Many other shipped creatures still go under the floor; the task file lists them with their depths. Each needs the
  same fix (grounding limbs and a KO on the floor), then a `GroundedClipsTest.GROUNDED` entry. A follow-up task is
  for the Lead to file.
- The slag tortoise's sheet says "legs still" in its KO. The legs now draw in as it tips, then hold.

## Files touched
- **New:** `assets_src/creatures/common/grounding.py`, this handoff.
- **Builds:**
  - `assets_src/creatures/{reef_crab,tide_crawler,slag_tortoise}/build_*.py`;
  - `assets_src/creatures/{wallcrab,wreck_crab,root_crab,rim_crawler,scree_crawler}/build_*.py` (one line each:
    `export_clips`).
- **Outputs:** the 8 GLBs under `assets/creatures/`. Materials are unchanged.
- **Shared:** `assets/PROVENANCE.md` (the 8 GLB rows' sources); `tools/tests/test_creatures.py`;
  `docs/kb/art/creatures/pipeline.md`.
- **Task:** `docs/kb/tasks/M3/M3-CRE-631-base-clips-under-the-floor.md`.

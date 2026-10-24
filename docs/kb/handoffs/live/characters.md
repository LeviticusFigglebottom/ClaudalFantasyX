# Live log: characters environment

**This environment owns this file** (CLAUDE.md §7a). Cloud session `session_01JqzzxgJU9Dmu7fRhmCG9aQ`, branch
`claude/characters` (cut from `claude/undertow-lead-handoff-423ixt` at 952ef7c). The Lead reads it hourly.

## Now
- **M2-CHR-02 Toma** (next): same layout as Rhen.

## Queue
1. ~~M2-CHR-01 Rhen~~ (review) → 2. M2-CHR-02 Toma → 3. Asha clips (M2-FP-07) → 4. Asha fidelity faults (lash comb, lid
   band, brow notch).

## Done
- **M2-CHR-01 Rhen → review** (reviewer: rendering or lead). `assets_src/characters/rhen/` on Asha's MPFB2 pipeline (imports
  her modules; `build_asha` as a helper library). 57,914 LOD0 tris, `rhen.glb` 4.37 MB. Review: docs/kb/art/characters/rhen_review.md.
  - **To merge:** `verify_blender_builds.py --job rhen --job asha` → asha 44 identical, rhen 31 identical. Shots: asha_* (10)
    unchanged; **6 NEW baselines** (rhen_front, rhen_q34, rhen_profile, rhen_back, rhen_face_neutral, rhen_face_smile), approved
    on lavapipe. No existing baseline re-approved. Godot `--filter=hero_stage` and `--filter=character_shading` green.
  - Shared-file edits: assets/PROVENANCE.md (rows appended), tests/screenshots/shots.json (6 entries after the asha block),
    tools/dev/blender_builds.json (job `rhen` after `asha`), asha_textures.py (3 knobs, Asha's defaults), asha_stage.gd
    (`character_name`).
  - Ask the PC GPU session for a capture of the Rhen face and hair shots.
- Setup: branch pushed; Godot 4.6.3, render deps and Blender 5.0.1 fetched.

## Un-pushed state
- None.

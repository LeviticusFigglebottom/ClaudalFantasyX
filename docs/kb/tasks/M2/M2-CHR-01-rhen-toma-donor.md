---
id: M2-CHR-01
title: "Rhen on the MPFB2 donor topology at slice fidelity (Toma split to M2-CHR-02)"
role: character
status: review
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters)"
depends_on: [M1-CHR-03]
milestone: M2
request-from: "lead"
reviewer: rendering
---
## Goal
**Scope (characters track, per the Lead 2026-10-24):** this file covers Rhen; Toma is split out to M2-CHR-02 (`M2-CHR-02-toma-slice-fidelity.md`). The characters track first filed its own `M2-CHR-01-rhen-slice-fidelity.md`; it is merged into this file and deleted.

M1-CHR-03 rebuilt Asha and the base bodies on the CC0 hm08 donor (ADR 0021). Its follow-up list named "Rhen and Toma `donor_mix` and face sliders", but no task was filed for it (review-sweep-O). The M2 slice puts both heroes in dialogue.

## Acceptance criteria
- [x] A `donor_mix`, macro mix and face slider set for Rhen (Toma: M2-CHR-02), per their SPEC §7.3 proportions and design sheets, behind the same interfaces as Asha's (parameters JSON, landmarks, `DEF-*` skeleton, the shape names).
- [x] Heavy modification per ADR 0021. Only the vendored CC0 data is used, and PROVENANCE has rows for every derived file.
- [x] LOD0 and LOD1 within the character budget; each GLB under 5 MB.
- [x] A first dialogue-range §14 pass recorded, with the stylisation rule from ADR 0019 (rhen_review.md §3; the dialogue skin material `skin_head_dialogue` carries the ADR 0019 painterly values).
### The characters track's criteria (merged)
- [x] `assets_src/characters/rhen/` builds `assets/characters/rhen/rhen.glb` (+ LOD1), textures and materials from
      source; reuses the Asha modules instead of copying them; every output under 5 MB.
- [x] A `rhen` job in `tools/dev/blender_builds.json`; `verify_blender_builds.py --job rhen` is byte-identical, and
      `--job asha` stays identical (shared modules may only gain knobs whose defaults keep Asha's bytes).
- [x] Rhen's emotion table (rhen.md §6) as `rhen_face_poses.json`, including the crooked smile.
- [x] A review stage plus new shots (front, three-quarter, profile, back, face neutral, face smile), baselines
      approved on lavapipe; no existing baseline re-approved.
- [x] PROVENANCE rows; an honest §14 assessment in `docs/kb/art/characters/rhen_review.md`.



## Notes
- **Built** (2026-10-24): 57,914 LOD0 tris (budget 58,500), LOD1 27,009; `rhen.glb` 4.37 MB, `rhen_lod1.glb` 1.30 MB;
  12 textures (largest 3.0 MB) and 17 materials. Review and honest §14 notes: `docs/kb/art/characters/rhen_review.md`.
- **Shared, not copied:** `build_rhen.py` imports `build_asha` as a library; `asha_textures.py` gained the knobs `PREFIX`,
  `SKIN_HEX`, `FRECKLES` (defaults = Asha). `asha_stage.gd` gained `character_name` (default "Asha"). How to add a hero:
  pipeline.md §12.
- **Gates run:** `verify_blender_builds.py --job rhen --job asha` (HYMN_BLENDER_BASE = merge-base 952ef7c): asha 44
  identical, rhen 31 identical. asha_* shots (10) compared with no drift (max rmse 0.00057). New baselines approved on
  lavapipe: rhen_front, rhen_q34 (his left: camera ThreeQuarterLeft), rhen_profile, rhen_back, rhen_face_neutral,
  rhen_face_smile. Godot `--filter=hero_stage` (2), `--filter=character_shading` (14) and `--filter=post_import` (17)
  green. `tools/tests` full run (454 OK).
  validate_data, taskboard --check, gdlint/gdformat clean.
- **Open (follow-ups, see rhen_review.md §4):** rig extras (lantern pendulum, coil, hem, sleeve chain); globe cracks and
  the oil-lamp light; a second hair pass (darker roots, a broken crown silhouette); a GPU capture from the PC session;
  rhen.md §6's soft_smile dimple contradiction (Art).
- **Import:** Rhen adopts the `characters` post-import rules from the start (`game/data/import/characters.json`,
  `import_script/path` in both `.glb.import`); the shots are byte-identical with the import-time materials.
- **Reviewer:** rendering (GPU look), or lead.

## Review log

---
id: M2-CHR-04
title: "Toma follow-ups: hair and beard cards, sash tails, sandal soles, rig extras, his clip set"
role: character
status: review
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters; worktree subagent)"
reviewer: rendering
depends_on: [M2-CHR-02]
milestone: M2
request-from: lead
---
## Goal
The open items in docs/kb/art/characters/toma_review.md.

## Acceptance criteria
- [x] Hair and beard read as hair up close, not flakes, and the hair reads black under the stage key.
- [x] Sash tails hang and fold, not stiff panels; the stencil doesn't ladder at mid range.
- [x] Reinforced sandal soles that read (toma.md §4 #6).
- [x] Rig extras per toma.md §9 (sash tails 2×4, pauldron hinge, shield bone, spear bone), exported as DEF-* bones.
- [x] A `toma` persona in assets_src/characters/asha/hero_clips.py (sway 70%, wide stance) with his clip set.
- [x] `verify --job toma` identical; toma_* shots re-approved after viewing.

## Notes
Write-up: docs/kb/art/characters/toma_review.md §5; pipeline.md §12 (hero bones, short-hair cards) and §13 (Toma's
clips). Handoff: docs/kb/handoffs/2026-10-24-character-6.md.
- Hair and beard: Toma's own short-hair atlas (`toma_shorthair.png`, toma_textures.short_hair_atlas: soft-sided tufts
  of tapered strands); fewer, wider, overlapping single-segment tufts (hair 1,280, beard 540, down from 920), the beard
  flatter on the jaw; the scalp paint keeps 60% density with the skin between the hairs shaded and cooled; cooler,
  deeper card colours, neutral low lobes and mostly wrapped-Lambert shading (per-card Kajiya shading was the flake
  look). On lavapipe the cap reads as a dark cropped mass with a soft hairline; the crown still takes an olive-brown
  sheen under the orange key (as Asha's black hair does on this stage). GPU look still wanted.
- Sash tails: `toma_costume.sash_tail`, 18 × 11 grids, gathered at the knot, plumb below the widest point, folds that
  deepen toward the hem, S-sway, twist, slanted hem; the stencil is three motif rows of falling size, not a repeated
  ladder.
- Sandals: `toma_costume.reinforced_sandal` (two-tier sole with a stitched welt, thicker heel, heel counter, straps).
  Rhen's `wrapped_sandal` outline came from one slice at the floor, inside the foot's silhouette; Toma's is the widest
  of four slices (Rhen unchanged).
- Rig extras: 11 bones appended in build_toma (DEF-sash_tail_a/_b chains of 4 on DEF-spine, DEF-pauldron on
  DEF-shoulder.L, DEF-shield on DEF-spine.003, DEF-spear on DEF-hand.R), with the tails, lames, shield and spear
  weighted to them; bb_rig unchanged. The 75 standard bones keep names and relative order (absolute joint indices
  move: the exporter walks the hierarchy).
- Clips: `toma` persona (sway 0.7, ankles 1.4× the shoulder-joint spacing, knees soft 7°, hips 2.7 cm lower) and ten
  clips: idle, walk, run, talk, spear_level, lower_spear, palms_level, catch_rhen, sit_steps, turn_seaward
  (`assets/characters/toma/anim/toma_clips.tres`). Asha's and Rhen's libraries are byte-identical.
- Numbers: LOD0 59,152 tris (budget 66,000), LOD1 27,544 (33,000); toma.glb 4.68 MB (was 4.86), toma_lod1.glb 1.38 MB.
- After the parent's `asha_costume._panel` / mouth-split merge: rebuild Toma (`assets_src/characters/toma/build.sh`),
  then rerun `python3 assets_src/characters/asha/hero_clips.py --hero toma` (the clips read the GLB's rest), then
  re-approve the toma_* shots.

## Review log

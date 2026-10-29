# 0140 — Asha's skirt: 16 panels, the even ones derived at runtime

- **Status:** accepted
- **Date:** 2026-10-28
- **Roles affected:** character (hero clips, rig probe, import), hero-integration (every Asha actor), rendering (review)
- **Author role:** character

## Context
The Lead's queue asks for "Asha's skirt as cloth" (big14), and the human's playtest saw a stiff bell in the kneels.
M2-CHR-522's floor drape stopped the crushed white wall, but 8 panels are too wide to fold. With 16 panels the pooled hem
folds (M2-CHR-542), but baking 16 panels makes `asha_clips.tres` 4.94 MB, over test_hero_clips' 4 MB text bound and near
the repo's 5 MB file cap.

The Lead chose (b): bake no skirt and solve it at runtime with `HeroHelperBones` on every actor. Conditions: under about
0.2 ms per hero, or fall back to (c), sparser keys. Measured:
- `HeroHelperBones.drive` costs about 107 ms per call in GDScript, even with the panel cloth cached. That is 500 times the
  budget.
- Sparser keys at 0.5° (the stage parity test allows 1°) still leave the library at 4.62 MB. Most of the skirt's bytes are
  per-track overhead, not keys.

## Options
1. Binary `.res` clip libraries: every scene that loads the `.tres` changes, which is cross-track.
2. Runtime solve everywhere: about 107 ms per hero per frame. Ruled out.
3. Sparser keys: 4.62 MB. Ruled out.
4. Bake half the panels and derive the other half at runtime by a closed-form rule from their baked neighbours.

## Decision
Option 4.
- **Which panels are baked:** Asha has 16 skirt panels (`helper_bones.SKIRT_SECTORS`). The odd-numbered ones lie over the
  legs at rest, about 22.5° either side of front and back. They are solved offline by `hero_clips.skirt_solve`, as before,
  and baked.
- **Which are derived:** the even-numbered ones (front centre, back centre, the sides) are never baked.
- **The rule for a derived panel:**
  - each level takes the larger of its two odd neighbours' swings, because their mean cut into a knee between them;
  - its hem takes their mean, because the larger folded the hem into spikes;
  - its gather is the mean of theirs;
  - its lowest bone swings `fold_deg` (6°) further out once the hem lies past `fold_from_deg` (cloth draped out on the
    floor), eased in over `fold_ease_deg`. So a pooled hem rolls into folds.
- **The same rule in both places:** `hero_clips.derive_folds` applies it offline, so the rig probe, the staff's pivot and
  the stage solve see it. `HeroHelperBones.apply_folds` applies it in the game, reading the odd panels' swings back out of
  their posed rotations.
- **How every actor gets it:** `HeroSkirtFolds`, a `SkeletonModifier3D`, runs `apply_folds` every frame after the
  animation. The characters import (`characters_post_import.gd`) adds one under every skeleton with derived panels, so every
  instance of `asha.glb` and `asha_lod1.glb` has it: field, cutscene and battle.

## Consequences
- `asha_clips.tres` stays at 3.82 MB, and the kneels' pooled hem folds.
- `apply_folds` costs about 0.037 ms per hero in the headless container (the test ceiling is 0.2 ms).
- An Asha played without the modifier (a hand-built scene that does not instance the imported GLB) shows the even panels at
  rest. `test_skirt_folds_are_derived_at_runtime` checks that the import adds the modifier and that no clip bakes a derived
  panel.
- A machine with a stale import cache needs `asha.glb` re-imported. The rebuilt GLB's new content hash forces this.
- The staff's skirt-clearing pivot changes with the narrower panels:
  - `PROP_SKIRT_CLEAR` goes from 35 to 50 mm, because the cloth bends more between its sample points;
  - it now also keeps the shaft above the fist `PROP_HEAD_CLEAR` from the head, because tipping the foot out swung the top
    into the head in pole_out.
- Only Asha's build makes skirt panels, so no other hero changes.

---
id: M2-CHR-542
title: "Asha's skirt as cloth: 16 panels so the pooled hem folds"
role: character
status: review
owner_session: "characters (claude/characters, worktree drape-wt)"
depends_on: [M2-CHR-522]
milestone: M2
reviewer: rendering
---
## Goal
The Lead's queue (big14): "Asha's skirt as cloth". M2-CHR-522's floor drape (8e7d5f67) stops the pooled underskirt
standing as a crushed white wall in the kneels. With 8 panels, though, the overskirt is still a smooth bell and the hem a
clean circle. A fluting pass on 8 panels (every other panel's lowest bone swung out when the cloth pools) changes almost
nothing: each panel is too wide to fold. With 16 panels the same fluting rolls the pooled hem into visible folds.

## Prototype (superseded by the build below)
- First built on a local branch `chr-skirt-16`; its patch file was removed once the build below merged.
- What it changes:
  - `helper_bones.SKIRT_SECTORS` 8 → 16 (only Asha's build makes skirt panels).
  - `flute_deg` 14 in `helper_bones.json`: odd-numbered panels' lowest bones swing further out, scaled by how far
    their plain gather would shorten them.
  - The same fluting in `HeroHelperBones`.
- Renders: kneel_over_rhen and bow_palms_flat show folds in the pooled hem. walk_cycle, run and front read as before.
  Asha's LOD0 is 64,952 triangles, the GLB 4.71 MB.

## Blockers (why it is not merged)
1. **Library size:** `asha_clips.tres` is 4.94 MB. That is over test_hero_clips' 4 MB text bound and close to the repo's
   5 MB file cap: 16 panels double the skirt tracks. Options:
   - (a) Save the libraries binary (`.res`, as the test's own comment says). Every scene that loads `asha_clips.tres`
     changes, a cross-track change.
   - (b) Bake no skirt tracks and let `HeroHelperBones` solve the skirt at runtime on every hero actor (field, cutscene,
     battle). This needs hero-integration to confirm every actor runs it, and a per-frame cost check.
   - (c) Key the skirt panels at a lower rate, or with a looser `key_tolerance_deg`. **Tried: not enough.** At 0.5° (the
     parity test allows 1°) the library is still 4.62 MB, because most of the skirt's 2.22 MB is per-track overhead
     (48 panel tracks in each of 66 clips), not keys. So it is (a) or (b).
2. **The staff:** its skirt-clearing pivot (`prop_pivot`) solves against the new panels. It tips the staff 41 mm into
   her head at pole_out@24 and across the skirt in walk@6. The pivot's search needs retuning for the narrower panels.
3. **turn_in_place_180@9:** the left thigh is 2 mm further through the skirt (Costume 35.95 / 34 and Body 48.83 / 47).

## Acceptance criteria
- [x] The Lead chose (b). Measured, it is about 107 ms per hero (the budget is 0.2), and (c) was 4.62 MB. So it is
      ADR 0140: the odd panels (over the legs) are baked, and the even ones are derived each frame by HeroSkirtFolds
      (0.037 ms). The library is 3.82 MB.
- [x] Rig probe clean: the staff pivot keeps 50 mm from the cloth and stays clear of the head; one ratchet raise,
      reasoned (Body count 24 -> 25).
- [x] Self-rendered kneel_over_rhen, bow_palms_flat, float_boat, walk_cycle and run, viewed. Asha verified identical on
      the three numpy paths.

## Notes
- Filed 2026-10-28 by the characters track.
- Built 2026-10-28 (ADR 0140, merged @ 67a1b2a0). Things learned:
  - The first even-derived rule took the mean of the neighbours at every level. It cut into the knee in float_boat,
    because the knees lie under the odd panels.
  - Taking the larger swing at the hem, with a 14° fold, folded it into paper-star spikes. So the hem takes the mean, and
    the fold is 6°.

## Review log

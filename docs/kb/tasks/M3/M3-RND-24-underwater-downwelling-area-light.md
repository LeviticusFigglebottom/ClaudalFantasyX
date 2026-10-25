---
id: M3-RND-24
title: "Underwater rig: a downwelling term and a per-area light scale (the Ch1 Underway's interiors and depth)"
role: rendering
status: todo
owner_session: ""
depends_on: [M3-ENV-05]
milestone: M3
request-from: environment
reviewer: environment
---
## Goal
The Ch1 dive (docs/kb/art/environments/oruvel_underway.md §0) walks from the crown at 6 m to a gallery and a terrace
at 21–22 m, much of it inside a drowned tower. Two things the `UnderwaterRig` (M2-RND-02, M2-RND-09) doesn't do yet
showed in the M3-ENV-05 preview, and the preview fakes both per shot
(`game/levels/_tests/oruvel_underway_kit/oruvel_underway_preview.gd`):

1. **Downwelling.** The post absorbs light along the camera's ray only. The sun reaching a surface at depth is not
   attenuated on its way down, so a floor at 22 m is lit by the full noon sun, warm and white (the first preview
   captures read as a sunlit beach). The preview tints the sun and the ambient by the rig's own transmittance over
   the subject's depth, exp(−σ·d) per channel, one value per shot. A shader term (the directional light attenuated
   by the water above each shaded point, `hymn_water_level` and the rig's σ) would do it per pixel, and would also
   brighten the tower's upper floors against its foot, which one value per shot cannot.
2. **A per-area light scale.** The rig lights its in-scatter with the scene's sun and no occlusion, so inside the
   tower the water glows as brightly as the open sea and drowns the lantern's pool. The preview scales the
   in-scatter (through a private copy of the rig's data, `light_reference`) and the ambient per area: open 1.0 /
   0.65, interior 0.33 / 0.22, deep 0.2 / 0.14. The zone needs an exported scale on the rig that a trigger volume or
   the zone script can set and blend (about 1 s) as Rhen walks from the crown into the galleries.

## Acceptance criteria
- [ ] A downwelling term (per pixel, or per object if that is the tier's budget) with σ from the rig's data; the
      terrace at 21 m reads teal-lit, the crown at 6 m warmer, without the preview's per-shot tint.
- [ ] An exported light scale on `UnderwaterRig` (in-scatter and, optionally, the ambient), blendable, with a test.
- [ ] Re-capture the M3-ENV-05 baselines (`ou_u04_lamp_gallery`, `ou_u12_terrace`) with the preview's stand-ins
      removed; Environment reviews.

## Review log

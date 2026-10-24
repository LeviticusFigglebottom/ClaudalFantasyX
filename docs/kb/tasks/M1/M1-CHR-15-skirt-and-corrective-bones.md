---
id: M1-CHR-15
title: "Skirt and corrective bones for deep poses (floor-length skirts in a lunge, armpits, spear turn)"
role: character
status: todo
owner_session: ""
depends_on: [M1-CHR-14]
milestone: M1
request-from: "character"
priority: normal
---
## Goal
M1-CHR-14 fixed every clip-frame fault that weighting and garment cuts can fix. Three linear-blend-skinning limits are left. Each is pinned as a ratchet in `tools/dev/rig_checks.json`.
1. **Asha's floor-length tube skirts in a deep lunge.** In `asha_clip_offer_hand` and `kneel_over_rhen` they stretch between the knees: the white under-layer twists and the back shin shows through.
2. **The upper arm sinking into the torso cloth** at the armpit when the clips lower the arms 38–42° from the bind pose. This affects all three heroes.
3. **Toma's spear grazing his forearm** for a few frames while the hand turns it.

## Approach (proposal)
- Add 4–6 skirt bones per skirt (front, back and sides), parented to the hips. Each `hero_clips.py` frame drives them from the thigh angles: a procedural drape that is still a deterministic, baked clip. Toma's rig extras (M2-CHR-04) are the pattern.
- Add one corrective bone per shoulder (a deltoid/armpit helper) that turns half as much as the upper arm, weighted into the armpit skin and the garment's armhole edge.
- Give `spear_level` and `lower_spear` an arm-lift key before the turn.

## Acceptance criteria
- [ ] Each ratchet in `rig_checks.json` comes down. Target: skin through cloth under 10 mm and garment in skin under 10 mm in every clip frame.
- [ ] The clip shots, viewed, show no skirt tear and no armhole overlap.
- [ ] Builds are reproducible.

## Notes
- Rebuild hygiene (from M1-CHR-14): when Rhen, Toma or the villagers next rebuild, have their texture runs set `asha_textures.PRE_ROUND = PRE_ROUND_DECIMALS` the way Asha's run does. That makes their PNGs host-independent too (the 8-bit rounding flips; see live/characters.md). Their builds also need the shape-delta grid.

## Review log

---
id: M1-CHR-15
title: "Skirt and corrective bones for deep poses (floor-length skirts in a lunge, armpits, spear turn)"
role: character
status: review
reviewer: rendering
owner_session: "characters (cloud session_01JqzzxgJU9Dmu7fRhmCG9aQ, branch claude/characters)"
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

- **2026-10-24, done (worktree subagent; handoff 2026-10-24-character-14.md, pipeline.md §17).**
  - **Helper bones:**
    - `DEF-armpit.L/.R` on every hero. Each turns 0.35 of the upper arm's own turn while the arm is lowered, and all of
      it once the arm is lifted 30°.
    - `DEF-skirt_0..7(.001)` on Asha: 8 two-bone panel chains on the hips.
    - Every clip keys these bones from the generic build path (`Skeleton.keyed`).
    - The runtime twin is `HeroHelperBones.drive` (AshaStage after `world_pose`; Haluna is M2-ENV-14). It matches the
      baked keys within 1° (test_hero_stage).
    - The parameters are in `game/data/characters/helper_bones.json`.
  - **Skirt solve:** each panel swings out by the least angle that keeps the cloth it carries at its rest clearance from
    the leg axes. The legs and hips under the skirts stay whole (decimated to 25%; LOD0 64,952), and the inner skirt
    is a convex tube.
  - **Toma's spear:**
    - It sits 3.4 cm out from the fist, and its foot is 1.2° forward.
    - `spear_level` and `lower_spear` run one path: the arm swings out while the hand turns the spear.
  - **Asha's staff:** it sits 1.6 cm out from the fist, and her staff arm hangs 6° wider.
  - **Rhen and Toma** got the host snaps: midline, UVs, shape noise and PRE_ROUND, plus a 1 µm position grid.
  - **Every-frame probe, worst before → after (mm):**

    | Hero | Check | Before | After |
    |---|---|---|---|
    | Asha | Costume | 43.8 | 32.8 (the sandal soles at rest; the skirts 0) |
    | Asha | VerseSleeve | 40.2 | 35.5 |
    | Asha | Body | 46.7 | 46.7 (extreme_pose; the clips 46 → 37.7) |
    | Rhen | Costume | 31.2 | 31.2 |
    | Rhen | Body | 61.7 | 61.1 (item; arms down < 30) |
    | Toma | Costume | 31.7 | 31.7 |
    | Toma | Props | 16.6 | 0 |
    | Toma | Body | 69.1 | 53.6 (toe through the trouser hem; armpit 18.5) |

    Exposed boundaries are 2 / 22 / 2, unchanged.
  - **Ratchets:** lowered in rig_checks.json, with the notes rewritten.
  - **Not met:** the 10 mm target.
    - The sandal soles sit inside the feet at rest.
    - The extreme pose and raised-arm clips still put the front of the shoulder past the armhole edge.
    - Rhen's and Toma's shirt and tunic sides sit against the hanging arm.
    - Toma's toes go through his hem.
  - **Look:** in the deepest poses (offer_hand, kneel, laugh, extreme_pose) the skirts read as a stiff, wide bell with
    faint creases at the sector seams. They are clean, but not soft. Viewed and approved as no worse than the torn
    look before; the rendering reviewer should judge.

- **2026-10-27, merged onto claude/characters with M2-CHR-12 and the stiff bell fixed (characters, new account).**
  - **Merge:** hero_clips.py keeps both blocks (M2-CHR-12 locomotion, then these helpers). The rebuilt GLBs are
    identical under `verify --job asha --job rhen --job toma` on all three numpy paths (native AVX-512, `X86_V4` off,
    `X86_V3 X86_V4` off): 44 / 31 / 38. This also closes M2-CHR-11's rhen and toma half.
  - **The stiff bell, fixed.** Two causes: the neighbour lag (20 deg per 45) dragged the side and back panels up with
    the front ones into a cone, and nothing let floor-length cloth rest on the floor. Now:
    - `lag_deg_per_45` 40: the sides hang by their own clearance;
    - **floor gather:** where a lower panel's cloth would pass `floor_clear_m` above the floor, the lower bone scales
      along its length (down to `gather_min`) and flares a little across it, so the cloth pools on the ground;
    - **overhang gather:** a lower panel swung out past 55 deg (lying over the calves in a kneel) ends a little past
      the legs that carry it, eased in over 20 deg of swing.
    - Baked as `scale_3d` keys on every clip (a still gather is two keys, so no clip leaves another's gather on the
      bone); `HeroHelperBones.drive` solves the same (test_hero_stage compares the rotations and the scales).
    - Viewed (cloud lavapipe, before the render move): kneel_over_rhen, laugh and offer_hand now drape and pool
      instead of fanning into a disc. Still stiff: `asha_extreme_pose` (the stress stage, thigh raised 90 deg) puts
      the front panel into a tent, because each panel has one joint and it sits above the knee; the white
      underskirt still spreads a plate of pooled cloth before the knees in offer_hand. Neither is in a gameplay clip.
  - **Library size:** the helper keys a slerp reproduces within `key_tolerance_deg` are dropped; asha_clips.tres is
    1.94 MB (cap 2 MB). Asha's next clips (M2-CHR-513, M3-CHR-05) need body-track key reduction or a higher cap.
  - **Ratchets after the merge** (every frame): Rhen Body count 42 (limit 44); Toma Body 73.9 mm at run@4, his toes
    through the trouser hem at the M2-CHR-12 run's toe-off (limit 75; follow-up in M2-CHR-513).
  - **Shots:** requested from the PC (asha_*, rhen_*, toma_*); re-approve after viewing its render.

## Review log

---
id: M3-CRE-655
title: "Act I regular to final quality: the raid hound reads crude (blocky segmented legs, a horse-like head) in its portrait and review shot"
role: character
status: review
owner_session: "creatures (worktree agent)"
reviewer: art
depends_on: [M3-CRE-650]
milestone: M3
request-from: lead
---
## Goal
ADR 0041. The bestiary portrait and review shot (viewed 2026-10-28, M3-CRE-652) show the Order's shoal-hound as
cylinders on stick legs with a long horse-like head in a red cage muzzle. Make it a lean, deep-chested hound: a
greyhound's legs with real joints, paws and hocks; a wedge head with ears and a jaw under the muzzle cage; the Order's
harness reading as leather and lacquer. Keep its bones, clips and vfx_anchors. Starts after M3-CRE-650 adds its weak
point, since that changes the same build.

## Notes
- 2026-10-28 (creatures worktree agent): re-modelled on the same rig, bone names, clips and contact times
  (assets_src/creatures/raid_hound/build_raid_hound.py; the sheet's "Final quality" section has the detail):
  - a lofted torso with a keel, a tuck, an arched loin and ribs; a broader, blunter breast;
  - greyhound legs with elbow, carpus, stifle and hock on hare feet with toes;
  - a wedge head over a separate jaw, with rose ears;
  - a Y-harness of tortoiseshell leather laid on the body, with brass rings and the Order's plate (the Level) at the
    withers;
  - a red-lacquered basket cage on a leather headstall, its lower half riding the jaw;
  - coat variation (saddle, brindle, pale underparts, wet mud on the legs and belly) through vertex colour, cavity
    and wetness.
- New `lacquer` and `metal` slots, with PROVENANCE rows appended. Budget raised to the regular ceiling of 8k (the
  reef crab's), built at 7,424 triangles (was 3,758).
- Node rests identical and the same 462 animation channels. Only the grounding's upper-leg corrections moved (worst
  0.074 in a quaternion component). GroundedClipsTest passes, with no allow-list entry.
- The weak-point scar (M3-CRE-650) keeps its size, colours and slant. Its centre moved onto the new breast beside the
  breast strap. It faces the review three-quarter at 0.43 and the battle camera at 0.77, and it was viewed reading in
  both.
- Self-rendered and viewed: creature_raid_hound, battle_boss_intro_inquisitor (the hound on the battle stage), and
  the portrait, which is re-baked into assets/ui/portraits/creatures/raid_hound.png. No baselines were written; the
  Lead re-approves both shots after viewing.

## Review log

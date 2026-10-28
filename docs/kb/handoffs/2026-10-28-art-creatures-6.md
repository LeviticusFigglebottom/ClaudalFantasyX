# Handoff — art (creatures) — 2026-10-28 #6

Worktree agent for M3-CRE-655 (ADR 0041: the raid hound to final quality). The branch was cut from
`claude/creatures` and is not pushed; the coordinator merges it.

## Done
- **The raid hound is re-modelled** as a lean, deep-chested greyhound on the same rig, bone names, clips and contact
  times (assets_src/creatures/raid_hound/build_raid_hound.py):
  - a lofted torso: keel, tuck, arched loin, ribs, and a broad, blunt breast;
  - greyhound legs with the elbow, carpus, stifle and hock, on hare feet with toes and dark nails;
  - a wedge head over a separate jaw, with dark lips, canines and rose ears;
  - a Y-harness of tortoiseshell leather cast onto the body: neck ring, breast strap, girth and back strap, with brass
    rings and the Order's plate (the Level) at the withers;
  - a red-lacquered basket cage on a leather headstall, its lower half riding the jaw;
  - coat variation through vertex colour, cavity and wetness: saddle, brindle, pale underparts, and wet mud on the
    legs and belly.
- **Materials:** two new slots, `lacquer` (clearcoat through vertex wetness, no darkening) and `metal` (brass). Their
  `.tres` files have PROVENANCE rows appended at the end.
- **Budget:** raised from 7k to the regular ceiling of 8k (the reef crab's); built at 7,424 triangles (was 3,758).
  The sheet records the per-part split.
- **The weak-point scar** (M3-CRE-650) keeps its size, colours, values and slant. Its centre moved onto the new
  breast, beside the breast strap and under the neck ring (SCAR_AT). It faces the review three-quarter at 0.43 and
  the battle camera at 0.77. The neck ring moved up the neck (NECK_RING_U 0.42) to clear it.
- **Rig and clips:** node rests identical; the same 462 animation channels. Only the grounding's upper-leg
  corrections moved (worst 0.074 in a quaternion component, the KO's hind legs).
- **Portrait** re-baked and committed (assets/ui/portraits/creatures/raid_hound.png, the viewed render).
- The sheet (docs/kb/art/creatures/act1/raid_hound.md, "Final quality") and the task are amended. The task is in
  `review` (reviewer: art).

## Renders (self-rendered in this container and viewed)
- `creature_raid_hound`:
  /tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-655/out6/creature_raid_hound.png
- `battle_boss_intro_inquisitor` (the hound on the battle stage, the battle camera on its -x side; the scar reads
  clearly):
  /tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-655/out6/battle_boss_intro_inquisitor.png
- Portrait: /tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-655/port6/raid_hound.png
- Posed clip previews (numpy, flat-shaded):
  /tmp/claude-0/-home-user-ClaudalFantasyX/5f90d4d2-2a3d-5363-b0be-fa05b2ee8fd4/scratchpad/M3-CRE-655/poses2.png
- No baselines were written. Both shots drift from their baselines by design.

## Gates (all run in the worktree)
- `verify_blender_builds.py --job creature_raid_hound`: 6 identical.
- `unittest tools.tests.test_creatures tools.tests.test_blender_builds`: 50 OK, GroundedClipsTest included.
- validate_data: 0 errors, plus the 1 warning that was already there (haluna shrine_offering).
- taskboard --check: OK.
- gdlint and gdformat --check: clean. No GDScript was touched.
- Godot `--import`, then `run_tests.tscn -- --filter=creature`: 78 run, 1 failed. The failure is the known
  test_creature_portraits missing-PNG one (`*_held` portraits).
- `-- --filter=vfx_anchors`: 3 run, 0 failed.

## In progress
- None.

## Exact next step
1. Merge this branch into `claude/creatures`.
2. On the full gate, view and re-approve the `creature_raid_hound` and `battle_boss_intro_inquisitor` baselines.
3. The art reviewer appends the task's Review log.

## Known issues
- In the KO, the clip's +40° ear key still lifts the drooped rose ears a little above level (a small fold over the
  head). The clips are kept as they are.
- In the howl, the breast strap's top follows the neck ring only most of the way (90% at the ring), so a small gap
  opens at the O-ring at full extension.
- The Order's plate sits on the withers. It shows from the battle camera's height but not in the review
  three-quarter, where the neck hides it.
- The Stillguard Inquisitor in `battle_boss_intro_inquisitor` is still a capsule stand-in. That belongs to another
  track and wasn't touched.

## Files touched
assets_src/creatures/raid_hound/{build_raid_hound.py,materials.json},
assets/creatures/raid_hound/{raid_hound.glb,materials/lacquer.tres,materials/metal.tres},
assets/PROVENANCE.md (two rows appended), assets/ui/portraits/creatures/raid_hound.png,
docs/kb/art/creatures/act1/raid_hound.md, docs/kb/tasks/M3/M3-CRE-655-raid-hound-polish.md, this handoff.

---
id: M3-CRE-635
title: "Act II bosses after their first PC render: the Avalanche Ram's head reads as a duck's; the Wakefin's review shot shows only its fin"
role: character
status: blocked
blocked-by: ADR 0041
owner_session: "worktree-agent-a1a26860cbf12c949"
reviewer: art
depends_on: [M3-CRE-624, M3-CRE-626]
milestone: M3
request-from: creatures
---
## Goal
The first PC renders (gpu/render-creatures-10f21a1, -2112578, -b99be56; viewed 2026-10-27) of the Act II bosses:
- **The Lamp Engine** (closed and opened): reads as its sheet. No change.
- **The Avalanche Ram:** the head reads as a duck's. The dark, flattened muzzle on a white face is a bill, so the
  woolback looks like a duck's head on a sheep. The sheet asks for an Ullari woolback, a long-necked, shaggy pack
  animal (a camelid read): a soft rounded muzzle in the coat's colour (darkened `laterite` only at the nose), long
  upright ears, eyes set at the sides, a narrower long head, and the neck slimmer under its fleece. The icicle fringe
  reads a little like teeth along the flank: fewer, longer and irregular, hanging from the lock tips, not in a row.
- **The Wakefin:** the creature stage's opaque floor hides everything below y 0, so the review shot is the fin and
  one tail tip. That is true to its battle read, but the review needs the fish. Add a second shot from below or
  through a stage with a water plane (the creature stage may take a `floor: false` option), and strengthen the
  spine wounds: one barely shows.

## Acceptance criteria
- [x] The Ram's head re-modelled to the camelid read; GroundedClipsTest still green; Blender verify identical
- [x] A Wakefin review shot that shows the whole fish; the spine wounds read at battle distance (to confirm on the PC render)
- [ ] PC renders viewed; baselines approved from the post-M3-CRE-630 render (no baselines from the pre-fix shas)

## Notes (2026-10-27, worktree-agent-a1a26860cbf12c949)
- **The Ram** (`6650b4cb`): the head re-modelled as a camelid's in `head()` (a lofted head, `HEAD_SEC`): long and
  narrow (0.75 m by 0.29 m), the cheeks deepest, a soft rounded muzzle in the coat's colour with `laterite` darkened
  only at the nose (slit nostrils, a split upper lip) and the lips, eyes at the sides under a soft brow, long upright
  ears drooping a little out, the woolly cap kept, a slim lower jaw frosted underneath. The neck is slimmer
  (`NECK_R`, `NECK_SHAG`). Icicles: 1-3 per lock chain on random strands, 0.14-0.32 m, sheathing the strand's end
  and hanging at most 0.11 m past it (the KO lays the lock ends on the ground); two uneven belly clumps (5); one under
  the jaw. The lock strands' frost is lighter and their tips blunter and less even, so they read as locks, not spikes.
  The rig's head and jaw bones are unchanged (`HEAD_C`, `MUZZLE_TIP` kept for the rig only), and so are the clips.
  - Triangles 15,179 -> 14,855 (budget 16k). `--report`: feet at y 0 at the end of every standing clip, KO lowest
    -0.001 (as before), hit peak 0.10 s.
  - Flat PIL silhouettes (scratch, not committed), before: a round pale cranium with a dark brown, flat-topped muzzle
    tube (a bill) and seven even icicles under the jaw (teeth); from the front a brown disc filling the face. After:
    side, a long, slightly nose-down head with a rounded pale muzzle, a dark tip only at the nostrils, an upright
    leaf-shaped ear; front, a narrow face between two tall upright ears, the eyes at the sides, two dark nostril slits.
- **The Wakefin** (`cadd3630`): CreatureStage `show_floor` (default true) and a `flank_high` view (yaw 68, pitch
  24); the new shot `creature_wakefin_body` hides the floor. `creature_wakefin` and all other shots are unchanged.
  The eight wounds: longer (0.24-0.54 m), three section rows wide, wandering like a tear, deeper (3 cm), their lips
  raised and faintly lit. They lie at the waterline (y about 0), which is why the floor hid all but one. 11,128
  triangles (unchanged).
- Verify: `creature_avalanche_ram` and `creature_wakefin` identical. No captures, no baselines.
- **Needs a PC render:** `creature_avalanche_ram`, `creature_wakefin`, `creature_wakefin_body` (new), and the
  Ram's and the Wakefin's bestiary portraits once M3-CRE-634 lands.

## Review log
- 2026-10-28, creatures: **paused by ADR 0041** (Act I at final quality first; the human's directive). The work done so far is merged on claude/creatures as is; nothing reverted. Resume when a new ADR lifts the pause.

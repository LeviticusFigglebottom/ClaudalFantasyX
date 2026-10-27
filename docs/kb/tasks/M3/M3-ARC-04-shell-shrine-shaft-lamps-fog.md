---
id: M3-ARC-04
title: "Shell Shrine: the three Shaft_* omni lights stop lighting the ShaftFog volume (the Lead's fog-lamp rule)"
role: architect
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: []
milestone: M3
request-from: environment
reviewer: rendering
---
## Goal
The Lead's rule (2026-10-24, from M3-RND-05's Reefball night): a light near a dense FogVolume keeps
`light_volumetric_fog_energy` at 0. Godot's default is 1.0, so a lamp that doesn't set it lights the volume and
bands it bright. `game/levels/ch03/shell_shrine/shell_shrine.tscn` (owned by m2-slice) has a dense `ShaftFog`
volume, and three of its omni lights are on the default: `Bounce/Shaft_b1`, `Bounce/Shaft_side_pool` and
`Bounce/Shaft_b3_lip`. env-art has already set `Bounce/Skylight` to 0, because it added that light under
M2-ENV-09. `shell_shrine_level.gd` `_pool_bounce()` builds an OmniLight3D in code, so set it there too.

## Acceptance criteria
- [x] Set `light_volumetric_fog_energy = 0.0` on the three `Shaft_*` lights and on the `_pool_bounce()` light.
- [ ] Re-capture the shrine shots and view them (requested from the PC in slice-polish.md). The shafts should read from the fog shader and the sun, not from
      lamp scatter. Re-approve them if they move.
- [x] Delete the shell shrine entry from `KNOWN_EXCEPTIONS` in `tools/tests/test_fog_lamps.py`, so the rule is
      enforced with no exceptions.

- **Renumbered (Lead merge, big8, 2026-10-24):** filed as M3-ARC-02, which collided with claude/m2-slice's M3-ARC-02 (debug chapter select; M3-ARC-03 is the big8 renumber of the dialogue voice hook). Now M3-ARC-04, the next id free across all branches.

## Review log

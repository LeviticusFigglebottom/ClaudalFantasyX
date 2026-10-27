---
id: M3-CRE-635
title: "Act II bosses after their first PC render: the Avalanche Ram's head reads as a duck's; the Wakefin's review shot shows only its fin"
role: character
status: todo
owner_session: ""
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
- [ ] The Ram's head re-modelled to the camelid read; GroundedClipsTest still green; Blender verify identical
- [ ] A Wakefin review shot that shows the whole fish; the spine wounds read at battle distance
- [ ] PC renders viewed; baselines approved from the post-M3-CRE-630 render (no baselines from the pre-fix shas)

---
id: M3-ENV-07B
title: "Ch1 Oruvel in the storm: the breaking-raft state of the raft-town kit (and Hullgnaw's split deck)"
role: environment
status: doing
owner_session: "env-art"
depends_on: [M3-ENV-07]
milestone: M3
request-from: environment
reviewer: rendering
---
## Goal
Follow-up to M3-ENV-07 (filed by env-art when the kit landed without its storm state). Ch1 C1-12 to C1-15
(docs/kb/story/beats/act1_ch01.md; §9 Environment request 1, "The storm variant"): the Rising out of a clear sky,
the town's drill, the breaking raft and Hullgnaw's fight on the net-pen hull, whose deck splits three ways at the
boss's phase change (§5). The kit is built for it: every raft is a deck lashed onto separate hulls
(docs/kb/art/environments/oruvel.md §2), so a broken state replaces pieces one for one.

## Acceptance criteria
- [ ] Storm pieces on the same frame: `raft_deck_broken` (a deck torn along a bearer, planks sprung, one hull
      pulling away, its lashings snapped and trailing), `plank_bridge_broken` (the C1-13 "the bridge goes" beat),
      `hull_capsized` (a cabin hull keel-up, awash), and debris (floating planks, a cabin's keel-roof adrift).
- [ ] The net-pen hull's three-way split as a rig the boss's phase change can drive: three sections of
      `net_pen` that pitch apart (separate pieces with their hinge points in the layout), the net torn between them.
- [ ] The sea drawn back off the reef (C1-12, O11): a far reef-edge piece with towers' crowns standing clear.
- [ ] The preview gains a `ch01_storm` phase (`lut_ch01_storm`, the colour script's storm sub-frame once Art adds
      it; act1_ch01 §9 Art item 1), with at most one composed view as a baseline.
- [ ] Tests; swap-in notes for m2-slice (the C1-13 run's triggers and the boss arena's split are theirs and
      Combat's).

## Notes
- Kell's beacon is lit in the drill (C1-12) and still lit in O18: a light the zone adds on the chandlery's roof
  (anchor in the M3-ENV-07 task), `light_volumetric_fog_energy = 0`.

## Review log

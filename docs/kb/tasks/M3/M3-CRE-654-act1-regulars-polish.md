---
id: M3-CRE-654
title: "Act I regulars to final quality: shoal skipper, slag tortoise, sail leech, oil slug read unfinished in the self-render"
role: character
status: review
owner_session: "creatures (worktree agent)"
reviewer: art
depends_on: [M3-CRE-652]
milestone: M3
request-from: lead
---
## Goal
ADR 0041 (Act I at final quality). The self-render of the 20 Act I regulars (M3-CRE-652, 2026-10-28) showed four that
read primitive at the review shot:
- **shoal_skipper:** a smooth tube body, ball eyes on stalks, block fins, stick legs. It needs a real mudskipper read:
  a blunt, wide head with a mouth line, goggle eyes set *in* the head top with lids, a tapering body with skin
  texture (mottling, wet sheen), fan pectoral fins it props on, and a dorsal sail with spines and membrane.
- **slag_tortoise:** stump legs and a featureless head. It needs scaled, clawed legs, a tortoise head with a beak and
  eye, a neck fold, and slag-crust detail on the dome.
- **sail_leech:** a featureless blue sheet. It needs a segmented ribbon body with a sucker disc, a frilled sail edge,
  and visible segmentation.
- **oil_slug:** the horns read as sausages. It needs real slug tentacles (two upper with eye tips, two lower), a
  mantle and a foot fringe, and a slick oil sheen.

## Done (2026-10-28, worktree agent; handoff docs/kb/handoffs/2026-10-28-art-creatures-5.md)
Each sheet's "Final quality (M3-CRE-654)" section lists the changes. The bones, the clip names, the contact times and
the weak points are kept; no grounding allow-list entry is added.

| Creature | Triangles before | Triangles after | Budget |
|---|---|---|---|
| shoal_skipper | 1,644 | 4,952 | 5k |
| slag_tortoise | 4,624 | 7,786 | 8k (raised from 6k) |
| sail_leech | 5,728 | 4,832 | 5k |
| oil_slug | 4,192 | 5,782 | 6k |

The shared builds rebuild the Act II variants: the scree crawler goes from 4,624 to 7,786 triangles and the fen leech
from 5,728 to 5,980.

**Checks:**
- verify_blender_builds is identical for all six jobs;
- test_creatures and test_blender_builds pass;
- validate_data and taskboard --check pass;
- gdlint and gdformat are clean;
- the Godot tests with `--filter=creature` fail only on the known test_creature_portraits missing PNGs.

**Self-render:** six shots (the four, plus the fen leech and the scree crawler) drift from their baselines as
expected. All were viewed; no baselines were written. Reviewer: art.

## Review log

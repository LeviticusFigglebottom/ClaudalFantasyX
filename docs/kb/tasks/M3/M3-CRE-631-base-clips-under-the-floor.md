---
id: M3-CRE-631
title: "Shipped base clips that dip under the floor, and the reef crab's faint weak point and budget"
role: character
status: todo
owner_session: ""
reviewer: art
depends_on: []
milestone: M3
request-from: creatures
---
## Goal
Measured from the GLBs by the Act II variant build (M3-CRE-628), in shipped Act I creatures, so their variants
inherit them:
- **reef crab** (and wallcrab, wreck crab, root crab): legs and claws go under y 0 in the KO, down to −0.28 m at the
  root crab's KO end. The weak-point crack's emission mask peaks at only 0.16, so it barely glows. The build is
  8,648 triangles against its sheet's 8k.
- **tide crawler** (and rim crawler): legs under y 0 in the KO, down to −0.32 m.
- **slag tortoise** (and scree crawler): the claws sit 4.5 cm under the floor at rest.

## Acceptance criteria
- [ ] The KO end poses keep every vertex at or above y 0 (fold the legs under the body), and the slag tortoise's
      rest claws on the floor
- [ ] The reef crab's weak point reads (mask about 0.6–1.0 on the crack, small and closed per ADR 0151); its
      triangles within 8k, or the sheet's budget amended with a reason
- [ ] Ride the M3-CRE-630 batch rebuild (one kit pass, every job verified); PC render of the affected creature and
      battle_choreo shots, viewed and re-approved

## Notes
- A test like tools/tests' grounded-KO check could cover every vertex rather than the root bone.

---
id: M3-CRE-632
title: "Ground every remaining creature's clips (the rest of the M3-CRE-631 sweep) and extend GroundedClipsTest to all"
role: character
status: todo
owner_session: ""
reviewer: art
depends_on: [M3-CRE-631]
milestone: M3
request-from: creatures
---
## Goal
M3-CRE-631 grounded the reef crab, tide crawler and slag tortoise families with `common/grounding.py` and added
`GroundedClipsTest` (every frame's lowest skinned vertex at or above −0.005 m). Its sweep measured the other shipped
creatures that still go under the floor (depths and the full list are in the M3-CRE-631 task file):
- **Grounded creatures:** scuttler −0.37, Cinder Matron −0.35, shoal skipper −0.32, raid hound −0.22, Drownbell −0.22.
- **Fliers, even with their hover:** ashwing −0.63, gull harrier and stormgull −0.28.
- **Possibly by design (check against their sheets first):** the Mangrove Drowner (roots in water), the Undertow's
  Reach (rises from the water), the spar-wraith, the flue moth.

## Acceptance criteria
- [ ] Each grounded creature passes GroundedClipsTest (grounding.py where a planted foot is the fix; re-key where a
      clip's body motion is)
- [ ] The fliers' clips stay above the floor with their `stand_in.hover` applied; extend the test to add the hover
- [ ] The by-design ones get an explicit, commented allow-list entry citing their sheet, or are fixed
- [ ] GroundedClipsTest covers every creature (less the allow-list)
- [ ] Blender verify identical; one PC render of the affected creature and battle shots, viewed and re-approved

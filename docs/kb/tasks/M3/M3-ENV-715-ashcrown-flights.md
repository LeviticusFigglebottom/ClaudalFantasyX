---
id: M3-ENV-715
title: "Ashcrown's steep flights as traversal paths (for M3-ARC-1216 and act1-chapters' Ch5 swap)"
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-09]
milestone: M3
reviewer: architect
---
## Goal
act1-chapters' Ch5 Ashcrown swap is blocked: the kit's flying stair is 48° and its vein stairs 60°, past the field
controller's 45° (M3-ARC-1216, three options). Env-art's position and its part:
- **Env-art recommends option 1, a traversal interact.** Option 2 means re-cutting the flights under 40°. That
  changes the temple's massing and its far silhouette from Pemakar, which is the chapter's image of the climb
  (ashcrown.md §0.1). The steepness is the design.
- For the traversal, the kit now exports every steep flight's line from the same numbers that build it.

## Acceptance criteria
- [x] `assets/environments/kits/ashcrown/ashcrown_flights.json` (`ac_flights.py`), in the kit frame. 13 flights:
      the flying stair (forecourt → tier 6, 48°, 172 risers, 5.1 m clear) and the vein stairs east and west for
      tiers 1–6 (60°, 20 risers, 0.9 m). Each has its foot, head, a landing 1 m past each end, and the floors it
      joins.
- [x] `test_ashcrown_kit.FlightTests`: committed, matching the kit, every flight steeper than 45°.
- [ ] The traversal itself (M3-ARC-1216, architect).

## Review log

---
id: M3-ARC-1216
title: A steep-stair traversal for the field (Ashcrown's 48° flying stair and 60° vein stairs)
role: architect
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: cinematics
---
## Goal
env-art's Ashcrown kit (ashcrown.md §0.1, §2.1) climbs the temple by a 48° flying stair and descends the trial by
60° vein stairs. The field controller has no step-up and walks floors up to 45°, so Act I's kit zones turn stairs
into ramps (ADR 0200), which can't stand in for these flights. Ch5's Ashcrown swap (M3-C05-1215) is blocked on a way
across them. Options (act1-chapters' preference first):
1. **A traversal interact**: a trigger at a flight's foot and head ("Climb" / "Descend") that plays a short climb
   (HeroMotion along the flight's line, camera on a rail) and places the party at the other end; the flight itself
   keeps a box collider so nobody walks it. Data: `traversals: [{id, from, to, path: [points], prompt_key}]` in the
   zone layout.
2. env-art re-cuts the flights under 40° (changes the temple's massing and its far silhouette from Pemakar).
3. A per-zone floor angle override for the controller (a 48° walk reads wrong at field speed; 60° doesn't work).

## Acceptance criteria
- [ ] A decision (ADR) and, for option 1, the traversal in the field with a test.

## Review log

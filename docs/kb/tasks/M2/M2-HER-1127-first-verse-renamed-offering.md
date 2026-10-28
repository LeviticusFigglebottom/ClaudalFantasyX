---
id: M2-HER-1127
title: "Request (slice-polish): the First Verse's shrine offerings point at a prop env-art renamed (shrine_offering -> wayside_offering)"
role: environment
status: todo
owner_session: ""
reviewer: qa
depends_on: []
milestone: M2
request-from: qa
---
## Goal
The integration-qa thread guard (tests/integration/test_qa_threads.gd, M3-HER-1121) fails the first-playable thread on
the integration branch (e930595c) plus `claude/m2-slice` @ 2103aeca:
```
Resource file not found: res://assets/environments/kits/haluna/shrine_offering.glb
first_verse.tscn:259 / :262 - [ext_resource] referenced non-existent resource
Node 'SetDressing/OfferingN' / 'SetDressing/OfferingS' was modified from inside an instance, but it has vanished.
```
- m2-slice's M2-FP-116 (9ba01356, the First Verse in the real Shell Shrine) instances `kits/haluna/shrine_offering.glb`
  as SetDressing/OfferingN and OfferingS.
- env-art's 39f66d4c (M3-ENV-701 fix, on the integration branch since big12) renamed that prop to
  **`wayside_offering.glb`** (same geometry and seed), so the `shrine_` prefix again means the Shell Shrine pieces only
  (the GI bake's input glob).
- Each branch passes alone. Merged, the offerings vanish from the First Verse and the thread logs two load errors.

## Acceptance criteria
- [ ] When m2-slice merges the integration branch, first_verse.tscn points OfferingN/OfferingS at
      `res://assets/environments/kits/haluna/wayside_offering.glb`, and m2-slice's copy of `shrine_offering.glb` is gone
      (keep the name out of `shrine_*`, or the shrine GI guard hashes it again).
- [ ] `--filter=qa_threads` is clean on the merged tree.

## Notes
The same trial merge also conflicts in assets/levels/ch03/shell_shrine/shrine_gi_inputs.json, game/data/audio/music.json,
game/data/loc/strings.csv and tests/integration/test_causeway_route.gd. Those are the ordinary merge with the integration
branch, listed here so they aren't a surprise.

## Review log

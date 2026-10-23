---
id: M1-ARC-05
title: Camera director cutscene control and debug overlay input fixes (review-sweep-A)
role: architect
status: doing
owner_session: architect-stream-5
depends_on: [M1-ARC-01, M1-ARC-02]
milestone: M1
request-from: "cinematics"
---
## Goal
Review-sweep-A findings on ARC-01/02.

## Acceptance criteria
- [ ] FieldCameraDirector.play_shot(shot, blend)/release() that suspend volume selection until released
- [ ] CameraShot.aim_node (aim at an actor/mark, not only the player)
- [ ] snap() mid-blend into the active shot ends the blend; snap re-latches input to the visible camera
- [ ] Debug overlay only consumes list keys on list pages (flags, teleport, Lattice); never swallows Enter/Space/Up/Down elsewhere
- [ ] F6 Lattice cheat respects Facet stack caps

## Notes
-

## Review log

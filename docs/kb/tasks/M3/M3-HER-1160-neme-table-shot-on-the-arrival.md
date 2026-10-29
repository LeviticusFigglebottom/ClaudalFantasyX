---
id: M3-HER-1160
title: "Haluna's NemeTable volume (shot B02) covers the Village spawn: the party walking in from the beach loses Asha and Toma off the frame"
role: cinematics
status: todo
owner_session: ""
reviewer: qa
depends_on: []
milestone: M3
request-from: qa
---
## Goal
The human's party-start fast-track is fixed: the beach and lane use FOLLOW shots (ADR 0194), and all three
heroes stay in frame. Self-rendered at the opening, the gap in the wall and the lane turn.

The walk guard (`test_qa_field_camera::test_the_walk_from_the_beach_to_the_village_keeps_the_party_in_view`) still
fails at its last steps, (-50, -2) → the Village spawn (-52, -2.6). That's inside the **NemeTable** volume (centre
(-52.5, 3, -2.2)), whose shot **B02** (M2-FP-109, the close shot at Neme's table) stands at (-47.8, 3.4, -1.6)
looking west. The party comes in from the east, so the followers trailing behind Rhen are behind or beside that
camera, and Asha and Toma leave the frame.

Either shrink NemeTable to the table itself, so the Village spawn and the lane's end fall in H09 (FOLLOW), or move
B02 to the table's west side so the camera faces the party as it arrives.

## Acceptance criteria
- [ ] The walk guard passes with its `B02` KNOWN shot removed.

## Review log

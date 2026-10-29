---
id: M3-HER-1159
title: "Four Act I spawns land in a field camera volume whose shot faces away from them (Brightwater DerelictDeck and Stern, Coilspire Encounter, Corrow Bastion)"
role: cinematics
status: todo
owner_session: ""
reviewer: qa
depends_on: []
milestone: M3
request-from: qa
---
## Goal
integration-qa's guard `tests/integration/test_qa_field_camera.gd` checks every Act I spawn (the party laid out, the
camera settled on the spawn's shot) for Rhen in frame, not walled off and not covered. On big16 (ff82858c), four
spawns fail because of their zone's camera volumes and shots:

| Zone | Spawn | Shot | What the camera does |
|---|---|---|---|
| ch04 brightwater_ferry | DerelictDeck (-7.8, 0.9, 18.3) | FerryWaist | Rhen is off the left edge (x -177 of 1920) |
| ch04 brightwater_ferry | Stern (-9.24, 0.9, 19.1, 180°) | FerryWaist | off the left edge (x -277) |
| ch08 coilspire | Encounter | GallerySouth | far off frame (x 22228): the shot looks away from the spawn |
| ch08 corrow | Bastion (-66.2, 12.0, -0.6) | WallGate | Rhen is behind the camera |

The camera volumes come from the playthrough passes (M3-C04-1226, M3-CIN-1220); the Brightwater layout merged
act1-chapters and env-art in big16. For each one, either shrink the volume so the spawn falls in a shot that faces
it, give the spawn its own volume, or make the shot a FOLLOW shot (ADR 0194: rides behind the leader along the
shot's heading).

## Acceptance criteria
- [ ] test_qa_field_camera passes with this task's KNOWN rows removed (`brightwater_ferry.tscn:DerelictDeck`,
      `:Stern`, `coilspire.tscn:Encounter`, `corrow.tscn:Bastion`).

## Review log

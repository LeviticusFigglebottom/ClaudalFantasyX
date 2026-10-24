---
id: M3-CRE-04
title: "Ch5 creature models: ashwing, slag tortoise, the Cinder Matron (vein sparker optional)"
role: character
status: doing
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: art
depends_on: [M3-CRE-01]
milestone: M3
request-from: lead
---
## Goal
The Ch5 creatures from docs/kb/art/creatures/act1/ through the pipeline; `model` on m2-slice's enemy rows (M3-C05-02) when they land. Foes on screen: Ashcrown stair 2–3, the Matron alone.

## Acceptance criteria
- [x] ashwing (first pass: 4.2k triangles; origin is its hover point; ember eye-spots per act1_ch05 §9)
- [x] slag_tortoise (first pass: 4.6k triangles)
- [x] cinder_matron (first pass: 21k triangles, phase `crust_breaks` hides the `Crust` mesh; CreatureActor phases gained `show`/`hide`)
- [x] vein_sparker (optional, m2-slice act1_ch05 §9: copper-green, the coiled charged tail, starlight charge; 3.9k triangles)
- [ ] A dedicated art pass on the Cinder Matron (see Notes)

## Notes
- 2026-10-24: the Matron reads as a stone guardian in phase 2 and as slag-crusted in phase 1, but she is still a stack of rounded blocks: a dedicated pass should carve the figure (a robe line, hands with fingers, a real Watcher face). Her phase id `crust_breaks` is a placeholder until m2-slice names the phase in enemies.json; the validator skips the phase-name check until an enemy uses the model.

## Review log

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
- [x] ashwing (first pass: 4.2k triangles; origin is its hover point)
- [x] slag_tortoise (first pass: 4.6k triangles)
- [x] cinder_matron (first pass: 21k triangles, phase `crust_breaks` hides the `Crust` mesh; CreatureActor phases gained `show`/`hide`)
- [ ] vein_sparker (optional, m2-slice act1_ch05 §9; not started)
- [x] A dedicated art pass on the Cinder Matron (see Notes): rebuilt as m2-slice act1_ch05 §9's forge-construct, 23.9k triangles

## Notes
- 2026-10-24: the Matron reads as a stone guardian in phase 2 and as slag-crusted in phase 1, but she is still a stack of rounded blocks: a dedicated pass should carve the figure (a robe line, hands with fingers, a real Watcher face). Her phase id `crust_breaks` is a placeholder until m2-slice names the phase in enemies.json; the validator skips the phase-name check until an enemy uses the model.
- 2026-10-24 (art pass): the encounter owners' beat sheet (m2-slice act1_ch05 §9 item 14) superseded the seated laterite Watcher, so the Matron is now a standing forge-construct: a bottle-kiln of riveted brass and copper plates with broad hips, a firebox belly, iron hoops, a yoke with pauldrons, a bell chimney-hood with a brass Watcher mask (closed eyes, open mouth grille), a ladle in her right hand, tongs in her left, a patina smith's apron, and a `glimmer_bound` heart behind a grated chest port (new `heart` material slot; `stone` became `metal`). The `Crust` mesh is pillowed slag cells over a molten underlayer (crisp ember cracks) and leaves a slit over the heart; in phase `crust_breaks` the plates under it run red-hot. Bone names, clips and the creatures.json phase are unchanged; `attack` is now a ladle pour-swing (contact still 0.85) and `cast` raises the tongs. 3.6 m tall, 23,866 triangles (18,620 body, 5,246 crust). The sheet (act1/cinder_matron.md) is rewritten; creatures README rule 3 names Lit Age constructs as the one `glimmer_bound` exception. Open for m2-slice: the re-crust telegraph (a phase `show: ["Crust"]`) and the quench reaction are VFX/presentation work.

## Review log

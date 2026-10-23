---
id: M1-CHR-07
title: Asha face round 3: smile driver, lip shape, hairline, brows, hair colour
role: character
status: todo
owner_session: ""
depends_on: [M1-CHR-04]
milestone: M1
request-from: "lead"
---
## Goal
From the review-sweep-J entries (file:line references there).

## Acceptance criteria
- [ ] Smile reads: the cheek raise 0.45 and lid squint 0.25 of asha.md:158 visibly drive in asha_face_smile (find the data or driver gap: shape-key names, the emotion mapping, or the weights); same audit for grief and every emotion tag
- [ ] Lips: a defined cupid's bow and vermilion border; no dark slit in the smile
- [ ] Hairline: no helmet edge; no stray flat cards at the temples; hair reads black per asha.md:121 (check albedo and shader tint with Rendering)
- [ ] Brows: hair strokes, not solid bars
- [ ] Blender rebuild gate byte-identical; GLB under 5 MB; §14 dialogue-range review re-run honestly, side by side with CHR-04; baselines re-approved with reasons

## Review log

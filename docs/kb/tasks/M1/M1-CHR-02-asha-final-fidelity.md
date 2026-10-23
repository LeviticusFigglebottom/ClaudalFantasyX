---
id: M1-CHR-02
title: Asha at final fidelity: modeled, rigged, shaded
role: character
status: review
owner_session: character-stream-3
reviewer: rendering
depends_on: [M1-CHR-01, M1-RND-04]
milestone: M1
request-from: ""
---
## Goal
SPEC §10.2 M1 exit criterion: one hero at final fidelity.

## Acceptance criteria
- [ ] 40–70k triangles with LODs; 2–4K face textures; hair cards
- [ ] Rigify body rig plus face blendshapes (visemes, brows, lids, ~30 expressions)
- [ ] Godot turntable scene plus 5 portrait shots for review
- [ ] Honest assessment against the §14 uncanny risk

## Notes
From review-sweep-B on M1-CHR-01 (do these FIRST, before blendshapes): rebuild the head with ring loops around the eyes and mouth and a nasolabial loop; fix split normals at UV seams (neck, shoulder yoke); soften the jaw-underside shelf; reshape the heavy variant; add extreme-pose baselines as a weight regression gate.
Blocked by Git LFS for 4K textures (ADR 0005).

## Review log

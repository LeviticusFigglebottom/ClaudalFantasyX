---
id: M5-A3P-1855
title: "The Undertow-heart (Ch21, Sefir's phase 2): the heart's battle body round his figure"
role: character
status: review
owner_session: "creatures-b (claude/creatures-b)"
reviewer: combat
depends_on: [M3-ENV-728]
milestone: M5
---
## Goal
The finale's Undertow heart (the Lead, 2026-10-31; act3_ending.md H05–H08): the held light Sefir draws into
himself, as the battle body of his phase 2, with his figure (the characters track's) at its centre. Env-art's heart
arena (column, floor, eyewall) stays theirs.

## Acceptance criteria
- [x] A design sheet: docs/kb/art/creatures/act3/undertow_heart.md.
- [x] Built, rigged and clipped, reproducible, with PROVENANCE rows, a portrait and a test; viewed.
- [ ] Combat: Sefir's phase-2 row (this body as his phase-2 model) and its skills. Characters: his figure at `Sefir`.

## Progress
- 2026-10-31: built. assets_src/creatures/sefir_heart/build_sefir_heart.py writes the GLB: 3.2k triangles, 17 bones.
  - The body: three helical bands of held light, three orbiting salt-glass shards, two tendrils and a foot ring.
  - Clips: idle and ready turn the bands exactly one band's spacing, keyed every frame, so the stripes sink in a
    seamless loop. Also attack (the draw, 0.9 s), cast (the tightening, 1.4 s), hit, phase_change (into the Letting)
    and `let_go` as the KO: the bands sink and tilt out under the KO fade, because held light never rises.
  - Also built: the creatures row `sefir_heart`, the battle scene with a `Sefir` node for his figure, the Blender
    job `creature_sefir_heart`, a portrait, PROVENANCE rows and tools/tests/test_sefir_heart.py.
  - Viewed: the portrait and a scratch render of `cast`.
  - Open questions are in the sheet: a model swap or a second row, his figure's clips, and the body in phase 3.

## Review log

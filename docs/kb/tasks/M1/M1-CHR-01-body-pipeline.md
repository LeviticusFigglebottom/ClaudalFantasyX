---
id: M1-CHR-01
title: Parametric body pipeline (Blender headless)
role: character
status: review
owner_session: character-stream-1
reviewer: rendering
depends_on: [M1-ART-01]
milestone: M1
request-from: ""
---
## Goal
SPEC §7.3 pipeline up to the sculpt-ready mesh.

## Acceptance criteria
- [x] ADR on MPFB use (SPEC §16 Q2 default: allowed as a tool, heavily modified). See ADR 0010: MPFB is unreachable here (no Ubuntu package, GitHub blocked, the PyPI "makehuman" wheel has no verifiable provenance), so the body is built from scratch procedurally.
- [x] build.py produces a 7–7.5-heads-tall base with clean topology for Rigify: 7.34 / 7.47 / 7.50 heads, all-quad, manifold, 21,120 tris, Rigify rig plus 75-bone `DEF-*` skeleton.
- [x] Deterministic and parameterized: byte-identical rebuilds, `variants/*.json` plus `--set`.

## Notes
- Source: `assets_src/characters/base_body/` (build.py, bb_params, bb_anatomy, bb_cage, bb_rig, preview.py, build_all.sh).
- Output: `assets/characters/base_body/base_body_{slender,athletic,heavy}.glb` (about 0.98 MB each, PLACEHOLDER tagged).
- Review: `game/levels/_tests/characters/base_body_test.tscn` and 11 `base_body_*` shots with baselines.
- Docs: `docs/kb/art/characters/pipeline.md` (parameters, topology, rig, weaknesses, the §14 assessment, and what M1-CHR-02 needs next).
- Tests: `tools/tests/test_base_body.py` (the Blender build test skips without Blender, about 15 s with it).
- Honest status: bodies read as believable adults at gameplay distance. The face is uncanny at close range and is M1-CHR-02's main job.

## Review log

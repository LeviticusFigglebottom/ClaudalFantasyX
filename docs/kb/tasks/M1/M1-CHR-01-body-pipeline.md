---
id: M1-CHR-01
title: Parametric body pipeline (Blender headless)
role: character
status: done
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
- 2026-10-23 rendering (review-sweep-B): **approve with fixes**, as a PLACEHOLDER-tagged pipeline foundation, not as art. The pipeline is the right shape: deterministic, parameterized, all-quad and manifold, Rigify plus a `DEF-*` skeleton, a believable 7.3–7.5-head stature, and three builds that are distinct in silhouette. The posed shot deforms cleanly at the hip and knee. The honest §14 assessment is accurate and, if anything, a little generous: at 5–15 m these read as mannequins rather than people (slender and athletic are hard to tell apart, with little muscle definition). At the Face shot it is firmly uncanny: a muzzle-forward mid-face, a slit mouth, small staring eyes, no nostrils, and lumps for ears. The fixes below are the ones that will cost more if they wait for M1-CHR-02.
  - **should-fix (topology for faces):** the head is a 12×12 box lattice ray-cast from the head centre, with 3×2 and 4×2 cell blocks turned into eye and mouth loops. That gives an eye rim of 20 verts and a lip line of 24 after subdivision, with no radial orbicularis loops (oculi and oris), no nasolabial loop, and poles at the block corners right where brows and cheeks deform. The 32 shapes and 10 visemes of the shared face API will pinch along the lattice grid, and pre-integrated SSS (SPEC §8.2.4) shows exactly that kind of curvature noise. Replace the head cage with a procedural loop-flow template (3–4 concentric rings around each eye and the mouth, a nasolabial loop, a jaw line) before M1-CHR-02 builds blendshapes on it. Topology changes invalidate shapes; parameter changes don't.
  - **should-fix (shading seams):** the Face shot shows a thin dark line at the neck/trapezius junction, and the heavy front shows a bright specular ridge along the shoulder yoke. Both look like normal splits at UV seams (the neck junction seam is listed) or at the yoke/armhole poles. Check that normals are computed before the seam split and survive glTF export (or export custom split normals), and add a curvature-bake preview to the review shots so seams are caught automatically.
  - **should-fix (jaw/neck blend):** the underside of the jaw is a hard shelf that casts a sharp shadow line onto the neck, because the smooth-union radius is too small there. Raise `k_join` locally at the jaw/neck (or add an SCM-to-mandible blend term). Otherwise every 3/4 close-up under a high key will show it.
  - **should-fix (heavy proportions, Toma's base):** the heavy torso reads as one ellipsoid "breastplate" from sternum to navel, with the head small against it and the shoulders sloping. Toma is a tank, not soft-bodied. Lower the belly fat pad, separate the pec and abdomen masses, widen the bideltoid and trapezius, and check `head_width_ratio` on that variant.
  - **should-fix (deformation coverage):** the only posed baseline is a mid knee raise. Battle sets (cast, attack ×3, victory) will hit an overhead arm, deep shoulder protraction, a spine twist and a 120°+ knee, which is where automatic bone heat usually collapses the armpit and knee. Add 2–3 extreme-pose baselines now, so weight fixes have a regression gate.
  - **nit:** the Face shot shows no visible effect of the SPEC §7.3 ×1.10 eye scale, because the lid aperture is narrow and there are no lid-thickness or white-of-eye cues. Recheck it after the lid pass.
  - **nit:** hands are tubes and feet are mittens (documented). Asha's sandals need separate toes before her costume pass.
- 2026-10-23 lead: closing as a pipeline foundation (PLACEHOLDER), on review-sweep-B; topology and shading fixes are folded into M1-CHR-02's acceptance criteria.

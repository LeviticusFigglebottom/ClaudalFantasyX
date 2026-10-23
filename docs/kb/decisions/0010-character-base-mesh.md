# 0010 — Character base mesh: built from scratch procedurally (no MPFB/MakeHuman)

- **Status:** accepted
- **Date:** 2026-10-22
- **Roles affected:** Character, Rendering, Cinematics, Animation, QA
- **Author role:** Character Artist (M1-CHR-01)

## Context
SPEC §7.3 needs a parametric human base body that becomes the sculpt-ready mesh for every hero (Asha first, M1-CHR-02). SPEC §16 Q2 asks whether MPFB/MakeHuman (CC0 meshes and targets) may be used. The default answer is "allowed as a *tool*, with heavy modification, logged in an ADR". Two other rules constrain this. SPEC §2 treats CC0 meshes as off-limits by default, and any exception "must be logged as a decision and flagged to the human". ADR 0005 requires every asset to be reproducible from the repo with Blender headless.

What we found in this sandbox on 2026-10-22:
- **Ubuntu archive** (the only package source we can reach, via `tools/dev/fetch_godot.py`'s index for the stonking, resolute, tenacious and devel dists): there is no `makehuman`, `mpfb` or MakeHuman-asset package.
- **GitHub** (MPFB2's home) and **download.tuxfamily.org** (the MakeHuman asset downloads) are refused by the egress proxy.
- **PyPI** has a project named `makehuman` (1.3.2, a 30 MB wheel). Its metadata lists no author, homepage or license. We could not confirm it is the MakeHuman project's own release, so its provenance is unverifiable. We did not download it.
- Blender 5.0.1 (the pinned Debian build) ships **Rigify** and the glTF exporter, and `numpy` works inside it. EEVEE cannot render headless here (no libEGL), so review renders come from Godot (ADR 0009).

## Options
1. **MPFB2 inside Blender, heavily modified.** This is the spec default. The add-on and its CC0 base mesh are unreachable from here, so a human would have to vendor them in, and the meshes would then be a CC0-asset exception that needs an ADR and a human flag (SPEC §2).
2. **The unverified PyPI `makehuman` wheel** as a topology donor. Unknown provenance, so it fails the spirit of §2 and we would be unable to state its licence in PROVENANCE.md.
3. **From scratch, procedural.** A parametric quad cage plus an anatomical signed-distance field, Catmull-Clark subdivision and surface projection, all in Blender Python and numpy. Every vertex comes from code in `assets_src/`.

## Decision
**Option 3.** The base body is generated entirely from scratch by `assets_src/characters/base_body/build.py`. No downloaded meshes, scans, targets, packs or CC0 assets are used. Q2 stays answered by its default ("MPFB allowed as a tool"), but **we do not exercise it**, because it is unreachable here and would add a §2 exception. If the human later wants MPFB, a new ADR supersedes this one. The body generator's interfaces (parameters JSON, landmarks, `DEF-*` skeleton, the asha.md §6.2 blendshape names) are designed so that a donor topology could be swapped in behind them.

How it works (details in `docs/kb/art/characters/pipeline.md`):
- **Parameters** (`variants/*.json`): height, heads tall, widths in head units, limb ratios, and the femininity, muscle and mass sliders. These become **landmarks** (`bb_params.py`).
- **Anatomy field** (`bb_anatomy.py`): ellipsoids, round cones and round boxes as muscle bellies, fat pads and bony landmarks, grouped by region. The face is a smooth head "egg" plus Gaussian sculpt displacement in face space.
- **Cage** (`bb_cage.py`): explicit quad topology. A torso tube carries armholes and a crotch split. Arm, leg, hand (4-sided fingers plus thumb) and foot tubes, and a box-lattice head with concentric eye and mouth loops. Each ring is ray-cast onto its own region's field.
- **One Catmull-Clark level**, then projection onto the joined field with tangential relaxation. Lid margins, the lip line and the mouth bag are pinned.
- **Rig**: Rigify's human metarig (face bones removed, `eye.L/R` added) is fitted to the landmarks and generated. A deform-only skeleton built from the `DEF-*` bones is exported, with Blender bone-heat weights.

## Consequences
- **Easier:** full provenance (`license: original`), byte-identical rebuilds (verified), and one parameter file per character that re-flows mesh and rig together. No human action is needed for M1.
- **Harder:** we own every anatomical detail. MakeHuman's decade of tuned targets would have given a better face and better hands sooner. Facial realism is the slowest part: today the face reads as a mannequin.
- **Uncanny-character risk (SPEC §14):** building from scratch *raises* the risk for faces and hands in the short term. The mitigations are:
  1. A face that is all named, data-driven displacement terms, so it can be tuned (and later driven by asha.md §6.2 shape keys) without re-modelling.
  2. M1-CHR-02 proves one hero at final quality before scaling, as §14 requires.
  3. If photoreal fails, lean on the §14 fallback, a painterly skin shader (M1-RND-04) and stronger stylisation (a slightly simplified face plane, crisp hair cards). The base pipeline supports this by construction.
  4. If the M1-CHR-02 face review fails twice, escalate Q2 to the human with the option of vendoring MPFB as a topology donor.
- **Watch:** bone-heat weights are automatic and unreviewed at the fingers and the crotch. The posed screenshot `base_body_slender_posed` is the regression check.

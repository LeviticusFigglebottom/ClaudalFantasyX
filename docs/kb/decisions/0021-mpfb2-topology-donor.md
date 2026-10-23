# 0021 — MPFB2 / MakeHuman CC0 data as the character topology donor (SPEC §16 Q2 = yes)

- **Status:** accepted
- **Date:** 2026-10-23
- **Roles affected:** Character, Rendering, Animation, Cinematics, Art, QA, Lead
- **Author role:** Character Artist (M1-CHR-03)
- **Supersedes:** [ADR 0010](0010-character-base-mesh.md) for the base mesh's topology, face and skin weights. The anatomy field, rig, costume, hair and parameter pipeline from 0010 stay.

## Context
ADR 0010 built the base body from scratch and named a trigger: if the M1-CHR-02 face review failed twice, SPEC §16 Q2 goes to the human. It failed twice (the M1-CHR-01 base face, then the CHR-02 hero face; [ADR 0019](0019-character-stylization.md), [`asha_review.md`](../art/characters/asha_review.md)). On 2026-10-23 the human answered Q2: **"yes, as a tool, with heavy modification, logged in an ADR"**.

SPEC §2 treats CC0 meshes as off-limits unless an exception is logged and flagged to the human, which the human has now answered. CLAUDE.md §2 also allows only *permissively licensed* code addons. MPFB2 ships two things under two licences (its `LICENSE.md`):

- **Program code** (every `.py`, shell script and configuration file): **GPLv3**.
- **Assets** (section C: "the base mesh and proxies, targets and modifiers, textures, ... rigs, poses and expressions, JSON data with mesh information"): **CC0 1.0** (`LICENSE.ASSETS.md`). The base mesh (`3dobjs/base.obj`) also carries its own CC0 header; the Rigify weights file has `"license": "CC0"`.

GitHub is reachable from the sandbox now (`git ls-remote https://github.com/makehumancommunity/mpfb2` works), so ADR 0010's "unreachable" reason no longer holds.

## Options
1. **Install MPFB2 in Blender and drive it.** Fastest, but the build would import GPL code. Rejected (CLAUDE.md §2).
2. **Vendor only the CC0 data and read it with our own code** (recommended). Our readers parse the plain-text formats (OBJ, `.target` lines, weights JSON, uv-layer face sets); nothing from MPFB2's code is copied, translated or imported.
3. **Keep the from-scratch face and stylise harder** (ADR 0019 option 3). Needs a SPEC §7.3 change. Not needed if option 2 works.

## Decision
**Option 2.**

**What is vendored** (`assets_src/third_party/mpfb2/`, 4.4 MB, every file under 5 MB):
- `LICENSE.md` and `LICENSE.ASSETS.md`, verbatim, which state the code/asset split.
- `data/3dobjs/base.obj`: the hm08 base mesh (13,380 skin vertices, 13,378 quads, closed and manifold, all quads).
- `data/rigs/rigify/weights.human_toes.json.gz`: the hand-made Rigify skin weights. The upstream file is 5.97 MB, so it is stored gzip-compressed, deterministically.
- `data/uv_layers/{lips,face,scalp}_solid.json.gz`: face sets (which quads are the lips, the face mask, the scalp).
- `data/targets/macrodetails/`: the young `{african,asian,caucasian}-{female,male}` and `universal-{female,male}-young-*muscle-*weight` targets (the macro mix).
- `data/targets/expression/units/{african,asian,caucasian}/`: 15 FACS-like expression units (brows, nose, mouth).

`tools/fetch_mpfb2.py` pins commit `b1a2dc98776da9d1eea751b159d42cf61778fe2e` of `https://github.com/makehumancommunity/mpfb2` and the exact data paths, clones to a temporary directory outside the repo, copies only that list, and writes `MANIFEST.json` (sha256 of each upstream file and stored file). `--check` verifies the vendored set offline. The check also fails if any `.py` or `.sh` file appears under the vendored folder.

**What is ours** (the heavy modification, `assets_src/characters/base_body/bb_donor.py`, behind the existing interfaces):
1. A **macro mix** of the donor's own targets, driven by our sliders (`femininity`, `muscle`, `mass`, plus the new `donor_mix_*` ethnic blend).
2. A **proportion warp** that carries the donor's joints onto `bb_params.Landmarks` (the SPEC §7.3 head canon in the variant or hero file). It is a polyharmonic radial-basis warp, and the head, hands and feet are carried by exact similarity transforms.
3. A **girth fit**: the torso, arm and leg cross-sections are scaled at low frequency to our anatomy field's (the width, depth, muscle and mass sliders), with the donor's surface detail on top.
4. **Eyes**: each lid margin is re-shaped onto our `EyeFrame` almond (SPEC §7.3 eyes ×1.10, Asha's 4° tilt and canthus), the lids are conformed to our globe, and the socket is tucked behind it. **Mouth**: the donor's resting lip parting is partly closed.
5. **Our face sculpt**: the bb_params face sliders (jaw, chin, cheekbones, nose bridge and tip, lips, corner lift, brow ridge) as face-space deformations. For the hero there is also one Catmull-Clark level on the face mask and lips, and a procedural detail pass in the normal map (lid creases, lower-lid line, lip lines).
6. The anatomy field is **re-seated on the donor skin** (a per-region offset grid), so costume panels, hair cards and sandals still ray-cast onto skin.
7. Behind the `Landmarks` interface, the face, finger and foot points are taken from the placed donor, so the Rigify rig (`DEF-*`, unchanged), the eyes and the teeth agree with the mesh.
8. The donor's **skin weights** are mapped onto our 75 `DEF-*` bones (helpers split onto their neighbours, face groups onto the head) instead of bone heat.
9. **Face shapes**: the asha.md §6.2 names are unchanged. Brows, nose sneer and the mouth shapes are the donor's expression units, re-targeted through steps 1–5. Lids, cheek raise, dimple, press and jaw stay procedural (the lids must slide on our globe).

**Licence bookkeeping:** `assets/PROVENANCE.md` lists the vendored files (license `CC0 1.0`) and marks every derived asset (the three base bodies and Asha's meshes and skin textures) `CC0 1.0 (MPFB2 data, ADR 0021) + original`.

## Consequences
- **Easier:** decades of tuned anatomy for free: lids, nose, lips, ears, hands, feet and loop flow, plus hand-made weights at the fingers and crotch. The face reads as a person (see asha_review.md §6 for the verdict). Base bodies are now 26,756 triangles (the donor's density) and still fully parametric.
- **Harder:** a third-party data dependency (pinned, reproducible, CC0). Two topologies existed in history, so anything keyed to the old cage's vertex order (none was committed) would break. The donor's hands and feet are dense, so the hero decimates them for LOD0. Morph-target normals are no longer exported: the GLB budget (ADR 0005, no LFS) cannot hold them on the denser head, so blended shapes shade with the rest normals.
- **Watch:**
  1. Never add MPFB2 code. Run `python3 tools/fetch_mpfb2.py --check` when the vendored folder changes.
  2. Rhen and Toma use the same path; their faces need their own `donor_mix_*` and face sliders.
  3. The donor's ears keep the native density (budget). A GPU review should check them at dialogue range.
  4. The macro mix includes ethnic blends. Choose them for each character with Art and Narrative, from the sheet, and never as a stereotype.

## Note, 2026-10-23 (M1-CHR-07, append-only)
"Morph-target normals are no longer exported" is partly reversed. Without them the cheek raise and lid squint shaded as at rest and did not read (the review-sweep-J smile gap). `assets_src/characters/asha/asha_glb.py` now adds sparse NORMAL deltas after the export, for the 30 expression shapes only (+0.53 MB; `asha.glb` 4.56 MB). The 10 visemes still have none, for the 5 MB cap. The pass is deterministic and covered by the asha rebuild gate, and `tools/tests/test_asha_face_drive.py` asserts it. Rhen and Toma get the same pass when they are built.

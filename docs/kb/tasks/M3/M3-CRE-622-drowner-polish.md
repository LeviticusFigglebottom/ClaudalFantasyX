---
id: M3-CRE-622
title: "The Mangrove Drowner, polish: knuckled tapering prop-roots, a folded core, less spider in the risen stance"
role: character
status: review
owner_session: "worktree-agent-a2773b09b6372eb5f"
reviewer: art
depends_on: [M3-CRE-621]
milestone: M3
request-from: creatures
---
## Goal
The first build (M3-CRE-621) reads as the sheet says at battle distance, but viewed close: the roots are smooth,
even tubes radiating from the top like legs (a real mangrove's prop-roots are knuckled, taper toward the mud and
arch down from the trunk), so the risen stance reads spidery (README rule 1 risk); and the core is a glossy,
featureless sphere.

## Acceptance criteria
- [x] Roots: knuckles every 0.4–0.7 m, taper, bark segments, lean outward from a visible trunk base
- [x] Core: folds and blisters, the wounds in the folds
- [x] Risen: four to six roots plant, the rest hang and trail (no even spider ring)
- [ ] Blender verify identical (done: 3 identical); PC render of creature_mangrove_drowner and _risen, viewed and
      approved (pending)

## Notes (worktree agent, 2026-10-27)
- **Roots** (`root_specs`, `root_rings`, `roots`): authored azimuths with gaps of 17-39 degrees (`ROOTS`), each root
  with its own departure height (2.05-2.7 m), foot radius (2.1-2.95 m), rise, lean and girth. A root is a Bezier
  arch (out and up off the base, a rounded shoulder, a lower limb leaning out to the mud), cut into a polyline at
  knuckles every 0.4-0.7 m, each knuckle kinked a few cm in and across the plane and only lightly rounded. Four
  rings per bark segment: the knuckle (+24% radius, dark crease in the cavity channel), its crease, the middle and
  the shoulder. Each segment has its own tint and furrow turn. The taper runs from 0.27 m to 0.1 m. The bones end at
  the knuckles nearest 0.3 and 0.58 of the length, so a root bends at a knuckle.
- **Trunk base** (`collar`, new, in the body on bone `root`): a buttressed bark collar from inside the core up to a
  torn top at about 2.8-2.95 m, with a flare under each root. The `Stump` now stands on it from 2.58 m up. Once the
  stump is hidden, the base's torn heartwood is the top of the risen silhouette.
- **Rootlets** (new): three frayed fine roots at the tip of each of the seven non-leg roots. They are under the water
  while it is rooted and dangle once it has risen. A torn root frays; a leg would taper to a point.
- **Core**: narrower (widest 1.22 m, was 1.66 m), so the water shows between it and the roots. It has eight deep
  folds hanging down it (one per wide gap between roots, with rolled lips), seven broad boils and 22 small blister
  domes crowding the folds' lips. The seams follow the folds' bottoms, 4 cm proud of the faceted crease.
- **Risen**: `LEGS` = 1, 3, 6, 8, 10 (five, unevenly spaced), each planted at the straightest fit within 0.35 m of its
  `RISEN` radius. `TRAIL` = 4, 5, 7 drag out behind, their tips just off the water. 0, 2, 9 and 11 (the drag's FRONT
  pair among them) curl in under the core. Every root's first bone droops 28-63 degrees, so no arch stands above
  the core like a knee. The body lifts 0.65 m (top about 3.6 m) and leans by `RISEN_TILT` (-6, 0, 4): reared back
  and canted. `solve_bend` gains `tilt`, `a_range` and `r_free`.
- **Kept**: bone names (48 bones), all clips, the contacts, the hit (peak 0.1 s), the KO sinking 0.45 m (each root
  now splays 0.6 m past its own foot), creatures.json, the GroundedClipsTest allow-list entry, and the palette
  (no green).
- **Triangles**: 16,370 -> 17,012 (body 16,234, stump 778).
- **Flat sketches** (scratch, not committed): side, front and top silhouettes of the rooted and risen poses, before
  and after. Rooted now reads as a cage of knuckled, arched roots of uneven length and spacing; the top view is
  ragged, not a sunburst. Risen lost the even ring of twelve and the high knees: from the side it is a hunched dome
  with a flat torn top, uneven stilts and roots dragging behind. **Residual risk:** straight from the front it is
  still a dark dome on splayed roots, which at a glance can read as a crouching arachnid (a tick more than a
  spider). The PC render has to decide.
- Sheet updated: five legs (was six), and model notes.

## Review log

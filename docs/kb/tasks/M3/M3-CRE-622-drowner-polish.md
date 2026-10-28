---
id: M3-CRE-622
title: "The Mangrove Drowner, polish: knuckled tapering prop-roots, a folded core, less spider in the risen stance"
role: character
status: done
owner_session: "creatures (worktree agent, redesign pass)"
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

## Notes (worktree agent, redesign pass, 2026-10-27)
Built to the amended sheet's silhouette rules (5eb244f8); the WIP (cc81201a) had the trunk, aerial roots and leaning
stance; this pass finished the plan, the clusters and the grounding.
- **Four bundles, not rays** (`CLUSTERS`, `ROOTS`, `CONVERGE`): front-right 58 deg, back 176, bank 263, front-left
  328 (the widest gap in front, where the core shows). Each root leaves the trunk up to 16 deg round from its bundle's
  heading, at its tier (1.08-2.3 m) and skewed off its own heading, then swings onto the heading late (power 1.6),
  feet staggered 1.8-3.85 m along it and +-0.4 m across, so a bundle's roots braid. The bank bundle reaches 2.7-3.85 m,
  the others 1.8-2.75 m. Limb stubs moved into the gaps (118, 222, 298 deg; one used to drop its aerial root through
  the core).
- **Risen in three clusters** (`RISEN_ROLL`, `RISEN_LEG_SPAN`): each leg's plane is turned about its heading to steer
  its foot: front-right 1 and 3 (az 68-93), front-left 5 and 6 (az 352-18, under the drag's 0 and 11 and the hanging
  4), the bank 7 and 9 (az 277) with the trails 8 and 10 rolled in alongside (az 269-271). `LEGS` is 1, 3, 5, 6, 7, 9
  (2 now curls in; 3 plants, as it comes down straight). Leg bends are capped at 55 deg (no hooked claws). The
  48-degree lean, lift and torn-up trunk are kept as reviewed.
- **On the water, every frame** (`grounded_clips`, uses `common/grounding.py`'s Poser): roots end 5 cm over y 0 and
  everything is flattened onto the water at rest (`on_water`); the core's underside rests on it. Each exported clip
  (with hit_b and idle_b) is re-keyed per frame: the mass lifts the least it takes, each root curls up (foot, middle,
  then first bone, about its own plane's tangent after its authored bend), each aerial root lifts. The KO no longer
  sinks: the roots let go and slide out along their bundles, the trunk keels back 15 deg pivoting on its foot's edge
  (`trunk_keel_lift`) and the mass slumps out onto the water (the water VFX takes the sinking). Aerial roots hang to
  0.14 m. **The GroundedClipsTest allow-list entry is removed.**
- **Measured** (numpy from the build, and the test from the GLB): triangles **14,700** (body 13,881, stump 819), 53
  bones, budget 18k. Lowest vertex per clip: idle +0.002, attack +0.002, cast +0.003, hit +0.002, ko +0.002,
  phase_change +0.002, idle_risen +0.002, attack_risen +0.002, cast_risen +0.002, hit_risen +0.002, hit_b +0.002,
  idle_b +0.003 (m). Kept: bone names, every clip, contacts, the spawn_wound seams (ADR 0151), creatures.json.
- **Flat silhouettes** (scratch, not committed: final_sheet.png, before = the first pass vs after; rooted, KO end,
  phase_change 1.2 s, risen): every top view is now lopsided bundles, never a sunburst; rooted reads as a tree over a
  root tangle. **Residual risk:** the risen front view is still a dark dome on roots splayed both ways (a crab/tick
  more than a spider), and the rooted top view keeps a few short pale spokes at the centre (limb stubs and the high
  roots' bleached shoulders). The PC render decides.
- Blender verify: 3 identical.

## Review log
- 2026-10-27, creatures (review of the first pass's silhouettes, side/front/top, rooted and risen): **still reads as a
  spider (a tarantula)** in every view, the top view most of all (a sunburst). The detail is better (knuckles, taper,
  folds), but the knuckled roots now read as segmented legs. The cause is topology, not detail: a central bulb with
  radial roots *is* a spider. Merged as a step; reopened for a **silhouette redesign**:
  - make it **vertical**: a tall, thick trunk (to about 3.5 m, cut by the canopy) standing *above* the cage, with the
    spawn core wedged **low inside** the roots, not a ball on legs;
  - put the prop-roots in **tiers** at different heights from the trunk, overlapping in depth: a tangle, not a ring;
    roots on one side longer (the bank side), so the plan view is lopsided, never radial;
  - hang thin, straight **aerial roots** from the trunk to the water: vertical lines that no spider has;
  - risen: it tears the trunk up with it and **leans**, walking on three or four root-clusters, the trunk tipping
    forward like a felled tree that walks; no even leg ring;
  - amend the sheet (docs/kb/art/creatures/act2/mangrove_drowner.md) first, then build; PC render to judge.
- 2026-10-27, creatures (review of the redesign's silhouette sheet): **no longer a spider.** Rooted reads as a tall
  stump over a tangle; every top view is lopsided bundles, not a sunburst. The risen front view (a dark dome on splayed
  roots) is the one remaining risk: the PC render judges it. Grounded in every clip with no allow-list (+0.002 m).
  14,700 triangles. Stays in review until the render is approved; then amend the sheet's lean (it says ~30°, the
  build leans 48°) to whatever the render keeps.
- 2026-10-28, art (creatures): **approved on the cloud render** (lead/gate-render-creatures-3b0e44b; baselines dc524c0c, portrait 41493382). Rooted, it reads as a tall bleached stump over a tangle of roots with the dark core wedged low. Risen, it is a tilted trunk on three root clusters. Neither reads as a spider. The sheet's "about 30°" lean stays at the built 48°; the sheet is amended to match.

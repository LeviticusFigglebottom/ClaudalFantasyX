---
id: M3-CRE-631
title: "Shipped base clips that dip under the floor, and the reef crab's faint weak point and budget"
role: character
status: review
owner_session: "worktree-agent-ab04148130b2b3dd6"
reviewer: art
depends_on: []
milestone: M3
request-from: creatures
---
## Goal
Measured from the GLBs by the Act II variant build (M3-CRE-628), in shipped Act I creatures, so their variants
inherit them:
- **reef crab** (and wallcrab, wreck crab, root crab): legs and claws go under y 0 in the KO, down to −0.28 m at the
  root crab's KO end. The weak-point crack's emission mask peaks at only 0.16, so it barely glows. The build is
  8,648 triangles against its sheet's 8k.
- **tide crawler** (and rim crawler): legs under y 0 in the KO, down to −0.32 m.
- **slag tortoise** (and scree crawler): the claws sit 4.5 cm under the floor at rest.

## Acceptance criteria
- [x] The KO end poses keep every vertex at or above y 0 (fold the legs under the body), and the slag tortoise's
      rest claws on the floor
- [x] The reef crab's weak point reads (mask about 0.6–1.0 on the crack, small and closed per ADR 0151); its
      triangles within 8k, or the sheet's budget amended with a reason
- [ ] Ride the M3-CRE-630 batch rebuild (one kit pass, every job verified); PC render of the affected creature and
      battle_choreo shots, viewed and re-approved. **Verify done, the render is pending (PC).**

## Notes
- A test like tools/tests' grounded-KO check could cover every vertex rather than the root bone.

## What was done (worktree agent, 2026-10-27)
Measured by skinning every baked frame of every clip from the GLB (no render). The floor problem was wider than the
KO: every clip of the crabs and the tide crawler, and every clip of the slag tortoise, put leg vertices under the
floor (the body bobs or leans while the feet are planted at y 0).

- **`assets_src/creatures/common/grounding.py` (new; creature_kit.py untouched).** `grounded(rig, mesh, clips,
  limbs)` poses the mesh at every frame exactly as the export does (checked: it reproduces the GLB numbers to 0.1 mm)
  and turns, or lifts, each listed limb by the least amount that keeps its vertices on the floor. A planted foot
  then stays planted while the body moves over it. Frames where a limb is clear keep their authored pose. `hit_b`
  and `idle_b` are derived from the authored clips first, so no correction is mirrored or scaled. The search steps
  through a limb's range before bisecting, so a limb that can't reach is never flung to its limit.
- **Reef crab** (`export_clips(rig, mesh)`; the wallcrab, wreck crab and root crab use it):
  - each walking leg turns up about z at its hip, and each claw up about x at its shoulder;
  - a new KO: the crab settles 0.22 m onto its plastron (it dropped 0.26 m and rolled 8°, now 3°), knees up 45°,
    shins curled in 28°, tips on the floor beside the body (`KO_BODY`, `KO_LEG_A`, `KO_LEG_B`);
  - the idle's one-leg shuffle was keyed −14°, pressing that leg into the floor; it now lifts (+14°);
  - **the weak point:** the crack is centred on the back rim's band (unit z −0.92), so its mask peaks at 1.00 and
    reads 0.59–1.00 on the crack (mean 0.93, 27 vertices over about 17 × 5 cm). It is one small closed mark that
    stays clear of the rim (ADR 0151). Before, it was centred higher, where the rim term cut it to 0.16. The root
    crab's lichen still keeps off it;
  - **the budget:** the plastron underside's lathe is 6 × 36 (was 8 × 72), since only its edge is ever seen. That
    takes the crab from 8,648 to 7,928 triangles. The dome, legs and claws (the silhouette) are untouched, so the
    sheet's 8k budget stands. The root crab is 8,888, the base plus its 960 root triangles.
- **Tide crawler** (`build_mesh`, `export_clips`; the rim crawler uses them): each leg turns up about z at its hip,
  each striking leg up about x. A new KO: it collapses 0.22 m (was 0.3 m, which also put its belly under) with a 4°
  roll, the knees sinking 10° and the shins splaying out 30° (`KO_DROP`, `KO_ROLL`, `KO_LEG`).
- **Slag tortoise** (`export_clips`; the scree crawler uses it):
  - the 4.5 cm was the stubby leg tube's rounded foot end, not the claws: each leg now has a flat sole at y 0;
  - each leg lifts into the shell (up to 0.2 m; at most 7.8 cm, in `hit_b`) wherever the shell's bob, pitch or roll
    would press it through the floor;
  - the KO roll now draws the legs in 40° as it tips and rises 4 cm by the end (`KO_TUCK`, `KO_RISE`), because the
    crust overhangs the roll's pivot. It ends lying on its side, 1.1 cm clear (the scree crawler 0.3 cm).
- **Test:** tools/tests/test_creatures.py `GroundedClipsTest` skins every frame of every clip of each listed GLB and
  requires the lowest vertex ≥ −0.005 m. It runs in about 3 s. It lists the 8 fixed here, plus 5 already clean
  (avalanche ram, ridge lynx, glass skate, conduit crawler, rime urchin). A hovering creature is refused, and the
  Wakefin is excluded by design, as the docstring says. Run on the old GLBs, it reports the old numbers.
- docs/kb/art/creatures/pipeline.md: an "On the floor" bullet. PROVENANCE: the 8 GLB rows list `common/grounding.py`.

### Before / after (metres, the lowest vertex over all frames of each clip; KO end = its last frame)
| Creature | idle | attack | cast | hit | ko | hit_b | idle_b | KO end |
|---|---|---|---|---|---|---|---|---|
| reef crab, wallcrab, wreck crab (before) | −0.086 | −0.137 | −0.080 | −0.097 | −0.325 | −0.129 | −0.036 | −0.276 |
| root crab (before) | −0.116 | −0.175 | −0.098 | −0.101 | −0.358 | −0.134 | −0.041 | −0.276 |
| tide crawler, rim crawler (before) | −0.086 | −0.098 | −0.012 | −0.116 | −0.317 | −0.152 | −0.005 | −0.316 |
| slag tortoise (before; rest −0.045) | −0.055 | −0.054 | −0.045 | −0.089 | −0.085 | −0.106 | −0.045 | −0.050 |
| scree crawler (before; rest −0.045) | −0.055 | −0.062 | −0.045 | −0.097 | −0.093 | −0.115 | −0.045 | −0.058 |
| **every one of the 8 (after)** | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 (tortoise +0.011, scree +0.003) |

The crabs' unposed bind pose is still −0.003 (a leg tip's cap, within the tolerance). The actor always plays a clip,
so it is never shown.

| Reef crab | Before | After |
|---|---|---|
| Triangles | 8,648 | 7,928 (budget 8k) |
| Weak-point mask peak | 0.156 (0 vertices over 0.5) | 1.000 (13 over 0.5; 0.59–1.00 on the crack) |

### Verify
`verify_blender_builds.py` prints identical for every touched job: creature_reef_crab 4, creature_wallcrab 4,
creature_wreck_crab 8, creature_root_crab 4, creature_tide_crawler 2, creature_rim_crawler 2,
creature_slag_tortoise 4 and creature_scree_crawler 4. `common/grounding.py` is under every creature job's
`common/**`, so the other 34 creature jobs were verified too: all identical, since none imports it.

### Checks
- `godot --headless --import`;
- Godot `--filter=creature` (37 run, 0 failed) and `--filter=battle` (687 run, 0 failed);
- `python3 -m unittest tools.tests.test_creatures` (11 OK) and `tools.tests.test_blender_builds` (28 OK);
- `validate_data.py` (0 errors), `gdlint`, `gdformat --check` and `taskboard --check`.

No screenshot was rendered here (PC only).

### For the PC render (pending)
- **Shots:**
  - `creature_reef_crab`, `creature_reef_crab_attack`, `creature_wallcrab`, `creature_wreck_crab`, `creature_root_crab`;
  - `creature_tide_crawler`, `creature_rim_crawler`, `creature_slag_tortoise`, `creature_scree_crawler`;
  - the `battle_choreo_*` shots (the sandbox's crabs).
- **What to judge:**
  - the crack glows at the back of the crab's shell, small and closed;
  - the feet stay on the floor;
  - the crab's and the crawler's KO end reads as folded, not sprawled;
  - the tortoise's flat soles.
- The slag tortoise's sheet says "legs still" for its KO. The legs now draw in as it tips and then hold still, so
  confirm that reads right.

### Found, not fixed here (follow-up)
Other shipped creatures also go more than 5 mm under the floor, measured the same way. A flier's figure below is
after its `hover` is added back.
- **Grounded creatures, in the KO:**
  - scuttler −0.37;
  - Cinder Matron −0.35;
  - shoal skipper −0.32;
  - raid hound −0.22;
  - bottle hermit −0.19;
  - vein sparker −0.18;
  - spawn polyp −0.13;
  - tower limpet −0.11;
  - glassfry −0.08;
  - wall polyp −0.025;
  - lamp engine −0.0065.
- **Grounded creatures, in other clips:**
  - Drownbell (cast) −0.22;
  - oil slug (hit_b) −0.09;
  - tannin archer −0.08, already at rest.
- **Fliers, in the KO:**
  - ashwing −0.63;
  - gull harrier and stormgull −0.28;
  - squall wing −0.16.
- **Possibly by design (check the sheets):**
  - hullgnaw (sinks between the planks; already exempt in test_a_ko_ends_on_the_ground);
  - mangrove drowner −3.10 (phase_change);
  - Undertow's Reach −1.33 (attack);
  - spar wraith −0.91 (KO);
  - flue moth −0.62 (KO, no hover);
  - lantern eel −0.58 at rest;
  - Wakefin (swims).

Each fix is the same: `grounding.py` limbs plus a KO that lies on the floor, then add the creature to
`GroundedClipsTest.GROUNDED`.

## Review log

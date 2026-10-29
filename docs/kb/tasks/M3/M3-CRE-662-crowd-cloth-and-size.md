---
id: M3-CRE-662
title: "Crowd follow-up: cloth never near skin (a perceptual metric, no fallback), and a smaller crowd (shared clip libraries)"
role: character
status: review
owner_session: "creatures (worktree agent)"
reviewer: art
depends_on: [M3-CRE-659]
milestone: M3
request-from: creatures
---
## Goal
The coordinator's review of M3-CRE-659's renders and data (2026-10-28):
1. **Cloth near skin.** In crowd_lineup_a two pale peach tops read close to bare skin. The generator's
   `draw_cloth` measures plain sRGB distance, and when 12 draws all miss `skin_min_distance` it keeps the farthest
   anyway. 3 body defaults and about 10 people's tints fall below the floor (56/47 units on the Brine Shoals wrights,
   38 on an Oruvel diver's sash). Fix:
   - a perceptual metric (CIELAB ΔE, hue-aware), with a floor that grey-on-tan passes and peach-on-tan fails;
   - no silent fallback: widen the draw or pick another swatch set, and fail loudly if none clears;
   - apply it to the bodies' default `_tints` too;
   - the validator checks the same metric.
2. **Size.** assets/crowd is 43 MB, of which 12.2 MB is clip and material text. If every crowd body shares the
   villager skeleton, share one AnimationLibrary (or a few, by age band) instead of one copy per body, if the import
   and actor scenes allow it. Report the new size.

## Notes (creatures worktree agent, 2026-10-28)
**1. Cloth never near skin.**
- **Metric:** `skin_delta_e` in `tools/validate_npc.py` is the one function the generator imports and the
  validator calls. It is CIE76 on CIELAB (D65) split into lightness, chroma and hue: `sqrt((k_l dL)^2 + dC^2 +
  (k_h dH)^2)`, with k_l 0.3 and k_h 0.5, so the chroma step weighs most. Unit weights give plain CIE76, which the
  tests check.
- **Floor 18.5, calibrated** in `ranges.json` `skin_clearance.calibration` and re-measured by the `SkinClearance`
  tests on the palette and the crowd's skin range (every community's skin endpoints and their midpoints).
  - Lowest pass: order_marble on the lightest skin, 20.6. Greys are 25.4 or more and gauze_white 22.5.
  - Highest fail: 16.7.
  - The floor sits mid-band. A grid over k_l in [0.2, 1] and k_h in [0.25, 2.5] finds no wider band.
- **Calibrated on renders.** I rendered M3-CRE-659's crowd_lineup_a with the old roster to find the review's two
  pale tops:
  - man_heavy_b's open-front cream (#D1C0A1 on #AC7A5D) reads as one with the skin at the V;
  - girl_tall's sand top (#BFAA86 on #A5765A).
- **A first pass failed by eye.** At k 0.75 and floor 24, the regenerated man_heavy_b got a lighter cream
  (#D7C9AF, 25.2), and the new crowd_lineup_a showed it still reading as skin.
  - With that as a fail pair, no weights can also pass creams on darker skin. I had judged two of those as cloth;
    I dropped those pairs.
  - So now creams and beiges fail near any crowd skin and are drawn away to whites, greys and colours.
  - Plain CIE76 can't do this: it ranks that cream (31.3) above the greys (26).
- **No silent fallback.** `draw_cloth` widens in order:
  - 12 draws from the slot's own mixes;
  - the community's other sets;
  - each of the slot's swatches mixed toward lacquer_black or gauze_white (away from the skin's lightness first),
    in steps 0.15–0.6;
  - then an error (SystemExit) naming the person or body.

  In the committed roster, 234 draws came from their own set and 3 from another set. None needed a darker or
  lighter mix, and none errored.
- **Applied** to the bodies' default `_tints` and to every person's tints. The validator checks both.
- **Before** (M3-CRE-659's data, final metric): 12 body default cloth tints and 23 person cloth tints were under
  the floor.
- **After:** 0. The lowest person is 18.5.
- **Changed, against M3-CRE-659:**
  - Body default cloth tints: 35 of 66, so 35 cloth materials were rebuilt across 17 bodies.
  - Person cloth tints: 88 of 168, across 42 of 56 people.
  - Hair tints: 31, as a side effect. Hair is drawn after cloth on the same seeded stream and still moves along
    each body's own hair mix.
  - Bodies, assignment, work clips and everything else in the roster: unchanged.

**2. Size: shared clip libraries.**
- **Libraries:** four, one per group (`ranges.json` `clip_libraries`): adult (13 bodies), elder (4), child (3:
  boy_tall, girl_tall, girl_teen) and child_small (2). Each is built in its reference body's job, from the job's
  fresh GLB, with the group's mean persona and every member's work clips.
- **Track roots:** the tracks are rooted at `crowd_skeleton`.
- **Hips height:** each library records the reference's hips rest height. The crowd post-import
  (`CrowdClipLibrary`) renames every body's armature and sets `Skeleton3D.motion_scale` to hips rest over the
  reference's, so the absolute hips track fits each body.
- **Verified by sampling bone positions** (hands, feet, toes, knees, head over every clip): each member's own clips
  against the library played on it.
  - Within the groups: at most 1.0 cm, and 0.4 cm in foot height. A tools test (`SharedClips`) holds this at
    1.5 and 0.6 cm.
  - One library for all: 4.7 cm off and the elders' lean flattened.
  - Children as one group: the small pair is 4.6 cm off, hence child_small.
- **Godot test:** each body loads with its group's single library resource and the right `motion_scale`, and its
  toes stay on its own floor in idle and talk.
- **Trade-off:** a body's own persona (sway, lean, arms) now only feeds its group's mean. That is about 1 cm at the
  hands, and wearers stay out of step by idle phase.
- **Size:**

  | | Before | After |
  |---|---|---|
  | Clips | 12.00 MB (22 per-body libraries) | 2.84 MB (four libraries) |
  | assets/crowd (tracked files) | 42.85 MB | 33.69 MB |

  Material text was only 0.23 MB of the 12.2.

**3. Rebuild.** All 22 bodies were rebuilt for the clips, then the 11 whose tints moved again were rebuilt after
the recalibration. GLBs, maps and actor scenes came out byte-identical; only the cloth materials and the clips
changed. `verify_blender_builds` prints identical for every `crowd_*` job, and `gen_crowd.py --check` is clean.

**4. Renders** (viewed in the container; no baselines written). Shots: crowd_lineup_a/b/c, crowd_market,
crowd_work, crowd_mourners, crowd_zone_brine_shoals, crowd_zone_bell_galleries.
- **lineup_a:**
  - girl_tall's sand top is now grey.
  - man_heavy_b's top is now a pale vest (#DCD1BC, 19.4) that reads as cloth beside the skin, as the white open
    top does in lineup_b. What still shows skin there is the fisher kit's open front, which is the costume.
- **lineup_b/c:** no cloth reads as skin.
- **Clips, on every age band:**
  - kneel_mourn and mend: knees on the floor;
  - vigil: hands joined;
  - sweep, fold and carry: right;
  - idle and talk: feet planted;
  - children and elders at their own heights, with no floating or sinking.
- **Brine Shoals:** the six wrights kneel at the water.
- **Bell Galleries:** the divers and the tender stand on the platform.
- **Capture:** every shot was `ok`.

## Review log

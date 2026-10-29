---
id: M3-CRE-628
title: "Build three Act II regulars (ridge lynx, cord moth, glass skate) and four variants from their sheets"
role: character
status: blocked
blocked-by: ADR 0041
owner_session: "worktree-agent-aac484d16edeb5a00 (creatures, cloud session_01EbDaRQ5n7hpvwuRG6jEDQY)"
reviewer: art
depends_on: [M3-CRE-620]
milestone: M3
request-from: lead
---
## Goal
The Act II regular foes from M3-CRE-620's sheets (docs/kb/art/creatures/act2/), through the creature pipeline
(docs/kb/art/creatures/pipeline.md):
- the regulars: the ridge lynx (Ch12), the cord moth (Ch12) and the glass skate (Ch16);
- the variants from act2/variants.md: the root crab (reef crab), the fen leech (sail leech), the scree crawler
  (slag tortoise) and the rim crawler (tide crawler).

**PC render pending:** this environment may not render (human directive). Every model was checked numerically from
its GLB, and no review shot has a baseline yet.

## Acceptance criteria
- [x] **The ridge lynx** (`assets_src/creatures/ridge_lynx/`, 6,988 triangles, budget 8k, 27 bones):
      - **Shape.** A long-legged winter lynx, 1.45 m from the rump to the nose, 0.77 m at the withers over the
        forelegs (its coat included), with the head at 0.80 m and the black ear tufts to 1.06 m. It has big snowshoe
        pads (13.6 × 17.6 cm, four toes each, the soles flat at y 0), a short black-tipped tail, and a frosted ruff
        (a thin flared collar round the cheeks, with both faces on their own vertices).
      - **The rig.** The sheet's quadruped: root, a `body` carrier, `spine0`..`spine3`, `neck0`/`neck1`, `head`,
        `jaw`, four legs of 3 (`*_upper`, `*_lower`, `*_paw`) and `tail0`..`tail2`, plus `ear_l`/`ear_r` for the
        idle's turning ears. The legs hang from `body`, so the spine breathes without moving a paw. Each leg is posed
        by a planar two-bone solve that keeps a planted paw where it stands, level, while the body crouches, lands
        or limps.
      - **Colours.** The coat is `overcast_slate`, going to `cumulus_shadow` on the belly, with faint `lacquer_black`
        spots and facial streaks. The ear tufts, tail tip, nose and eye-lines are `lacquer_black`, the eyes
        `dusk_gold` (black pupils), and the ruff's points frosted `salt_glass` (× 0.95).
      - **The weak point.** The old sling wound on the camera-side flank (−x) is a small aslant slit with dark raised
        lips, glowing `spawn_wound` (15 emissive vertices). The sheet asks for it small.
- [x] **The cord moth** (`assets_src/creatures/cord_moth/`, 4,144 triangles, budget 5k, 12 bones):
      - **Shape.** A broad-winged moth 1.40 m across, hovering at chest height. Its origin is the hover point:
        creatures.json `stand_in.hover` 1.25 puts the body at 1.31 m. The wings are held flat and wide, with a slight
        dihedral. It has a furred slate thorax and banded abdomen, big black eyes, and feathered antennae (a flat
        comb either side of each shaft).
      - **The knot rows**, its one exaggeration: three cord rows across each forewing and two across each hindwing,
        laid along the span like stitched lines. Each row is a thin raised strip (its own `knot` slot) whose knots
        widen and stand proud of the cord. They come in counted groups (single knots, clusters of two to four, now and
        then a long knot), drawn from a seeded sequence, so the pattern is abstract and original and copies no real
        script. The rows alternate the cords' faded dyes: `lacquer_red` mixed 30% toward `sand_cloth`, and
        `sea_blue_cloth` mixed 25% toward it. The knots keep the full dye and the cord between them is 18% darker.
      - **The rig.** The sheet's: root, `body`, four wing bones a side (`fore_l0`/`fore_l1` and `hind_l0`/`hind_l1`,
        root and outer half of each wing) and the antennae.
      - **Colours.** The wings run from `sand_cloth` at the root to `cumulus_lit` × 0.9 (held under the albedo
        ceiling), with a dusky fringe. The body is `overcast_slate`, and the eyes `lacquer_black`. The weak point is a
        small `spawn_wound` crack across the top of the thorax (24 emissive vertices).
- [x] **The glass skate** (`assets_src/creatures/glass_skate/`, 2,624 triangles, budget 4k, 14 bones):
      - **Shape.** A broad rounded disc 1.40 m across and 1.22 m from the snout's point to the rear. Its underside lies
        flat at y 0, and the back rises to 0.12 m over the body (0.16 m at the eye turrets). It has a thick tail
        (0.9 m) with two small dorsal fins, and black eyes on raised turrets with spiracles behind them.
      - **The rig.** The sheet's disc chains of 3 a side (`disc_l0`..`disc_l2`, `disc_r0`..`disc_r2`, skinned like the
        sail leech's wings) and a tail of 4, plus root, `body` and `eye_l`/`eye_r` (the idle moves only the eyes and
        the breathing back).
      - **The exaggeration**, the nearly clear back: `foam_white` × 0.9 mixed with `cumulus_lit` × 0.88 (both held
        under the albedo ceiling). It goes glassy `salt_glass` × 0.92 toward the thin margins, with a faint ripple
        mottle like sand under water. The material is glossy and clear-coated with a strong rim sheen (`back`:
        roughness 0.08 wet, `wet_darken` 0.95, `rim_sheen` 0.55).
      - **Other colours.** The belly is `bone`, and the eyes `lacquer_black`. The weak point is a short split across
        the spine at the tail root, glowing `spawn_wound` with dark raised lips (21 emissive vertices).
- [x] **The variants** are each the base's rig and clips with a new materials.json and a creatures.json row. The base
      build module is imported, not copied, as the wallcrab, wreck crab and stormgull do, and each job lists the base
      folder as a source.
      - **`root_crab` on `reef_crab`.** Longer climbing legs come from two new base parameters, `LEG_KNEE` (0.62,
        0.47, 1.7 → 0.70, 0.62, 1.85) and `LEG_FOOT` (0.80, 2.3 → 0.96, 2.5). The span is 1.94 m (the reef crab's
        1.62), and the knee rises to 0.62 m.
        - Colours: bark plates of `timber_weathered` and `laterite`, dark bark fissures for the mortar seams (mixed
          from `tortoiseshell` and `lacquer_black`), grey `overcast_slate` lichen spots, and bark-brown legs.
        - A knot of four mangrove roots grips the back over the old tile plate. The roots twist round each other at
          the knot, trail off the rim as aerial roots, and keep clear of the crack and the eyes.
        - 9,608 triangles: the reef crab's 8,648 plus 960 for the roots.
      - **`fen_leech` on `sail_leech`.** It is ribbon-flat and longer through new base parameters: `THICK`, `DOME`,
        `FRILL`, `FRILL_WAVES`, `SLIT_Z`, `EYE`, `TAIL_Z0`/`TAIL_STEP`, `TAIL_PATH`, `TAIL_R` and `TAIL_CHAIN`, plus
        the existing `HALF_W`/`HALF_L`.
        - It is 0.88 m wide (the sail leech's 1.4), 2.36 m nose to rear (1.30) and 2.74 m with the tail, half as thick, and
          has no canvas frill.
        - Its back is wet `lacquer_black` (18% toward `tortoiseshell` in the noise), with faint annuli. The underside
          is a faint tannin-amber: `dusk_gold` × 0.42 mixed 25% toward `tortoiseshell`.
        - The four `spawn_wound` slits run down the longer back. 5,728 triangles.
      - **`scree_crawler` on `slag_tortoise`.** New base parameters: `SHELL_CELLS` (22 → 40), `SHELL_LUMP` (0.06 →
        0.08), `SHELL_FLAT` (faceted plates) and `SKIN_SHAG` (0 → 0.022 m of tufted skin).
        - The shell is frost-split slate scree (`overcast_slate`, `storm_slate`, each split face its own stone's
          tone), with `salt_glass` rime in the splits and on the crown.
        - The skin is a cold grey-brown (`timber_weathered` mixed with `overcast_slate`), and the eyes stay
          `lacquer_black`. The base's `spawn_wound` neck crack stays. 4,624 triangles.
      - **`rim_crawler` on `tide_crawler`.** A palette variant with no base change.
        - The carapace is chalky `mortar_white` × 0.94, dry: the vertex wetness drops to 0.2 on the chalk.
        - `lacquer_black` stays in the joints, still wet: each leg segment's ends, the tips dipped black, and the
          body's underside.
        - The wounds are dimmer: emission 1.0 (the base's 2.2), pulsing slower. 2,712 triangles.
- [x] **Base builds unchanged.** The base parameters default to the bases' own values, written so the arithmetic is
      the same, and each base build (sail leech, slag tortoise) gained a `build_mesh(rig, name)`. The numpy outputs
      (rig, mesh arrays, clip keys) of the old and new base modules compare equal. `verify_blender_builds.py` prints
      identical for every touched job: `creature_reef_crab` 4, `creature_wallcrab` 4, `creature_wreck_crab` 8,
      `creature_sail_leech` 2 and `creature_slag_tortoise` 4.
- [x] **Every new job is deterministic** (`--threads 4`): `creature_ridge_lynx` 3, `creature_cord_moth` 5,
      `creature_glass_skate` 4, `creature_root_crab` 4, `creature_fen_leech` 2, `creature_scree_crawler` 4 and
      `creature_rim_crawler` 2 identical.
- [x] **Clips.** Every hit peaks at 0.10 s (the fen leech's at 0.13 s, its base's).
      - **The ridge lynx:**
        - `idle` (3 s loop): a breath, the tail flicks, one ear turns, then the other.
        - `attack` (1.4 s): the crouch is the telegraph (the body down 0.15 m and back, the paws planted, ears flat).
          At 0.47 s it launches into the leap (the root up 0.64 m at 0.6 s, forelegs reaching, hind legs streaming).
          At 0.7 s, the contact, it comes down on the back row, forelegs raking and jaw open. It lands in a crouch at
          0.84 s and straightens. It plays in place, and the paws end where they stood.
        - `cast` (1.6 s): the yowl. It braces back with its paws planted, raises its head, opens the jaw 34° and lays
          its ears flat, the tail lashing.
        - `hit` (0.5 s): it twists aside. The body turns 16° about the vertical and slides off the line, the spine
          and head whip round, and the paws stay on the ground. `hit_b` is the kit's mirror.
        - `ko` (3 s): it limps two steps (the second dips onto the stiff fore, which barely lifts), sags, and lies
          down on its left side in the snow, the old wound toward us, legs loose and head laid on the ground.
      - **The cord moth:**
        - `idle` (2.4 s loop): a slow hover, three quick beats then a long glide, the antennae swaying.
        - `attack` (1.1 s): a dart and a wing-strike. The wings go up and back, it darts in and down 0.22 m, and at
          0.5 s, the contact, the wings slam down and forward.
        - `cast` (1.6 s): the unravel. It rises and tips 38° up toward the party, and opens its wings full (forewings
          forward, hindwings back), holding them 0.55–1.15 s so the knot rows face the camera.
        - `hit` (0.5 s): it tumbles, rolled 38° and pitched 22°, dropping 0.12 m.
        - `ko` (2.6 s): it drifts down like a dropped scarf, falling the 1.25 m hover in a decaying side-to-side swing
          and roll, the wings rippling and going slack, and lies flat on the floor with the wingtips drooped to it.
      - **The glass skate:**
        - `idle` (3.2 s loop): buried. Only the back breathes and the eyes turn on their turrets.
        - `attack` (1.2 s): it erupts. The disc presses, it heaves up 0.5 m nose-high with its edges curled (0.36 s),
          then slaps down on the target, edges whipping down (0.5 s, the contact), and settles.
        - `cast` (1.6 s): the hide. A ripple runs out along both edges twice, the body wriggles and the tail sweeps,
          and the eyes draw down. The sand cloud is VFX.
        - `hit` (0.5 s): it buckles, the edges folding up, the body kinking and rolling, the tail whipping. `hit_b` is
          authored, not the kit's mirror (which would curl the edges down into the sand): the roll and the tail go
          the other way, 1.35× heavier.
        - `ko` (1.6 s): a last shudder lifts its edges, they settle flat, the tail goes slack and the eyes sink.
      - **The variants** play their bases' clips unchanged.
- [x] **Materials.** Every materials.json is written by write_materials.py. The slots:
      - the lynx: `coat` (with the wound's emission) and `eye`;
      - the moth: `wing`, `knot`, `body` (with the crack's emission) and `eye`;
      - the skate: `back` (with the split's emission), `belly` and `eye`;
      - each variant: its base's slots, re-tuned (bark, a wetter leech, rough scree, chalk with dimmer wounds).
- [x] **PROVENANCE rows** for the 7 GLBs and 17 materials, in their own commit.
- [x] **Battle scenes and creatures.json rows.** No enemies.json rows and no phases.
      - `ridge_lynx`: contacts attack 0.7 and cast 0.75, `ko_fade_sec` 1.2, `stand_in.yaw_deg` 60 (three-quarter, like
        the ram), and portrait yaw 40, pitch 10. Its median albedo luminance is 0.214, so it keeps the default rim.
      - `cord_moth`: contacts attack 0.5 and cast 0.55, `ko_fade_sec` 1.0, `stand_in` yaw 60 and hover 1.25, and
        portrait yaw 60, pitch 30 (the wings' top). Median 0.287.
      - `glass_skate`: contacts attack 0.5 and cast 0.8, and portrait pitch 35 (a flat disc). Median 0.605.
      - `root_crab`: contacts attack 0.5 and cast 0.7 (its base's), and portrait rim 2.8 and kick 1.8 (median 0.117,
        dark).
      - `fen_leech`: hover 1.38 and contact attack 0.7 (its base's), and portrait rim 2.8 and kick 1.8 (median 0.047).
      - `scree_crawler`: contact attack 0.55, and portrait rim 2.8 and kick 1.8 (median 0.171).
      - `rim_crawler`: contact attack 0.55. Median 0.585, so it keeps the default rim (pale, unlike its base).
- [x] **Import.** The import rule lists the seven folders, and each `.glb.import` runs the creatures post-import
      script.
- [x] **Unit tests** in tests/unit/test_creature_actor.gd. They were checked to fail with a 0.7 m leap threshold and a
      5 cm flat band.
      - The lynx: the rig, the pounce's contact, the paws back at rest at the end of every clip, the crouch (the body
        down over planted paws), the leap's height, and the KO lying low above the ground.
      - The moth: the rig, the hover, the strike's contact, and the KO coming down by exactly the hover.
      - The skate: the rig, the eruption, and the KO lying flat.
      - The variants: each has its base's bones and clips (same lengths), the root crab's knee is higher, and the fen
        leech is longer.
- [x] **Shots** `creature_<id>` for all seven (three-quarter, idle) in tests/screenshots/shots.json, with their stage
      scenes. None is captured and none has a baseline.
- [ ] **PC render pending:** no captures in the cloud environment (human directive). The PC renders the seven shots,
      a reviewer views them, and only then do their baselines go in.
- [ ] **Encounters** (not this task): enemies.json rows with `model` when the Ch10, Ch12 and Ch16 encounters are
      designed.

## Numeric check (no render)
Measured from each exported GLB, every clip frame by frame: glTF node animation, joint matrices and linear blend
skinning. "Peak" is the frame of greatest mean displacement from the rest pose. Heights are over the ground (y 0).
The fliers' heights include their hover; their clips' own numbers are 1.25 m (moth) and 1.38 m (leech) lower.

**The ridge lynx.** In every frame of every clip it stays at or above the ground: the lowest is −0.003 m, in the
`idle_b` fidget, the kit's 0.3× echo of the yowl's leg solve. The paws are at y 0 in the rest pose and at the end of
every clip but the KO.

| Clip | Length | Peak | Lowest..highest y | End of clip |
|---|---|---|---|---|
| rest | — | — | 0.000..1.060 | — |
| idle | 3.0 s | (loop) | 0.000..1.066 | loops to its start |
| attack | 1.4 s | 0.60 s (the apex; contact 0.7) | 0.000..1.713 | rest |
| cast | 1.6 s | 0.90 s | 0.000..1.066 | rest |
| hit | 0.5 s | 0.10 s | 0.000..1.061 | rest |
| hit_b | 0.5 s | 0.10 s | 0.000..1.061 | rest |
| ko | 3.0 s | 3.00 s (the end) | 0.000..1.060 | 0.002..0.437, lying on its side, the head at 0.17 |
| idle_b | 1.13 s | 0.63 s | −0.003..1.066 | rest |

**The cord moth** (the body at 1.31 m when hovering):

| Clip | Length | Peak | Lowest..highest y | End of clip |
|---|---|---|---|---|
| rest | — | — | 1.256..1.412 | — |
| idle | 2.4 s | (loop) | 1.225..1.773 | loops to its start |
| attack | 1.1 s | 0.50 s (contact 0.5) | 0.766..1.908 | the idle's first pose (wings 8° up) |
| cast | 1.6 s | 0.30 s (the tip-up; wings open 0.55–1.15) | 1.184..1.728 | the idle's first pose |
| hit | 0.5 s | 0.10 s | 0.537..1.798 | rest |
| hit_b | 0.5 s | 0.10 s | 0.461..1.817 | rest |
| ko | 2.6 s | 2.60 s (the end) | 0.006..1.758 | 0.006..0.112, on the floor |
| idle_b | 1.13 s | 0.40 s | 1.256..1.517 | 1.256..1.430 |

**The glass skate.** Nothing goes below y 0 in any frame; the lowest is −0.0002, the underside resting on the sand.

| Clip | Length | Peak | Lowest..highest y | End of clip |
|---|---|---|---|---|
| rest | — | — | 0.000..0.163 | — |
| idle | 3.2 s | (loop) | 0.000..0.173 | loops to its start |
| attack | 1.2 s | 0.37 s (the heave; contact 0.5) | 0.000..0.984 | rest |
| cast | 1.6 s | 1.10 s | 0.000..0.199 | rest |
| hit | 0.5 s | 0.10 s | 0.000..0.396 | rest |
| hit_b | 0.5 s | 0.10 s | 0.000..0.520 | rest |
| ko | 1.6 s | 0.20 s (the shudder) | 0.000..0.200 | 0.000..0.130, flat |
| idle_b | 1.13 s | 0.77 s | 0.000..0.163 | rest |

**The variants** (lowest..highest y over each clip; hits peak where their bases' do):

| Variant | Triangles | Rest | idle | attack | cast | hit (peak) | ko, over the clip and at its end |
|---|---|---|---|---|---|---|---|
| root_crab | 9,608 | −0.003..0.722 | −0.116..0.740 | −0.175..1.274 | −0.098..1.291 | −0.101..0.722 (0.10 s) | −0.358..0.722; ends −0.276..0.499 |
| fen_leech | 5,728 | 1.498..1.645 | 1.448..1.695 | 0.705..1.797 | 1.498..1.667 | 1.283..1.703 (0.13 s) | 0.045..1.645; ends 0.045..0.387 |
| scree_crawler | 4,624 | −0.045..0.818 | −0.055..0.828 | −0.062..0.837 | −0.045..0.818 | −0.097..0.818 (0.10 s) | −0.093..1.239; ends −0.058..1.216 |
| rim_crawler | 2,712 | −0.001..0.746 | −0.085..0.770 | −0.098..1.002 | −0.012..0.746 | −0.116..0.746 (0.10 s) | −0.317..0.746; ends −0.316..0.465 |

- **Inherited from the bases (unchanged clips, the same as the base GLBs measure):**
  - the reef crab's and tide crawler's clips dip their leg tips and claws under the floor, most in the KO (the reef
    crab's crusher hand at −0.28 at the KO's end, the tide crawler's legs at −0.32);
  - the slag tortoise's claws sit 4.5 cm under the floor at rest, and its KO rolls it onto its side;
  - the reef crab's weak-point crack has an emission mask of at most 0.16, so it glows faintly, and the root crab
    inherits that;
  - the roots (the root crab's own geometry) never go under the floor.

  Each root bone's KO stays grounded (tools/tests' check), and the fen leech's KO comes down by its hover (1.38).
- **Colours against palette.json.** Every swatch used is in palette.json. A swatch above the albedo ceiling
  (`cumulus_lit`, `foam_white`) is darkened under it, as the notes above say.
  - The linear vertex luminance stays between the floor (0.0101) and the ceiling (0.8014) on every model:
    - the ridge lynx 0.0101..0.6508;
    - the cord moth 0.0101..0.7042 (the wing 0.2995..0.7042, the knot rows 0.1085..0.2237);
    - the glass skate 0.0101..0.7114;
    - the root crab 0.0101..0.1750;
    - the fen leech 0.0101..0.5854 (0.5854 is the glowing eyes and slits, `spawn_wound`);
    - the scree crawler 0.0101..0.5464;
    - the rim crawler 0.0101..0.6569.
  - The emissive vertices (mask > 0.5) are the weak points: 15 (the lynx), 24 (the moth), 21 (the skate), 152 (the
    fen leech: slits and eyes), 12 (the scree crawler), 190 (the rim crawler: wounds and eyes), and 0 for the root
    crab (its base's faint crack).

## Notes
- **Proportions.** They were judged on flat numpy/PIL sketches in the scratchpad: orthographic, painter's algorithm,
  vertex colour times a Lambert term. These are not engine renders and are not committed.
- **For the first PC render:**
  - **The lynx:** the coat's tufts at battle distance, the ruff's frost against the slate, and the crouch reading as
    the telegraph from the party's side.
  - **The moth:** whether the knot rows read as knotted cord at battle distance in the idle (wings flat, seen from the
    camera's height), and in the cast, when it tips up to show them. The portrait's pitch of 30.
  - **The skate:** whether the glossy pale back reads as nearly clear against the Pale Rim's white sand. The creature
    shader is opaque, so the read relies on the gloss, rim sheen and margins. Also the margin's thin edge on a light
    floor.
  - **The variants:** the root crab's root knot reading as roots, not a net; the scree's faceted stones; the rim
    crawler's black joints.
- **The battle height.** The glass skate is 0.16 m tall. Its battle spec's `height` (damage numbers, VFX anchors)
  needs setting low when its encounter row is written.
- **Not modelled, by the sheets (VFX):**
  - the lynx's steaming breath and the snow its yowl shakes off the rocks;
  - the skate's sand cloud (the hide) and the water;
  - the `glimmer_held` motes from the wounds.
- **The moth's unravel** (removing a buff) is the cast clip only. The ability is battle design's.

## Review log
- 2026-10-28, creatures: **paused by ADR 0041** (Act I at final quality first; the human's directive). The work done so far is merged on claude/creatures as is; nothing reverted. Resume when a new ADR lifts the pause.

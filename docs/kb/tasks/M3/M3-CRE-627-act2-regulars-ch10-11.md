---
id: M3-CRE-627
title: "Build four Act II regulars (Ch10-11): tannin archer, gallery ray, rime urchin, conduit crawler"
role: character
status: blocked
blocked-by: ADR 0041
owner_session: "worktree-agent-a754445358ec40463 (creatures, cloud session_01EbDaRQ5n7hpvwuRG6jEDQY)"
reviewer: art
depends_on: [M3-CRE-620]
milestone: M3
request-from: lead
---
## Goal
Four Act II regular foes from M3-CRE-620's sheets, through the creature pipeline (docs/kb/art/creatures/pipeline.md):
- the tannin archer (`tannin_archer`, act2/tannin_archer.md, Ch10);
- the gallery ray (`gallery_ray`, act2/gallery_ray.md, Ch11);
- the rime urchin (`rime_urchin`, act2/rime_urchin.md, Ch11);
- the conduit crawler (`conduit_crawler`, act2/conduit_crawler.md, Ch11: a Lit Age construct, so its bound light is
  `glimmer_bound`, creatures README rule 3).

**Their first PC render is pending.** This environment may not render (human directive), so every model was checked
numerically from its GLB, and the four review shots have no baseline.

## Acceptance criteria
- [x] **The tannin archer** (`assets_src/creatures/tannin_archer/build_tannin_archer.py`):
      - **Shape.** An archerfish 1.1 m long (the snout at z +0.55, the caudal fin's edge at −0.55), deep-bodied (0.39 m
        at its deepest) and flat-sided (0.16 m across). It lies nose-up 11° along a mangrove root, half out of the
        water. The mouth is upturned (a jutting lower jaw), the eyes large and set forward, and the dorsal and anal
        fins set far back. The root rises out of the water behind it, arches under its belly (crown at y 0.18) and dips
        back in ahead, with a knee beside the tail.
      - **The exaggeration.** Its size, and the force of the jet (the jet is VFX).
      - **Colours.** The back is `deep_teal_shadow` going `abyss_navy` (lifted onto the albedo floor). The flanks are
        `sand_cloth` crossed by six `lacquer_black` bars, the first through the eye. The belly is `bone`, the eye a
        `dusk_gold` iris round a `lacquer_black` pupil. The gill slit is the weak point: a thin `spawn_wound` line on
        the body slot's emission mask. The root is `timber_weathered` going `tortoiseshell` where the water stains it.
      - **Budget and rig.** 4,464 triangles (budget 6k), 10 bones: root (the root prop; it never moves), `spine_0`
        (the head, pivoting at the body's centre), `spine_1`..`spine_4`, `tail`, `jaw`, `pec_l`/`pec_r`.
      - **Clips.** `idle` (2.4 s loop: the pectorals scull, the head tracks a target, the tail holds it). `attack`
        (1.2 s: it rises off the root, sights along its mouth, spits; contact 0.55 s). `cast` (1.8 s: the long aimed
        jet at the back row, nose up 20°, held; contact 0.9 s). `hit` (0.5 s: it flinches and rolls, the tail slaps;
        peak 0.1 s). `ko` (1.8 s: it jerks, rolls off the root onto its side and settles at the water).
- [x] **The gallery ray** (`gallery_ray/build_gallery_ray.py`):
      - **Shape.** A broad diamond 1.6 m across and 1.0 m from snout to rear, thin at the wings with a raised body
        down the middle (0.15 m deep at most). Its wingtips sweep up a little. A whip tail runs 1.1 m behind, with
        pelvic lobes at its root.
      - **The exaggeration.** It glides through the air between pools (the hover).
      - **A flier.** The origin is its hover point. creatures.json's `stand_in.hover` is 1.4 m (head height, the
        sheet's), and the KO drops the root by exactly that.
      - **Colours.** The back is `salt_glass` mottled toward `cumulus_shadow`, darker down the ridge, and the belly
        `bone`. The eyes on top are `lacquer_black`. The wing margin is the outer 16% of the disc, in its own `margin`
        slot: the same pale skin with a faint `sea_glow` emission (the ray's own light, not glimmer). The two
        spiracles behind the eyes are the weak points: small `spawn_wound` slots on the body slot's emission.
      - **Budget and rig.** 4,104 triangles (budget 5k), 12 bones: root, `body`, `wing_l0`..`wing_l2` and
        `wing_r0`..`wing_r2` (out from the body, each hinging along the ray's length), `tail_0`..`tail_3`.
      - **Clips.** `idle` (3.0 s loop: a slow undulating glide in place, the wings' stroke running out to the tips, the
        body bobbing against it, the tail swaying). `attack` (1.2 s: it banks up on its right, then sweeps its left wing
        down across the target; contact 0.6 s). `cast` (1.6 s: it settles 1.35 m down into the pool, the floor, and
        rises again; contact 0.9 s). `hit` (0.5 s: it flips half over and rights itself; peak 0.1 s). `ko` (2.0 s: it
        falters and slides down to lie flat on the floor).
- [x] **The rime urchin** (`rime_urchin/build_rime_urchin.py`):
      - **Shape.** A test 0.9 m across (0.72 m tall), on a lumpy ice plinth 1.3 m across and 0.15 m high. It carries
        184 spines, from 0.2 m underneath to 0.9 m (twice its radius) on top, each bowed a little upward. A rime crust
        thickens the outer half of the upper spines. Bone tube feet reach down to the ice, and the mouth (five teeth in
        a ring) is underneath. The top spine stands at 1.79 m, and the spines' reach is 2.1 m across.
      - **The exaggeration.** The rime.
      - **Colours.** The test is `abyss_navy` lifted with `deep_teal_shadow`, its ten ambulacral bands a shade
        lighter. The spines are `deep_teal_shadow` at the root, going `salt_glass` and, where the rime is, toward
        `foam_white`, held under the albedo ceiling (30% `foam_white` into `salt_glass` at most). The tube feet are
        `bone`. The mouth's ring and teeth are the `spawn_wound` weak point. The plinth is `salt_glass` ice frosted on
        top.
      - **Budget and rig.** 8,822 triangles (budget 9k), 10 bones: root (the plinth), `body` (the test, pivoting at its
        centre), `sector_0`..`sector_7` (the spine field by azimuth from the front). A spine is skinned to the body at
        its root and to its sector toward its tip, so a sector leans its spines without tearing them off the test.
      - **Clips.** `idle` (3.0 s loop: the sectors sway outward and in, a wave running round the field like wind in a
        field). `attack` (1.1 s: it rocks back, showing the mouth to the front, then rolls in, the front spines
        stabbing; contact 0.5 s). `cast` (1.4 s: every sector turns to the target, the top spines tipping forward and
        the sides swinging round; contact 0.8 s). `hit` (0.45 s: the spines clench and the test flinches; peak 0.1 s).
        `ko` (2.0 s: a last clench, then the spines droop out and the test settles 4 cm onto its ice).
- [x] **The conduit crawler** (`conduit_crawler/build_conduit_crawler.py`):
      - **Shape.** A clear salt-glass dome 0.7 m long, 0.47 m wide and 0.45 m to its crown. It has a brass rim and two
        brass ribs over the shell, a belly plate and a head housing. Six thin brass legs of two stand on
        `lacquer_black` pads at y 0. Two short fore-arms end in a round brush (left) and a wiper blade (right).
      - **The exaggeration.** It has kept working for four hundred years: the brass is worn to `bronze_patina` in the
        low places and in patches.
      - **Colours.** The shell is `salt_glass`. Its bound light, `glimmer_bound` (steady, no pulse: README rule 3,
        color_script.md rule 2), shows through the crown on the shell slot's emission mask. The frame is `brass` going
        `bronze_patina`, the joints and feet `lacquer_black`, and the bristles `sand_cloth`. The weak point is the
        shell's seam: a raised `spawn_wound` bead down the back where its halves meet, in its own `seam` slot.
      - **Budget and rig.** 4,752 triangles (budget 5k), 18 bones: root, `body`, `leg_{l,r}{0,1,2}_a/_b` (front to
        back), `arm_l_a/_b` (the brush), `arm_r_a/_b` (the wiper).
      - **Clips.** `idle` (2.0 s loop: the arms scrub back and forth, never into the floor, and the feet tick in two
        alternating tripods). `attack` (1.0 s: it rocks back and cocks the brush, then jabs it straight out; contact
        0.45 s). `cast` (1.6 s: the repair, leaning in with the arms working fast and the feet pattering; contact
        1.0 s). `hit` (0.5 s: knocked up off its feet, it rocks on its legs; peak 0.1 s). `ko` (1.6 s: its knees fold
        up and the body sinks 0.15 m between them onto the belly plate, its arms folding under its chin).
- [x] Each GLB is deterministic (`--threads 4`). `verify_blender_builds.py --job creature_<id>` prints identical for
      every output of all four jobs. `python3 build_<id>.py --report` prints the per-clip numbers without Blender.
- [x] materials.json and the `.tres` from write_materials.py; the four Blender jobs; PROVENANCE rows (their own
      commit).
- [x] Battle scenes `game/creatures/<id>/<id>_battle.tscn` and the creatures.json rows. No phases, no enemies.json rows
      (no Act II encounter exists yet).

      | Row | Contacts (attack, cast) | stand_in | portrait |
      |---|---|---|---|
      | tannin_archer | 0.55, 0.9 | default (yaw 90: side-on, the bars and the root read) | yaw 50, pitch 12 |
      | gallery_ray | 0.6, 0.9 | yaw 60, hover 1.4 | yaw 30, pitch 35 (from above: the diamond) |
      | rime_urchin | 0.5, 0.8 | default | pitch 10 |
      | conduit_crawler | 0.45, 1.0 | default | yaw 40, pitch 20 |

      None is dark (median albedo luminance below), so no row takes the dark `rim_energy` 2.8 / `kick_energy` 1.8.
- [x] The import rule lists the four folders, and each `.glb.import` runs the creatures post-import script.
- [x] tests/unit/test_creature_actor.gd: a shared `_act2_regular` check (the strike and the cast play on their clips
      at their contact seconds, no phases, exactly the sheet's bones), plus one test each:
      - the archer raises its head to aim the long jet, and its KO rolls it off the root, which stays put;
      - the ray's hover is 1.4, its wings undulate, the cast settles it into the pool, and the KO's root lands on the
        floor;
      - every urchin sector clenches on the hit and turns on the cast, and the KO settles the test on the unmoving
        plinth;
      - the crawler's legs end every strike and hit back where they stood, and its KO sinks it between its legs onto
        its belly without any leg going under the floor.
- [x] Shots `creature_tannin_archer`, `creature_gallery_ray`, `creature_rime_urchin` and `creature_conduit_crawler`
      (three-quarter, idle) in tests/screenshots/shots.json, with their stage scenes.
- [ ] **PC render pending:** no captures in the cloud environment (human directive). The PC renders the four shots, a
      reviewer views them, and only then do their baselines go in.
- [ ] Encounters (not this task): enemies.json rows with `model` when the Ch10 and Ch11 encounters are designed.

## Numeric check (no render)
Measured from the exported GLBs by evaluating every baked frame (30 fps) of every clip: glTF node animation, joint
matrices and linear blend skinning. The builds' numpy `--report` agrees. "Peak" is the frame of greatest mean
displacement from the rest pose. Heights are metres on the stage (y 0 is the floor or the water).

**Tannin archer** (the fish: every vertex but the root prop, which stays at −0.083..0.184 in every frame; its ends dip
into the water). The fish rests 0.017..0.582.

| Clip | Length | Peak | Fish lowest..highest | End of clip |
|---|---|---|---|---|
| idle | 2.4 s | (loop) | +0.013..0.588 | loops |
| attack | 1.2 s | 0.47 s (contact 0.55) | +0.017..0.676 | rest |
| cast | 1.8 s | 1.13 s (contact 0.9) | +0.017..0.769 | rest |
| hit | 0.5 s | 0.10 s | +0.017..0.635 | rest |
| hit_b | 0.5 s | 0.10 s | +0.017..0.650 | rest |
| ko | 1.8 s | 1.37 s | −0.066..0.620 | −0.066..0.258: on its side at the water, rolled 0.3 m off the root |
| idle_b | 1.3 s | 0.80 s | +0.017..0.603 | rest |

**Gallery ray** (on the stage, with its 1.4 m hover added). The ray rests 1.351..1.500, the tail tip at z −1.56.

| Clip | Length | Peak | Lowest..highest | End of clip |
|---|---|---|---|---|
| idle | 3.0 s | (loop) | 1.294..1.565 | loops |
| attack | 1.2 s | 0.60 s (contact 0.6) | 0.726..2.048 | rest |
| cast | 1.6 s | 0.90 s (contact 0.9) | 0.001..1.500 (the underside on the pool) | rest |
| hit | 0.5 s | 0.10 s | 0.760..2.024 | rest |
| hit_b | 0.5 s | 0.10 s | 0.691..2.050 | rest |
| ko | 2.0 s | 2.00 s | −0.004..1.955 | −0.001..0.148: flat on the floor; the root dropped 1.40 (tools/tests' flier check) |
| idle_b | 1.13 s | 0.63 s | 0.946..1.500 | rest |

**Rime urchin.** At rest the plinth spans 0.000..0.147, the test 0.126..0.860 and the spines 0.384..1.794. The plinth
never moves.

| Clip | Length | Peak | Lowest..highest | Spines' lowest | End of clip |
|---|---|---|---|---|---|
| idle | 3.0 s | (loop) | 0.000..1.802 | 0.301 | loops |
| attack | 1.1 s | 0.50 s (contact 0.5) | 0.000..1.817 | 0.089 | rest |
| cast | 1.4 s | 0.80 s (contact 0.8) | 0.000..1.795 | 0.033 | rest |
| hit | 0.47 s | 0.10 s | 0.000..1.823 | 0.384 | rest |
| hit_b | 0.47 s | 0.10 s | 0.000..1.817 | 0.178 | rest |
| ko | 2.0 s | 2.00 s | 0.000..1.817 | 0.052 | 0.000..1.640: the test settled to 0.073, the spines drooped |
| idle_b | 1.0 s | 0.57 s | 0.000..1.795 | 0.303 | rest |

**Conduit crawler.** The six foot pads stand at y 0.000 at rest (their centres at 0.011). The shell's crown is at
0.452.

| Clip | Length | Peak | Lowest..highest | Feet's lowest | End of clip |
|---|---|---|---|---|---|
| idle | 2.0 s | (loop) | −0.001..0.462 | −0.001 | loops (feet at +0.006: the idle's bob) |
| attack | 1.0 s | 0.47 s (contact 0.45) | 0.000..0.490 | 0.000 | rest |
| cast | 1.6 s | 1.17 s (contact 1.0) | 0.000..0.478 | 0.000 | rest |
| hit | 0.5 s | 0.10 s | −0.001..0.562 | −0.001 | rest |
| hit_b | 0.5 s | 0.10 s | −0.001..0.601 | −0.001 | rest |
| ko | 1.6 s | 1.27 s | 0.000..0.452 | 0.000 | 0.000..0.305: the belly plate 0.018 off the floor, the feet where they stood |
| idle_b | 1.13 s | 0.83 s | 0.000..0.460 | 0.000 | rest |

**Colours against palette.json.** Every vertex albedo is a palette swatch, or a mix or darkening of the swatches the
sheet names. The albedo floor (#1D1916) is 0.0101 in linear luminance and the ceiling (#EBE7DF) 0.8014.

| Creature | Linear luminance | Median (linear / sRGB) | Below floor, above ceiling | Weak point (verts with emission > 0.5) |
|---|---|---|---|---|
| tannin_archer | 0.0101..0.6683 | 0.154 / 0.426 | 0, 0 | gill slit: 10, albedo `spawn_wound` × 0.65 blended |
| gallery_ray | 0.0101..0.7114 | 0.590 / 0.789 | 0, 0 | spiracles: 100, `spawn_wound` × 0.65 (the margin: 582 verts of `sea_glow` emission) |
| rime_urchin | 0.0188..0.7798 | 0.451 / 0.698 | 0, 0 | mouth ring and teeth: 157 |
| conduit_crawler | 0.0101..0.7302 | 0.237 / 0.523 | 0, 0 | seam: 242, `spawn_wound` × 0.65 (the shell: 58 verts of `glimmer_bound` glow) |

The dark-portrait rule follows the Act I rows that take `rim_energy` 2.8: flue_moth (sRGB median 0.189) and
squall_wing (0.101), and the Wakefin (0.113). All four regulars sit well above 0.2, so none takes it.

## Notes
- **Palette usage limits to settle at review (art):**
  - palette.json's `spawn_wound` limit says "never a non-Undertow creature's weak point". The creatures README (rule
    3) and all four sheets give every creature's weak point `spawn_wound`, as the Act I reef beasts already have it.
    The builds follow the sheets. If art wants reef beasts and constructs to use another swatch, it is one colour per
    build.
  - `foam_white` is "foam texture only". The rime urchin's sheet names it for the rime. The build mixes at most 30% of
    it into `salt_glass`, under the ceiling.
- **The gallery ray's shot:** CreatureStage doesn't apply the stand-in's `hover`, so the ray is shown at its origin,
  with the disc's underside at −0.05 and the floor cutting through it, as with the other fliers' shots. Check the
  framing on the PC render; in battle, FighterStandIn lifts it 1.4 m.
- **The conduit crawler's light dims on the KO** (by the sheet), but the creature shader's emission is static. It
  needs the VFX or the actor to fade the shell slot's emission (a request when the encounter exists). Its "scuttles to
  the engine" cast plays in place (the sequencer moves it), like every strike.
- **Not modelled, by the sheets:** the archer's jet, the ray pool's flare, the urchin's frost bloom and the rime
  melting on its KO. These are VFX.
- **For the first PC render:**
  - the archer's bars at battle distance, and whether the root reads as a root;
  - the ray's pale disc against a salt-glass floor (the sheet wants it nearly that colour), and the margin's sea-glow;
  - the urchin's spine field (faceted, flat-shaded quads) and whether the rime reads white enough;
  - the crawler's crown glow through the shell, and its thin legs at 9 m.

## Review log
- 2026-10-28, creatures: **paused by ADR 0041** (Act I at final quality first; the human's directive). The work done so far is merged on claude/creatures as is; nothing reverted. Resume when a new ADR lifts the pause.

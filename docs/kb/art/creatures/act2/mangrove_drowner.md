# The Mangrove Drowner (`mangrove_drowner`), Ch10 boss

**Where:** Ossa Fen, in the roots of an old mangrove at the edge of the Kirru channels (act_outline Ch10: "spawn in
the roots, two phases"). The first boss after the act break into "The Truth".

## The idea

Undertow-spawn that took root. It came up the estuary as a slick of black water and stayed in the cage of a
mangrove's prop-roots, and the roots grew around and through it. Its body **is** the root cage now: arched roots
like ribs, bark gone black and wet where it lives, and its wounds open between the roots. The fen's dead should
lift (the farewell-tide); the motes it has dragged down are snagged in its roots, a pale drift of `glimmer_held`
that never sinks and never rises.

The one exaggeration: **a mangrove's roots used as a body**. Every root is a real prop-root (arched, knuckled,
barnacled at the waterline); there are simply too many, and they move.

## Silhouette

- **Rooted (phase 1):** a **tree first**. A thick, vertical dead trunk (about 1.2 m through) stands well above the
  roots and goes up to a snapped top at about 4.2 m (the canopy above it died and broke away; the battle frame cuts
  near there). At its foot a lopsided tangle of prop-roots, about 2.4 m high, reaches far out on the bank side and
  only a little on the other, and the spawn's dark mass is wedged low between the roots, at the water. Thin aerial
  roots hang straight down from the trunk's limb stubs to the water. Reads as a drowned mangrove standing in the
  fen, taller than wide.
- **Risen (phase 2):** it tears the trunk up with it. The snapped top splinters off; the trunk, still about 3 m of
  it, tips forward like a felled tree that walks, and the roots gather into **three clusters** that plant (the bank
  side's longest roots, a back cluster and a front cluster under the lean), two roots in each. The rest hang or
  trail with frayed, torn tips, the two front roots reach for the drag, and the spawn's mass hangs in the root ball
  under the trunk's foot. No even ring of legs and nothing radial: a leaning trunk on three uneven root-feet.
- Snagged motes: a dozen small pale lights hung in the roots like caught lanterns (VFX), the only soft thing on it.

### Silhouette rules (M3-CRE-622 redesign; the first pass read as a spider in every view)

A central bulb with roots radiating evenly from it **is** a spider, however knuckled the roots are. So:

1. **Vertical first.** The trunk is the tallest, thickest shape: no root arch rises within 1.5 m of the snapped
   top, and the trunk's width at the roots is at least a quarter of the cage's width.
2. **The core is wedged low,** not carried: the spawn mass sits at the water (its top under about 1.3 m), pushed
   to the front between two root clusters so its wounds face the party, pinched where the roots clamp it. Never a
   ball held up on roots.
3. **Tiers, not a ring.** Roots leave the trunk in three tiers (low about 1.0-1.4 m over the core's shoulders, mid
   about 1.5-1.9 m, high about 2.0-2.4 m), overlapping in depth, and curve sideways as they go down so neighbours
   cross: a tangle.
4. **Lopsided plan.** The roots come in four clusters with wide gaps (one at the front, where the core shows). The
   bank side's cluster (its right, −x) reaches about 3.4-3.9 m; the others 1.7-2.8 m. From the top it is a trunk
   with four uneven root-bundles and a few forks, never a sunburst.
5. **Verticals no spider has:** thin, straight aerial roots from the trunk's limb stubs to the water. Risen, they
   still hang plumb from the tipped trunk.
6. **Risen:** the trunk leans forward (about 30 degrees) and the stance is three planted root-clusters of two roots,
   unevenly placed; everything else hangs, trails or reaches. Smooth, gnarled roots (low knuckles): segmented
   joints read as legs.

Checked from flat silhouettes of the GLB's vertices (side, front, top; rooted and risen) before the PC render.

## Palette

Roots `timber_weathered` drying to `bone` at the top (sun-bleached bark), going `lacquer_black` and clearcoated
below the waterline; barnacle bands `coral_stone_weathered`. The core `lacquer_black` to `abyss_navy`, wet. Wounds
`spawn_wound` between the roots. Snagged motes `glimmer_held`. No green: the canopy above it has died.

## Battle read and clips

- **At battle distance:** a pale dead trunk over a lopsided tangle of roots, a black mass with cyan seams wedged
  at its foot; after the phase, a leaning trunk walking on three root-feet.
- `idle`: the roots flex with the tide (a slow 4 s breath); the core shifts inside; snagged motes sway.
- `attack` (the drag): two roots reach out along the water and haul back; contact at 0.7 s of 1.4 s. Its
  telegraph is the water drawing toward it first.
- `cast` (the rising water): the roots spread and the wounds flare, and the water climbs the roots.
- `hit`: the cage shudders and the core recoils inside it; peak near 0.1 s.
- `ko`: the roots let go one by one and it sinks; as it goes, the snagged motes come loose **upward** (the
  foreshadow of the Letting: VFX, `glimmer_lift`, the one place a spawn's death shows it, and it is the motes,
  not the spawn).
- **Phase `uprooted`** (50% HP): `phase_change` (2.2 s): it wrenches free, the snapped top of the trunk (`Stump`)
  splinters off and falls, the trunk tips forward and three root-clusters plant; `idle_risen` from then on.

Budget ≤ 18k triangles. Rig: a core chain of 4 (the spawn mass), twelve roots of 3 bones (six become legs in three
clusters in phase 2), the snapped top (`stump`, hidden after the phase) and its splinters, and one bone per aerial
root (so it hangs plumb when the trunk tips).

**Break part (proposal):** the snagged-mote roots (two of them). Breaking one frees its motes (they lift) and
weakens the drag.

## Model notes (M3-CRE-622)

- **Trunk:** part of the body up to a torn break at about 3 m (bark furrowed lengthwise, a buttress flaring under
  each root); above it the snapped top (`Stump`, about 2.9-4.2 m, splinters on top) is its own mesh. Bare limb
  stubs at about 2.6-3 m carry the aerial roots.
- **Roots:** each leaves the trunk at its tier's height, leans out over a low shoulder and comes down to the mud,
  curving sideways. Gnarled, not segmented: a slight swelling every 0.4-0.7 m, the bark between two its own
  weathering, tapering to about 0.1 m at the mud, the free tips frayed into fine roots. Some roots fork near the
  water.
- **Core:** wedged at the water between the trunk's foot and the front roots, wider than tall, bulging into the
  gaps between root clusters and pinched where they clamp it, with deep folds (in the gaps), broad boils and small
  tight blisters crowding the folds' lips. The `spawn_wound` seams (the weak point, ADR 0151) run down the bottom of
  the folds, most of them on the front.
- **On the water (M3-CRE-622):** y 0 is the water and nothing goes under it in any clip (GroundedClipsTest, no
  allow-list): the feet rest on it, flattened, and the aerial roots stop just short of it. The `ko` keels the dead
  tree over backward on its foot's edge while the mass slumps out onto the water; the sinking is the water's VFX.
- **Clusters in plan:** the roots of a cluster leave the trunk spread round it and converge on its heading toward
  their feet; once risen, the legs' planes turn so the stance is three planted pairs (front-right, front-left under
  the drag, the bank with its trailing roots alongside), the wide gap behind.

**Lean, as approved (2026-10-28):** the risen trunk leans **48°**, not the "about 30°" written above. The render shows it as a felled tree walking, and that is the approved reading.

## As built (M4-CRB-002, the move pass to the Act I bar, 2026-10-30)

Audited from the battle camera in `ossa_fen_roots` and up close (scratch clip sheets, five beats per clip). The
model read as the sheet asks (a pale dead trunk over a lopsided tangle, the black mass with cyan seams wedged at its
foot; risen, a leaning trunk on root-feet), but it was not finished to the Act I bar: one `attack` and one `cast` for
every skill; no `intro`, `ready`, authored `idle_b` or risen versions of most clips; every root's foot slid and lifted
whenever the trunk moved (up to 24 cm in the haul, risen legs hovering 17 cm); clips started from the rest pose
rather than idle's first frame (small pops); no VFX anchors; and the snag roots the fight breaks had no motes and no
broken state. What changed:

- **Planted roots.** Every root that stands on the water is held there by IK at every frame (`plant_roots`: damped
  least-squares turns added to the authored bends, so a root's arch still lifts and parts over its planted foot). Rooted,
  all twelve stand; risen, the six legs. A root lets go only where its clip reaches, stamps or dies. Where a turned
  tip would dip, the foot stands a few millimetres higher instead of being curled up by the grounding pass.
- **Stances.** Every clip starts and ends on its phase's idle first frame: rooted clips on `idle`'s, risen clips on
  `idle_risen`'s, and `phase_change` from the one to the other.
- **The snag roots (break parts).** The two drag roots (0 and 11, front-left, on the party's and the camera's side) each
  hold a cradle of four fine rootlets slung under their arch with six snagged motes caught in it (`SnagA`, `SnagB`;
  `mote_snag`, `glimmer_held`, steady), each cradle rigid on its own bone (`snag_root_a`, `snag_root_b`) under its
  root's middle bone. Broken (`SnagABroken`, `SnagBBroken`), the cradle is torn: its frayed ends hang from their knots and
  the motes are gone (their lift is VFX, `glimmer_lift`). The battle scene starts with the broken meshes hidden.
- **Anchors** (unweighted): `vfx_wound` on the largest front fold's seam (on `core2`), `vfx_core` at the mass's centre
  (`core1`), `vfx_phase` at the trunk's torn top, where the snapped top splinters off (`root`). creatures.json
  `vfx_anchors`: core `vfx_core`, wound `vfx_wound`.

**Clips** (rooted / risen):

- `intro` (2.6 s): a dead tree with the mass drawn back under it; the mass heaves up between the roots (0.9-1.35 s),
  the arches lift, the trunk shudders and the aerial roots swing; it drops back, rebounds and settles on idle.
- `ready` / `ready_risen` (1.6 s loops): the mass up 10 cm, the two drag roots lifted off the water and trembling;
  risen, the trunk rears 4° back off its lean.
- `idle_b` (1.4 s): a low front root knuckles up over its planted foot and resettles; the mass shifts.
- **drowner_haul** `attack` / `attack_risen` (1.4 s, contact 0.7): the two drag roots rise and hang over the water
  (0-0.5 s), reach out along it and haul back.
- **rising_water** `rising_water` / `rising_water_risen` (2.0 s, contact 1.0): the arches lift and part over their
  planted feet and the mass heaves up (0-0.9 s), a last surge at 1.0 s, a pulse, and it settles.
- **drowner_snag** `snag` / `snag_risen` (1.6 s, contact 0.75): one drag root rises and hangs high, its tip down
  (0-0.6 s), drops at full speed, curls its tip up round the hero's legs and pulls (to 1.2 s), then lets go. Risen it
  is solved under the tipped trunk.
- **root_stamp** `root_stamp_risen` (1.8 s, contact 0.8; phase 2 only): the trunk rocks back off its lean and rises
  while the front pair of root-feet (legs 5 and 6) lift 0.75 m and draw in (0.1-0.65 s); it lurches forward and
  stamps them down where they stood at 0.8 s; the trunk shudders and settles.
- **drink_the_fen** `cast_risen` (2.0 s, contact 1.0; retimed from the built 1.8 s): the trunk sinks onto its legs and
  the hanging roots dig at the water (0-0.8 s), the mass swells and pulses as it draws, then lets go.
- `cast` (1.8 s, contact 1.0): the generic fallback, unchanged.
- `hit`, `hit_b` / `hit_risen`, `hit_b_risen` (0.6 s, peak 0.1 s): the cage shudders, the mass recoils; `hit_b` the
  other way, heavier.
- `snag_break` / `snag_break_risen` (0.8 s): the drag roots jerk as one is torn, the mass flinches, the roots sag.
- `phase_change` (2.2 s): as built (M3-CRE-622), now from idle's first frame to `idle_risen`'s, the legs planted
  where the stance stands them.
- `ko` (3.2 s, phase 1; unchanged) and `ko_risen` (2.6 s, the KO in phase 2 through the `clips` map): it shudders,
  the root-feet let go one by one and slide out as the trunk sags, then the dead tree keels over backward on its
  foot's edge and the mass slumps out onto the water.

**Clip map for combat** (ready to paste into creatures.json `clip_by_skill` once the skills are in skills.json; the
phase `clips` map already sends each clip to its risen version):

| Skill (proposed id) | Clip | Contact (s) | Phase 2 plays |
|---|---|---|---|
| `drowner_haul` | `attack` | 0.7 | `attack_risen` (0.7) |
| `rising_water` | `rising_water` | 1.0 | `rising_water_risen` (1.0) |
| `drowner_snag` | `snag` | 0.75 | `snag_risen` (0.75) |
| `root_stamp` | `root_stamp_risen` | 0.8 | (phase 2 only) |
| `drink_the_fen` | `cast` → phase map | 1.0 | `cast_risen` (1.0) |

`drink_the_fen` is phase 2 only: map it to `cast` (the phase sends it to `cast_risen`) or straight to `cast_risen`.
`contact` is already in creatures.json for every clip above. **Break parts**, ready to paste once the skill that
silences them is in skills.json (keyed by that skill, as the Drownbell's `toll`):
`"break_parts": {"drowner_haul": {"whole": ["SnagA", "SnagB"], "broken": ["SnagABroken", "SnagBBroken"]}}` (or one
part per root if combat splits them). **Boss seat** (proposal for battle_sandbox.json `boss_seats`, M3-CRB-011): on
Slot0 the trunk fills the frame's left third with its top cut and the bank roots crossing toward the camera; at
`[-5.0, 0.0, -3.0]` the whole tree reads, the party clear.

- **Barnacles** have seven sides, not five (up close the five-sided ones read as flat pentagons).

**Checked:** every frame of every clip on or over the water (the lowest vertex 2 mm up, GroundedClipsTest with no
allow-list); a planted foot slides at most a few centimetres risen and not at all rooted, and stands up to 7 cm higher
where a jolt turns its tip down (the build's `--report`). The bestiary portrait is re-baked from the new idle.

**Budget:** 17,676 triangles (body 14,457; `Stump` 819; each snag cradle 816 whole, 384 broken), under the 18k. 58
bones (the 53 built, the three anchors and the two snag bones).

## Own VFX (M4-A2P-058)

The creature's own effects live in its battle scene (`AmbientVfx`, CreatureAmbientVfx), driven by
`game/data/creatures/creature_vfx.json`; skill VFX stay battle-presentation's (effects.json).

- **The snagged motes' drift.** Around each cradle (`snag_root_a`, `snag_root_b`), seven tiny `glimmer_held` motes
  drift in the cradle's own space, a few millimetres a second in every direction, never rising and never sinking:
  held, not falling. A soft `glimmer_held` halo sits on each cradle so the beads read through the fen's fog. Both show
  only while the cradle's mesh (`SnagA`, `SnagB`) does.
- **The lift.** When a cradle's mesh is hidden (the break part, once combat keys `break_parts`), or 0.5 s / 0.8 s into
  the KO for a cradle still holding, its six motes come loose **upward**: 0.2-0.4 m/s, blending `glimmer_held` to
  `glimmer_lift` in Oklab (colour script rule 1's one sanctioned blend) and whitening to `glimmer_lift_hi`. On the KO
  the lift also swaps the cradle to its broken mesh, so the beads are gone as the motes rise.
- **The drag.** While a drag root hauls (`attack`/`attack_risen` 0.45-1.25 s, `snag`/`snag_risen` 0.55-1.3 s) and as it
  wrenches free (`phase_change` 0.2-1.6 s), churned water and silt (`foam_white` to `sand_wet` to `timber_weathered`)
  puffs off its foot and water drips from it; a wider churn spreads round the trunk's foot on the water at the
  `phase_change` (0.5 s), the `root_stamp_risen` (0.8 s) and the `intro`'s heave (0.9 s).
- **Viewed** (lavapipe, scratch fixtures in `ossa_fen_roots` at the boss seat; battle camera and close): the motes and
  halos read as the soft thing on it; the KO lift rises as a few pale sparks; the drag reads close up as a faint
  haze at the root tips. On the sand bank where the preview seats it the churn is quiet; in water it would read more.

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

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

- **Rooted (phase 1):** a dome of arched roots 3.2 m high and 5 m across, standing in the water, a dark mass
  inside; the trunk above is cut out of frame by the canopy. Reads as a cage, wider than tall.
- **Risen (phase 2):** it tears out of the tree. Six of the roots become legs, and the body lifts to 3.6 m, a
  black core hung in a ring of roots. Taller than anything in Act I except the Reach.
- Snagged motes: a dozen small pale lights hung in the roots like caught lanterns (VFX), the only soft thing on it.

## Palette

Roots `timber_weathered` drying to `bone` at the top (sun-bleached bark), going `lacquer_black` and clearcoated
below the waterline; barnacle bands `coral_stone_weathered`. The core `lacquer_black` to `abyss_navy`, wet. Wounds
`spawn_wound` between the roots. Snagged motes `glimmer_held`. No green: the canopy above it has died.

## Battle read and clips

- **At battle distance:** a black dome of pale-topped roots with cyan seams inside; after the phase, a walking
  cage.
- `idle`: the roots flex with the tide (a slow 4 s breath); the core shifts inside; snagged motes sway.
- `attack` (the drag): two roots reach out along the water and haul back; contact at 0.7 s of 1.4 s. Its
  telegraph is the water drawing toward it first.
- `cast` (the rising water): the roots spread and the wounds flare, and the water climbs the roots.
- `hit`: the cage shudders and the core recoils inside it; peak near 0.1 s.
- `ko`: the roots let go one by one and it sinks; as it goes, the snagged motes come loose **upward** (the
  foreshadow of the Letting: VFX, `glimmer_lift`, the one place a spawn's death shows it, and it is the motes,
  not the spawn).
- **Phase `uprooted`** (50% HP): `phase_change` (2.2 s): it wrenches free, the trunk stump splinters, and six roots
  plant as legs; `idle_risen` from then on.

Budget ≤ 18k triangles. Rig: a core chain of 4, twelve roots of 3 bones (six become legs in phase 2), the trunk
stump (hidden after the phase).

**Break part (proposal):** the snagged-mote roots (two of them). Breaking one frees its motes (they lift) and
weakens the drag.

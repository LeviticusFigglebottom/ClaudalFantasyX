# Wick crawler (`wick_crawler`), Ch19

**Where:** the Iskarra Lamp Spire (act_outline Ch19: the party climbs it to shut down the founders' anchor-engine).
**Kind:** Lit Age construct. **Role:** it **relights** (buffs) the spire's other constructs until it is shut down.
The chapter designer sets its stats, skills and AI.

## The idea

A Lit Age lamp-tending machine, still on its rounds. Its body is a brass lamplighter's pole carried on many fine
hooked legs, made for walking the spire's lamp-ropes from lamp to lamp. At its head are a pair of wick-shears and a
snuffer cone. Carried upright on its tail is its own taper, a small bound light in a glass thimble, held high the way a
lamplighter holds the pole. It trims wicks that went out a thousand years ago and touches its taper to lamps that
have no oil. It isn't hostile. It keeps the lamps lit.

The one exaggeration: **a lamplighter's pole that walks.** Its parts are a real lamplighter's kit (the pole, the
taper, the shears, the snuffer) on a millipede's many legs.

**Kept apart from the conduit crawler** (Ch11), the other Lit Age tender. The conduit crawler is a round glass dome
on six legs, its light inside. The wick crawler is long, low and segmented, with its light held up high on a pole.
They share brass and bound teal (both are the Lit Age's work), not a silhouette.

## Silhouette and size

- **Body:** a segmented brass tube **1.5 m long**, seven segments tapering from 0.16 m across at the head to 0.1 m at
  the tail, carried 0.3–0.36 m off the floor on **fourteen** fine legs (seven pairs), each leg ending in a rope hook.
- **The pole:** from the last segment a thin brass pole rises 1.0 m, leaning forward over the back, with the taper's
  glass thimble at its tip **1.4 m** up. The pole is the read: a long, low thing with one high point of light.
- **The head:** a pair of wick-shears (0.22 m blades) and a snuffer cone on a short arm.
- **Battle camera** (about 110 px a metre at 720p): the body is about 165 px long and 40 px tall, with a 150 px pole
  and its light on top. On a slot it spans about 1.5 m along its facing. With `stand_in.yaw_deg` 90 that runs along the
  battle axis, inside the 2.1–2.3 m between the sandbox's enemy marks. Its silhouette is unlike any other Act I–III
  foe's.
- **Stand-in:** `height` 0.6 (the body), radius 0.4. The pole stands above it, as the rime urchin's spines stand above
  its 0.9 m test. So `chest` (0.36 m) lands on the body, and hits strike the machine, not the light.

## Palette

| Part | Albedo | Light |
|---|---|---|
| Body segments, pole | `brass`, going to `bronze_patina` in the joints and the underside | none |
| Legs, hooks, hinge pins | `lacquer_black` | none |
| Shears, snuffer | `brass` worn bright on the blades' edges | none |
| The taper's thimble | `salt_glass` | `glimmer_bound` `#4FB3B0`, energy 1.2, **steady** (README rule 3: a construct). It never flickers like a flame, which is its wrongness. |
| The oil reservoir at the pole's foot | `brass` | the weak point (below) |

Ch19's spire interior is "bound-teal and stone-grey" (color_script.md Ch19 LUT intent), so the brass reads warm
against stone. The taper is the only light on it.

## Weak point (ADR 0151)

**One small closed `spawn_wound` mark:** a hairline seam round the filler cap of the oil reservoir at the pole's
foot, 5 cm, on the camera side. It is a construct, so it has no open seam and sheds no motes. It is the part that feeds
the taper, so breaking it is what shutting it down means.

## Battle read and clips

**At battle distance:** a low brass many-legged thing with a pole held up over its back and a steady teal point of
light on the end.

| Clip | Length | Contact or peak | What it shows |
|---|---|---|---|
| `idle` | 3.0 s, loop | | A wave runs down the fourteen legs, front to back, as they tick in place. The shears snip at nothing, twice. The pole sways a few degrees. The taper's light doesn't change. |
| `attack` (the trim) | 1.1 s | contact 0.5 s | The head rears 20° and the shears snap shut at the target. |
| `cast` (the relight) | 1.6 s | contact 0.95 s | The pole bows forward over its head and the taper dips, as if touching a wick: the buff on an ally. Then it lifts back. |
| `hit` | 0.5 s | peak 0.10 s | The body kinks sideways in the middle, the legs on that side splay, the pole whips. |
| `ko` | 1.6 s | | The legs curl in under it, pair by pair from the head back. It rolls onto its side and the pole lies along the floor, the taper still lit in its glass. The light going dark is not modelled (the shader's emission is static, as the conduit crawler's); the KO fade covers it. |

Strikes play in place (the pipeline's clip contract). The relight's `step` travel toward an ally is the
sequencer's.

## Rig and budget

44 bones:
- `root` and a spine chain of 7 segments;
- `head`, two shear blades and the snuffer arm;
- fourteen legs of 2;
- a pole chain of 3, and the `taper`.

Four slots: `body`, `leg`, `taper`, `glass`. **Budget ≤ 6k triangles.** The legs are thin tubes (about 60 triangles
a segment); most of the budget goes to the segments' rims and the shears.

## Grounding

Grounded. The fourteen feet stand at y 0. The legs go through `common/grounding.py` as planted limbs in `idle`,
`attack`, `cast`, `hit`, `hit_b` and `idle_b`, so the feet stay put as the body rears and kinks over them. The `ko`
lifts `root` so the curled body lies on the floor and not through it.

## Open questions (for Combat and the chapter designer)

- **Which constructs it relights.** The chain lamp, by the roster. Does a broken (KO'd) construct get relit (a revive),
  or only buffed while standing? The clip is the same either way.
- **Does it ever stand on a lamp-rope** (a hanging arena prop) instead of the floor? Its hooks allow it. That needs a
  prop and a grounding exemption, so the floor is the proposal.
- **The Lamp Spire is on the cut list** ("shorten it to a single boss arena", act_outline Cut Notes). If the spire is
  cut, does the wick crawler move into the boss arena as an add, or go?

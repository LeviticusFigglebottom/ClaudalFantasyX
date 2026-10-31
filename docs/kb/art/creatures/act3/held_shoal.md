# Held shoal (`held_shoal`), Ch20

**Where:** the Undertow layers (act_outline Ch20: rooms of drowned memory, "an Oruvel market, a Corrow kitchen, a
Reefball crowd, suspended in dark water"). **Kind:** Undertow-spawn made of held light. **Role:** it is
**untargetable while it drifts** and strikes when the room's memory turns, so it teaches reading the layer, not the
foe. Combat and the chapter designer decide what "the memory turns" is and how it is shown.

## The idea

The sea's memory of fish: a school of fish made of **held** light, drifting in the drowned rooms. Each fish is held
motes in a fish's shape, as Nhoa is held motes in a woman's. The school circles one drowned thing, a fisher's **glass
net float** wrapped in a scrap of net. A float should rise, and this one hangs still at the shoal's heart, crusted
with the spawn's wet black. The shoal is held to it. It is the Oruvel market's catch, remembered by the people who
sold it and ate it and drowned, going round and round something that will never come up again.

The one exaggeration: **fish of light.** The animal is a real school of small reef fish (a mackerel's long, narrow
body), and the float is a real fisher's float.

## Held light: how it must move

The shoal is held light from end to end, so it moves the held way (color_script.md rule 1, palette.json
`mote_direction_rule`): **sideways or down, never rising.** Held motes drift at 0.05–0.2 m/s, mostly sideways, with a
downward bias.

- **No fish ever rises.** In every clip, each fish moves in the horizontal plane or downward. The fish stay level and
  never pitch up. Their tails beat side to side (yaw), never up and down. The whole shoal never pitches or rolls.
- This holds for the clips' own returns too. A motion that has to come back (a lunge, a recoil) is horizontal, so
  coming back is horizontal. Only the KO sinks, and the KO doesn't come back.
- **Checked by the build:** `--report` prints the largest upward step of any fish vertex between consecutive baked
  frames in any clip (tolerance 1 mm). It must be 0.
- The float is an object, not light. It hangs at a fixed height and is carried with the shoal.

## How a school of light is built without particles

Like Nhoa's motes (`vowbound/nhoa.md`, "How made of motes is built"), **skinned geometry**, not particles:
- **24 fish in three rings of 8**, at 0.75, 1.0 and 1.25 m, the rings 1.8, 2.0 and 1.7 m across.
- Each fish is about 26 small flattened beads (1.5–3.5 cm, Nhoa's six-triangle bipyramids) scattered round a fish
  outline 0.32–0.42 m long. Each fish has a dark inner body, a thin fish-shaped shell in `abyss_navy`, so it reads as
  light held in deep water.
- Each fish is skinned to two bones: its body and its tail.
- Each ring is a bone that turns the ring about the vertical axis.
- Within a ring the fish are **identical and evenly spaced**, with the same tail-beat phase pattern.
- The rings differ from each other in fish size, turn direction and bead seed.

**The idle loop by symmetry.** In a 6.0 s idle, each ring turns exactly one fish-spacing (45°): the lower and upper
rings one way, the middle ring the other. At the radius of the rings that is about 0.12 m/s, inside held light's drift
speed. The last frame is fish *i* where fish *i + 1* started, and since the fish are identical the picture loops
seamlessly though the bones don't. If the wrap ever shows a pop, the fallback is rings that sway ±20° and back (a
`Clip.wave`, still sideways only).

## Silhouette and size

- **At rest:** a loose drum of small cyan lights, three rings stacked between 0.65 and 1.35 m, 2.0 m across, slowly
  counter-turning round a dark float (0.3 m across) that hangs at 1.0 m in the middle. The fish's outlines read; the
  float shows as a dark gap at the heart.
- **Battle camera** (about 110 px a metre at 720p): about 220 px across and 80 px tall, each fish 35–45 px. That is a
  wide, flat silhouette unlike any standing foe. It takes one enemy mark. Its 2.0 m width fits the 2.1–2.3 m between
  the sandbox's marks, but only just, so two shoals side by side would touch (open questions).
- **Stand-in:** `height` 1.5, radius 1.0. `chest` (0.9 m) lands near the float, `head` (1.5 m) just above the top
  ring.

## Palette

| Part | Albedo | Light |
|---|---|---|
| The fish's beads | `salt_glass` `#BFE6E0` | `glimmer_held` `#7FC6D9`, energy 1.2, steady. The mask varies 0.4–1.0 per bead so each fish has depth. |
| The fish's inner bodies | `abyss_navy` `#061A2B` | none |
| The float's glass | `salt_glass`, where the crust leaves it bare | none (it is glass, not light) |
| The float's crust (spawn carapace) | `lacquer_black` to `abyss_navy`, wet (clearcoat) | none |
| The scrap of net | `sand_cloth` darkened wet | none |
| The seam on the float | | `spawn_wound` `#3FE0C8` (the weak point) |

**`glimmer_held` throughout:** palette.json allows it for held motes and the Undertow's held light, and the shoal is
both. No `glimmer_bound`: nothing here is bound. No `glimmer_lift`: nothing here is released. Ch20 is lit by held
cyan, `act3_abyss`, so the shoal is part of the room's light, which is what makes it hard to see as a foe at first.

## Weak point (ADR 0151)

It is Undertow-spawn, so its weak point is **the spawn's form: one short open seam in the wet carapace**, 8 cm, its
lips raised and faintly lit in `spawn_wound`. The shoal has no carapace of its own: light has no skin. So the carapace
is the crust on the float it is held to, and the seam is a crack through that crust and the glass under it. Any
`glimmer_held` motes it sheds are battle VFX, sideways and down.

Its weak point is the thing that holds it, not a fish (pillar 4: one answer to where to strike). While the shoal
drifts the rings hide the float. When it turns and strikes, the float shows.

## Battle read and clips

**At battle distance:** a slow, flat, turning drum of small cyan fish round a dark heart. It is part of the room until
it moves.

| Clip | Length | Contact or peak | What it shows (all of it horizontal) |
|---|---|---|---|
| `idle` | 6.0 s, loop | | the rings counter-turn one fish-spacing; tails beat; the float hangs still |
| `idle_turned` | 4.0 s, loop | | the targetable state: the rings drawn in tight (1.0 m across) round the float, so it shows; the turning slower |
| `attack` (the turn) | 1.2 s | contact 0.55 s | the three rings swing forward together as a stacked column toward the target, each at its own height, and back. The fish turn to face the target as they go. |
| `cast` | 1.6 s | contact 0.9 s | the rings spin up and tighten, then flare outward (a wider ring at each height): the room's memory turning on the party |
| `hit` | 0.5 s | peak 0.10 s | the rings are pushed sideways away from the blow and scatter outward, then gather back, horizontally |
| `ko` | 2.0 s | | the float drops to the floor first. The fish lose their rings and **sink**, falling apart slowly as they go down, and lie as a scatter of held lights on the floor round it. |

`hit_b` is the kit's mirror (still horizontal). The kit's `idle_b` fidget must be checked by the build's rise report,
because it is derived from a clip.

## Rig and budget

54 bones:
- `root`, `float`;
- three ring bones;
- 24 fish of 2 (body, tail);
- `seam` (an attach for the shed motes).

Four slots: `beads`, `fishbody`, `float`, `crust`. **Budget ≤ 6k triangles:**
- about 3.7k for the beads (24 × 26 × 6);
- about 1k for the inner bodies;
- about 0.9k for the float, crust and net.

## Grounding or hover

Built hovering, with its origin on the floor (as Nhoa and the chain lamp), so it needs no `stand_in.hover` and the VFX
anchors' fractions land on the shoal. The lowest fish is at 0.65 m in every clip except the `ko`, which sinks
everything onto the floor (y ≥ 0).

## Open questions (for Combat and the chapter designer)

- **"When the room's memory turns."** What drives it: a turn count, the layer's own event, or the party doing
  something in the room? And how does the player read it before it happens (pillar 4)? The art offers `idle_turned`
  as the targetable look. Showing it needs a status- or phase-driven idle on CreatureActor (Tech): phases are by HP,
  and the part cues show and hide nodes but don't change the idle.
- **Its row:** a phase or status with `untargetable` while it drifts (the Undertow's Reach's breach phase uses that
  key). Which, and for how long?
- **Two shoals in one fight** would need marks more than 2.2 m apart, or a smaller ring (1.6 m) for the encounter.
- **The other rooms.** Is the shoal only the Oruvel market's (fish), or does each remembered room get its own held
  memory (a Corrow kitchen's smoke, a Reefball crowd's ball)? Those would be new sheets, not this one.

## As built (M5-A3P-1803, 2026-10-30)
`assets_src/creatures/held_shoal/build_held_shoal.py`, as the sheet:
- **Shape:** 5,817 triangles, 54 bones, the four slots. The seam's light is on the `crust` slot's emission mask.
- **The rise rule holds:** `--report` measures the light's largest upward step between baked frames as 0.000 mm in
  every clip, `idle_b` and `hit_b` included.
- **Loops:** the idle loops by symmetry (each ring turns one fish-spacing over 6 s). `idle_turned` draws the rings in
  to 1.0 m across and is listed in the row's `loop`.
- **Simplified:** in the attack the fish keep their ring heading rather than turning to face the target (the rings
  swing forward together).
- **Still open:** the status- or phase-driven idle that would show `idle_turned` is Tech's (open questions).
- Portrait, and review shot `creature_held_shoal`.

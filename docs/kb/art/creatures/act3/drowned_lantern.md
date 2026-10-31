# Drowned lantern (`drowned_lantern`), Ch20

**Where:** the Undertow layers (act_outline Ch20), in the remembered rooms of Oruvel and Corrow. **Kind:**
Undertow-spawn made of held light. **Role:** it **drains MP**, and it **lights the party's way when broken**, the first
foe whose death makes the room brighter. The chapter designer sets its stats and AI.

## The idea

The street lamps and kitchen lamps of the remembered rooms, gone wrong. A hanging lamp's glass globe, drowned and
remembered, has become a jelly. The globe is its bell, crusted over its old brass cap with the spawn's wet black. The
lamp's chain and its frayed wick-cords hang beneath it as the jelly's long arms. Where its flame was, there is a
cluster of **held** light, cold cyan, that never burned anything. It swims as a jelly swims, pulsing its glass skirt,
and it goes nowhere: held light can't rise, so each pulse only holds it where it is.

The one exaggeration: **a lamp that swims.** Every part is a real hanging lamp's: the globe, the brass cap and its
hanging ring, the chain, the wick. It moves like a moon jelly.

**Kept apart:**
- From the **Drownbell** (Act I's boss bell). The Drownbell is a 2.4 m bronze bell standing on legs. The lantern is a
  small glass globe, lit from inside, floating, with chains hanging below.
- From the **chain lamp** (Ch19). The chain lamp is an eight-sided brass cage hung on a chain from above, in bound
  teal. The lantern is a round globe with no chain above it, in held cyan.

## Held light: how it must move

The light inside is held (color_script.md rule 1): **sideways or down, never rising.**
- The light cluster rides one bone, `heart`, and the lantern's travel rides `root`. Neither ever moves upward in any
  clip.
- The pulse is the skirt's flex. The glass and chains may flex, because they are not light.
- The idle holds its height. The MP drain draws its arms sideways. The KO sinks.
- **Checked by the build:** `--report` prints the largest upward step of the `heart` and `root` bones between baked
  frames. It must be 0.

**The light inside, without particles:** about 90 small beads (Nhoa's bipyramids, 2–4 cm) in a loose cluster 0.22 m
across at the globe's centre, all skinned to `heart`, so it reads as motes held in the shape of a flame that isn't
there.

## Silhouette and size

- **The globe:** a three-quarter sphere of glass **0.6 m across**, open below in a skirt of eight glass lobes. Its
  centre is at **1.25 m**, so it spans 0.95–1.55 m, at the party's chest. The crusted cap and its hanging ring rise to
  1.65 m.
- **The arms:** the old chain and two frayed wick-cords, plus five finer cords, hanging from inside the skirt to
  0.35 m above the floor. Long, thin, swaying lines under a lit globe.
- **Battle camera** (about 110 px a metre at 720p): a 66 px glowing globe on 130 px of hanging lines, 145 px in all,
  narrow and vertical. It fits any enemy mark with room; three would stand apart.
- **Stand-in:** `height` 1.65, radius 0.35. `chest` (0.99 m) lands on the globe's lower half, `head` on the cap.

## Palette

| Part | Albedo | Light |
|---|---|---|
| The globe | `salt_glass`, crazed (cavity in the craze lines) | none: the light inside shows through the open skirt and the bare glass |
| The cap's crust (spawn carapace) | `lacquer_black` to `abyss_navy`, wet (clearcoat), over the old `brass` cap where it shows, dulled toward `bronze_patina` | none |
| The chain | `lacquer_black` iron, wet | none |
| The wick-cords | `sand_cloth` darkened wet | none |
| The held light inside | `salt_glass` beads | `glimmer_held` `#7FC6D9`, energy 1.2, steady (mask 0.5–1.0 per bead) |
| The seam in the globe | | `spawn_wound` `#3FE0C8` (the weak point) |

**`glimmer_held` throughout.** No `oil_lamp`, though these were oil lamps once: their flame is gone, and what is in
them is the dead (pillar 2). No `glimmer_bound`: these are not Lit Age lamps. No `glimmer_lift`, even at the KO (see
the clips).

**Oruvel and Corrow:** one model. The two towns' lamps can differ in the cap's metal where the crust leaves it bare
(Oruvel `brass`, Corrow `bronze_patina`), as a palette variant row if the chapter designer wants both (open questions).

## Weak point (ADR 0151)

It is Undertow-spawn, so its weak point is **the spawn's form: one short open seam**. It is a crack running down
from the crust into the globe's glass, 12 cm, its lips raised and faintly lit in `spawn_wound`, on the camera side.
Any `glimmer_held` motes it sheds are battle VFX, sideways and down. One seam, not a row of them: it is small, and the
one seam is where it breaks.

## Battle read and clips

**At battle distance:** a cold lit globe at chest height, hanging on nothing, trailing long lines, its skirt pulsing.

| Clip | Length | Contact or peak | What it shows |
|---|---|---|---|
| `idle` | 3.2 s, loop | | Two slow pulses a loop: the skirt's lobes draw in 15° and open. The arms trail and sway sideways. It drifts 0.1 m side to side at a constant height. The light holds still in the middle. |
| `attack` (the sting) | 1.1 s | contact 0.5 s | The skirt clenches and two cords lash out sideways at the target. |
| `cast` (the drain) | 1.8 s | contact 0.8 s | Every arm reaches sideways toward the target and draws back slowly. The drawn light (VFX) comes back along them, sideways, into the globe: MP drained. |
| `hit` | 0.5 s | peak 0.10 s | The globe is knocked sideways and tilts 12° about its centre; the arms whip; the skirt snaps shut and opens. |
| `ko` | 2.4 s | | The seam splits down the globe. The held light inside **slips down** out of the open skirt and settles on the floor beneath as a still scatter of beads (sinking, held: allowed). Then the empty globe and its chains sink after it and lie dark on the floor. |

**"The room gets brighter" when it is broken.** The model gives the light a place to land (the beads on the floor at
the KO's end). The brightening itself can't be the model's: a fallen foe fades out (`foe_ko_alpha` 0), and the
shader's emission is static. So it is presentation: a light left at the KO point, or the room's grade lifting
(open questions). That light should be `glimmer_held` and stay on the floor, not rise. Breaking the lamp frees its
light into the room, but that is not a release: the light is still held.

## Rig and budget

25 bones:
- `root`, `globe`, `heart` (the light);
- `heart_l` and `heart_r`, the heart's two children, which split the cluster of beads as it falls in the `ko`;
- eight skirt lobes;
- the chain (3), two wick-cords (2 each) and five fine cords (1 each).

Five slots: `glass`, `crust`, `chain`, `cord`, `light`. **Budget ≤ 4k triangles:** about 1.6k for the globe and
lobes, 0.5k for the light's beads, 0.6k for the cap and crust, and the rest for the chain and cords.

## Grounding or hover

Built hovering, with its origin on the floor (as Nhoa), so it needs no `stand_in.hover`. Its lowest point (a cord's
end) is at 0.35 m in every clip except the `ko`, which ends with everything on the floor (y ≥ 0).

## Open questions (for Combat and the chapter designer)

- **The brightening.** A light left where it broke (battle VFX), the arena's grade lifting a step per lantern
  (rendering), or the next room's path lit (environment)? The model only lands the light on the floor.
- **Does the brightening stay** after the battle, in the explored room, so the player's way through the layer is
  literally lit by what they broke? That is the chapter designer's and environment art's.
- **Oruvel and Corrow:** one row, or two palette rows (the cap's metal)?
- **The drain's contact:** one target or all? The clip reaches toward one. A drain on all needs the arms to spread.

## As built (M5-A3P-1804, 2026-10-30)
`assets_src/creatures/drowned_lantern/build_drowned_lantern.py`, as the sheet:
- **Shape:** 3,502 triangles, 25 bones, five slots. The weak point is the globe's crazed seam (`wound`), the vfx core is
  the `heart`.
- **The rise rule holds:** the `heart` is parented to the root, not the globe, so the glass tilts and the light
  doesn't. `--report` measures the heart, the root and every light bead at 0.000 mm of upward step in every clip.
- **KO:** the light slips down out of the skirt and settles on the floor; then the empty globe sinks (the `globe` bone,
  keyed every baked frame; the root stays at the floor origin) and rolls 70° onto its side. The arms and globe lift
  only as far as the floor needs (grounding.py).
- **Hit:** knocked sideways and tilted, eased in over 0.14 s so the chain doesn't pop (the audit's worst pop is 5%
  on `hit_b`).
- Portrait, and review shot `creature_drowned_lantern`.

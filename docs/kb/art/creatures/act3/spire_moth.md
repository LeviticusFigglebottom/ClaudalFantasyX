# Spire moth (`spire_moth`), Ch19: variant of the flue moth

**Where:** the Iskarra Lamp Spire (act_outline Ch19). **Kind:** beast, a variant of the flue moth
([`../act1/flue_moth.md`](../act1/flue_moth.md), Ch8 Coilspire). **Role:** a fragile swarm that **blinds** (Accuracy
down). The chapter designer sets its stats and AI.

## The idea

Moths of the same kind as Coilspire's soot moths, but these have lived for centuries on the Lamp Spire's lamp-glass,
which the bound lamps keep warm. Generations on glass have made them pale and glassy. There is no soot here and no
fire, so they carry no embers. Their scales are fine as glass dust, and when they flare, their spread hindwings throw
back the lamplight into the eyes. It is a beast, not spawn, and not a construct. Its one exaggeration is still its
size, as the flue moth's is: a moth the size of a dog.

The roster's link: Coilspire's moths came up the flues to a keeping flame. The spire's moths came to the bound lamps
and never left.

## What changes from the flue moth

A variant on the flue moth's rig, mesh and clips (act2/variants.md: "a variant is a base's rig and clips with a new
materials.json, new proportions in its build parameters where the base allows them, and a creatures.json row").

| | Flue moth (base) | Spire moth |
|---|---|---|
| Fur | `lacquer_black` into `volcanic_stone`, embers (`ember_orange`, slow pulse) | `bone` into `lit_ceramic`, with `coral_stone_weathered` in the cavities; **no embers** |
| Forewings | `volcanic_stone` and `overcast_slate`, black soot zig-zags | `salt_glass`, with fine `cold_blue_stone` veins where the zig-zags were; glossy (low roughness, high specular, a strong rim sheen), so they read as glass under the dusk key |
| Hindwings (shown in the flare) | `ember_orange` edged `lacquer_red_deep`, emissive | `gauze_white` paling from `salt_glass` at the root, edged `brass`; **not emissive**. The flare reads by catching the light (specular and rim sheen), and the glint is battle VFX |
| Antennae | `bone` darkened | `brass`-tinted `bone` |
| Eyes | `lacquer_black`, wet | the same |
| Weak point | none modelled (built before ADR 0151) | one small closed mark (below) |
| Size, silhouette, clips | 0.85 m long, crouched, forewings folded like a roof | **unchanged** |

**Silhouette and size** are the base's. It is 0.85 m long and low, with the thorax at 0.24 m and its feathered
antennae up. At about 110 px a metre it is a 95 px roofed crouch. That keeps it apart from the cord moth (Ch12, a
hovering flier with its wings open) and the ashwing (wings spread). Pale on the spire's grey stone, it reads lighter
than anything else in Ch19.

**The build needs base parameters**, because the look is vertex colour (pipeline §1): a palette map, the ember amount
(0 here), the wing pattern's colours, and a weak-point mask. The base's defaults reproduce the flue moth exactly, and
`creature_flue_moth` must still verify identical (as the root crab's legs did, M3-CRE-628). The materials.json is new.
The `fur` slot's emission colour becomes `spawn_wound` at energy 1.0 with no pulse, for the mark. The `wing` slot's
emission is 0.

## Palette

`bone`, `lit_ceramic`, `coral_stone_weathered`, `salt_glass`, `cold_blue_stone`, `gauze_white`, `brass`,
`lacquer_black`, and `spawn_wound` for the weak point only. Every albedo is inside the floor and ceiling
(`gauze_white` is the ceiling itself, used only on the hindwings' pale middle). No glimmer: it is a beast (README
rule 3). The bound lamps it lives on are the spire's, not its own.

## Weak point (ADR 0151)

**One small closed `spawn_wound` mark:** a crack in the camera-side thorax plate, 4 cm, closed, the cord moth's
kind of mark. A beast, so no seam and no motes. It is on the `fur` slot's emission mask, and the rest of the mask is 0
(the base's ember mask is off).

## Battle read and clips

**At battle distance:** a pale, glassy, roof-winged moth crouched on the stone. When it flares, a sudden spread of
white wings.

The flue moth's clips, unchanged (contacts from its creatures.json row):

| Clip | Length | Contact or peak | What it shows here |
|---|---|---|---|
| `idle` | 2.4 s, loop | | antennae comb the air, the glass wings shiver |
| `attack` (the buffet) | 1.1 s | contact 0.5 s | the wings clap open and it lunges: glass dust (VFX) |
| `cast` (the flare: the blinding) | 1.4 s | contact 0.6 s | it rears and spreads every wing, the pale hindwings shown: the Accuracy-down. The glint off them is battle VFX: a specular flash of the scene's own light, never a glimmer swatch and never a light of its own |
| `hit` | 0.5 s | peak 0.12 s | a flinch, the wings half open |
| `ko` | 1.4 s | | it tips onto its side, wings splayed along the floor |

`hit_b` and `idle_b` come from the kit as for the base. The hit's peak is 0.12 s, inside the 0.10–0.20 s window.

## Rig and budget

The flue moth's, unchanged: 22 bones (root, thorax, head, two abdomen bones, two antennae, four wings, six legs of 2).
Three slots: `fur`, `wing`, `eye`. **Budget ≤ 5k triangles** (the base is about 3.1k; the mark adds a few dozen).

## Grounding

Grounded, as the base: six planted feet through `common/grounding.py`, and the KO's root lift. No change.

## Open questions (for Combat and the chapter designer)

- **"A swarm":** three spire moths as three combatants (the proposal, one per enemy mark), or one combatant that is a
  cluster of three moths? A cluster is a new model, not a variant (three bodies on one rig, about 9k), and it reads as
  one target.
- **Its affinities.** The flue moth absorbs fire and is weak to ice (act1_ch08 §9). The spire moth has no fire in it.
  Is it the same family in Combat's tables, or new?
- **Should the base flue moth get its ADR 0151 mark too?** It has none. That is a change to a shipped creature, so the
  proposal is a separate polish task, not this variant.

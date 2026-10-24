# Spawn-polyp (`spawn_polyp`)

> *"Soft cyan mouths that open in the floodwater around the bell and feed it. Kill one and the tide grows another."*
> (`LORE_SPAWN_POLYP`)

**Battle role:** the Drownbell's healer in the Flood (phase 2). Two rise with the water, more on `rouse_polyp`. Its
one skill is `polyp_mend`, a heal on the bell. The read has to say **small, soft, feeding the bell, more where that
came from**.

## The idea

Undertow-spawn, so it carries the shared language (SPEC §7.5): a **dark, wet, lacquer-black carapace** and **glimmer
wounds**. It is a cluster of soft tube-mouths, like a sea-squirt colony or a clump of tube anemones, rooted in a
cracked black shell that sits on the drowned causeway. Each tube ends in a round soft mouth, and the inside of every
mouth glows `spawn_wound`. They open toward the bell and pulse.

The supernatural part is what the mouths are for. They do not eat. They pass something, held light, along to the
bell.

## Silhouette

- **A cluster, not a single form**: a low cracked black base 0.5 m across, five tube-mouths of different lengths
  rising from it (the tallest to 0.6 m) and leaning outward and toward +Z, like fingers of a half-open hand.
- **The mouths** are the only bright shapes: five cyan rings.
- It is meant to be seen **under the flood water** (the flood rises to +0.6 m, so a polyp is just covered): the glow
  must carry through the water, and the silhouette is mostly the glowing rings and the dark mass.

## Palette

| Part | Swatch | Notes |
|---|---|---|
| Base shell | `lacquer_black` `#1D1916` to `abyss_navy` `#061A2B` | Glossy clearcoat, wet. Cracks in it seep `spawn_wound` faintly |
| Tubes | `deep_teal_shadow` `#0E4A55`, soft, a little translucent | Lighter toward the mouths |
| **Mouth interiors** | `spawn_wound` `#3FE0C8`, emissive | The glow that reads through the water (the M2-RND-04 polyp light sits at its chest anchor) |
| Shed motes (VFX) | `glimmer_held` `#7FC6D9`, sinking | `polyp_mend`'s stream, owned by BattleBossVfx |

## The battle read

- **At 9 m, under water:** five small cyan rings around a dark lump, below the surface sheen. It reads as *alive and
  feeding* because the rings pulse in turn.
- **Idle:** the tubes sway as if in a current (a slow wave across the five), and the mouths open and close out of
  phase with each other, a ripple of light.
- **Facing:** the mouths lean outward and toward the model's **+Z**, like a half-open hand (the stage turns +Z to face
  the party). A lean toward the bell can't be built into the pose: polyps spawn in any enemy slot, so the bell may be
  on either side. The feeding read comes from the cast clip and BattleBossVfx's mote stream, which is aimed at the
  bell at play time (M2-CRE-07).

## Clips

| Clip | Read | Timing |
|---|---|---|
| `idle` (loop) | The current sway and the out-of-phase mouths | 2.8 s |
| `attack` (no slice skill) | The tubes draw in and lash forward together | 0.9 s |
| `cast` (`polyp_mend`) | **All five mouths open wide together and stretch toward the bell**, hold and pulse twice (the held motes stream out of them), then relax | 1.5 s, release at 0.6 s |
| `hit` | The mouths snap shut and the tubes pull down into the base | 0.4 s |
| `ko` | The tubes wilt and fold over into the base one after another; the mouths close last. It holds, a dark lump | 1.4 s |

## Notes for the model

- Tubes: tapered tubes along short curves, each with a lip ring and an inner emissive cap; base: a cracked dome of
  beveled black plates (shares the Drownbell's carapace treatment).
- Bones: root, base, three per tube (15), and a ring of six lip bones per mouth (30) that flare out or pinch shut
  for the open/close (the kit keys rotation and location only, so not a scale).
- Budget: ≤ 5k triangles: up to five can be on stage with the bell.
- Battle VFX anchors (fractions of 0.6 m): chest 0.36 m is the mouths' height, where the polyp light sits.

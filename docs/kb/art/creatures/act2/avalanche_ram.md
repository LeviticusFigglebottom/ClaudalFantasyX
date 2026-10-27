# The Avalanche Ram (`avalanche_ram`), Ch12 boss

**Where:** the terrace wall above Keth Pass, where drowned glimmer seeps out of a Lit Age terrace (act_outline Ch12:
"a woolback grown monstrous on drowned glimmer seeping from a Lit Age terrace wall").

## The idea

An Ullari woolback, a long-necked shaggy pack animal, that drank where the seep runs and grew. It is
still a woolback: the long neck, the shaggy coat, the soft muzzle. But it stands 3 m at the head and its fleece has
matted into plates of ice and wool, and where the fleece parts the seep's cold light shows through. The woolback
was someone's: a frayed herd-cord with a few knots is still tied round its neck.

The one exaggeration: **size, and the light under the fleece**. Nothing horned or demonic: the Ullari's own animal,
too big.

## Silhouette

- A long-necked, deep-chested animal 4 m long, the neck rising to 3 m, the head low when it charges.
- The fleece hangs in heavy frozen locks to the knees; ice beards it at the jaw and belly.
- The herd-cord at its neck, with its knots: the small, human detail.

## Palette

Fleece `sand_cloth` (undyed wool) gone grey (`overcast_slate` in the shadows), ice `salt_glass` on the locks; muzzle and legs
`laterite` darkened; seep light through the partings `spawn_wound` (the weak points), shedding `glimmer_held`; the
herd-cord `lacquer_red` faded.

## Battle read and clips

- **At battle distance:** a huge shaggy long-necked animal, pale, with cyan seams in its coat.
- `idle`: the neck sways, it chews, breath steams (VFX), the locks swing.
- `attack` (the charge): the head drops, a stamp, and it drives through; contact at 0.75 s of 1.6 s.
- `cast` (the bellow): the neck rises and it calls; snow sheds off the terrace wall (the field hazard, VFX).
- `hit`: it staggers back, the neck whips, ice cracks off; peak near 0.1 s.
- `ko`: it kneels, then lies down; the herd-cord is the last thing in frame. (Pillar 1: no gore, no thrash.)

Budget ≤ 16k triangles. Rig: a quadruped (spine 5, neck 5, head, jaw, four legs of 3), plus six fleece-lock chains
of 2 that lag the body.

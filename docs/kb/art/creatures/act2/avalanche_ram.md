# The Avalanche Ram (`avalanche_ram`), Ch12 boss

**Where:** the terrace wall above Keth Pass, where drowned glimmer seeps out of a Lit Age terrace (act_outline Ch12:
"a woolback grown monstrous on drowned glimmer seeping from a Lit Age terrace wall").

## The idea

An Ullari woolback, a long-necked shaggy pack animal, that drank where the seep runs and grew. It is
still a woolback: the long neck, the shaggy coat, the soft muzzle. But it stands 3 m at the head and its fleece has
matted into heavy wet plates, and where the fleece parts the seep's cold light shows through. The woolback
was someone's: a frayed herd-cord with a few knots is still tied round its neck.

The one exaggeration: **size, and the light under the fleece**. Nothing horned or demonic: the Ullari's own animal,
too big.

## Silhouette

- A long-necked, deep-chested animal 4 m long, the neck rising to 3 m, the head low when it charges.
- The fleece hangs in heavy sodden locks to the knees; the wool hangs wettest and darkest at the jaw and belly.
- The herd-cord at its neck, with its knots: the small, human detail.

## The head (M3-CRE-635)

The first PC render read the head as a duck's: a dark, flattened muzzle on a white face is a bill. The head is a
camelid's now (a llama's or an alpaca's proportions, not a copy of either):
- long and narrow (0.75 m, 0.29 m wide), deepest at the cheeks, the nose a little down;
- a soft, rounded muzzle in the coat's colour, `laterite` darkened **only at the nose and the lips** (slit nostrils,
  a split upper lip), a slim lower jaw with a wet beard underneath;
- eyes at the sides under a soft brow; long upright ears, their tips drooping a little out; the woolly cap kept;
- the neck slimmer under its fleece.

The dripping lock ends are few and uneven: one to three per lock chain (0.1-0.2 m past the strand's end, blunt and
rounded, soaked dark), two clumps under the belly and one under the jaw. Never a row of even spikes: that reads as
teeth.

**No ice (M4-A2P-059, ADR 0015, 2026-10-30).** The Ram's terrace is Ch12's set piece, so nothing on it is ice or frost:
the ice plates are wet mats of wool (`sand_cloth` and `overcast_slate` soaked dark, glossy by wetness), the icicles are
sodden lock ends, the ice beard is a wet one, and the `ice` material slot is gone. Snow on the pass is weather.

## Palette

Fleece `sand_cloth` (undyed wool) gone grey (`overcast_slate` in the shadows), the wet mats and lock ends soaked dark (no ice: M4-A2P-059); muzzle and legs
`laterite` darkened; seep light through the partings `spawn_wound` (the weak points), shedding `glimmer_held`; the
herd-cord `lacquer_red` faded.

## Battle read and clips

- **At battle distance:** a huge shaggy long-necked animal, pale, with cyan seams in its coat.
- `idle`: the neck sways, it chews, breath steams (VFX), the locks swing.
- `attack` (the charge): the head drops, a stamp, and it drives through; contact at 0.75 s of 1.6 s.
- `cast` (the bellow): the neck rises and it calls; snow sheds off the terrace wall (the field hazard, VFX).
- `hit`: it staggers back, the neck whips, water and snow shake off the locks (VFX puffs, no shards); peak near 0.1 s.
- `ko`: it kneels, then lies down; the herd-cord is the last thing in frame. (Pillar 1: no gore, no thrash.)

Budget ≤ 16k triangles. Rig: a quadruped (spine 5, neck 5, head, jaw, four legs of 3), plus six fleece-lock chains
of 2 that lag the body.

# The Wakefin (`wakefin`), Ch15 boss

**Where:** the open sea at night, aboard the drifting bridal barge with no lamp (act_outline Ch15: "an
Undertow-spawn that followed the first wake out of Ansedra's lagoon"). Fought in the dark, by sea-glow.

## The idea

Undertow-spawn drawn by the first wake in four hundred years. It is a long, black, sail-finned fish: a real
sailfish's shape, its dorsal fin a tall blade that cuts the water and stands 2.2 m above it. In the dark it is
mostly that fin, and the sea-glow it stirs runs along its flanks like a lit seam. When it rises to strike, the
body shows: wet lacquer black, the wounds along the spine.

The one exaggeration: **the fin**. A sailfish's dorsal sail, grown into a blade that can cut a barge's rail.

## Silhouette

- Most of the fight: the fin alone, a tall swept blade circling the barge, with a bright sea-glow wake.
- On the attack: the whole fish breaches alongside, 6 m long, the bill first.
- Nothing else in the game is a fin in the water: it reads at once, even in the dark.

## Palette

Body and fin `lacquer_black` to `abyss_navy`, clearcoat-wet; fin membrane `deep_teal_shadow` where the sea-glow
lights it from below; the wake and flank seam `sea_glow` (VFX and emission); wounds along the spine `spawn_wound`.
The scene has no other light (pillar 4: the timeline and the sea-glow still say who acts next).

## Battle read and clips

- **At battle distance:** a black blade with a glowing wake, circling.
- `idle`: it circles at the barge's edge (the fin cuts and turns), surfacing a little on each pass.
- `attack` (the cut): it breaches along the rail and the fin sweeps across the deck; contact at 0.8 s of 1.6 s.
  The telegraph is the sound and the sea-glow brightening along its path.
- `cast` (the dive): the fin goes under, the water goes dark, then a ring of sea-glow marks where it comes up.
- `hit`: the fin jerks and the body rolls; peak near 0.1 s.
- `ko`: it rolls belly-up and drifts away from the barge, the wake fading.

Budget ≤ 14k triangles. Rig: a spine chain of 10, the bill, the dorsal fin (3 bones, so it folds and flares),
pectorals, tail lobes.

## Review shots (M3-CRE-635)

- `creature_wakefin`: the battle read, the creature stage's opaque floor at the waterline, so the blade alone.
- `creature_wakefin_body`: the same stage with `show_floor = false`, seen from high on its flank (`flank_high`):
  the whole fish under its waterline, for reviewing the body, the seam and the wounds.

The eight spine wounds are open seams (M3-CRE-635): longer (0.24 to 0.54 m), three section rows wide, wandering
across the rows like a tear, their lips raised and faintly lit. They lie at the waterline, so in battle they show
when it breaches.

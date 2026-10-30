# Gallery ray (`gallery_ray`), Ch11

**Where:** Sunken Vey, the drowned galleries. **Kind:** reef beast. **Role:** a flier among the columns, out of
reach every other turn (it glides above the water line).

**The idea:** a pale cave ray that lives in the flooded corridors of the Vey, nearly the colour of the salt-glass
floors, gliding from pool to pool. The one exaggeration: **it glides through the air between pools**, wings spread,
like a flying fish.

**Silhouette:** a broad diamond 1.6 m across with a whip tail, flying at head height; wingtips curl as it turns.

**Palette:** back `salt_glass` to `cumulus_shadow`, a faint `sea_glow` along the wing margin (its own light, not
glimmer); belly `bone`; eyes on top `lacquer_black`; weak point `spawn_wound`, small: one closed mark on the camera-side spiracle's valve
(amended by M3-CRE-645, ADR 0151).

**Clips:** `idle` (a slow undulating glide in place); `attack` (it banks and sweeps a wing: contact 0.6 s of
1.2 s); `cast` (it settles into a pool and the water flares with its glow); `hit` (it flips and recovers; peak
near 0.1 s); `ko` (it slides into the water and sinks flat). Budget ≤ 5k triangles. Rig: body, wing chains of 3
a side, tail of 4.

**Polish for the battle read (M3-CRE-645, from the approved PC render fce2e82).** At review distance the first build
read as a flat pale sheet with two eyes. What changed, within the 5k budget (4,104 to 4,504 triangles; the bones, clip
names and contact times are unchanged):
- **Shape:** a raised midline keel from between the eyes to the tail root, with four low tubercles raked back over its
  rear; the pectoral muscle bulging either side of the body, with a shaded groove where it meets the body; each eye on
  a raised socket under a dark brow ridge that arches round its outer side; each spiracle in a raised rim.
- **Tail:** a whip, thick at the root and tapering fast to a thin lash, with dark bands toward the end and a dark,
  serrated barb lying along its top near the root, pointing back.
- **Surface:** the back mottles further toward `cumulus_shadow` and carries pale `salt_glass` freckles over the wings;
  the trailing edge and wingtips are a shade darker, so the outline holds against a pale floor.
- **Weak point:** one small closed mark (ADR 0151). The camera-side (-x) spiracle's valve is shut, with a small
  `spawn_wound` lens on it (the body slot's emission); the other spiracle is a plain dark opening. The two glowing
  open spiracles are gone.
- **Idle:** the wing wave's amplitude grows out along the wing (6, 10 and 20 degrees, each bone lagging the last), so
  the tips curl behind the wave as it glides.

## The Act II read fix (2026-10-30, ADR 0205)
At battle distance the pale disc vanished on pale salt-glass and was seen edge-on from head height. The back is now
dusky: `cumulus_shadow` mottled toward a `cumulus_shadow`/`lacquer_black` mix, with dark rosettes (6 per metre) and the
pale `salt_glass` freckles kept, so it is still a cave ray's dappled back but reads against a pale floor. The margin's
`sea_glow` is twice as bright (1.6), and the body's wet clearcoat is 0.25 (from 0.6), since its sheen at the grazing
battle angle washed the back white. It hovers at 0.95 m (from 1.4), below the battle camera, so the camera sees its back.

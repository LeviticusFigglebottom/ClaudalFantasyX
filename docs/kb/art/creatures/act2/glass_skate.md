# Glass skate (`glass_skate`), Ch16

**Where:** the Pale Rim, the white shallows. **Kind:** reef beast. **Role:** an ambusher, untargetable until it has
acted once (learn to wait).

**The idea:** a skate that buries itself in the white sand of the Rim's shallows, its back the colour of the water
over sand, so only its eyes and the line of its back show. The one exaggeration: **its back is nearly clear**, like
the water over it.

**Silhouette:** a broad rounded disc 1.4 m across with a thick tail, lying flat in shin-deep water; when it rises to
strike, the disc lifts and curls at the edges.

**Palette:** back `foam_white` to `cumulus_lit` with a faint `salt_glass` sheen, a rim of `sand_wet` round the margin
(M3-CRE-645); eyes `lacquer_black` on raised turrets; belly `bone`; weak point (the tail root) `spawn_wound`, small.

**Clips:** `idle` (buried: only the eyes and the breathing back move); `attack` (it erupts from the sand and slaps:
contact 0.5 s of 1.2 s); `cast` (it settles and stirs a cloud of white sand: the hide); `hit` (it buckles; peak
near 0.1 s); `ko` (it flattens and lies still). Budget ≤ 4k triangles. Rig: disc chains of 3 a side, tail of 4.

**Polish for the battle read (M3-CRE-645, from the approved PC render fce2e82).** The first build read as a flat pale
sheet. The nearly clear back stays (its role is ambush), but the silhouette now has edges. What changed, within the 4k
budget (2,624 to 3,638 triangles; the bones, clip names and contact times are unchanged):
- **Thornback rows:** ten dark-tipped thorns raked back down the midline, from behind the eyes to just short of the
  tail-root split; three on each shoulder; and six along the tail to the first dorsal fin. Each thorn grows from
  `sand_wet` toward `lacquer_black` at its tip.
- **A rim of darker pigment:** a band of `sand_wet` round the margin, broken a little by the ripple mottle, with the
  margin's edge strip the same. The back's rings sit closer together toward the margin, so the band holds its line.
- **The eyes on turrets:** the turrets stand taller (0.072 m over the back), darken toward the top, and each eye has a
  black lid ring round its base, so they read as eyes on stalks, not beads. The eye bones are unchanged.
- **The spiracles** are now small modelled dark openings behind the eyes. Painted onto the back's coarse centre, they
  had smeared grey.
- The weak point is unchanged: the one small split at the tail root, between dark lips (ADR 0151).

# Gull harrier (`gull_harrier`)

> *"A sea-bird grown too large on the leavings of storms. Too quick for heavy weapons."* (`LORE_GULL_HARRIER`)

**Battle role:** the striker. The fastest enemy in the slice (agility 24, evasion 30), weak to ice. `dive_rake`, a
physical strike, and it goes for the weakest when it is hurt. The read has to say **fast, airborne, hard to pin**.

## The idea

A gull that has fed for years on what storms leave on the beaches and grown to the size of an albatross. Haluna's
houses carry carved **lintel-gulls** that always face the sea (haluna.md). The harrier is the living answer to them:
the one gull that **faces the land**. It wears the storm's leavings: a trailing hank of torn net-twine and kelp
caught on one leg, and in its throat, still lodged, a **lamp-diver's bone hook** with a few centimetres of line.

The one exaggeration is **scale**: a real gull's shape at a size no gull reaches, with the heavier hooked beak a
scavenger that size would need.

## Silhouette

- **Long, narrow, crooked wings** in a shallow gull's "M" (bent at the wrist), 2.5 m from tip to tip. In the
  battle frame the wingspan is wider than any hero is tall: it is the widest thing in a normal fight.
- **A compact body** (0.45 m deep) and a short fanned tail with the trailing twine hanging under it.
- **A heavy hooked beak**, a raptor's hook on a gull's head.
- It **hovers** at 1.05 m (its stand-in spec), so its shadow on the ground under it is part of the read.

## Palette

| Part | Swatch | Notes |
|---|---|---|
| Back, upper wings | `cumulus_shadow` `#8FA7C4` | A grey-blue gull mantle |
| Head, underparts, under-wing | `foam_white` `#EEF6F4`, kept under the albedo ceiling | |
| Wing-tips (primaries) | `storm_slate` `#3E4A57`, ragged | The ragged dark tips are the read in flight |
| Beak, legs | `dusk_gold` `#F2A64A` muted toward `sand_cloth` `#C9B48E`; the beak's hook `tortoiseshell` `#6B3A1E` | |
| Eye | `lacquer_black` with a `sun_gold` ring | |
| Twine and kelp | `timber_weathered` `#7E6A55`, `foliage_shadow` `#1E4A3A` | |
| **Weak point** | `spawn_wound` `#3FE0C8` | The bone hook's wound in the throat, a small glow under the beak |

## The battle read

- **At 9 m:** a wide pale-and-grey "M" floating above the ground with dark tips. It reads at once as *a bird*, and
  the hover height separates it from the ground creatures.
- **Idle:** hovering: a slow, deep wingbeat (one beat a loop, with a glide between), the body rising 6 cm on the
  downstroke and settling, the head steady (birds stabilise the head), the twine swinging.
- **Facing:** side-on to the camera, head toward the party, so the wings are seen full.

## Clips

| Clip | Read | Timing |
|---|---|---|
| `idle` (loop) | One deep beat and a glide; the body bobs, the head holds still | 1.6 s |
| `attack` (`dive_rake`) | **Tell:** a climb (two quick beats, up 0.6 m). **Strike:** the wings fold half back, it drops forward and down, the talons swing forward and rake (0.2 s). **Recover:** wings open, it swings back up to its hover | 1.4 s, contact at 0.75 s |
| `cast` (no slice skill; for later) | It rears in the air, wings spread wide and held, the beak opens in a cry | 1.2 s |
| `hit` | It loses a wingbeat: one wing buckles, it drops 0.25 m and tips, then catches itself | 0.6 s |
| `ko` | The wings fold and it falls; at the ground it lands on its breast with **one wing left spread**, the head down. It holds | 1.4 s |

## Notes for the model

- Feathers are layered cards in the wings (primaries, secondaries, coverts as overlapping blades); the body is a
  lofted spindle. No alpha cards: blades with real geometry, so it renders on every tier and on lavapipe.
- Bones: body, neck, head, beak, two arm chains per wing (shoulder, elbow, wrist), tail, two legs, the twine.
- Budget: ≤ 9k triangles.
- Battle VFX anchors are measured from the **hover** (the stand-in's base): the spec height 0.45 m is the body.

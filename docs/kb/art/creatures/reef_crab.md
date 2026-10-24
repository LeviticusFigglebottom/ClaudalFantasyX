# Reef crab (`reef_crab`)

> *"Its shell is grown from the coral of drowned houses. Blades skid off it; only a heavy, patient blow will crack
> it."* (`LORE_REEF_CRAB`)

**Battle role:** the defender. High defense, slow (agility 8), weak to lightning, absorbs water. `pinch` (a physical
strike) and every third turn `brine_spit` (a ranged spit). Its read has to say **armoured, slow, heavy**.

## The idea

A shore crab that settles in the rubble of drowned houses and grows its shell **out of them**. Coral overgrows the
masonry it shelters in, and the crab's carapace takes that coral in, so its back is a low dome of coral-stone plates
with **white mortar lines** running between them, like a Haluna roof course seen from above (haluna.md: the
village's signature from above is red tile with white lime mortar). One plate on its back is a whole **red roof tile**
it never shed. It is the village, carried by something that does not know what a village was.

The one exaggeration is the **masonry carapace**. Everything else is a real crab: eight walking legs, two chelae,
stalked eyes, a flat face.

## Silhouette (side and three-quarter)

- **Wide and low**: a flattened dome about 1.0 m across the carapace, 0.62 m to the top of the shell, 1.4 m across
  the leg-tips. At battle distance it is a **low trapezoid** with the legs as a fringe under it.
- **Asymmetric chelae**: the crusher (its left, the camera side when it faces the party) is twice the size of the
  cutter, and its fixed finger is a slab of the same coral-stone. That asymmetry is its signature, and the crusher
  rising is its tell.
- **Stalked eyes** stand clear of the shell, the only small vertical forms on it.
- The legs are long and spidery compared with the heavy shell, so it stands up off the ground on them rather than
  squatting; the gap of light under the shell matters to the read.

## Palette (palette.json)

| Part | Swatch | Notes |
|---|---|---|
| Carapace plates | `coral_stone_weathered` `#B9AE98`, sun-bleached toward `coral_stone` `#E8DCC4` on top | Dry on top, so rough (0.8) |
| Plate seams | `mortar_white` `#E6E1D6` | A thin line network, the graphic signature |
| The roof tile | `roof_clay` `#B5523A` | One plate, high on the back; the only saturated note |
| Legs, chelae, underside | `laterite` `#A8573A` shading to `tortoiseshell` `#6B3A1E` at the joints | Wet below the waterline: albedo ×0.55 and gloss, as the kit's wet rule |
| Eyes | `lacquer_black` `#1D1916`, glossy | |
| **Weak point** | `spawn_wound` `#3FE0C8`, small | A crack in the coral at the back of the shell where it meets the abdomen; it shows only when the crab rears (cast) |

## The battle read

- **At 9 m:** a pale, low, wide shape with one big claw. Pale stone against the darker causeway reads in any of the
  slice's lights, and the roof-tile red is a single small accent.
- **Idle:** slow and planted. The body bobs 1 to 2 cm on the legs, the mouthparts work, the eyes swivel, the crusher
  opens and closes once per loop. A one-leg shuffle every loop says it is alive without making it nervous.
- **Facing:** it stands **side-on to the party** (crabs walk sideways), crusher forward.

## Clips

| Clip | Read | Timing |
|---|---|---|
| `idle` (loop) | Bob, eye swivel, the crusher opening and closing once | 2.4 s |
| `attack` (`pinch`) | **Tell:** the crusher lifts high and opens wide, the body tilts back on the rear legs (0.35 s). **Strike:** a scuttle forward and a snap down (0.15 s). **Recover:** back to its place | 1.2 s, contact at 0.5 s |
| `cast` (`brine_spit`) | It rears up on its back legs, the shell tilts 25° and shows the `spawn_wound` crack, the mouthparts flare, a short heave forward | 1.3 s, release at 0.7 s |
| `hit` | The shell drops and both chelae pull in to guard the face: a defender's flinch, not a stagger | 0.5 s |
| `ko` | The legs give way in pairs, the shell drops to the ground, it settles tilting a little to one side, and the legs curl in under it. It holds the last frame | 1.4 s |

## Notes for the model

- Plates: about 14 low polygonal slabs on the dome, each slightly lifted, beveled, the seams between them filled with
  the mortar colour (a vertex-colour band, not a texture).
- Budget: ≤ 8k triangles, one skinned mesh. The legs and chelae are rigid segments on bones (no blend needed).
- Battle VFX anchors (fractions of 0.62 m): feet 3 cm, chest 37 cm (the front of the shell), head 62 cm (the top
  of the shell, where damage numbers start).

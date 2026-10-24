# The Drownbell (`drownbell`), boss of the vertical slice (B10)

> *"A temple bell the sea took and kept. It still rings for the drowned, and the drowned still answer. Strike its rim
> quickly and the toll dies in its throat."* (`LORE_DROWNBELL`)

**Battle role:** the slice's two-phase boss (vertical_slice.md §5, docs/kb/design/battle_ctb.md "The Drownbell").
Phase 1, **the Toll**: `hood_slam`, and `toll_gather` every third turn, which charges the `toll` (it pushes the whole
party back on the timeline); three quick hits on its **rim** (`weak_point`, `PART_DROWNBELL_RIM`) break the charge.
Phase 2, **the Flood** (at 40% HP): the water rises, two spawn-polyps rise with it and mend the bell, and Ilun's
Floodnet clears the field. The read has to say **ancient, heavy, sacred and wrong**, and it has to make the rim
obvious as the thing to hit.

## The idea

The Shell Shrine once had a great bronze bell under its fan-shell roof. The sea took it in an old storm. The Undertow
kept it, and it grew a body. Now it is a bell-hood with a creature living in it: the bell is its shell, and under the
rim, where the clapper hung, there is a dark wet mass that walks it on six short black legs and **rings it from the
inside**. It rises when a verse is sung (N-07) because a bell answers a voice.

The one exaggeration is the bell **walking**. A bronze bell (the hood) and a hermit's body (the legs and the mass under
it) are both real things; together they are ours.

**Originality check.** Not a "living bell-tower" monster, not a jellyfish (no translucent bell or trailing veil),
not a hermit crab in a shell (the body is not a crab). The bell's decoration is our own Shell Shrine motif (haluna.md
§3.3: the overlapping stone **fan-shells**), cast in relief round the shoulder of the bell.

## Silhouette

- **A tall bell**: 2.4 m from the ground to the crown, a **rim 0.85 m in radius** (1.7 m across) whose lip sits at
  **0.29 m** (the `rim` anchor, 0.12 × 2.4 m), so in ankle-deep water the rim is just clear of the surface and in the
  Flood it goes under. The waist narrows to 0.62 m radius and the shoulder rounds into a **crown** with a broken
  hanging loop (the shackle it hung from, snapped).
- **The rim is a thick, flared lip**, heavier than a real bell's, ringed with a band of barnacle growth and three
  bright `spawn_wound` cracks: it is the brightest, most textured edge on the figure, so the eye goes to it before
  the tutorial line does.
- **Under the rim**, in the 0.29 m gap: the glossy black legs and the edge of the mass, glinting cyan where wounds
  are.
- **Wounds on the hood**: long vertical cracks in the bronze that bleed `spawn_wound` cyan light and shed
  `glimmer_held` motes (BattleBossVfx), seaward and down.
- A **bell-rope**, rotten and weed-hung, trails from the crown loop down one side into the water.

## Palette

| Part | Swatch | Notes |
|---|---|---|
| Bell bronze | `bronze_patina` `#5F8A78` over `brass` `#B08D57` | Verdigris in the hollows and on the shoulder, worn brass on the crown and the high points of the fan-shells (a vertex-colour cavity mask). Metallic, rough 0.45 |
| Wet lower bell | the bronze darkened ×0.55, gloss | The kit's wet rule; the wet line sits about 0.6 m up |
| Fan-shell relief | `brass` highlights | A band of 12 shells round the shoulder |
| Barnacles on the rim | `coral_stone_weathered` `#B9AE98` | |
| Legs, the mass | `lacquer_black` `#1D1916`, clearcoat | The Undertow-spawn carapace |
| **Wounds (hood cracks, rim cracks)** | `spawn_wound` `#3FE0C8`, emissive | The rim's three cracks are the weak point and glow brightest |
| Motes (VFX) | `glimmer_held` `#7FC6D9` | BattleBossVfx |
| Rope, weed | `timber_weathered` `#7E6A55`, `foliage_shadow` `#1E4A3A` | |

## The battle read

- **At 9 m:** a tall green-bronze bell standing in the water, a bright cyan-cracked rim at its foot. The tallest thing
  in the slice; it is twice Asha's height when it rears.
- **Idle:** the bell rocks very slightly (±1.5°) as if a swell moves it, and every loop the legs shift under the rim:
  it is standing, not placed. The rope swings.
- **The rim and the toll** (BattleBossVfx owns the light): `toll_gather`'s rim glow is an OmniLight at the rim anchor,
  so the model's rim must be where the anchor is. The `cast` clip carries the gather.

## Clips

| Clip | Phase | Read | Timing |
|---|---|---|---|
| `idle` (loop) | 1 | The swell rock and the leg shift | 3.2 s |
| `attack` (`hood_slam`) | both | **Tell:** it rears up on its legs, the bell lifting 0.5 m and tilting back. **Strike:** it drops forward and slams the rim down. **Recover:** it settles | 1.5 s, contact at 0.8 s |
| `cast` (`toll_gather`, `toll`, `flood_surge`, `undertow_surge`, `rouse_polyp`) | both | It draws back and **swings**: a long, heavy rock of the whole bell (the toll's swing; the BattleBossVfx shockwave and the `drownbell_toll` SFX land on the far end of the swing) | 1.8 s, the ring at 1.0 s |
| `hit` | both | A short shudder, the bell ringing in its own body (a fast, small vibration of the hood) | 0.5 s |
| `phase_change` | 1 → 2 | **The Flood:** the legs fold under it, and the bell **sinks 0.5 m** into the rising water and settles tilted 6° toward the sea. It holds there: the Flood idle is the held end of this clip plus the swell rock | 2.4 s |
| `ko` | 2 | It tips seaward, slowly, and lies on its side, rim toward the sea, the bell half under. Its motes slide seaward (`bell_release`). It holds | 2.6 s |

**The broken rim.** The rim is a separate piece of the bell mesh with its own bone, `rim`. The model ships a
`rim_broken` node (a section of the lip missing, the crack gone dark) beside the whole `rim`; the actor swaps them on
`charge_broken` and swaps them back when a new toll gathers (the toll charges again, the rim mends: the bell is the
Undertow's, and the Undertow mends). Hooks for that are in [`pipeline.md`](pipeline.md) "Boss hooks".

## Notes for the model

- The bell is a lathe profile (a polyline of about 30 points from crown to lip) swept around 48 segments, with the
  fan-shell band, the cracks and the barnacles added on top; the inside of the bell is modelled (it shows when it
  rears and tips).
- Bones: `root`, `bell` (the hood), `rim`, six legs × 2, `rope` × 3.
- Budget: ≤ 16k triangles.
- Battle VFX anchors (fractions of 2.4 m): feet 0.12 m, **rim 0.29 m**, chest 1.44 m, **hood 2.04 m**, head 2.4 m.

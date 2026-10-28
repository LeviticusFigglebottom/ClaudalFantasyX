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
`RimBroken` node (about 105° of the lip missing on the camera side, the crack gone dark, the legs and the black mass showing through) beside the whole `Rim`; the actor swaps them on
`charge_broken` and swaps them back when a new toll gathers (the toll charges again, the rim mends: the bell is the
Undertow's, and the Undertow mends). Hooks for that are in [`pipeline.md`](pipeline.md) "Boss hooks".

## Notes for the model

- The bell is a lathe profile (a polyline of about 30 points from crown to lip) swept around 48 segments, with the
  fan-shell band, the cracks and the barnacles added on top; the inside of the bell is modelled (it shows when it
  rears and tips).
- Bones: `root`, `bell` (the hood), `rim`, `mass`, six legs × 2, `rope` × 3 (19).
- Budget: ≤ 20k triangles in the file (the boss's allowance; the hero battle models are 27–30k). As built: 19.4k, of which the two rim variants are about 3.4k each and only one draws, so about 16k on screen.
- Battle VFX anchors (fractions of 2.4 m): feet 0.12 m, **rim 0.29 m**, chest 1.44 m, **hood 2.04 m**, head 2.4 m.

## Final pass (M3-CRB-003)

ADR 0041 (Act I at final quality). The model now builds the sheet's forms instead of primitives
(`assets_src/creatures/drownbell/build_drownbell.py`); the silhouette, the rim (lip at 0.29 m, radius 0.85 m) and
the anchor heights are unchanged.

- **The bell is cast work.** It has double beads at the sound bow (0.60 / 0.645 m) and the shoulder (1.95 / 1.985 m),
  plus a single bead at the waist. Between two beads runs a band of raised inscription in an invented script: glyphs
  of three to six strokes on a 3×5 node grid, a lozenge between every seventh, and no real script. Above it, a frieze
  of twelve running waves curls under eleven cast **fan-shells**, each a domed wedge from a hinge with five raised
  ribs and a scalloped edge. The twelfth slot, on the face, holds the **shrine sigil**, a roundel with a notched
  border: a fan of five rays rising from a pearl over two arcs of the swell. All of these are cast pieces conforming
  to the surface, raised 4–13 mm with sunk edges.
- **Worn and doomed.** Brass shows on every high point. Verdigris sits in the hollows with a pale bloom over brown
  run-streaks, and a salt tide line rings it at 0.83 m with weed and wet below. The bell carries eleven dents and fine
  pitting (in the material's detail bump). A petalled **strike seat** on the waist (azimuth −42°) is worn bright and
  scored where the shrine's beam struck it. An **old mend** (azimuth 50°) is a darker, browner riveted plate with a
  chipped corner, over a closed, unlit crack that runs out from under it.
- **The wounds** (ADR 0151) are open seams. Torn bronze lips peel outward, bright at the tear, over dark walls, with
  the `spawn_wound` light along the floor. They branch upward from the rim. The biggest is at azimuth 8°, with a chip
  out of the lip under it. Four more run at −66°, 100°, 148° and −150°, and three short ones sit on the rim only. The
  weak point stays the rim: its seams are the widest and brightest, on a material with more emission, and they spill
  light on the crusted lip.
- **Facing the cameras.** The battle and boss-intro cameras see the model from about azimuth −20° (measured from the
  old shots), the review stage from +35°, and the party stands at +90°. The face therefore carries the biggest wound,
  the sigil above it and the strike seat. The rope hangs down the left flank at −95°, framing the silhouette.
- **The crown** is a cast plate with a moulded edge carrying the central hanging loop. Four canons stand round it;
  the one toward the party is snapped short and bright at the break. A stub of rusted chain (three links and a
  broken-open fourth) hangs off the loop.
- **The rope** is three-strand hemp. Its lay twists down it, bleached over the crown and dark and slimed below the
  tide line. It has a knot round its canon, a popped strand and weed clinging along its lower run. Its end lies on the
  ground and unravels into three strands and loose fibres.
- **The rim** is darker, wetter bronze crusted with barnacle colonies (three to five packed together, one big in
  each) and weed at the lip. `RimBroken` loses 105° of the lip round the biggest wound (azimuth −44° to 61°). Its
  fractures are jagged faces of raw bright bronze, and its light is out (the remaining seams glow at 0.3).
- **The mass** is wet black flesh, folded underneath, plated where the legs leave it. Wound slits glow between the
  folds, and a puckered maw at the underside, ringed by curved plates, glows where the flood pours out.
- **The legs** are jointed Undertow-spawn carapace. Each femur is two telescoping, keeled plates that dip under the
  lip (clear of it by about 3 cm) and rise to a spurred knee outside the rim. A glossy deep-teal joint membrane
  follows, then a cuffed tibia with a spine, another membrane, and a hooked tarsus curling in to grip the ground. The
  femurs carry barnacles where they leave the mouth. The feet now stand at a radius of 1.1 m (was 0.92 m).
- **Materials:** `bronze` `detail_scale` 18 → 26, `detail_albedo` 0.16 → 0.2, `detail_bump` 0.3 → 0.6 (the pitting).
  The slots are unchanged (`bronze`, `rim`, `carapace`, `rope`).

**Clips:** every first-pass clip is kept by name. `idle`, `attack` (contact 0.8 s; it now rears 0.42 m on legs
extended to the ground), `cast` (the toll, contact 1.0 s unchanged; the rope's trailing end drags), `hit`,
`phase_change` and `idle_flood` (the legs let go and splay; the stage's sink and tilt in creatures.json are
unchanged), and `ko`. The kit adds `hit_b` and `idle_b`. Two clips are new:

- `ready`, a 2.0 s loop: lifted 5 cm on braced legs, leaning 2.5° toward its foe, the rim shivering and the rope
  swinging quicker.
- `intro`, 2.8 s: it starts low and sprawled on splayed legs, tilted, with the mass drawn up. The legs unfold and
  plant, it pushes up to full height (1.3 s), draws back and tolls once, softly (the ring at about 2.08 s; the
  strike-ring VFX is battle-presentation's), and settles on idle's first frame.

No creatures.json change. Every baked frame of every clip stays on the floor (`common/grounding.py`: the legs, the
rope's end and, for `ko` and `intro`, the root).

**VFX anchors** (unweighted bones):
- `vfx_wound`: in the rim's biggest wound (azimuth 8°, 0.40 m), under `rim`.
- `vfx_core`: the bell's centre (1.15 m), under `bell`.
- `vfx_phase`: the mouth at the lip's height (0.29 m), pointing down where the flood pours, under `bell`.

**Budget:** 23,811 triangles (≤ 24k), with about 22.3k drawn at once since only one rim variant shows:

| Part | Triangles |
|---|---|
| Bell bands and inside | 8.0k |
| Inscription | 0.6k |
| Waves | 0.6k |
| Sigil | 0.8k |
| Fan-shells | 1.2k |
| Strike seat | 0.4k |
| Mend | 0.5k |
| Hood wounds | 1.5k |
| Crown | 1.1k |
| Rope | 1.4k |
| Mass | 0.9k |
| Legs | 2.8k |
| `Rim` | 2.4k |
| `RimBroken` | 1.5k |

22 bones; the GLB is 2.6 MB.

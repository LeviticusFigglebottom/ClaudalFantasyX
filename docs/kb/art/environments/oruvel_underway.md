# Oruvel Underway: Design Notes

Owner: Environment Artist (M3-ENV-05). Lighting and the underwater look: Rendering. Gameplay placement (tether
points, bell-room rest points, encounters, collision): m2-slice (swap-in note in the M3-ENV-05 task file).
Story: [act outline Ch1 "Lamp-Diver"](../../story/beats/act_outline.md), the Ch1 beat sheet
[act1_ch01.md](../../story/beats/act1_ch01.md) C1-02 to C1-07 and its §9 Environment request 2, [bible
§3 Oruvel](../../story/bible.md) ("a raft-town of lashed hulls moored above a drowned Lit Age district of
coral-crusted concrete towers; lamp-divers go down with oil lanterns to salvage pre-Edict metal and glass"),
decisions_log N-02 (Rhen's lantern burns oil). Grade: [color script `ch01`](../color_script.md) and its 2026-10-24
underwater notes (M2-ART-02). Look: [tech/underwater.md](../../tech/underwater.md) after M2-RND-09. Colours:
[palette.json](../palette.json). Zone: `game/levels/ch01/oruvel_underway/`. Kit:
`assets_src/environments/kits/oruvel_underway/`. Preview: `game/levels/_tests/oruvel_underway_kit/`.

**The feeling in one line:** a quiet, competent morning alone in a drowned tower: teal water full of slanting
light, white Lit Age ceramic going green, a reef growing on the roofs of the dead city and half of it
bleached, and one small warm flame that is Rhen's.

**Influences** (references.md, in words): tropical reef slopes at 20–30 m in very clear water, where the light is
blue-green, colour drains out of everything beyond arm's length, and a torch brings back the reds of the coral
only inside its own pool; drowned concrete structures colonised by reef (piers, wrecks, flooded buildings), where
straight cast edges soften under crust and every horizontal surface grows a garden; seagrass meadows on sand
whose blades lean together in a current; partly bleached coral, bone-white branches standing among living ones.
**Our originals:** the Lit Age lamp-columns (a fluted ceramic shaft, a ring capital and an empty bound-light
housing, its glass long gone), the tide-gauge wheel, the divers' knotted cord across the stair (one knot per diver
who turned back, "a hundred knots, some new"), the tower's breathing current shaft, the bell-rooms with their
calcite tide-ring, and the dead ship whose black ribs lie on the terrace.

**Act I rule.** This is the first playable frame of the game and it is Act I: the sorrow is beauty with an
ending, not murk. The water is luminous teal, never grey-green and never navy at these depths; the reef is
bright where the lantern reaches it; the dark is reserved for the stairwell going down, the canyon off the
terrace's edge, and the doorways. The lantern is the only warm thing in every frame, and nothing else in the
zone glows: **no bound light anywhere** (every housing is empty and dark, beat sheet C1-05), and the only
glimmer is the held cyan motes sinking down the stairwell (U06).

---

## 0. Layout, Orientation, and Lighting

**Geography (world north = −Z, +X east; heights in metres, the sea surface at y 0).** Oruvel's hulls are
moored over a drowned Lit Age block: a **podium** (a broad low building) whose roof, silted into a sea
floor, lies at **−22.4 m**, with a **tower** rising from it to a broken crown **6 m** under the hulls. The
streets round the podium are **−48 m** down: a dark canyon that the divers never enter.

```
                       N (-Z)            hull keels at -1 m (the raft-town above)
                         |
     apron ...... terrace (sea floor, silt datum -22.6; 12 m cells to ±66 m) ......
     .    +--------------+---------------------------------+  seagrass meadow, coral heads,
     .    | gauge room   |=| lamp gallery (F9, 6.4 m tall)  |  Lit Age fragments, the dead
     .    | (wheel,shaft)|  two rows of dead lamp-columns   BREACH ==> ship's ribs (the landmark)
     .    |--------------|                                  |  (the east wall's south bay fell
     .    | stair lip  <== cord                             |   outward; sand spills in)
     .    +--------------+---------------------------------+
     .      TOWER 36 x 12 m (6 x 2 bays), x -18..18, z -6..6
     ~~~~~~~ terrace edge (z ~62): the broken roof lip, then the canyon (-48 m, dark) ~~~~~~~
                         S (+Z)
```

- **Floors are counted the Lit Age way, from the street up** (F1 at −48 m, 3.2 m a storey). The podium holds F1
  to F8. **F9 is the tower's lobby at the terrace's height (−22.4 m), a double-height lamp gallery** (6.4 m to the
  F11 slab), and **F14 is the crown floor at −6.4 m**, its walls broken off between −3.5 and −5 m. So "nobody goes
  below the ninth floor" is literal: the gallery is the deepest a diver walks, and the stair at its west end goes
  down into the podium, where the low lights sink.
- **The route** (beat sheet §3, the fiction of weighted divers on tether points): the drop into the crown (F14,
  U01) → bell-room 1 under the F14 slab on F13 (U03) → tether drops through two **collapsed floors** (F12, F11) →
  the **lamp gallery** on F9, running 30 m east-west (U04, U05) → the **stair lip** at the gallery's west end
  (U06) → the **gauge room** off the stair landing, in the tower's north-west corner (U07) → up the **current
  shaft** in the west core to the crown (U08) → surfacing (U09).
- **The breach.** The south bay of the tower's east wall at F9–F10 has fallen outward onto the terrace (a 6 × 6.4 m
  hole, the slab of F11 its lintel), so the gallery opens to the sea floor and the morning light comes in from the
  east, behind the player: the gallery reads from bright
  (east, the breach) to dark (west, the stair). Sand has spilled in through it as a tongue across the gallery
  floor.
- **The terrace** (the sea floor of the dive): silt and shell sand over the podium roof, 132 × 132 m round the
  tower (12 m cells, none under the tower, so the ground stops at its walls), with a seagrass meadow on its open east side, coral heads grown on rubble and on the fallen wall, Lit
  Age fragments, divers' leavings, and **the dead ship**: a coastal trader that sank onto the roof generations
  ago, now a keel and two rows of black ribs arching out of the sand, crusted and grown over. **Its rib-timbers are
  the kind Hullgnaw wears** (act1_ch01 §9 Creatures: "a dead ship's black rib-timbers like a corset"), so the
  player has walked past the ribs before the boss rises through a deck in the town: the environment plants it,
  nothing says it (Narrative to confirm whether the spawn grew here).
- **The terrace edge** on the south side is the podium's broken roof lip: slab layers, rebar, and then nothing,
  the canyon falling away into deep teal-black. It is the Underway's one read of "the deep", outside.

**Tide and time.** The dive is **08:40–09:55** (beat sheet C1-02 to C1-07), earlier than the colour script's
10:30 raft-town frame, so the sun is lower and in the east and the shafts slant. Water is the lagoon at mid tide
(y 0); the surface waves are the lagoon set (`lagoon_waves.tres`).

**GI recommendation:** SDFGI off on every tier (the shafts and the lantern carry it; SDFGI on lavapipe loses
the fill, the Haluna README's finding). Sky ambient + SSAO, scaled down inside the tower by area (below).

| Sub-frame | Use | Time | Sun elev / az | Key | Ambient | Underwater rig | Exposure / grade |
|---|---|---|---|---|---|---|---|
| `ch01_underway` (open) | The crown (U01), the terrace (U12, U13), the breach | 08:45 | 42° / 105° | `#FFEFE1` (the `ch01` key), energy 3.0 | sky, 0.65 | the Act I look (scatter and transmit `lagoon_teal`, deep `deep_teal_shadow`), light level ≈ 1.0 | exposure 0.65, saturation ×1.12 (the `ch01` frame); `lut_ch01_raft`'s intent (+8% in cyans and oranges) |
| `ch01_underway_int` | The gallery (U04, U05), bell-room (U03), the collapsed floors | — | (same sun; the walls shadow it) | — | sky, 0.22 | in-scatter light level × 0.33 | as open |
| `ch01_underway_deep` | The stair lip (U06), the gauge room (U07), the foot of the shaft | — | — | — | sky, 0.14 | in-scatter light level × 0.2 | as open |

**Downwelling.** The rig absorbs light along the camera's ray only, not on the light's way down, so a floor at 22 m
was lit by the full sun (the first preview captures read as a sunlit beach). The sub-frames therefore tint the key
and the ambient (the `ch01` fill `#8FC3E0`) by the rig's own transmittance over the subject's depth, exp(−σ·d) with
σ from `lagoon_teal` over 40 m: at the terrace (21 m) the key is teal and about half as bright, red nearly gone, so the
lantern's pool is the only place the reef's warm colours come back. **Request to Rendering (M3-RND-24): a downwelling
term on the rig** (the directional light attenuated by the water above each shaded point), which would also brighten the tower's
upper floors against its foot; the preview's per-shot tint is a stand-in.

**Why the interior sub-frames.** The rig's in-scatter is lit by the scene's sun with no occlusion, so inside the
tower the water would glow as brightly as the open sea and drown the lantern pool. The interior and deep frames
scale the in-scatter to the light that reaches the room. The preview does it by area (one value per shot);
**the zone needs a per-area override on the rig (request to Rendering, M3-RND-24: an `UnderwaterRig` light-level scale that a
trigger volume or the zone script can set and blend over ~1 s)**.

**Rhen's lantern** is the rig's (`oil_lamp` `#FFB16E`, energy 9, range 9 m, the post's warm halo, M2-RND-09). It
is the only warm light and the only practical in the zone: every Lit Age housing is dead. It hangs at Rhen's
shoulder (≈1.5 m); in the preview it is placed per shot beside the lens.

**Value structure.** Open frames: about 60% upper-mid teal (lit water, the Snell window, sunlit sand and ceramic),
the darks in the tower's openings, the ribs and the canyon. Interior frames invert it: the lantern pool and the
breach's light are the two bright shapes, the rest mid-to-low teal, the stair void the darkest value. The lantern's
warm pool is always the focal value inside the tower; outside, the tower's sunlit flank and the bright surface are.

---

## 1. Mood by Moment

1. **The drop (U01).** Rhen hangs on his tether in the crown. Above him the surface is a bright sheet broken by the
   dark lattice of Oruvel's hulls, and shafts slant down past the broken walls. The ceramic of the crown's last
   cladding catches the light. Calm, competent, alone.
2. **The bell-room (U03).** A sealed room on F13 whose ceiling holds trapped air: a still mirror above, the walls
   above the air line pale and dry, a white calcite tide-ring at the line. The only place he talks aloud.
3. **The collapsed floors.** Slabs broken and hanging on their rebar, holes the tether drops through, coral
   gardens on every horizontal edge, the light coming down through the holes from the floors above.
4. **The lamp gallery (U04, U05).** Two rows of dead lamp-columns, white ceramic gone green, receding west into the
   dark; the breach behind floods the floor with morning teal; the lantern's warm pool brings the colour back to
   the nearest column and the coral on its base. Coral curtains hang across the side bays (one hides the old diver's
   tin).
5. **The low lights (U06).** The gallery ends at a stairwell going down into the podium. A divers' knotted cord is
   tied across it. Held motes drift sideways and down, sinking past the lantern's reach. The water here is dim and
   still. Rhen does not go near them.
6. **The gauge room (U07).** A sealed room off the landing: the tide-gauge wheel, a two-metre ring of brass and
   patina on its ceramic housing, the only bright metal in the zone, lit gold by the lantern.
7. **The terrace (U12, U13).** Seen through the breach and walked briefly: a seagrass meadow leaning in the current,
   coral heads half bleached, the dead ship's ribs, white fragments of the Lit Age in the sand, and the tower rising
   pale out of it into the bright water. The most beautiful frame of the dive, and the saddest.
8. **The shaft (U08).** The tower breathes with the tide up its west core; weed streams upward; Rhen rides it,
   humming, toward the light.

---

## 2. Kit Pieces (origin at the base, +Y up; module 6 m bays, 3.2 m storeys; ground cells 24 m)

| Kit | Pieces | Key dimensions and parameters |
|---|---|---|
| **Sea floor** | `seafloor_patch_a`, `seafloor_patch_b` (12 × 12 m cells, two bays, so they stop at the tower's walls), `seafloor_edge` (12 m cell with the podium's broken lip), `seafloor_far` (apron 492 m with a 132 m hole; the canyon floor south of the terrace) | Silt and shell sand over the roof: current ripples (texture), low relief ±0.3 m, a half-buried slab end; cell edges at y 0 so a and b tile in any yaw. Edge cell: the lip wanders along local z ≈ +2 m (periodic, so edge cells join), then a broken face of two slab layers and rebar falling 14 m. |
| **Sand tongue** | `sand_drift` | A 9 × 6 m tongue of sand spilling through a breach: 0.9 m deep at its root, feathering to 0 along a lobed edge. |
| **Tower shell** | `tower_bay`, `tower_bay_solid`, `tower_bay_broken`, `tower_pier` | Bay: 6.0 m × 3.2 m × 0.35 m cast wall with a 2.4 × 1.7 m window (sill 0.8 m); white ceramic cladding in two bands across the outer face (the sill band and the spandrel band, 0.6 m panels, about half fallen in runs), so each storey reads as a pale ribbon over bare cast piers. The inner face, the gallery's (M3-ENV-705), has a cast skirting, a stepped cornice, a fillet down each pier's edge, the window's reveal framed, and sponge and coral crust low on the wall. Solid: a blind bay (recessed panel). Broken: the window's head and the top broken away along a falling line, rebar stubs. Pier: a 0.7 m square corner column, 3.2 m. |
| **Floors** | `floor_slab`, `floor_slab_broken` | Slab: 6 × 6 × 0.3 m with a coffered underside (two ribs each way). Broken: the same slab cracked through and hanging on its rebar at 24°, a 2.5 m hole (a tether drop point), coral on the high edge. |
| **Rooms** | `bell_room`, `current_shaft`, `stair_flight` | Bell-room: a 6 × 6 × 3.2 m sealed room with a 1.0 m door, walls above the air line (0.7 m under the ceiling) dry and pale, a calcite tide-ring at the line, calcite drips. Shaft: one storey (3.2 m) of a 2.6 m cast duct (14 staves, two slotted vents) with brass ring bands, a grating and weed streaming upward; stacks. Stair: one straight flight 3.2 m down over 6.0 m with a half landing, side walls, a broken ceramic balustrade with one length of brass rail. |
| **Lit Age** | `lamp_column`, `lamp_column_fallen`, `lit_fragments` | Column: 5.4 m, a fluted ceramic shaft (0.32 m) on a stepped base, a ring capital and an open lamp housing (brass cage, two glass shards, the core dark); encrusted low, algae film high. Fallen: the same broken in two on the sand. Fragments: a cluster of cladding panels, a conduit length, a cracked housing and ceramic shards, 4 × 3 m. |
| **Salvage** | `gauge_wheel`, `gauge_wheel_cut`, `hinge_door`, `pipe_run` | Gauge wheel: a 2.0 m brass tide-gauge wheel (96 teeth, six spokes) between ceramic cheeks on a plinth with a dial; the cut state loses its rim (spoke stubs, cut faces bright). Door: a 6 m wall bay with a 1.0 m door, the ceramic door hanging open on three brass hinges (the top one already cut). Pipe run: 6 m of twin brass pipes on brackets with two valves and one cut gap. |
| **Growth** | `coral_head_a`, `coral_head_b`, `seagrass_patch`, `coral_curtain` | Coral head: a 1.6–2.4 m bommie on rubble: a lobed brain-coral boulder, a dozen branching thickets (a third to a half bleached bone-white), plate coral, four sea fans and tube sponges. Seagrass: a 3 × 3 m patch of ~240 strap blades 0.4–1.1 m, leaning with the current, tips browned. Curtain: a 3.0 × 2.8 m hanging mass of soft coral, fans and weed across an opening (the shutter reveal). |
| **Story props** | `divers_cord`, `tether_line`, `wreck_ribs` | Cord: 2.4 m of hemp across a stair, ~100 knots, a quarter of them new and pale, frayed tails. Tether: 6 m of line from the surface with a lead weight and a brass clip. Ribs: the dead ship, 15 m: a keel, 13 pairs of black frames arching 2.6 m out of the sand, a few planks, the stem post, coral grown on the frames. |
| **Above** | `hull_keels` | Oruvel from below: three lashed hulls' bottoms (11 m, 8 m, 7 m) with weed beards, crossbeams and a dive mooring line: the dark lattice in U01. A stand-in until the raft-town kit (act1_ch01 §9 item 1) ships its own. |
| **Preview only** | `diver_lantern` | A 0.3 m brass oil lantern with a lit flame, for the preview frames. Rhen's lantern is Character Art's; this is a stand-in. |

**Budgets (triangles, LOD0 / LOD1):** ground cells 2,000 / 100, edge cell 4,000 / 300, apron 3,500 / 800, tower bays and slabs 3,500 /
200, rooms 8,000 / 600, lamp columns 4,000 / 300, gauge wheel 9,000 / 600, coral heads 9,000 / 700, seagrass
5,000 / 400, wreck ribs 12,000 / 900, small props ≤ 3,000 / 250. LOD1 begins at 70 m (the Haluna table); every
piece is a chain (`<piece>`, `<piece>-lod1`), so one LOD draws at every distance (vegetation.md "One LOD at
every distance"). Underwater nothing is seen beyond ~60 m, so LOD1 is almost never drawn in play; it is kept for the
raft-town's top-down views through clear water.

## 3. Materials (palette.json names)

| Slot | Shader | Look |
|---|---|---|
| `ou_concrete` | weathering (Haluna `coral_concrete`) | Lit Age coral-concrete drowned four hundred years: grey-green (`coral_stone_weathered` greyed), an algae film over everything (`#4F5A3A`, 35–70%), coralline crust in the barnacle layer (a dusky rose from `roof_clay` greyed, `#A98078`), erosion on every edge |
| `ou_concrete_dry` | weathering | the bell-room above the air line: paler, no growth, calcite in the hollows |
| `ou_calcite` | weathering | the bell-room tide-ring: `bone` white crust |
| `ou_ceramic` | weathering (Haluna `coral_concrete`, painted) | white Lit Age ceramic (`lit_ceramic`) "gone green with coral": a thinner algae film, crust in the joints, the paint still pale where the lantern lands |
| `ou_silt` | weathering (new `silt` texture, triplanar) | silt and shell sand: pale warm grey (`sand_wet` × `coral_stone_weathered`, about `#9A927F` dry), current ripples, shell hash, burrows |
| `ou_rebar`, `ou_iron` | standard | rust (`#5A3422`), dark iron (`#4A3A30`) |
| `ou_brass`, `ou_patina` | standard | `brass` (metallic 0.85, roughness 0.45: the one bright metal) and `bronze_patina` verdigris, assigned per triangle from a seeded patina field (crevices and undersides first) |
| `ou_glass_dark` | standard | the empty housings' last shards: dark, slightly glossy, no light (`#2C3639`) |
| `ou_timber_tar` | weathering (Haluna `timber`) | the dead ship's frames: black-brown (`#3A3029` face), crust and algae |
| `ou_hull` | weathering (Haluna `timber`) | the raft-town's hull bottoms: dark tarred timber with weed and crust |
| `ou_coral_bone`, `ou_coral_ochre`, `ou_coral_rose`, `ou_coral_teal`, `ou_sponge` | weathering (new `coral` texture, painted) | the reef: bleached `bone` (`#D9CDB4`), ochre (`dusk_gold` greyed, `#B08A55`), dusky rose (`roof_clay` greyed, `#A8705F`), soft teal fans (`faded_teal_cloth`, `#5E9A96`), sponge (`laterite` greyed, `#8C5E45`). Underwater the reds go first: these read grey-teal beyond 3 m and come back only in the lantern's pool, which is the point |
| `ou_seagrass`, `ou_seagrass_tip` | standard, two-sided | blades `palm_green` greyed toward olive (`#4E6A3A`), browned tips (`#7A6E45`) |
| `ou_weed` | standard, two-sided | streamer weed in the shaft and on the hulls: olive (`#525A36`) |
| `ou_cord_old`, `ou_cord_new` | weathering (Haluna `woven_panel`) | the cord: grey-brown hemp gone soft (`#7E705A`), and the new knots, pale (`sand_cloth`) |
| `ou_lead` | standard | the tether weight (`#55585A`) |
| `ou_flame` | standard, emissive | the preview lantern's flame: `oil_lamp` at emission 3.0 |

Weathering channels follow haluna.md §4 (**R moss, G salt, B wet, A erosion**). Everything is below the water, so the
shader's wet layer is always on: the materials set `wet_darken` near 1 (the post already absorbs) and keep
roughness moderate. Moss and salt layers are off underwater (except the bell-room's dry walls); **growth is the algae
and barnacle layers over the whole depth range** (`algae_band_m` −60 to −1.5 m), plus the coral and seagrass pieces.

---

## 4. Composed Shots (vFOV = 2·atan(12 / mm); heights above the local floor)

Shot ids follow act1_ch01.md §7 (U01–U11 are the beat sheet's; U12–U14 are this sheet's). **◆** marks the preview
shots built in `oruvel_underway_kit/`.

| # | Lens (vFOV) | Height | Framing | What the shot is about |
|---|---|---|---|---|
| U01 ◆ | 24 mm (53.1°) | 1.0 m above the crown floor, looking up 55° | The broken crown walls frame the bright surface; the hulls a dark lattice across it; shafts slant down; the tether runs up into the light. | The opening frame of the playable game: alone, and good at this. |
| U02 | rail | — | The default rail down through the crown. (Cinematics.) | |
| U03 | 35 mm (37.8°) | at the air line | The bell-room from the water's surface level: the mirror ceiling, the tide-ring. (Cinematics; needs a second WaterSurface for the air pocket, m2-slice and Rendering.) | |
| U04 ◆ | 18 mm (67.4°) | 1.6 m, on F9 at the breach end, looking west | Two rows of dead lamp-columns receding into the dark, the stair lip a black mouth at the far end; morning teal spills across the sand tongue from behind; the lantern's warm pool on the nearest column. | Beauty in a dead place. Light draws things to it. |
| U05 | 35 mm | 1.5 m | The coral-curtain reveal with the shutter open. (Gameplay.) | |
| U06 ◆ | 50 mm (27.0°) | 1.5 m at the stair lip, looking down the flight | The knotted cord across the frame, held motes sinking below it into the dark; the lantern's reach ending on the third step. Held motes ≤ 5% of the frame. | The first held light. A rule he was taught and doesn't understand. |
| U07 ◆ | 28 mm (46.4°) | 1.4 m in the gauge room | The wheel as a ring of brass in the lantern light, the pipe run and the hinged door behind; dark beyond the pool. | The job. |
| U08 | 24 mm | in the shaft, looking up | The shaft from inside, weed streaming up toward the light at the crown. (Cinematics.) | The ride up, humming. |
| U09–U11 | — | — | Surfacing (U09), going under (U10, U11) belong to the raft-town sheet. | |
| U12 ◆ | 24 mm (53.1°) | 1.5 m on the terrace, 26 m east of the breach, looking west | The tower rising pale out of the meadow into the bright water, the breach a dark mouth at its foot; the dead ship's ribs in the left third; a coral head and seagrass in the near ground; the lantern's pool on the sand at the lower right. | The most beautiful frame of the dive, and doomed. |
| U13 ◆ | 35 mm (37.8°) | 0.9 m, low among the ribs | The dead ship's ribs arching against the bright water, crusted, a coral head grown in the hold, the tower faint behind. | Plants Hullgnaw's corset without a word. |
| U14 ◆ | 35 mm (37.8°) | 2.5 m, kit row | Review only: the props and growth pieces in a row on the sand, open light. | The kit, side by side. |

**Registered baselines (the repo's binary budget: at most two):** U04 (`ou_u04_lamp_gallery`) and U12 (`ou_u12_terrace`): the inside and the outside of the kit, the lantern's warm pool against the teal in both.

## 5. Review Checklist

- [ ] The lantern is the only warm value in every frame, and it reads in the `oil_lamp` family (h 45–95°), never green.
- [ ] No bound light: no housing glows, nothing in the zone emits but the lantern (and the preview's flame).
- [ ] Act I water: hue 195–215° in the open, the darks teal, not navy or grey (the M2-RND-09 bands).
- [ ] Held motes (U06) sink, ≤ 5% of the frame, and are the only cyan points.
- [ ] Growth reads as growth (crust, film, gardens on the horizontals), not as dirt.
- [ ] The breach-to-stair gradient (bright east, dark west) reads in U04; the stair void is the darkest value.

## 6. The Preview (M3-ENV-05)

`game/levels/_tests/oruvel_underway_kit/oruvel_underway_preview.tscn` composes the kit for the ◆ shots (its README
lists the files), on the existing `UnderwaterRig`. Read of the final captures (lavapipe, 960 × 540):
- **U04** (baseline): two rows of dead lamp-columns receding into the dark, the lantern's warm pool on the nearest
  column and the floor, the windows and the breach's morning light cool teal on the right and across the near floor,
  coral curtains in the left bays, the far end falling to dark. The strongest interior frame.
- **U12** (baseline): the tower rising pale out of the meadow with its storeys banded in surviving ceramic, the
  breach a dark mouth with columns inside, the dead ship's ribs at the left, seagrass in the near ground, a half
  bleached coral head and the lantern's warm pool on the sand at the lower right.
- **U06**: the knotted cord across the frame, the stair going down, held motes (about 2–3% of the frame) sinking
  into the dark below it. **U07**: the wheel, a ring of brass and verdigris in the lantern's light, the shaft beside
  it. **U01**: broken crown walls at the frame's foot, a hull's dark keel across the Snell window, the tether rising.
  **U13**: the ribs in a row against the tower. **U14**: the kit row.
- Known limits: inside the tower the lantern's halo is a warm haze over much of the frame whenever the lamp is within
  ~2.5 m of the lens (the rig's single-scatter halo, as designed); the coral boulders read as lumpy masses more than
  as brain coral at game distance; the hulls seen from the terrace are dark ellipses against the dark total
  internal reflection; the coral curtain reads as hanging rags at a distance. No figure: Rhen is Character Art's.

## Revisions
- 2026-10-24 (env-art, M3-ENV-05): first version, written against the act outline Ch1, the Ch1 beat sheet (C1-02 to
  C1-07, §7 shot ids, §9 Environment request 2), bible §3 Oruvel, decisions_log N-02, the colour script `ch01` row and
  its underwater notes, tech/underwater.md and M2-RND-09, before any geometry. The floor count (F9 = the gallery at the
  terrace, "nobody goes below the ninth floor") and the dive's earlier sun (08:45, 42° / 105°) are this sheet's calls;
  the colour script's `ch01` row still describes the 10:30 raft-town.
- 2026-10-24 (env-art, M3-ENV-05, after the preview): the tower is **36 × 12 m** (6 × 2 bays) and the ground cells
  **12 m**, so the cells stop at the tower's walls and the stairwell stays clear of silt; the breach is one bay (the
  east wall's south bay), not the whole wall (the first captures read as a building on stilts); the cladding runs in
  **two bands per storey** (the panels scattered over the piers read as a checkerboard); the sub-frames add the
  **downwelling** tint (the first captures were lit like a sunlit beach) and the deep area keeps a little teal
  (ambient 0.14, in-scatter × 0.2); the dive opens the glimmer gate at the colour script's 1.5 for the held motes.

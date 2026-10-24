# Brightwater Crossing, the Ferry Deck at Sea: Design Notes

Owner: Environment Artist (M3-ENV-08). Lighting: Rendering (the `ch04_derelict` daylight sub-frame is
Rendering's, requested by the beat sheet §9; glimmer in the rigging is VFX). Gameplay placement: m2-slice
(swap-in note in the task file).
Story: [act outline Ch4 "The Pilgrim's Wake"](../../story/beats/act_outline.md) (the dawn ferry, Ysolde boards,
the ferry is never attacked, the drifting trader, the name-board), [the Ch4 beat sheet](../../story/beats/act1_ch04.md)
C4-09 to C4-15 and its §7 shot list (F01–F06, D01–D08) and §9 environment request (the ferry *Kind Weather*:
two-masted Low Reaches coastal ferry, deckhouse with a small Order shrine as the save point, passengers'
awning, cargo lashed amidships, the skiff on its davits, a lookout's perch), [bible §5.1](../../story/bible.md)
(the Low Reaches: red clay and white mortar, the lintel-gull that faces the sea and cries warning, reach-bands,
sea-law and the name-board), [ADR 0017](../../decisions/0017-act-one-restaging.md) (d) (the ferry is never
attacked: nothing on this deck is an arena). Grade: [color script `ch04`](../color_script.md) and its
`night_sea` water look. Colours: [palette.json](../palette.json). Kin: M3-ENV-06's `derelict_deck_night`
arena (`assets/environments/arenas/derelict_deck_night/`, built from the Brine Shoals kit's
`bs_derelict.py`).
Zone: `game/levels/ch04/brightwater_ferry/`. Kit: `assets_src/environments/kits/brightwater_ferry/`. Preview:
`game/levels/_tests/brightwater_ferry_kit/`.

**The feeling in one line:** a small, warm, lamp-lit ship carrying a girl to her death across a sea that
glows from underneath, past the hulls the last Rising drowned: the safest place in Act I, and the saddest.

**Influences** (references.md, in words): Austronesian and Malay coastal traders, broad-beamed plank ships
with high sterns, a long tiller and canted four-sided sails on slung yards; the passenger ferries of island
straits, where families sleep on deck under an awning among their bundles and the cargo is lashed down the
middle; harbour lanterns, a horn-and-glass oil lamp in an iron cage hung from a hook. **Our originals and
transformations:** the trader's canted sail → **the Low Reaches lug**: one tall four-sided sail on each
mast, its yard slung steeply aft, its foot on a boom, the cloth sand-coloured and patched, with a single
**sea-blue reef band** (a Low Reaches ship shows its harbour's cloth); the carved bow guardian of many seafaring
cultures → **the stem-gull**: the lintel-gull from the Haluna roofs (bible §5.1) carved at the stem head,
facing the sea ahead, so the ferry carries the village's warning-bird; the harbour lantern → **the deck
lantern**: an iron cage with a glass chimney and a sheet-iron hood, hung from the awning ridge, the rails
and the stern. The Order's shrine aboard is a wall niche in the deckhouse with a marble basin, the only
white stone on the ship.

**Kin to the derelict (M3-ENV-06).** The ferry is built in the same vocabulary as `arena_derelict_deck`, so
the player reads both as ships of one sea: deck planks laid fore and aft with dark seams; a broad
covering board under the bulwark; a bulwark of stanchions, three inner strakes and a cap rail; a hatch with
a heavy coaming; tarred hull sides falling to the sea. The difference is care: the ferry's planks are
scrubbed pale and whole, its bulwark unbroken and its cap rail oiled, its sheer strake painted sea-blue with
a red line; the derelicts are the same forms silvered, stove in, dismasted and awash.

**Act I rule (references.md "No grimdark desaturation in Act I").** The night is blue, not grey: the sky
navy (`#0B1630` / `#1E2E4E`), the sea teal and glowing, the lamp pools saturated warm. The sorrow is in what
the frame holds (the wrecks on the reef, the Cantor's bundle among the families'), never in mud.

---

## 0. Layout, Orientation, and Lighting

**The frame (kit and preview, north = −Z, +X east).** The ferry lies with her **bow to the north (−Z)**, her
origin on the centre line at the main deck's level amidships, the waterline at **y −1.6** in her frame; in the
preview she floats with the main deck at **world y +1.6** over the sea at the datum (0). She sails north
up the strait with the trade wind on her **starboard beam** (from the east-north-east, 70°), so her sails
belly to port (−X). Pemakar is ahead, Haluna astern. The strait's **reef edge** runs along the east
(starboard) side 120–600 m off, and on it lie the **drowned hulls** of the last Rising (the same Rising that
took Oruvel): dark silhouettes, dismasted and awash, standing out against the glowing water.

```
                       N (−Z)  Pemakar, a day's sail
                         |          · reef edge, awash ·  derelict_hulk_b (bow up)
            bowsprit  ───┼───                               ·
                fore hatch (grating)  windlass                  derelict_hulk_a (dismasted, listed)
                  FOREMAST (z −8.0)                         ·
         ┌─ passengers' awning (z −7.2 … −3.2) ─┐       reef_awash
   port  │  mats, bundles, lanterns              │ starboard   ← trade wind from the ENE (70°)
  (−X)   gangway ═══ (z −2.6 … −1.6) ═══ gangway         · the moon sets in the WSW (250°)
         │  cargo lashed  [ main hatch ]  cargo  │
                  MAINMAST (z +2.4), lookout's perch at +10 m
              [ DECKHOUSE z +3.4 … +7.4: door forward, the Order niche inside ]
               ladders ╱ POOP DECK (+0.9 m) ╲ ladders, tiller, stern lantern
                       skiff on its davits over the stern (z +12.6 …)
                         S (+Z)  Haluna, astern
```

**The ship (main deck at y 0 in the kit frame; dimensions in metres).**
- **Hull:** 26.6 m from stem (z −14.0) to transom (z +12.6), beam 6.8 m at the deck (the bulwark's inner
  face at x ±3.4 from z −5 to +7), easing to the stem forward and to 2.7 m half-beam at the transom;
  draught 1.6 m (the hull sides run down to y −2.2 so the swell never shows under them).
- **Main deck (walkable, flat):** y 0 from the bow to z +7.6; planks 0.2 m fore and aft, pitch-dark seams.
  **Rail height 0.95 m** (cap rail top). **Gangways** (bulwark gaps for the gangplank and for lying alongside
  in C4-11) at z −2.6 … −1.6, port and starboard.
- **Poop deck:** y +0.9 from z +7.6 to the transom, reached by two ladders at its fore edge (x ±2.5), with
  the **tiller** (3.2 m) on the rudder head at the stern and the **stern lantern** on its post.
- **Hatches:** the **main hatch** (2.2 × 1.8 m coaming, 0.45 m tall, at z +0.2) closed with hatch boards under
  a lashed tarpaulin; the **fore hatch** (1.2 × 1.2 m, z −10.2) with an open grating over the dark hold; a
  small **scuttle** on the poop.
- **Masts:** **foremast** at z −8.0 (11.5 m above deck), **mainmast** at z +2.4 (14.5 m), each with a lug
  sail on a slung yard and a foot boom; **three shrouds a side** to chain-plates outside the bulwark, ratlines
  on the mainmast's; a forestay to the bowsprit and a spring stay between the mastheads; the **lookout's
  perch** (a 1.0 m round top with a hoop rail) on the mainmast at +10.0 m.
- **Deckhouse:** 3.8 × 4.0 m (x ±1.9, z +3.4 … +7.4), walls 2.1 m with a cambered roof and a low rail, a door
  in the fore face (toward the mainmast), two windows a side lamp-lit from inside; inside the door, the
  **Order niche** (the save point): a marble basin on a plinth in an arched recess on the after wall.
  Walkways 1.3 m wide pass it on both sides to the poop ladders.
- **Passengers' awning:** a ridge spar on four posts over the deck between the foremast and the gangways
  (z −7.2 … −3.2, 4.4 m wide, ridge at 2.4 m), faded teal cloth, lanterns from the ridge; beneath it rolled
  mats, bundles, baskets and a bedroll (the passengers' places: the family, the traders, the Reed).
- **Cargo:** lashed down both sides of the main hatch (crates, bales in sacking, water jars in a rack) under
  a net, with lashing to ring-bolts.
- **The skiff** on two iron davits over the transom, 4.2 m, its painter and falls to cleats.
- **Bow:** the bowsprit (4 m), the stem-gull at the stem head, a windlass and two bitts.

**The sea around her.** Open water to every horizon: the preview's `WaterSurface` (the `night_sea` look). On the
starboard side the reef edge: `reef_awash` coral heads breaking the surface at intervals, and the two drowned
hulls on it. Nothing to port but the sea and the setting moon.

**Tide datum:** `tide_line_y = 0.0` (Haluna). No tide plays here; the waterline is the sea's mean level.

**GI recommendation:** an open exterior at night with practical light. **No SDFGI**: sky-colour ambient at the
`ch04` fill (`#2A4A6E` at 0.2) + SSAO; the lanterns are shadowless omnis except the two over the main deck
(the awning's after lantern and the stern lantern), which cast shadows on GPU tiers.

| Sub-frame | Use | Time | Moon elev / az | Key | Fill | Rim | Fog | Sea-glow | LUT |
|---|---|---|---|---|---|---|---|---|---|
| `ch04` (color script; the crossing's first quarter-hour, before first light) | C4-10 Brightwater Crossing, C4-15 coda | 05:50 | 18° / 250° (setting, astern-to-port) | **lamp `#FFB16E`** (~2,900 K), the lanterns at **1.2** each (pools ~7 m) | `#2A4A6E` at 0.2 (sky ambient tinted to it) | the moon `#9DB4D9` at **0.28** (outside the pools; rule 3: 0.28 ≤ 2.5 × 0.12) | albedo `#22354F`, volumetric density 0.008 (GPU tiers; off on lavapipe) | **0.12** (`night_sea`) | `lut_ch04_wake` (M3-ENV-06's, read-only): warm pools kept saturated, outside cooled and desaturated 15%, the black point lifted to `night_sky` |
| `ch04_derelict` (requested of Rendering, beat sheet §9) | C4-11 to C4-14 | 07:30–08:40 | sun ~15° | — | — | — | — | — | not this kit's preview |

**Exposure, key product and water** (ADR 0014): exposure 1.10, the lantern key 1.2 inside its pool, the moon
0.28 × 1.10. Water: **`night_sea`** (σ 2 / 0.5 / 0.42 m⁻¹ × 1.0; `col_scatter_shallow` `#1FA3A6`, `col_deep`
`#061A2B`, `col_sss` `#1C6B78`, caustics 0.25), validated at `#003845` with glow 0.12. Waves: an open-sea swell
from the east-north-east (wavelengths 64 / 33 / 17 / 8 m, amplitudes to 0.32 m), longer than any lagoon's.

**Value structure (color script rule 3, the practical-keyed night).** (1) the lantern flames and the lit
deckhouse windows; (2) what they light, inside their pools: the scrubbed deck, the awning's underside, the
sails' lower thirds, the bundles; (3) moonlit cloth and rails outside the pools; (4) **the glowing sea**,
the frame's one teal field and its brightest water; (5) the navy sky, then shadow. The drowned hulls are
the darkest large shapes in the frame, read as silhouettes **against the glowing sea**, never against the
sky alone. Nothing whiter than the foam; the sails stay below the lit deck's value.

---

## 1. Mood by Moment

1. **The gangplank (C4-09, F01, 06:00).** The seaward landing is the Shell Shrine islet's (Haluna kit); the
   ferry lies alongside, lamps still lit from her night at the berth. The landing steps are not in this kit.
2. **Brightwater Crossing (C4-10, F02–F04).** Under way before first light: the lanterns sway, the sails
   are pale shapes overhead, the sea glows along the hull. Families asleep under the awning, the traders
   awake by the cargo, the Reed at the gangway. Ysolde and Asha at the starboard rail; on the reef edge
   beyond them, the black ribs of the drowned. The safest place in Act I: no battle ever happens here.
3. **The drifting trader (C4-11, F05).** In daylight (Rendering's `ch04_derelict`), off the bow. The
   *Seventh Terrace* is not this kit (see §6).
4. **The coda (C4-15, F06).** The wrapped name-board on the deck by the main hatch, the child's leaf-boat on
   it, Toma's ink kit. Under way again; the lanterns lit again at dusk.

---

## 2. Kit Pieces (origin on the ship's centre line at main-deck level amidships unless stated, +Y up)

| Kit | Pieces | Key dimensions and parameters |
|---|---|---|
| **The ship** | `ferry_hull` | Hull, main deck, poop deck and ladders, covering boards, bulwarks (stanchions every 1.2 m, three inner strakes, cap rail at +0.95 m) with the two gangways, the main hatch (closed, tarpaulin lashed), the fore hatch (grating) and the poop scuttle, the rudder head and tiller, the bowsprit, the stem-gull, windlass and bitts, chain-plates. Hull sides: tarred below the wale, the sheer strake painted sea-blue with a red line, a little tumblehome. Same plank, seam and bulwark proportions as `arena_derelict_deck`. |
| | `ferry_rig` | Both masts (0.26 / 0.30 m at the partners, tapering), the slung yards and foot booms, the two lug sails (wind-filled to port, sand cloth with a sea-blue reef band and a few patches), shrouds to the chain-plates (ratlines on the main), forestay, spring stay, halyards and sheets to the rail, the lookout's perch. In the hull's frame. |
| | `ferry_deckhouse` | 3.8 × 4.0 m, 2.1 m walls of lime-washed boards over a sea-blue dado, corner posts, a cambered roof with a low rail, the door (open) and four lamp-lit windows, the Order niche on the after wall inside (marble basin on a plinth, arched recess). In the hull's frame. |
| | `ferry_awning` | Four posts, ridge spar, the cloth in a shallow catenary between ridge and side lines, its edges scalloped where it is lashed. In the hull's frame. |
| | `ferry_cargo` | Lashed down both sides of the main hatch: crates (0.6–0.9 m), bales in sacking, a rack of six water jars, a cargo net over each stack, lashings to ring-bolts. In the hull's frame. |
| | `ferry_skiff` | The skiff (4.2 m, clinker strakes, thwarts, oars) on two iron davits over the transom with its falls. In the hull's frame. |
| **Passengers** | `passenger_bundles` | One cluster (origin on the deck at its centre, about 2 × 1.5 m): two cloth bundles tied at the neck (indigo and sand), a basket with a lid, a rolled sleeping mat, a bedroll, a water gourd. Placed several times under the awning and by the rails, turned. |
| **Lamps** | `ferry_lantern` | A deck lantern (origin at its hanging ring): iron cage 0.36 m tall, glass chimney (emissive `oil_lamp`, the flame's glass), sheet-iron hood. The preview's rig adds one OmniLight3D at the flame (0.2 m below the ring) per placement, **`light_volumetric_fog_energy` = 0** (the Lead's rule). |
| **The drowned** | `derelict_hulk_a` | A trader of the ferry's kind, 22 m, grounded on the reef edge with an 8° list to starboard, dismasted (the mainmast a 4 m stump, the foremast gone at the deck), the bulwark stove in along half its length, her deck silvered and half awash. Origin at her waterline on the centre line. |
| | `derelict_hulk_b` | The fore half of another hull, bow-up at 14°, the stern under water, a raked foremast with a broken yard and a rag of sail. Origin at the waterline. |
| | `reef_awash` | A 40 × 16 m patch of reef crest: dark coral heads just breaking the surface, a few higher blocks, to set the hulls on. Origin at the datum. |

**Budgets (triangles, LOD0 / LOD1):** hull 60,000 / 6,000; rig 40,000 / 4,000; deckhouse 16,000 / 1,600; awning
6,000 / 600; cargo 14,000 / 1,400; skiff 10,000 / 1,000; bundles 8,000 / 800; lantern 1,500 / 200; hulk a
16,000 / 1,600; hulk b 12,000 / 1,200; reef 8,000 / 800. LOD1 begins at 70 m and every piece is a chain
(`<piece>`, `<piece>-lod1`), so exactly one LOD draws at every distance (vegetation.md "One LOD at every
distance"); the far pieces' LOD1 keeps the masts and the broken yard, because at 300 m the silhouette is the
whole read.

## 3. Materials (palette.json names)

| Slot | Shader | Look |
|---|---|---|
| `bf_deck` | weathering (Haluna `timber`) | the main deck: `timber_weathered` scrubbed pale (holystoned), dark pitch seams from the geometry, salt in the seams (G), the planks dry |
| `bf_timber` | weathering (Haluna `timber`) | rails, posts, ladders, spars, the tiller: oiled timber, warmer than the deck, worn on edges (A) |
| `bf_timber_tar` | weathering (Haluna `timber`) | the hull below the wale and the hatch coamings: tarred near-black brown (the Brine Shoals `bs_timber_tar` tone), barnacles and weed low |
| `bf_paint_blue` | weathering (Haluna `timber`, painted) | the sheer strake and the deckhouse dado: `sea_blue_cloth` `#3C78A8` paint, salt-chalked and worn through on edges |
| `bf_limewash` | weathering (Haluna `timber`, painted) | the deckhouse boards: `mortar_white` lime-wash greyed (`#D2CCC0`), so it stays under the foam |
| `bf_lacquer_red` | standard | the sheer strake's line and the stem-gull's beak: `lacquer_red` |
| `bf_carved` | weathering (Haluna `timber`) | the stem-gull: carved `timber_weathered`, the wear (A) lightening its crest |
| `bf_canvas`, `bf_canvas_blue`, `bf_canvas_awning` | weathering (Haluna `woven_panel`, painted) | sails: `sand_cloth` `#C9B48E`, the reef band `sea_blue_cloth`, the awning `faded_teal_cloth` `#5E9A96`; salt-stained low |
| `bf_tarpaulin` | weathering (`woven_panel`, painted) | the main hatch's tarpaulin: tarred canvas, dark |
| `bf_rope` | weathering (`woven_panel`) | tarred hemp: shrouds, lashings, nets |
| `bf_iron`, `bf_brass` | standard | chain-plates, davits, the lantern cages and hoods (wet rust-dark iron); the ship's bell and the lantern rings (`brass`, salt-dulled) |
| `bf_lamp_glass` | standard, emissive | the lit lantern chimney and the deckhouse windows' glow: `oil_lamp` `#FFB16E` |
| `bf_interior_dark` | standard | the hold under the grating, the deckhouse's shadowed interior: deep shade above the albedo floor |
| `bf_marble` | standard | the Order niche's basin and plinth: `order_marble` |
| `bf_cloth_indigo`, `bf_cloth_sand`, `bf_cloth_red`, `bf_basket` | weathering (`woven_panel`, painted) | the passengers' bundles: `indigo_dye`, `sand_cloth`, `lacquer_red_deep`; baskets in `thatch` |
| `bf_earthenware` | weathering (Haluna `coral_concrete`, painted) | water jars: unglazed clay toward `roof_clay` |
| `bf_wreck_timber`, `bf_wreck_tar` | weathering (Haluna `timber`) | the drowned hulls: silvered decks and tarred sides gone grey with salt, heavy barnacles and weed to the waterline |
| `bf_wreck_canvas` | weathering (`woven_panel`, painted) | the rag of sail: `sand_cloth` darkened and rotted |
| `bf_reef` | weathering (Haluna `coral_stone`, darkened) | reef heads: dark wet coral toward `volcanic_stone`, weed |

Weathering channels follow haluna.md §4 (**R moss, G salt, B wet, A erosion**). No moss at sea. The ferry
carries light salt (G) in seams and on the rails and the hull's wet band (B) low; the drowned carry heavy
salt, wet and erosion everywhere.

---

## 4. Composed Shots (vFOV = 2·atan(12 / mm); heights above the local deck or sea)

All at `ch04`. **◆** marks the preview shots built in `brightwater_ferry_kit/`. The beat sheet's **F02–F04**
are rail cameras on this deck; F01 (the islet's landing) is the Haluna kit's, F05/F06 are daylight and the
derelict (§6).

| # | Lens (vFOV) | Height | Framing | What the shot is about |
|---|---|---|---|---|
| B01 ◆ (F02) | 24 mm (53.1°) | 1.6 m above the poop deck by the stern lantern, looking forward along the centre line | The deckhouse roof in the foreground, the lamp-lit main deck beyond it, the awning glowing under its lanterns, both sails pale against the navy sky, the bowsprit pointing at the dark; the sea-glow at the rails on both sides. Sky ≈ 40%. | The crossing: a warm small world going forward into the dark. |
| B02 ◆ (F03) | 35 mm (37.8°) | 1.4 m on deck at the port rail by the foremast, looking aft and to starboard | Under the awning: bundles, mats and a basket in a lantern's pool, the posts and ridge framing the cargo and the mainmast beyond. | The passengers' places: people carrying their lives in cloth. |
| B03 ◆ (F04) | 50 mm (27.0°) | 1.5 m at the starboard gangway, looking out over the rail east-north-east | The cap rail and a lantern on the left third, the glowing sea, and on the reef edge the two drowned hulls black against the glow, the coral heads breaking white. | Ysolde and Asha at the rail; the dead the sea has already taken. |
| B04 ◆ | 35 mm (37.8°) | 1.2 m above the sea, 42 m off the port quarter | The whole ferry on the night sea, lanterns along her, the deckhouse windows lit, the sails catching the moon, a lamp's reflection broken on the swell, the glowing water round her. | Beauty in decline: the ship carrying the Cantor. |
| B05 ◆ | 35 mm (37.8°) | 1.5 m on deck before the deckhouse door | The open door, the Order niche inside with its marble basin in the window light, the mainmast's foot and a lantern framing it. | The save point: the Order's small white place aboard. |
| B06 ◆ | 18 mm (67.4°) | 30 m above the sea, off the starboard bow, looking down and aft | The layout as a diagram: deck, hatches, awning, cargo, deckhouse, poop, rig, and the reef with its hulls. | The player sees the space (pillar 4). |
| B07 ◆ | 85 mm (16.1°) | 1.6 m at the bow by the stem-gull, looking out to starboard-ahead | The stem-gull's carved head in the foreground's edge, the dismasted hulk on the reef in the glowing sea beyond. | The warning-bird facing the drowned. |

**Registered baselines (the repo's binary budget: at most two):** chosen after viewing (§6).

## 5. Review Checklist

- [ ] Rule 3 order: flames > the lit pools > moonlit cloth > the glowing sea > the sky; the sea is the
      brightest water and the frame's one teal field; the drowned read against the glow.
- [ ] The lamp pools read as pools with a falloff, not a frame-wide key; outside them the deck is moonlit blue.
- [ ] Shadows teal-navy, never neutral black (rule 5); the black point is `night_sky`.
- [ ] The ferry and the derelicts read as kin (planks, seams, bulwark, covering board, tarred sides).
- [ ] Nothing on the ferry suggests a fight: no arena markers, no weapons racks; the Order niche is small.
- [ ] Every lantern's light sets `light_volumetric_fog_energy` = 0.
- [ ] Red ≤ 5% (the strake line, the beak, a bundle), gold 0%; no bound light (teal, still) anywhere in Ch4.

## 6. The Preview (M3-ENV-08)

To be written after the captures are viewed.

**Not in this kit:** the ***Seventh Terrace*** (the boardable derelict of C4-11–C4-14, with its galley, hold,
name-board and its sails' set and lowered states) is one hero ship across Ch1 (moored at Oruvel, O07/O13) and
Ch4 (act1_ch01.md §9: "build it once"), so it is a follow-up (**M3-ENV-08B**), built after M3-ENV-07's
Oruvel kit settles the mooring. Its hull should come from this kit's hull generator (the same vocabulary,
Pemakar lacquer and copper sheathing). The islet's seaward landing (F01) is a Haluna kit addition.

## Revisions

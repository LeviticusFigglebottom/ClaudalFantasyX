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
took Oruvel): dark silhouettes, dismasted and awash, standing black on the moon's glade. The moon is a waning
crescent low in the **east** (88°, 16°), up before the sun as a waning moon is at 05:50, so its glade lies across
the reef and behind the drowned.

```
                       N (−Z)  Pemakar, a day's sail
                         |          · reef edge, awash ·  derelict_hulk_b (bow up)
            bowsprit  ───┼───                               ·
                fore hatch (grating)  windlass                  derelict_hulk_a (dismasted, listed)
                  FOREMAST (z −8.0)                         ·
         ┌─ passengers' awning (z −7.2 … −3.2) ─┐       reef_awash
   port  │  mats, bundles, lanterns              │ starboard   ← trade wind from the ENE (70°)
  (−X)   gangway ═══ (z −2.6 … −1.6) ═══ gangway         · the crescent low in the east (88°), its glade on the reef
         │  cargo lashed  [ main hatch ]  cargo  │
                  MAINMAST (z +2.4), lookout's perch at +11.6 m
              [ DECKHOUSE z +3.4 … +7.4: door forward, the Order niche inside ]
               ladders ╱ POOP DECK (+0.9 m) ╲ ladders, tiller, stern lantern
                       skiff on its davits over the stern (z +12.6 …)
                         S (+Z)  Haluna, astern
```

**The ship (main deck at y 0 in the kit frame; dimensions in metres).**
- **Hull:** 26.6 m from stem (z −14.0) to transom (z +12.6), beam 6.8 m at the deck (the bulwark's inner
  face at x ±3.4 from z −5 to +7), easing to the stem forward and to 2.7 m half-beam at the transom;
  draught 1.6 m (the hull sides run down to y −2.4 so the swell never shows under them). The sheer is lowest
  amidships and sweeps up 1.05 m to the stem and over the last 2.4 m before the poop; the forefoot is cut away
  (the stem rakes 2.2 m from the sheer to the keel).
- **Main deck (walkable, flat):** y 0 from the bow to z +7.6; planks 0.2 m fore and aft, pitch-dark seams.
  **Rail height 0.95 m** (cap rail top). **Gangways** (bulwark gaps for the gangplank and for lying alongside
  in C4-11) at z −2.6 … −1.6, port and starboard.
- **Poop deck:** y +0.9 from z +7.6 to the transom, reached by two ladders at its fore edge (x ±2.6), with
  the **tiller** (3.2 m) on the rudder head at the stern and the **stern lantern** on its crook. On the poop the
  planking stops 0.35 m above the deck and an **open quarter rail** (stanchions, a mid rail, the cap rail) stands
  above it, so the stern's silhouette is a rail against the sky, not a box.
- **Hatches:** the **main hatch** (2.2 × 1.8 m coaming, 0.45 m tall, at z +0.2) closed with hatch boards under
  a lashed tarpaulin; the **fore hatch** (1.2 × 1.2 m, z −10.2) with an open grating over the dark hold; a
  small **scuttle** on the poop.
- **Masts:** **foremast** at z −8.0 (11.5 m above deck), **mainmast** at z +2.4 (14.5 m), each with a lug
  sail on a slung yard and a foot boom; **three shrouds a side** to chain-plates outside the bulwark, ratlines
  on the mainmast's; a forestay to the bowsprit and a spring stay between the mastheads; the **lookout's
  perch** (a 1.24 m round top with a hoop rail) on the mainmast at +11.6 m. The main's fife rail stands forward
  of the mast, so nothing blocks the deckhouse door; the fore's stands aft of its mast.
- **Deckhouse:** 3.8 × 4.0 m (x ±1.9, z +3.4 … +7.4), walls 2.1 m with a cambered roof and a low rail, a door
  in the fore face (toward the mainmast), two windows a side lamp-lit from inside; inside the door, the
  **Order niche** (the save point): a marble basin on a plinth in an arched recess on the after wall.
  Walkways 1.3 m wide pass it on both sides to the poop ladders.
- **Passengers' awning:** a ridge spar and two side spars on six posts over the deck between the foremast and the gangways
  (z −7.2 … −3.2, 4.4 m wide, ridge at 2.4 m), faded teal cloth, lanterns from the ridge; beneath it rolled
  mats, bundles, baskets and a bedroll (the passengers' places: the family, the traders, the Reed).
- **Cargo:** lashed down both sides of the main hatch (crates, bales in sacking, water jars in a rack) under
  a net, with lashing to ring-bolts.
- **The skiff** on two iron davits over the transom, 4.2 m, its painter and falls to cleats.
- **Bow:** the bowsprit (5.2 m, lying beside the stem head to starboard, clear of the gull), the stem-gull at
  the stem head, a windlass and two bitts, and the **bow lantern** on a crook from the starboard cap rail, which
  lights the gull from behind.

**The sea around her.** Open water to every horizon: the preview's `WaterSurface` (the `night_sea` look). On the
starboard side the reef edge: `reef_awash` coral heads breaking the surface at intervals, and the drowned
hulls on it. Nothing to port but the dark sea.

**Tide datum:** `tide_line_y = 0.0` (Haluna). No tide plays here; the waterline is the sea's mean level.

**GI recommendation:** an open exterior at night with practical light. **No SDFGI**: sky-colour ambient at the
`ch04` fill (`#2A4A6E` at 0.2) + SSAO; the lanterns are shadowless omnis except the two over the main deck
(the awning's after lantern and the stern lantern), which cast shadows on GPU tiers.

| Sub-frame | Use | Time | Moon elev / az | Key | Fill | Rim | Fog | Sea-glow | LUT |
|---|---|---|---|---|---|---|---|---|---|
| `ch04` (color script; the crossing's first quarter-hour, before first light) | C4-10 Brightwater Crossing, C4-15 coda | 05:50 | 16° / 88° (a waning crescent, low in the east) | **lamp `#FFB16E`** (~2,900 K), the lanterns at **1.2** each (pools ~7 m) | `#2A4A6E` at 0.2 (sky ambient tinted to it) | the moon `#9DB4D9` at **0.28** (outside the pools; rule 3: 0.28 ≤ 2.5 × 0.12) | albedo `#22354F`, volumetric density 0.008 (GPU tiers; off on lavapipe) | **0.12** (`night_sea`) | **`lut_ch04_crossing`** (this kit's `bf_zone_lut.py`): M3-ENV-06's `ch04_wake` (warm pools kept saturated, outside cooled and desaturated 15%, the black point lifted to `night_sky`) with the sea's teal (165–215°) spared the cool cut, so the sea stays the frame's one teal field (rule 3 (c)); `ch04_wake` alone turns a whole-frame sea navy-grey |
| `ch04_derelict` (requested of Rendering, beat sheet §9) | C4-11 to C4-14 | 07:30–08:40 | sun ~15° | — | — | — | — | — | not this kit's preview |

**Exposure, key product and water** (ADR 0014): exposure 1.10, the lantern key 1.2 inside its pool, the moon
0.28 × 1.10. Water: **`night_sea`** (σ 2 / 0.5 / 0.42 m⁻¹ × 1.0; `col_scatter_shallow` `#1FA3A6`, `col_deep`
`#061A2B`, `col_sss` `#1C6B78`, caustics 0.25), validated at `#003845` with glow 0.12. Waves: an open-sea swell
from the east-north-east (wavelengths 64 / 33 / 17 / 8 m, amplitudes to 0.32 m), longer than any lagoon's.

**Value structure (color script rule 3, the practical-keyed night).** (1) the lantern flames and the lit
deckhouse windows; (2) what they light, inside their pools: the scrubbed deck, the awning's underside, the
sails' lower thirds, the bundles; (3) moonlit cloth and rails outside the pools; (4) **the glowing sea**,
the frame's one teal field and its brightest water; (5) the navy sky, then shadow. The drowned hulls are
the darkest large shapes in the frame, read as silhouettes on the moon's glade and the paler sky over it. At a deck's
eye height the far sea mostly mirrors the sky (the sea-glow is strongest looking down), so the glade, not the
sea-glow, is what lights the horizon behind them. Nothing whiter than the foam; the sails stay below the lit
deck's value.

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
| **The ship** | `ferry_hull` | Hull, main deck, poop deck and ladders, covering boards, bulwarks (stanchions every 1.2 m, three inner strakes, cap rail at +0.95 m) with the two gangways, the main hatch (closed, tarpaulin lashed), the fore hatch (grating) and the poop scuttle, the rudder head and tiller, the bowsprit, the stem-gull, windlass and bitts, chain-plates, the fife rails, the open quarter rail on the poop, and the crooks the stern and bow lanterns hang from. Hull sides: tarred below the wale, the sheer strake painted sea-blue with a red line, a little tumblehome. Same plank, seam and bulwark proportions as `arena_derelict_deck`. |
| | `ferry_rig` | Both masts (0.26 / 0.30 m at the partners, tapering), the slung yards and foot booms, the two lug sails (wind-filled to port, sand cloth with a sea-blue reef band and a few patches), shrouds to the chain-plates (ratlines on the main), forestay, spring stay, halyards and sheets to the rail, the lookout's perch. In the hull's frame. |
| | `ferry_deckhouse` | 3.8 × 4.0 m, 2.1 m walls of lime-washed boards over a sea-blue dado, corner posts, a cambered roof with a low rail, the door (open) and four lamp-lit windows, the Order niche on the after wall inside (marble basin on a plinth, arched recess). In the hull's frame. |
| | `ferry_awning` | Six posts, the ridge spar and two side spars, the cloth sagging between them, a scalloped valance along each side, lashings to the cap rail. In the hull's frame. |
| | `ferry_cargo` | Lashed down both sides of the main hatch: crates (0.6–0.9 m), bales in sacking, a rack of six water jars, a cargo net over each stack, lashings to ring-bolts. In the hull's frame. |
| | `ferry_skiff` | The skiff (4.2 m, clinker strakes, thwarts, oars) on two iron davits over the transom with its falls. In the hull's frame. |
| **Passengers** | `passenger_bundles` | One cluster (origin on the deck at its centre, about 2 × 1.5 m): two cloth bundles tied at the neck (indigo and sand; the cloth falls in folds from the gather, a cord binds the neck, a corner hangs loose), a basket with a lid, a rolled sleeping mat, a bedroll, a water gourd. Placed several times under the awning and by the rails, turned. |
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
| B03 ◆ (F04) | 50 mm (27.0°) | 1.2 m at the starboard rail just aft of the gangway, looking east toward the crescent | The open gangway and the warm cap rail across the foreground, the moon's glade on the sea, and on the reef edge three drowned hulls black on it, the reef heads glittering. | Ysolde and Asha at the rail; the dead the sea has already taken. |
| B04 ◆ | 35 mm (37.8°) | 1.2 m above the sea, 42 m off the port quarter | The whole ferry on the night sea, lanterns along her, the deckhouse windows lit, the sails catching the moon, a lamp's reflection broken on the swell, the glowing water round her. | Beauty in decline: the ship carrying the Cantor. |
| B05 ◆ | 50 mm (27.0°) | 1.5 m on deck before the deckhouse door | The open door, the Order niche inside with its marble basin in the window light, the mainmast's foot and a lantern framing it. | The save point: the Order's small white place aboard. |
| B06 ◆ | 18 mm (67.4°) | 30 m above the sea, off the starboard bow, looking down and aft | The layout as a diagram: deck, hatches, awning, cargo, deckhouse, poop, rig, and the reef with its hulls. | The player sees the space (pillar 4). |
| B07 ◆ | 50 mm (27.0°) | 2.7 m on the forecastle, port of the foremast, looking ahead | The port bow rail in the foreground, the stem head with the stem-gull and the bowsprit on the right, the bow-up hulk on the reef ahead. | The warning-bird facing the drowned. |

**Registered baselines (the repo's binary budget: at most two):** B02 and B03 (§6).

## 5. Review Checklist

- [ ] Rule 3 order: flames > the lit pools > moonlit cloth > the glowing sea > the sky; the sea is the
      brightest water and the frame's one teal field; the drowned read on the moon's glade.
- [ ] The lamp pools read as pools with a falloff, not a frame-wide key; outside them the deck is moonlit blue.
- [ ] Shadows teal-navy, never neutral black (rule 5); the black point is `night_sky`.
- [ ] The ferry and the derelicts read as kin (planks, seams, bulwark, covering board, tarred sides).
- [ ] Nothing on the ferry suggests a fight: no arena markers, no weapons racks; the Order niche is small.
- [ ] Every lantern's light sets `light_volumetric_fog_energy` = 0.
- [ ] Red ≤ 5% (the strake line, the beak, a bundle), gold 0%; no bound light (teal, still) anywhere in Ch4.

## 6. The Preview (M3-ENV-08)

`game/levels/_tests/brightwater_ferry_kit/brightwater_ferry_preview.tscn` composes the kit for the ◆ shots (its README
lists the files): the ferry at her origin (hull, rig, deckhouse, awning, cargo, skiff), seven passengers' places, nine
lanterns, and on the reef edge to the east four drowned hulls on twelve reef patches. Read of the final captures
(lavapipe, 960 × 540):
- **B02** (baseline): the frame that carries the chapter: under the awning, the families' bundles, mats, a basket
  and a bedroll in the lanterns' pools, the jar rack and the main hatch's tarpaulin, the deckhouse's door and its
  lantern beyond, the dark sea past the rail. Warm, small and safe; the only blue is the sea and the sky.
- **B03** (baseline): the strongest open-sea frame: through the open gangway, the crescent's glade across the
  sea, and on it the drowned black and still, the reef heads glittering cyan where the glade meets them. Pillar 2
  on its own.
- **B01** forward along the starboard walkway from the poop (the lit deckhouse windows, the lanterns down the
  walkway, the mainsail lit warm from below, the glowing sea to starboard); **B04** the ferry from the sea,
  backlit by the crescent: a silhouette of rig and sails with the lanterns and windows the only warmth (it reads as
  night, not as detail); **B05** the Order niche through the door (the marble basin and arch in the cabin
  lantern's light); **B06** the overview (the deck plan, hatches, awning, cargo, deckhouse, poop and rig on the
  glowing sea); **B07** the bow: the stem-gull and bowsprit against the dark, the bow-up hulk ahead.
- Known limits: the ship is still (no roll or pitch; the zone may add one), and the swell passes through the hull
  below the deck, where nothing shows; the rig's lines are tubes (no blocks at every lead); the fore wall's
  lime-wash reads as dark boards where the door lantern cannot reach it (B05); the far sea at deck height is the
  sky's mirror more than glow, which is why the moon is in the east (§0); the drowned are generic traders, not the
  *Seventh Terrace* (M3-ENV-08B); the volumetric fog (0.008) is off on lavapipe.

**Not in this kit:** the ***Seventh Terrace*** (the boardable derelict of C4-11–C4-14, with its galley, hold,
name-board and its sails' set and lowered states) is one hero ship across Ch1 (moored at Oruvel, O07/O13) and
Ch4 (act1_ch01.md §9: "build it once"), so it is a follow-up (**M3-ENV-08B**), built after M3-ENV-07's
Oruvel kit settles the mooring. Its hull should come from this kit's hull generator (the same vocabulary,
Pemakar lacquer and copper sheathing). The islet's seaward landing (F01) is a Haluna kit addition.

## 7. The *Seventh Terrace* (M3-ENV-08B): one hero ship for Ch1 and Ch4

Story: [act1_ch01.md](../../story/beats/act1_ch01.md) C1-09 bark 5 (Sadi Moru's coaster at the outer mooring,
loading salvage; the insert on the name-board, O07), C1-12 (O13: she casts off and runs under full sail, the last
time anyone sees her crewed), §7 (O07 "must match D06 exactly") and §9 item 4 ("build it once"); [act1_ch04.md](../../story/beats/act1_ch04.md)
C4-11 to C4-14 (F05, D01–D08), §5 (the Spar-Wraith under the mainmast, its sail-membranes along her shrouds, "when
it dies, the sails come down"), §7 and §9 item 2 (boardable deck, the galley's four bowls, the hold's copper ingots
and lamp-housing, the stern name-board, sails set and torn with a lowered state, spawn membrane on the rigging,
fenders and boathooks between the hulls, never a lashing). Mooring: [oruvel.md](oruvel.md) §0 (the outer mooring,
open water west at (−58, 8)). Materials: the Pemakar kit's lacquer and copper (pemakar_materials.py's
`kit_lacquer_*`, `kit_copper_raw`), written as this kit's own `bf_*` slots. Grade: Ch1 is the colour script's
`ch01` (10:30); Ch4 is **`ch04_derelict`**, which Rendering has not added yet (requested in act1_ch04.md §9 and
the M3-ENV-08 handoff), so the Ch4 view uses a **provisional** frame (below) that Rendering replaces.

**The feeling in one line:** the same proud little ship twice: busy and argued-over in the sun at Oruvel, then
three days later sailing on with nobody aboard, the table still laid.

**Influences** (references.md, in words): the battened lug sails of East and Southeast Asian coastal traders
(cloth stiffened by horizontal battens, so a lowered sail stacks on its boom in folds); Pemakar's own lacquer
craft (bible §5.2; Thai and Burmese black-and-red lacquer, already in references.md §2). **Our originals:**
the **terrace sail**: each battened lug has *seven* cloths between its battens, so a set sail reads as stepped
bands and a lowered one stacks into terraces on the boom; the **hull in lacquer and copper**: black-lacquered
topsides with one red-lacquered sheer strake and a red wale, copper sheathing from the keel to a hand's breadth
above the waterline, verdigris at the wet line; the **name-board** in **Pemakar terrace script**, an original
script whose glyphs are stacks of stepped bars (each glyph a little hillside of terraces), carved in relief,
red lacquer on a black ground, inside a copper-banded frame, with a seven-step terrace emblem at each end.

### 7.1 The ship (kit frame: bow to −Z, origin on the centre line at main-deck level amidships, waterline y −1.5)

- **Hull:** `bf_common.HullForm` (the ferry's and the drowned hulls' generator, so all three read as one sea's
  ships): 21.0 m from stem (z −11.0) to transom (z +10.0), half-beam 3.0 m, transom half 2.3 m, keel y −2.2;
  a stronger bow rise (1.6 m) and sheer than the ferry (a coaster built to carry, not to ferry). **Main deck**
  flat at y 0; **poop** at y +1.0 from z +5.2 aft, the helm **wheel** on it (act1_ch04 C4-11: "the wheel turning
  by itself"), the rudder hung on the transom with its head inside the counter, so nothing crosses the
  name-board. **Gangways** port and starboard at z +0.9 … +1.9 (the boarding place in C4-11 and the mooring's
  gangplank in Ch1). Same plank, seam and bulwark proportions as the ferry and `arena_derelict_deck`.
- **Bands:** copper sheathing below y −1.15 (0.35 m above the waterline: the copper boot-top shows in every
  view), black lacquer above, a red-lacquered wale at y −0.45 and a red sheer strake under the cap rail; the
  counter (the transom above the wale) in deep red lacquer, so the black name-board stands out on it; its planks' seams show, a black moulding frames it, and copper nail-heads run along the wale (M3-ENV-705).
- **Main hatch (open)** at z −3.6, 1.8 × 1.6 m coaming, a ladder down into **the hold** (y −1.9 floor, from
  z −5.4 to −1.8): copper ingots in crossed stacks, crates, and on a shelf **the lamp-housing** Rhen sold the
  skipper (a dead Lit Age ceramic housing with a brass rim; C4-12 "he finds the housing and puts it back").
- **Masts:** foremast at z −6.8 (11.0 m), mainmast at z −0.6 (14.0 m), each with a battened lug; three shrouds
  a side to chain-plates (ratlines on the main), a forestay to the bowsprit, a spring stay. The deck round the
  mainmast is open from the hatch's after coaming to the galley (the Spar-Wraith's arena, §5: 3.6 m clear fore
  and aft, the full beam athwart).
- **Galley:** a deckhouse 3.2 × 2.6 m (x ±1.6, z +2.4 … +5.0), walls 2.0 m, black lacquer boards over a red
  dado, the door in the fore face toward the mainmast, a window each side. Inside: the table athwartships with
  **four bowls**, the meal half-eaten (rice and a ladle left in the pot), two benches, a clay stove with a copper
  pot, the galley's hourglass on a shelf (Ysolde's bark), a lamp hook.
- **Poop:** the wheel on a pedestal at z +7.0, the scuttle, the stern lantern's post (unlit), the open quarter
  rail. **The name-board** hangs on the transom's outer face, centre y +0.95, on two copper brackets (the hull
  carries the brackets; the board is its own piece, so Ch4 can take it away).

### 7.2 The states (the pieces each state places; all share the ship's origin)

| State | Beats | Pieces |
|---|---|---|
| **moored, crewed** (Ch1) | C1-09 (O07) | `terrace_hull`, `terrace_name_board`, `terrace_galley`, `terrace_hold`, `terrace_rig`, **`terrace_sails_furled`** (yards lowered onto the booms, the sails stacked and tied with gaskets, lazy-jacks taut), **`terrace_moored`** (mooring lines to the stage raft, rope fenders on the port side, the gangplank out, salvage crates and a lamp-housing crate by the hatch, a lantern on the boom gallows) |
| **under sail** (Ch1 O13; Ch4 F05, C4-11 to C4-13) | O13, F05, D01–D05, D07 | `terrace_sails_set` in place of the furled sails (wind-filled, two cloths torn at the leech, sheets hauled), no `terrace_moored`; in Ch4 add **`terrace_membrane`** (the spawn membrane webbing the shrouds and fringing the main yard, `spawn_wound` seams faint in daylight) and **`terrace_derelict`** (three days drowned: a capsized bucket, a slack sheet across the deck, spilled coils, salt-crusted weed on the rails) |
| **sails lowered** (Ch4) | C4-14 after the Canticle (D08 → F05) | `terrace_sails_lowered` in place of the set sails (the yards fallen onto the booms askew, the cloth in loose folds hanging over the booms and the rail), no membrane (it died with the wraith), and no `terrace_name_board` once Rhen has taken it |
| alongside (Ch4) | C4-11 to C4-14 | **`alongside_gear`** in the *ferry's* frame: four rope fenders hung outside her port bulwark and three boathooks laid across the gap to the derelict's cap rail. **Nothing ties the hulls together** (sea-law: never lash a living hull to a drowned one) |

The name-board is the **same piece** in both chapters (one `.glb`, one material set); O07 and D06 frame it with
the same lens from the same point in the ship's frame (§7.4), so the carving matches by construction.

### 7.3 Budgets and materials

Budgets (triangles, LOD0 / LOD1): hull 40,000 / 4,000; wheel 2,500 / 300; name-board 8,000 / 800; galley
10,000 / 1,000; hold 10,000 / 1,000; rig 14,000 / 1,400; sails set 24,000 / 2,400; sails furled 12,000 / 1,200; sails lowered
14,000 / 1,400; membrane 8,000 / 800; moored 8,000 / 800; derelict 6,000 / 600; alongside gear 4,000 / 400.
LOD chains as the rest of the kit (LOD1 from 70 m).

| Slot | Shader | Look |
|---|---|---|
| `bf_lacquer_black` | standard, clearcoat (the Pemakar kit's `kit_lacquer_black`) | topsides, the galley's walls, the poop break, the name-board's ground: `lacquer_black` `#1D1916` |
| `bf_lacquer_red_deep` | standard, clearcoat | the counter (behind the name-board) and the galley's dado: `lacquer_red_deep` `#7A1712` |
| `bf_lacquer_red` (the ferry's) | standard, clearcoat | the sheer strake, the wale and the name-board's glyphs and emblems: `lacquer_red` `#B3261E` (≤ 8% of any frame) |
| `bf_copper_sheathing` | `env_bronze` (Tamsule's copper-alloy stack) | the sheathing: `hair_copper` `#A65A2A` darkened, worn bright on edges, `bronze_patina` verdigris gathered low and in streaks |
| `bf_copper_bright` | standard, metallic | the hold's ingots, the galley pot, the name-board's frame band and brackets: raw copper `#A65A2A` |
| `bf_canvas_tan` | weathering (`woven_panel`, painted) | the terrace sails: tanned cloth `#A8865E` (`sand_cloth` toward `sand_wet`), salt low |
| `bf_ceramic` | standard | the lamp-housing: Lit Age ceramic `#DCE3E0`, dead (no glimmer anywhere: C4-12's housing is empty) |
| `bf_rice` | standard | the half-eaten meal: `bone` `#E6DAC0` |
| `bf_membrane` | standard, glossy | the spawn membrane: wet black (`lacquer_black`), a hard sheen, double-sided |
| `bf_spawn_wound` | standard, emissive | the membrane's seams: `spawn_wound` `#3FE0C8` at a low energy (faint in daylight; the motes are VFX's) |

Reused: `bf_deck`, `bf_timber`, `bf_timber_tar` (inside the hold), `bf_rope`, `bf_iron`, `bf_brass`,
`bf_earthenware`, `bf_interior_dark`, `bf_tarpaulin`, `bf_lacquer_red` (small trim).

### 7.4 Shots (D for the derelict, act1_ch04.md §7; O07 and O13 for Ch1, act1_ch01.md §7)

| # | Lens (vFOV) | Height | Framing | About |
|---|---|---|---|---|
| O07 ◆ (Oruvel preview) | 85 mm (16.1°) | 9 m astern of the transom, 0.25 m below the board's centre, 0.6 m to starboard (ship frame) | The name-board fills the frame's middle: the terrace-script name, the two seven-step emblems, the copper band; the transom's black lacquer and the red sheer strake around it; the quarter rail above. | The plant: the board the player will see again. |
| O21 ◆ (Oruvel preview, review) | 35 mm (37.8°) | 1.4 m above the water, off her starboard quarter | The *Seventh Terrace* at the outer mooring: furled terrace sails, the stage raft alongside with its salvage, the gangplank, the counter and its board, the town's edge at the right. | She was real and busy. |
| O13 | — | — | She casts off under full sail (`terrace_sails_set`): the storm variant's frame (M3-ENV-07B, Cinematics). | |
| D01 | 35 mm | 1.6 m on the ferry's port rail | Across the gap: the fenders, the boathooks on her cap rail, her starboard chain-plates. | The jump. |
| D02 ◆ | 24 mm (53.1°) | 1.6 m above the poop, by the wheel, looking forward | The set sails overhead, the main deck, the open hatch, the galley roof, the membrane on the shrouds against the low sun. | A dead ship, sailing. |
| D03 ◆ | 50 mm (27.0°) | 1.5 m at the galley door | The table: four bowls, the pot, the benches, the hourglass. | The crew were at their food. |
| D04 ◆ | 35 mm (37.8°) | at the hatch coaming, looking down | The hold: ingots, crates, the lamp-housing on its shelf. | What Rhen sold her skipper. |
| D05 | 24 mm | low on deck under the mainmast, tilted up | The wraith (Character Art) in the membrane-webbed shrouds against the low sun through the sails. | |
| D06 ◆ | 85 mm (16.1°) | **the same point as O07 in the ship's frame** | The name-board; Rhen's hooks enter from the top (character). | Must match O07. |
| D07 | 35 mm | 1.6 m on deck | Phase 2 under the mainmast. | |
| D08 | 50 mm | 1.5 m at her starboard rail | The sea alongside, the motes going down (VFX). | |
| D09 ◆ (review) | 35 mm (37.8°) | 1.4 m above the sea, 30 m off her starboard bow | The lowered state from the sea: the sails fallen on the booms, the ferry beyond (setup toggles the state). | She is only a hull now. |

**Provisional `ch04_derelict` (until Rendering adds it):** 08:10, the sun at 15° / 100° (low in the east, ahead
of the ships' beam), key `#FFD9B0` at 2.6, sky ambient at 0.5, exposure 0.75, no grade LUT, the open-sea day water
(this preview's own material, the `lagoon_clear` scatter over a deep `#0E4A55` at absorption ×1.0), the trade
wind from the ENE. The ferry's lanterns are out. Registered baseline (at most one): **O07** (the plant).

### 7.5 Review checklist (M3-ENV-08B)

- [ ] O07 and D06 show the same board, same carving, same framing in the ship's frame.
- [ ] Reads as Pemakar (black and red lacquer, copper), not Low Reaches (no sea-blue paint on her), and as kin to
      the ferry (the same plank deck, bulwark and covering board).
- [ ] The three sail states read at a glance: furled tidy (Ch1), set and torn (under way), fallen askew (C4-14).
- [ ] No lashing between the ferry and the derelict; fenders and boathooks only.
- [ ] Red ≤ 8% of any frame; `spawn_wound` only on the membrane's seams; no glimmer anywhere on the ship.
- [ ] The deck round the mainmast is open for the boss (no prop within 1.8 m of the mast's foot).

### 7.6 The previews (M3-ENV-08B)

Ch1: `game/levels/_tests/oruvel_kit/` places her at the outer mooring with a third dresser
(`oruvel_seventh_terrace_layout.json`, generated by `ov_preview_layout.py` from `bf_terrace.py`; her stage raft is
the Oruvel kit's), views **O07** (registered baseline `oruvel_o07_name_board`) and **O21**. Ch4:
`game/levels/_tests/brightwater_ferry_kit/brightwater_derelict_preview.tscn` (HalunaMood's day mood at the
provisional `ch04_derelict` frame) with the ferry and the derelict alongside; four dressers (the ships, the set sails
and membrane, the lowered sails, the name-board) so a shot's `setup.nodes` shows a state (D09 hides the set sails, the
membrane and the board and shows the lowered sails). The night preview and its baselines are untouched. Read of the
final captures (lavapipe, 960 × 540):
- **O07** (baseline): the board centred on the deep-red counter: the two seven-step emblems, the terrace-script name
  in red relief on black, the copper band and brackets, the board's shadow on the counter; the quarter rail and the
  wheel above. Reads at a glance as a carved, lacquered name; no letter of any real alphabet.
- **D06**: the same board from the same point in her frame (the test checks it to 2 mm); the low sun rakes the counter
  with the rigging's shadows. Same carving, different hour: the match holds.
- **O21**: her starboard quarter at the mooring: black hull, red strakes, the copper boot-top green at the wet line,
  the furled terrace sails tied on the booms, the stage raft with salvage, the gangplank, the board on the counter.
- **D01** (the gap): the boathooks laid from the ferry's rail across to her cap rail, her starboard topsides, the
  galley, the wheel, the membrane dark on the shrouds above. **D02** (the deck under sail): the main's terrace sail
  over the port walkway, the galley's roof and its open smoke hatch, the ferry beyond. **D03**: the galley's table,
  four bowls with the meal half-eaten, the copper pot, under the smoke hatch's light. **D04**: down the hatch to the
  after bulkhead: the white lamp-housing on its shelf, the ingots and crates. **D09**: the lowered state from her
  port bow: the sails fallen on the booms, a bight over the port rail, the ferry beyond.
- Known limits: the provisional frame is not Rendering's `ch04_derelict`; the membrane reads as dark webs (the wraith
  and the motes are Character Art's and VFX's); the furled stacks read as tied bundles more than cloth at a distance;
  the hold is dark on lavapipe away from the hatch's light; the ships are still (no roll); collision is m2-slice's
  (`anchors.walk` in the derelict layout lists the walkable boxes).

## Revisions

- **M3-ENV-08B (env-art, after the preview):** the Seventh Terrace (§7). Changed from the first notes: her lacquer is
  the Pemakar kit's standard clearcoat (the weathering stack's lacquer-over-timber let the grain and the salt through
  and read as grey timber in the low sun); the counter is deep red so the black board stands out; the bow rise went
  from 1.25 to 1.6 m; the terrace script's glyphs became stepped-hill profiles (the first bar glyphs read as Latin
  letters and digits); O21 moved to her starboard quarter to show the mooring. Found: the ferry's transom fan
  (`bf_common.transom`) is culled from astern (the same fan built inside-out on the Seventh Terrace showed her
  interior); `bf_terrace` builds its transom as a grid instead. Not fixed in the ferry (its baselines do not see it).

- **After the preview (M3-ENV-08):** the moon moved from setting in the WSW to a waning crescent low in the east
  (a waning moon is up before the sun at 05:50), because at a deck's eye height the far sea mirrors the sky and the
  drowned, set against "the glowing sea", vanished; on the crescent's glade they read. A kit LUT
  `lut_ch04_crossing` replaces `lut_ch04_wake` in this zone (that grade greys a whole-frame sea). The hull gained a
  sheer sweep, a raked forefoot and an open quarter rail on the poop (the side view read as a box); the bowsprit
  moved beside the stem head (it ran through the stem-gull); the main's fife rail moved forward of the mast (it
  stood in front of the deckhouse door); a bow lantern was added on a crook. B03, B05 and B07 were reframed.

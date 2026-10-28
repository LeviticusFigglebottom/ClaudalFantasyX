# Ashcrown, the Lightning Temple: Design Notes

Owner and build: Environment Artist (M3-ENV-09). Lighting review: Rendering. Gameplay placement (spawns, triggers, the trial's walk, the Cinder Matron's arena, collision): m2-slice (swap-in note in the task file).
Story: [act outline Ch5 "Terraces of Ash"](../../story/beats/act_outline.md) (the temple trial: "catch a strike from the ash-plume at the crown and walk it down the stair-mountain's copper veins, tier by tier, before it fades"; Asha binds **Kahre**; the *Cinder Matron*, a magma-crusted temple guardian construct), [bible §5.2](../../story/bible.md) (stair-mountains: stepped tiers of dark volcanic stone that climb the hillside itself, each smaller than the last, crowned by a lacquered red pavilion; open-hand gates; **Ashcrown**: "a stair-mountain built into the lip of a caldera that still breathes ash. Dry storms crackle in the plume, and Lit Age copper veins the tiers, so the strikes run down the mountain like water down the terraces"), [vowbound.md §2](../../story/vowbound.md) (Kahre, once **Daro Pemakan**, a seventy-one-year-old terrace smith; a smith's hammer is his keepsake; "It's like setting the tools down"), [decisions_log N-09](../../story/decisions_log.md) (Ashcrown is Lightning, not fire: "ash-plumes breed dry lightning, so a smith's hammer-crack becomes thunder"). No Ch5 beat sheet exists yet (M3-C05-01 is in progress); these notes follow the outline and leave every gameplay placement open.
Grade: [color script](../color_script.md) `ch05` ("temple at 13:00"; its frame values are the festival night, so the day sub-frame is defined in §0). Colours: [palette.json](../palette.json). References in words only: [references.md](../references.md) §2 (Balinese and Javanese stepped terraces and volcanic stone; Thai and Burmese lacquer, gold leaf and tiered roofs).
Zone: `ch05/ashcrown` (`game/levels/ch05/ashcrown/`, m2-slice's, not built yet).
Kit: `assets_src/environments/kits/ashcrown/` → `assets/environments/kits/ashcrown/`. Preview: `game/levels/_tests/ashcrown_kit/`.
The far temple: [pemakar.md §2.4](pemakar.md) `ashcrown_silhouette` and `ash_plume` (generator `pemakar_skyline.py`). This kit is the same building up close (§0.1).

**The feeling in one line:** a black stair-mountain on the lip of a breathing crater, dusted grey, veined with green copper, and crowned in red under a plume that never stops: the oldest Cantor's forge, still warm, waiting for one more strike.

**Influences** (references.md §2): stepped volcanic-stone temple terraces that climb the hill they stand on (Balinese and Javanese) **+** black-and-red lacquer, gold leaf and a tiered roof (Thai and Burmese) **+** our own originals and transformations:
- Stepped temple mountain → **a stair-mountain whose stair flies**: the front stair does not cut into the tiers, it leaps over them on piers and arches, so the ambulatories under it stay open all the way round. That is what the trial needs (the strike is walked *round* each tier, along the copper), and it is the temple's signature line from the town.
- Lit Age conduits (Pemakar's veins in the terrace walls) → **the veins of Ashcrown**: two bands of green copper down each tier's face, joined along each ambulatory by a channel in the paving, so the copper zig-zags down the mountain like the leaf-boat channels in the town below (the same architecture of descent, in metal).
- A lightning rod → **the ash crown**: the copper spire above the pavilion ends in a ring of seven blackened copper prongs, one per tier, cupped upward like the open-hand gates' palms. It is the strike-catcher that gave the temple its name.
- A smith's forge → **the anvil hall**: the binding chamber inside the lowest tiers is a smithy for the dead. Its floor veins run to a great stone anvil, clad in copper, under a shaft that drops straight from the pavilion; the hall's far end is open to the crater, so the plume's foot glows at the end of the nave.

**Checked against the story (before any geometry):**
- Act outline Ch5, the trial: "catch a strike from the ash-plume **at the crown**" → the ash crown on the spire (§2.3); "walk it down the stair-mountain's copper veins, **tier by tier**, before it fades" → the vein path (§0.2): a continuous copper line from the crown down every tier's face and along every ambulatory, ending at the anvil. The flying stair keeps the ambulatories unbroken. The strike state is a material swap (`ac_copper_live`) on the same geometry, so gameplay can light the path tier by tier.
- Outline Ch5, Kahre: the hall is a forge (§2.4) because Daro was a smith; the anvil is the binding place. The hammer keepsake is his, not the set's: nothing in the kit is a hammer.
- Outline Ch5, the Cinder Matron: the forecourt (§0.1, 64 × 26 m, flat, open to the sky, the stair foot at its back) is the natural arena; the anvil hall is the alternative. The kit leaves both clear of clutter in their middle. Placement is m2-slice's.
- Bible §5.2: stair-mountain of dark volcanic stone, tiers smaller as they rise, red lacquered pavilion on top; an **open-hand gate** at the stair head (the Pemakar kit's gate, re-used; §2.6); copper veins the tiers; dry storms in the plume. The plume and the caldera are Pemakar's (the same `ash_plume`, the same crater), seen from 80 m instead of 900.
- Color script `ch05`: "temple at 13:00". The day frame is §0's `ch05_temple`. The LUT keeps the volcanic stone neutral-cool as the festival grade does, so the two frames read as one mountain.
- Pemakar.md: the silhouette's seven tiers, its front stair, its pavilion and spire, and its copper strips are matched number for number (§0.1). The materials are the Pemakar kit's (written again under this kit's own slot names, from the same maps; §3).

---

## 0. Layout, Orientation, and Lighting Sub-frame

**Frame (world north = −Z, +Y up, metres).** The kit's origin is **the Pemakar layout's `ashcrown_silhouette` origin**: `pemakar_skyline.massif_rim_point()`, the caldera's south lip, (0, 306.72, −682) in the Pemakar town's coordinates. Axes are the same and the temple faces **south (+Z)**, down the mountain to Pemakar and the sea. Every number below is in this frame. To place this kit in the Pemakar town frame, add (0, 306.72, −682); to place the Pemakar pieces in this frame, subtract it.

**The crater.** The caldera's centre is 78 m north of the origin (z −78), 70 m in radius; its floor is about 47 m below the lip, and the vent (the plume's foot) is in its middle at y −57 (Pemakar places the plume there). The rim behind the temple drops 11 m in the first 18 m into the bowl, so the temple's back stands right at the edge.

### 0.1 The temple's massing (matched to `ashcrown_silhouette`)

| Part | Silhouette (pemakar_skyline.ashcrown) | This kit |
|---|---|---|
| Tiers | 7; tier k scale f = 1 − k/8.5; width 58 f, depth 38 f; centre z = −1.2 k; base y −4; heights 10 (k = 0), then 6 | **Same numbers.** Tops at y 6, 12, 18, 24, 30, 36, 42. The ambulatory round each tier is 2.2 m wide at the sides and 3.4 m at the front (the 1.2 m northward step per tier). The walls are taken 8 m below y −4 as a buried footing, so the cut crest never shows a gap. |
| Parapet lips | 0.4 m lip on each tier top | A coping course 0.5 m with a dressed lip (the ambulatory's edge). |
| Copper strips | one 0.5 m strip per front face at x = ±0.3 w | **The veins** at the same x, 0.5 m wide, each tier; joined along the ambulatories (§0.2). |
| Front stair | a slab 6 m wide at about 48°, climbing every tier | **The flying stair**, 6 m wide at 48°, from the forecourt (z 39.8, y −4) to the top tier's front edge (z −1.6, y 42), 172 risers of 0.267 m. It rests on paired piers at each tier's front edge (pier heights 11.6, 9.4, 7.3, 5.1, 2.9, 0.8 m above the ambulatories), so every ambulatory runs on under it. |
| Pavilion | 4 red posts (±4 × ±3 m) on the top tier at z −8.4; a three-tier hip roof 12 × 10, 9 × 7.5, 6 × 5 m at 32°, red tile, gold ridge; a copper spire 14 m | **Same**, with 8 posts (the corners and mid-sides), a plinth 0.6 m, a lacquered ceiling, and the spire ending in the ash crown. |
| (not in the silhouette) | — | **The forecourt** at y −4 in front of tier 0 (z 19 → 45, x ±32), on a battered substructure down to the slope; **the pilgrims' causeway** climbing to it on axis; **the anvil hall** inside tiers 0 and 1. |

The silhouette floats over the slope at its front (the rim drops 42° in front of the lip: −17 m at tier 0's face, −31 m at the forecourt's edge). The near temple therefore stands on a **substructure** the silhouette leaves out: the forecourt's retaining walls (up to 27 m at the front), and the causeway. From the town, at 600 m and more, that is a dark stepped base under the same seven tiers. A follow-up for the Pemakar kit: swap `ashcrown_silhouette` for this kit's LOD1 pieces (`ashcrown_tiers`, `flying_stair`, `crown_pavilion`, `forecourt`, `pilgrim_causeway`), so the far and near temples are one mesh as well as one design.

**The approach (south to north).**
1. **The pilgrims' causeway** (the top of the pilgrims' stair, the lamp thread seen from Pemakar): the hillside stair leaves the slope about 101 m south of the forecourt (z 146) and climbs the last reach on a raised causeway of fitted volcanic blocks, straight on axis, 5 m wide, at 0.22 / 0.23 m risers with a 1.8 m landing every 32 risers (the slope falls about 0.5 m per m here, so a gentler stair never meets it). Its battered sides grow from nothing to 27 m at the top, and lamp pillars stand at every landing. Under it the mountain falls away to the town; nothing else stands this high.
2. **The open-hand gate** at the head (z 45.5): the Pemakar kit's gate, re-used at 1.6× (5.1 m forearms, palms cupped over the walk). Pilgrims step through the held space onto the forecourt.
3. **The forecourt** (y −4, z 19 → 45, x ±32): dressed volcanic paving, ash packed in the joints; a low parapet on the sides and front; lamp pillars along the sides; tier 0's two veins turn in along its foot to the hall door. It stands on **lower tiers** stepping down the slope: three battered bands (to y −12, −20, then into the slope), each with a 2.4 m ash ledge at its foot, the stair-mountain continued downhill. The flying stair's foot is 5.2 m in from the gate.
4. **Under the stair:** the flying stair's first span crosses the court and meets tier 0's face 17.5 m up. Beneath it, in tier 0's face on axis, is **the hall door** (4.5 × 6 m, a plain lintel of dressed stone and a copper threshold). The door is in the stair's shade all day.
5. **The anvil hall** (floor y −4, inside tiers 0 and 1, x ±7): the vestibule (z 19 → 15, ceiling y 2.5), the nave (z 15 → −16, ceiling y 8, two rows of five square pillars at x ±4.2, lamp brackets on the walls), the anvil at z −8.4 under the shaft, and **the crater loggia** at the north end (z −16 → −19.5): the back of tier 0 open 12 m wide and 8 m tall over the crater, a low balustrade, and beyond it the plume's foot 60 m away and 53 m down, glowing in the vent.
6. **The crown:** the flying stair, or the ambulatories and their vein stairs, climb to the top tier (y 42); the pavilion stands over the shaft; the ash crown is 64 m above the forecourt.

### 0.2 The vein path (the trial)

From the ash crown the copper runs down the spire, through the pavilion's floor into **the shaft**, and down the shaft to the anvil (the strike's short way down, which the trial does not take). On the outside, from the pavilion's plinth a vein runs to each front corner of the top tier and down the tier's face at x = ±0.3 w₆ (±5.1 m), then along the ambulatory below as a channel in the paving, outward to x = ±0.3 w₅, and down that face; and so on, tier by tier, two lines zig-zagging outward and down, like the town's leaf-boat channels. At tier 0's foot each line turns inward across the forecourt to the hall door, and inside the floor channels converge on the anvil. Walked end to end, one line is about 140 m long. **Strike state:** `ac_copper_live` (emissive `starlight` `#DCE6FF`, a faint `ember_orange` core) swapped onto the vein surfaces. Each tier's veins are their own material slot (`ac_vein_t6` at the crown down to `ac_vein_t0`, then `ac_vein_floor` across the court and the hall; all the same verdigris by default), so gameplay can light the path a tier at a time by overriding one slot.

**Water datum:** none (the sea is 307 m below). The weathering shader's tide, algae and barnacle layers are off, and the salt layer is **ash fall** as in Pemakar (pemakar.md §4), heavier here (ash falls on Ashcrown daily).

**GI recommendation:** day exterior, sky ambient plus SSAO, no SDFGI (as Haluna and Pemakar). The anvil hall is an interior lit by its openings: on lavapipe and in the zone it uses a **ReflectionProbe with interior ambient** (ambient `#2B2622` × 0.8 inside the hall's box) so the sky ambient does not flood it, plus its practicals (the forge trough at the anvil, the wall lamps) and, until GI, two daylight stand-ins (§0 table). Rendering decides the GPU tiers' GI.

| Sub-frame | Use | Time | Sun elev / az | Key | Fill | Sea-glow | LUT |
|---|---|---|---|---|---|---|---|
| `ch05_temple` | Ashcrown by day: the approach, the forecourt, the trial, the boss (A01–A08) | 13:00 | 58° / 225° (high, south-west: the tiers' west faces lit, the east faces in shade) | sun through the ash veil `#FFF0DC` (~5,200 K, `sun_noon` dulled), energy 2.8 | ambient `#8E959C` (ash haze over `overcast_slate`) 0.45; sky zenith `#5F6E80`, horizon `#C9BCA7`; distance haze `#8C8882` (exponential 0.0018) | 0 | `lut_ch05_ashcrown`: saturation ×1.0 (M3-ENV-705; was ×0.88); greens pulled to grey-olive (ash on every leaf); copper verdigris, lacquer red and ember lifted (+18%; was +6%); shadow toe cooled toward `storm_slate` `#3E4A57`; highlights roll off a little toward cream. Exposure 0.72, S-curve 0.5 |
| `ch05_temple_int` | The anvil hall (A04, A05) | 13:00 | — | the crater loggia (sky and plume); daylight stand-ins until GI: the sky down the shaft `#C9D2DA` 5 onto the anvil, the court's bounce through the door `#D9CBB8` 3; the forge trough `#E0702E` 1.6; ten wall lamps `#FFB16E` 2.4 | interior ambient `#2B2622` 0.8 (ReflectionProbe) | 0 | same LUT; exposure 1.05 |

**Lighting notes:**
- **The order of values by day:** (1) the hazy sky and the sunlit ash on every ambulatory and ledge (the pale horizontals); (2) the lacquer red and the copper; (3) the sunlit tier faces; (4) the plume's body (darker than the sky everywhere: it is a column of ash, lit on its sun side, dark under); (5) shadow under the flying stair and in the hall, which goes to `storm_slate` teal-grey, never neutral black.
- **Ash veil:** the sun is never clean: the key is dulled and softened (shadow blur up), and a distance haze (`#8C8882`, exponential fog 0.0018) swallows the town 600 m below. No volumetric god rays on lavapipe.
- **The black stone eats light.** Volcanic stone at `#3A3A3F` lit by a few oil lamps reads as nothing, so the hall needs its daylight (shaft and door) as well as its lamps; the stand-ins are shadowless OmniLights (`light_volumetric_fog_energy` 0) to be replaced by Rendering's GI choice.
- **Dry lightning** is not in the static frames. The strike (a bolt from the plume to the ash crown, a flash, the veins lit) is a gameplay effect for Rendering/VFX; the kit supplies the target point (the crown's top, §2.3) and the `ac_copper_live` material.
- **The plume** is Pemakar's `ash_plume` with its own `env_ash_plume` material; at 13:00 its ember underside is too faint to read except down in the vent, where the kit's `plume_vent` (§2.5) adds the glow.

---

## 1. Mood

A mountain made of night, under a grey sky that is falling as ash. Everything horizontal is pale (ash on the paving, on every coping, in every joint of the stair); everything vertical is near-black volcanic stone. Into that, three colours only: the green of the copper veins zig-zagging down, the lacquer red of the pavilion high on top, and, deep in the hall, the orange of a forge that has never been let go out. The plume stands behind it all, close enough to hear.

**Three quiet signs of the decline:** ash drifted knee-deep in the corners of the upper ambulatories, where nobody sweeps any more; copper vein bands broken and bridged with newer, brighter copper (repairs that are getting more frequent); and the ash crown's prongs, three of the seven bent and burned short by strikes.

---

## 2. Kit Pieces

Origins in the kit frame (§0) unless stated. Every piece is `<piece>` + `<piece>-lod1` (LOD1 from 70 m, chained per vegetation.md "One LOD at every distance"). Budgets are LOD0 / LOD1.

### 2.1 The stair-mountain
| Piece | Dimensions and parameters | Budget |
|---|---|---|
| `ashcrown_tiers` | The seven tiers (§0.1): each tier's four faces as coursed ashlar (`ac_ashlar`, 0.5 m courses; tier 0's walls run on 20 m below y −4 as a buried footing), a plinth course at each foot, a parapet coping of chamfered 2.4 m blocks (0.8 m, the silhouette's lip), the ambulatory paving on its top (ash-dusted), and the copper veins and channels (§0.2), each tier's on its own slot `ac_vein_t<k>`, with brighter repair bands. Tier 0's front face is pierced by the hall door, its back face by the crater loggia. **Vein stairs**: a steep (60°) flight 0.9 m wide down each tier's front face just outside each vein, so the trial can follow the strike down. **Buttresses** (M3-ENV-705): stepped piers every ~5 m up the front and side faces, their top third set back, clear of the door, the stair, the veins and the vein stairs. | 30,000 / 2,400 |
| `flying_stair` | 6.0 m wide, 48°, 172 risers 0.267 m on a 1.6 m-thick spine; dressed cheek walls 0.9 m high; paired piers (1.4 × 1.6 m, a dressed base and a stepped capital) on the forecourt and at each tier's front edge carrying the spine; its foot a solid flight on the forecourt (z 39.8 → 37.6). The treads are worn hollow on the centre line and ash lies at their back edges and sides. | 14,000 / 1,200 |
| `crown_pavilion` | On the top tier at z −8.4: a 0.6 m plinth 14 × 11 m, eight lacquered posts 0.5 m, a black lacquer ceiling, the three-tier hip roof (Haluna's `village.hip_roof`, re-slotted red lacquer tile and gold ridge), and the copper spire (14 m) ending in **the ash crown**: a ring of seven prongs 1.6 m tall, cupped upward, three of them bent and burned short. The conductor drops from the spire's foot into the shaft's mouth in the floor. **Strike target:** the crown's centre, top (y ≈ 64). | 9,000 / 900 |

### 2.2 Approach
| Piece | Dimensions and parameters | Budget |
|---|---|---|
| `forecourt` | The court at y −4, z 19 → 45, x ±32: dressed volcanic paving slabs (1.2 × 0.9 m courses, set out from the axis), ash in the joints; the copper channels from tier 0's foot to the door; a 0.7 m parapet on the sides and the front (open 5 m on the axis for the gate); the substructure below: battered retaining walls (8°) of coursed ashlar down to y −60 (they bury into the slope). | 14,000 / 1,000 |
| `pilgrim_causeway` | The pilgrims' stair's last reach: from the gate (z 45, y −4) south and down, 4 m of stair between 0.5 m cheek walls, risers 0.22 / goings 0.23, a 1.8 m landing every 32 risers, on a battered causeway (10°) of coursed ashlar whose sides go 3 m into the slope; 101 m long, until the stair meets the hillside. Treads worn, ash at the risers. | 11,000 / 700 |

### 2.3 The anvil hall
| Piece | Dimensions and parameters | Budget |
|---|---|---|
| `anvil_hall` | The interior shell (seen from inside only): the vestibule (ceiling y 2.5), the nave and the crater loggia (§0.1, item 5); paving with the copper floor inlay converging on the anvil; walls with a pilaster at every pillar and a stone lamp bracket (dish and flame, soot above) between; ten square pillars 1.0 m with stepped capitals (the anvil's bay has none), each with corner beads, a framed sunk panel on every face between two copper bands, and a red lacquer frieze edged in gold leaf under the capital (M3-ENV-705); a beamed ceiling at y 8 with the shaft's mouth (3 × 3 m) over the anvil and the shaft itself up to the pavilion; the loggia's balustrade (0.9 m). | 20,000 / 1,400 |
| `anvil_altar` | The binding place at z −8.4: a stepped plinth 5.0 × 3.6 m, the anvil stone (3.0 × 1.4 × 1.2 m, one waisted block lofted round a rounded rectangle, with a copper-clad horn), copper bands at its foot and waist (the waist band renewed), straps over the top, a strike-scar of fused copper across its face, a forge trough in front (2.5 × 0.6 m, `ac_forge_glow` embers), and the conductor rod from the shaft to the anvil's back. | 5,000 / 500 |

### 2.4 Ground and crater
| Piece | Dimensions and parameters | Budget |
|---|---|---|
| `crest_ground` | The zone's terrain, in place of the Pemakar massif: `pemakar_skyline.massif_height` (read-only) sampled on a polar grid round the origin, 0.6 m apart near the temple and coarsening to 120 m at 1,100 m out, with fine rock detail and ash (VC.G) on the near part; carved under the temple's footprint (to y −8) and under the forecourt and causeway (their walls cover the cut). It runs down to the town and the sea in the south and into the crater in the north. | 40,000 / 6,000 |
| `plume_vent` | The plume's foot in the crater floor (at z −78, y −57): a spatter cone 30 m across with a glowing throat (`ac_vent_glow`) and cinder slopes, sized to sit inside `ash_plume`'s base. | 3,000 / 400 |

### 2.5 Re-used (not in this kit)
Pemakar kit, placed by layout (read-only): `ash_plume_near` (M3-ENV-11: `ash_plume`'s surface, dense, for close views; at (0, −56.7, −78), as Pemakar places `ash_plume`), `open_hand_gate` (×1.6 at the causeway head), `lamp_pillar` (forecourt sides and causeway landings). Vegetation: none on the crest (ash has killed it); a fern or a sugar-palm on the lower causeway would help, on the wish list with Pemakar's.

---

## 3. Materials (against palette.json)

One `.tres` per slot (`ac_materials.py`), written with the Haluna kit's writers (by path) from the Pemakar kit's maps where the material is the same stone, so near and far are one material.

| Slot | Shader | Palette | Notes |
|---|---|---|---|
| `ac_ashlar` | weathering | `volcanic_stone` `#3A3A3F` | This kit's map `ashlar_courses` (2.4 × 1.0 m: 0.5 m courses of 0.6–1.4 m blocks, tight joints, pitted faces); ash fall on G, heavy; moss off (too high and too much ash); orange lichen spots 6%. |
| `ac_dressed` | weathering | `volcanic_stone` +1 | Copings, piers, the stair's treads and cheeks, the hall's walls and pillars: Pemakar's `volcanic_stone` map, tile 0.7 m, shallower pits. |
| `ac_paving` | weathering | `volcanic_stone` +1 | This kit's map `paving_slabs` (1.2 × 0.9 m slabs with ash-filled joints); ash coverage 0.4–0.85. |
| `ac_ground` | weathering | ash over `volcanic_stone` | Pemakar's `ash_soil` map; the crest and the crater slopes. |
| `ac_ground_far` | weathering (no detail) | `volcanic_stone` | The lower mountain: as `kit_volcanic_far` (moss bands on the terraces below), 8 m tile. |
| `ac_cinder` | weathering | `volcanic_stone` −1, `laterite` flecks | The vent cone: dark cinder, rust-red oxidation. |
| `ac_vein_t0` … `ac_vein_t6`, `ac_vein_floor`, `ac_copper_vein` | Standard | `bronze_patina` `#5F8A78` | Verdigris: metallic 0.35, rough 0.55 (as Pemakar's `kit_copper_vein`). One slot per tier so the strike can light the path a tier at a time; `ac_copper_vein` is the spire, the conductor and the anvil's cladding. |
| `ac_copper_new` | Standard | `hair_copper` `#A65A2A` | The newer repair bands, the ash crown's burned tips, the threshold. |
| `ac_copper_live` | Standard, emissive | `starlight` `#DCE6FF` | The strike state (not on any mesh by default; gameplay swaps it onto the vein slot). |
| `ac_lacquer_red`, `ac_lacquer_black`, `ac_gold_leaf` | Standard | `lacquer_red`, `lacquer_black`, `gold_leaf` | Pavilion. Red ≤ 8% and gold ≤ 3% of any frame. |
| `ac_forge_glow` | Standard, emissive | `ember_orange` `#E0702E` | The forge trough (emission 3). |
| `ac_vent_glow` | Standard, emissive | `ember_orange` → `oil_lamp` | The vent's throat (emission 2.5). |
| `ac_soot` | Standard | `lacquer_black` | Soot on the hall's ceiling over the trough, the shaft's walls. |
| `ac_interior_dark` | Standard | `#2B2622` | The shaft's depth. |
| `ac_wick_flame` | Standard, emissive | `oil_lamp` `#FFB16E` | The hall's lamp flames (emission 8). |
| `ac_plume_day` | env_ash_plume (Pemakar's shader) | `overcast_slate` body, `ash_fall` aloft | The preview's noon parameters for Pemakar's `ash_plume_near` (the kit's own material, overriding `kit_plume` by placement): paler, softer-edged, the ember kept low to the vent; solid (opacity 1, alpha_mottle 0.04); and the shader's `near` group (M3-ENV-11): a `#98A4B0` sky lift 0.3 (0.6 of it all round), back-scatter 0.5, the vent's ember 0.9 on the lowest 10%, billow shading 0.6, sky-up 0.6, the bumped billow normal (9 m heads, 0.8) inside 80–240 m, all gone by 800 m. |

**Ash** is the proposed `ash_fall` swatch `#8C8882` (pemakar.md §3), still for the Art Director to adopt.

---

## 4. Weathering (the haluna.md §4 stack, as Pemakar re-purposes it)

Vertex colours **R moss, G salt (here ash), B wet, A erosion**. Tide, algae and barnacles off. G (ash) is written by the generator from the upward normal × noise (Pemakar's `ash_pass`, read-only), heavier than in the town (amount 0.95, floor 0.1): ash lies on every tread, coping and capital, drifts into corners and the backs of treads. R carries only lichen (sun-facing faces, sparse). B is unused (no water at the crown). A (erosion) as Haluna, edges lightened 4%.

---

## 5. Composed Camera Shots

Conventions as haluna.md §5: lens is full-frame equivalent; Godot `Camera3D.fov` is vertical, vFOV = 2·atan(12 / mm). Height is above the local floor or ground. ◆ marks the shots built in the kit preview; ★ those registered as screenshot baselines.

| # | Sub-frame | Lens (vFOV) | Height | Framing | What the shot is about |
|---|---|---|---|---|---|
| A01 ◆★ | `ch05_temple` | 18 mm (67.4°) | 1.6 m on the causeway's top landing, 1.7 m south of the gate, tilted up 31° | Looking **north** up through the open-hand gate: the two forearms and cupped palms frame the flying stair, which runs from the court up the axis over the seven tiers; the veins zig-zag down the tier faces either side; the spire's tip above the stair head; the plume rising behind, leaning west (left). | Arrival: the trial waiting at the top of a stair you climb on your hands. |
| A02 ◆ | `ch05_temple` | 28 mm (46.4°) | 1.7 m at the forecourt's south-east corner | Looking north-west across the ash-drifted paving to tier 0's face and the flying stair's first span; the hall door dark under it; lamp pillars down the court's side; the copper channels leading to the door. | The court where the guardian waits. |
| A03 ◆ | `ch05_temple` | 35 mm (37.8°) | 1.6 m on the forecourt, west of the stair foot | Under the stair: the spine and the first pier overhead, the hall door in shade, a slice of sunlit ash beyond. | Going in under the stair. |
| A04 ◆★ | `ch05_temple_int` | 24 mm (53.1°) | 1.5 m in the nave, just inside the vestibule | Looking **north** down the nave between the pillars: the floor veins converge on the anvil and its glowing trough in the middle distance; the shaft's pale light falls on it; beyond, the crater loggia frames the plume's foot glowing in the vent, the bowl's far wall and the column rising out of frame. | The forge at the plume's foot. |
| A05 ◆ | `ch05_temple_int` | 50 mm (27.0°) | 1.8 m, 6.5 m south-east of the anvil | The waisted anvil with its horn and copper bands, the trough's embers in the foreground, the conductor rod rising into the shaft; the loggia's balustrade and the crater beyond. | Setting the tools down. |
| A06 ◆ | `ch05_temple` | 28 mm (46.4°) | 1.6 m on tier 2's front ambulatory, west of the stair | Looking east along the ambulatory: the copper channel in the paving leading to the next vein band, tier 3's face on the left with its vein; the flying stair crossing overhead on its pier; the mountain falling away on the right to the haze. | Tier by tier: the path the strike will take. |
| A07 ◆ | `ch05_temple` | 24 mm (53.1°) | 1.6 m at the flying stair's head (the top tier's front edge) | Looking **south** and steeply down the flying stair: its cheek walls run to the court small below and the gate at its edge; the mountain falls away beyond into the haze where Pemakar is. (From the pavilion's plinth the stair and the court are hidden below the top tier's edge.) | The whole pilgrimage of the chapter, seen from the top. |
| A08 ◆ | `ch05_temple_int` | 24 mm (53.1°) | 1.7 m in the hall, just north of the anvil's plinth | **The crater loggia** (restored, M3-ENV-11): the loggia's dark piers, lintel and balustrade frame the plume's near face, 8 m beyond the balustrade and filling the opening: a wall of rolling ash heads lit by the sky, the temple's shadow across it. | The plume, close enough to hear. |
| A10 ◆★ | `ch05_temple` | 28 mm (46.4°) | 1.6 m on the crater's west outer slope, 110 m west of the temple, below the rim | The plume close: the column rising over the crater's lip, lumpy with heads, its sunlit west side against the veiled sky; the temple's tiers and the ash crown on the right edge. (Was this table's A08, "on the crater rim west of the temple"; on the rim itself the column is 20 m away and fills the frame.) | The thing they came to catch. |
| A09 | strike | 85 mm (16.1°) | from the forecourt | The ash crown at the moment of the strike, the veins lit to the first tier. | The trial (Rendering/VFX; the kit gives the target and the material). |

The preview adds two overview cameras that are not composed shots: **O1** (35 mm, 110 m south-east and 40 m up: the whole stair-mountain on its lower tiers, the crater and the plume) and **O2** (50 mm, 560 m south and 230 m down: the temple as the town sees it, under the plume).

---

## 6. Review Checklist for This Zone
- [ ] Grayscale value check: pale horizontals (ash) and dark verticals (stone) read in every exterior shot; one focal shape each (the stair line, the anvil's glow).
- [ ] The near temple matches the silhouette: seven tiers, sizes, heights, the stair's line, the pavilion and the spire (§0.1; a test checks the numbers).
- [ ] Red ≤ 8% and gold ≤ 3% of any frame; volcanic stone neutral-cool, not brown; copper reads green, with a few bright repair bands.
- [ ] Shadows (under the stair, in the hall) go teal-grey, never neutral black.
- [ ] The vein path is continuous from the crown to the anvil, and no stair or pier breaks an ambulatory.
- [ ] Nothing in the kit is a hammer (the keepsake is Kahre's), and no Vowbound or glimmer emits on screen.

## 7. The Preview (M3-ENV-09)

`game/levels/_tests/ashcrown_kit/` (README there): all nine views captured on lavapipe and iterated; baselines `ashcrown_a01_approach` and `ashcrown_a04_anvil_hall`. An honest read of the final frames:
- **A01** (★) is the strongest: the open hands frame the flying stair and the stepped tiers, the veins read as green zig-zags, the plume stands behind. The forearms are near-black silhouettes, and the pavilion hides behind the stair head (only the spire's tip shows), which is the geometry seen from below.
- **A04** (★) reads as a forge for the dead: the floor inlay leads to the glowing trough and the anvil, the pillars march to the loggia, the plume stands like a grey wall at the nave's end. The conductor rod is a bright vertical in the middle of the frame (lit by the shaft stand-in).
- **A02, A03** read (the stair's diagonal, its shadow on tier 0, the door under the first span); the court is empty (it is the boss's floor). **A05** reads as an anvil with its horn, bands and embers. **A06** is plain (a walk, a wall, a vein, haze). **A07**'s background is a flat haze: the lower mountain has no detail at that distance. **O1** shows the massing and the lit plume well; in **O2** the plume's billows show facets.
- Weak points: the noon is flat by design (the ash veil), so the frames depend on the pale-ash horizontals against dark walls; the Pemakar plume, made for 900 m, shows sharp facets closer than about 300 m and is near-black on its shaded side; the walls are textured planes (no per-course relief); the lower slope is untextured at distance.
- **M3-ENV-11 (the near plume):** the plume is now `ash_plume_near` with the `near` shader group. **A10** is the best plume frame: a column of rolling heads over the crater's lip, its sunlit side modelled, the temple and crown on the right. **A08** (the crater loggia) reads as a wall of ash heads in the loggia's frame; it is soft and plain (the near face is 8 m away and in the temple's shadow all day, so only the sky lift and the bumped heads model it). **A01** and **A04** improved (A01's black shards are gone; A04's loggia no longer shows the crater rim through the plume). **O1** is smooth with a lifted shade side; **O2** still shows a few torn shards high in the column (edge-faded overhangs, not facets). The vent's foot is never in frame from the hall (the balustrade hides it).

## Revisions
- 2026-10-24 (env-art, M3-ENV-09): first version, before geometry. Defines the `ch05_temple` and `ch05_temple_int` sub-frames (the colour script's `ch05` row is the festival night); records the substructure the silhouette leaves out and the Pemakar follow-up (swap the silhouette for this kit's LOD1).
- 2026-10-24 (env-art, M3-ENV-09, after the lavapipe passes): as built. The sun moved to 58° / 225° and cooled to `#FFF0DC` 2.8 (at 66° / 200° the south faces were flat and the tiers had no modelling); the haze is an exponential 0.0018 (0.008 hid the crest at 100 m). The causeway is steeper (0.22 / 0.23 m, landings every 32 risers) and 101 m long: the slope falls about 0.5 m per m, so the first stair never met it. The forecourt stands on three stepped lower tiers (one 56 m wall read as a pedestal). The corner stairs became **vein stairs** beside each vein (the trial follows the strike down); the stair's lamp niches and the hall's niches are lamp brackets or left out. The hall needed daylight stand-ins (§0) and the `ch05_temple_int` exposure. A01 moved to the gate (18 mm) and A07 to the stair head; O1 and O2 added as overviews. §7 added.
- 2026-10-24 (env-art, M3-ENV-09B): the Pemakar follow-up is done. Pemakar's preview layout and the Lanternfall arena place this kit's `ashcrown_tiers`, `flying_stair`, `crown_pavilion`, `forecourt` and `pilgrim_causeway` at the rim point (this kit's origin), LOD1 from 600 m as in this preview, instead of `ashcrown_silhouette`; Pemakar keeps its own massif as the ground (no `crest_ground` there).
- 2026-10-24 (env-art, M3-ENV-11): the crater-loggia view is back as **A08** (from the hall, framed by the loggia; the original A08 rim view is **A10**, moved down the west outer slope). The plume is Pemakar's new `ash_plume_near` (pemakar.md §2.4), LOD0 to 900 m, with `ac_plume_day`'s near parameters (§3). Baselines A01 and A04 re-approved for the plume only; A10 registered as the near plume's baseline (A08 is A04's loggia from closer, which A04 already guards).

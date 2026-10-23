# Visual References (words only)

Owner: Art Director (M1-ART-01). SPEC §2, §3.1, §7.1.

**Guardrail.** This file contains no images, no links to images, no traced shapes, and no copied text. It describes the general qualities of *Final Fantasy X* (Square, 2001) and its published concept art as remembered principles, at the level of genre and mood, which SPEC §2 permits. This is the only file under `docs/kb/art/` that may name the inspiring game. Every other art doc speaks in our own terms. Do not add screenshots or "for reference" downloads here or anywhere else in the repo.

Our thesis (SPEC §7.1): **painterly realism, saturated by sun and water, lit by the dead.**

---

## 1. What the inspiring art does well (and what we take from it)

### 1.1 Palette tendencies
- **Saturated warm highlights over cool shadows.** Daylight scenes in the concept paintings put sunlight at a warm cream to pale gold and shadows at teal or blue-violet. There is almost never a neutral grey shadow. *We take:* teal-tinted shadow toe in every daylight LUT (`deep_teal_shadow`, `#0E4A55`).
- **Turquoise water as the dominant hue** of coastal scenes. It is brighter and greener than real deep ocean, and it shades from near-white over sand to sapphire in a band only a few metres wide. *We take:* a depth-graded water ramp (below, §1.7).
- **Accent triad: gold, red lacquer, turquoise.** These are used sparingly on costume and architecture against large fields of sand, stone, sky, and water. *We take:* hard frame-area limits on gold (≤5%) and lacquer red (≤8%), set in [`palette.json`](palette.json).
- **Festival color is achieved with many small saturated notes** (banners, cloth, flowers), not with saturated large surfaces. The large surfaces stay pale and sunlit.

### 1.2 Value structure
- **High-key daylight:** about 60–70% of a daytime frame sits in the upper value range (sky, sand, sunlit stone). The darks are concentrated in one or two shapes (a doorway, foliage, a figure's hair) that frame the focal point.
- **Night is not dark, it is blue.** Night scenes keep readable mid-values in blue and teal, with the spectral glow (glimmer motes) and oil flames supplying the brightest values in the frame. Pure black is reserved for very small accents. The measurable night value order, in which the sea-glow is the brightest *water* value, is in the color script, rule 3.
- **Figures read against the background by value first and hue second.** A dark-haired character is set against a bright sky, and a pale costume against dark foliage. *We take:* every composed shot gets a value-check (the grayscale debug view) before any color review.

### 1.3 Silhouette language
- **Characters are identifiable from silhouette alone,** through one or two oversized, asymmetric elements per character: a single huge sleeve, one armored shoulder, a long staff, a trailing sash, a distinctive hairstyle. The body underneath is realistically proportioned.
- **Props extend the silhouette vertically or diagonally** (staffs taller than the bearer, swords worn on the back at an angle), so a group shot reads as a set of distinct shapes.
- **Creatures** are grounded in real animals (rays, crabs, birds, big cats) with one supernatural exaggeration (scale, a glowing organ, an armored crest).

### 1.4 Costume asymmetry principles
These are the principles we extract for our own designs. They are not descriptions of any existing costume.
1. **One side carries the story.** Concentrate ornament, length, and color on one side (one sleeve, one pauldron, one leg wrap), and leave the other side bare or simple. A ratio of about 70:30 of visual weight works well.
2. **Mix registers.** A grounded, culturally specific base garment (a wrap-skirt, a vest, a sash) carries one bold fantasy element in a different material (gauze, lacquer, oversized metal).
3. **Belts, straps, and sashes cross the body diagonally,** breaking up the symmetry of the torso and leading the eye toward the face.
4. **Skin is part of the design.** A bare shoulder or forearm is a deliberate value and color shape (and a place for tattoos and bands), not an absence.
5. **Silhouette over surface.** The design must read at 64 px tall in grayscale. Detail (embroidery, gold thread) is only a reward at close range.

### 1.5 Architecture motifs
- **Organic curves meet heavy masonry:** sweeping curved roofs over massive stone bases, arches rounded rather than pointed, and water channels and pools built into the architecture.
- **Ruins are always partly drowned or overgrown.** Doomed grandeur is the default, with intact sacred buildings set against them.
- **Sacred spaces use vertical light:** a single shaft from an oculus or a gap in the roof, falling on water or a statue.
- **Scale contrast:** human-sized villages next to colossal ancient structures, so the past feels bigger than the present.

### 1.6 Sky and cloud treatment
- **Enormous skies** that take up 40–60% of exterior frames, holding big, sculpted cumulus with hard sunlit tops and soft blue-lilac undersides (`cumulus_shadow`, `#8FA7C4`, never grey).
- **Atmospheric perspective is strong:** distant islands fade to a pale cyan-blue within 2–4 km, which flattens them into layered silhouettes.
- **Sunset skies** are gold and orange at the horizon going to deep blue at the zenith, with almost no pink or magenta. *We take:* the LUT clips hue drift toward magenta in sunset frames.

### 1.7 Water color by depth
The remembered quality is luminous turquoise shallows over pale sand, deepening fast. Our target ramp (sunlit, noon, clear water over white sand):

| Depth | Color | Swatch |
|---|---|---|
| 0–0.3 m | near-transparent, sand shows through tinted pale aqua | sand plus `turquoise_shallow` at 20% |
| 0.3–1 m | luminous turquoise | `turquoise_shallow` `#3FD0C9` |
| 1–4 m | lagoon teal | `lagoon_teal` `#1FA3A6` |
| 4–15 m | reef blue | `reef_blue` `#1569A0` |
| 15–30 m | deep teal | `deep_teal_shadow` `#0E4A55` |
| > 30 m, or night | abyss | `abyss_navy` `#061A2B` |

The shader gets there with tuned absorption (the validated water looks per frame are in the [color script](color_script.md), "Water looks"), and the art target checks the result against this ramp. The ramp's hexes are **inputs**. Compare screenshots against their `onscreen_hex` in palette.json (README.md, "Two kinds of colour value"). Caustics are bright and sharp in the 0.3–4 m band.

### 1.8 How light from the dead reads at night
- In the inspiring art, the spirits of the dead appear as **drifting colored motes** that make night scenes feel sacred rather than frightening. They are soft and luminous, they gather in large numbers at rites, and they bloom gently.
- **We change it** with our own story logic: mote *direction and hue* carry meaning. Rising, warm pale-gold motes mean released, and sinking, cool cyan motes mean held (see the color script's narrative light rules). And our sea always glows faintly at night, because the dead have been sinking into it for a thousand years.
- At night the glimmer glow is the brightest value in the frame, and everything else is lit to support it: blue-navy fills, faint teal sea-glow from below (the brightest value *of the sea* and the frame's one teal field, not of the frame: color script rule 3), and warm oil-lamp pools as the only counterpoint.

### 1.9 UI quality
A clean, translucent deep-blue menu style with thin light linework and soft gradients. We take only the *qualities* (translucency, deep blue, thin lines, calm motion), and redesign the layout, ornament, and iconography from scratch (see [ui.md](ui.md)).

---

## 2. Real-world cultural influences (to combine, never to replicate)

SPEC §3.1 and bible §5. Every zone **combines at least two influences** and adds one original idea that belongs to its own culture. **No real sacred site, temple plan, deity image, sacred symbol, or ritual garment is reproduced one-to-one.** Influences guide material, silhouette, construction logic, and texture. Treat each tradition as a living culture, not a costume box.

| Influence | What we borrow (material and construction level) | What we never do |
|---|---|---|
| **Okinawan and Ryukyuan coastal villages** | Low houses with red clay tile roofs mortared in white lime. Coral-stone walls, curved and dry-stacked. Windbreak planting. Stone guardian figures on roofs, which we transform into our *lintel-gull*, a wooden seabird. | Copying specific guardian figures or recognizable shrine layouts. |
| **Polynesian navigation and tattoo traditions** | Star-path navigation as a cultural idea. Bands and linear motifs on forearms, **designed fresh** as reach-bands (one band per voyage). Outrigger and lashed-hull construction. | Reproducing real tattoo motifs, which carry genealogy and meaning for living families. Our bands are plain geometric rings with original tick patterns. |
| **Balinese and Javanese temple architecture** | Stepped terraces climbing hillsides. Split and paired gateways, transformed into our open-hand gates. Volcanic stone. Water temples and channel systems. | Copying split-gate profiles, temple plans, or carved deity figures. |
| **Khmer stone ruins** | Laterite and sandstone galleries, corbelled passages, carved faces at monumental scale (transformed into our Watchers, which have closed eyes and open mouths), and trees growing through stone. | Copying a specific temple's face towers or bas-relief compositions. |
| **Thai and Burmese lacquer and gold leaf** | Black and red lacquer with gold-leaf figuring, tiered roofs, gilded signboards, and the lacquer-box craft. | Reproducing Buddhist iconography, stupa profiles, or specific religious objects. Our bowl-domes are inverted bowls, an original form. |
| **Andean high-altitude culture** | Many-sided fitted mortarless stone, terraces, dense woven textiles, knotted cord records (transformed into our keth), and llama-like pack animals (our woolbacks). | Copying specific textile designs or site layouts. Our weave patterns are original tide patterns. |

**Process rule:** when a design sheet cites an influence, it must also name the original transformation, for example "Ryukyuan roof-guardian → lintel-gull: a seabird, wood not ceramic, facing the sea not the street."

---

## 3. What we must NOT do

1. **No chibi, super-deformed, or toy-like proportions.** Heroes are 7–7.5 heads tall, with eyes only 10% larger than realistic. No oversized hands or feet, no rounded "vinyl figure" forms, and no candy-plastic materials.
2. **No comedic staging or rendering.** No sweat-drops, no anime vein marks, no cartoon impact frames, no comedic fall-overs, no squash-and-stretch on humans. Humor lives in dialogue and performance, never in the rendering (pillar 1).
3. **No pixel-copied UI.** No reproduction of the inspiring game's menu layouts, window frames, cursor shapes, fonts, icon shapes, or battle-window placement beyond what SPEC §7.6 mandates by function. The window shape, corner, cursor, and icons in `ui.md` are original.
4. **No copied designs.** No costume, creature, summon, weapon, or building that a fan of the inspiring game could name. If a reviewer says "that's X," redesign it. Do not argue the point.
5. **No reference images in the repo, ever:** no paintovers of copyrighted frames, and no "temporary" mood boards. Describe things in words here.
6. **No asset packs, CC0, or generated imagery** (SPEC §2, §16 Q5). Every texture comes from a script or shader in the repo.
7. **No neutral-grey daylight shadows,** no pure-black crushed nights, and no magenta sunsets.
8. **No real sacred iconography,** including the Order's Level symbol used carelessly. The Level is ours, and it appears only on Order objects.
9. **No grimdark desaturation in Act I** to signal seriousness. The sorrow comes from beauty with an ending, not from mud.
10. **No glimmer used as generic "magic sparkle."** Every mote obeys the direction and hue rule. Spell VFX that are not glimmer use their element's own color language and must never be gold rising motes (that look is reserved for release).

# Asha Velamir: Design Sheet

Owner: Art Director (M1-ART-01). Build: Character Artist (M1-CHR-01, M1-CHR-02). Shaders: Rendering (M1-RND-04).
Story source: [`story/characters/asha_velamir.md`](../../story/characters/asha_velamir.md). Colors: [`palette.json`](../palette.json).

**One-line read:** a slender, very upright young woman who stays still while everyone moves. A tall dark staff on her right, a pale gauze sleeve trailing from her right shoulder to her knee, a bare left shoulder with a long black braid over it, and a black-and-gold high collar. White, sea-blue, black lacquer, and gold.

**Status:** this sheet is the M1 hero target (SPEC §10.2). This sheet sets the shared conventions that Rhen and Toma reuse: **§6 face shapes**, **§4.2 mask packing**, and **§8 budgets**.

---

## 1. Proportions

| Measure | Value | Notes |
|---|---|---|
| Height (barefoot) | **1.63 m** | Sandals add 1 cm. |
| Head height (vertex to chin) | 0.222 m | **7.34 heads**, inside the SPEC §7.3 range of 7–7.5. |
| Shoulder width (acromion to acromion) | 1.62 heads (0.36 m) | Slender, not frail. |
| Waist / hip width | 1.10 / 1.45 heads | |
| Crotch height | 3.55 heads from the floor | Slightly long legs, about +2% over the realistic base. |
| Arm span | 1.00 × height | |
| Hand length | 0.78 head | Realistic. No enlargement. |
| Neck length (chin to sternal notch) | 0.42 head | A long neck that the high collar frames. |
| **Eyes** | **eyeball and palpebral fissure scaled ×1.10** (fissure 30 → 33 mm, iris 11.7 → 12.9 mm) | Keep the interpupillary distance realistic (62 mm). Move the inner canthi 1 mm closer to the midline so the eyes don't read as wide-set. |
| Posture | Spine neutral, chin level, shoulders down and back, weight centered | Her default idle is *stillness*: idle sway amplitude is 40% of the party default. |

**Stylization limits:** skin is slightly painterly (see §8 shader notes). No other features are enlarged. Lips are realistic, nose is realistic and slightly narrow at the bridge, and hands and feet are realistic.

---

## 2. Silhouette from Three Angles

**Read test:** in a flat black silhouette at 64 px tall, Asha must be identifiable against all six other party members by the staff, the sleeve flag, and the braid line. Check in Godot with the silhouette debug view (unshaded black material on a white background) at 64, 128, and 256 px.

### 2.1 Front (0°)
- A **tall, narrow vertical**. The staff, held in her right hand, rises 0.32 m above her head, and its lantern cage makes a small open diamond at the top. It is the highest point of any party group shot.
- **Right side (viewer's left):** the verse-sleeve hangs from the shoulder as a long, pale, semi-transparent flag that ends at the knee. It is the widest part of her silhouette below the shoulder (0.22 m wide at the cuff, flaring).
- **Left side (viewer's right):** a clean bare shoulder curve, crossed by the dark braid falling over the front of the shoulder to the hip.
- The **collar** stands 6 cm above the neckline, which gives a crisp vertical neck shape.
- The **wrap-skirt** flares into an A-line. The hem is asymmetric: mid-calf on the left, ankle on the right, which echoes the sleeve's diagonal weight.

### 2.2 Three-quarter (45°, her right side toward camera: the hero angle)
- The sleeve and the staff overlap into one strong mass on the near side. Keep 6–10 cm of air between them in the idle pose so they don't merge.
- The collar reads as a curved lacquer plane catching a sharp specular highlight. The gold wave figures run from the right shoulder diagonally to the left hip.
- The sash tails hang from the right hip, adding a second, shorter vertical next to the sleeve.

### 2.3 Profile (90°)
- A straight, upright line from heel to crown, with a slightly lifted chest.
- The sleeve trails behind the arm in motion and hangs straight at rest. The braid is visible as a thick rope over the front of the left shoulder.
- The skirt's wrap overlap shows as a stepped layer at the left front: the white under-layer is visible below the blue.
- The staff is held slightly forward of the body (5–8 cm), so in profile it reads as a separate line, never as a spine.

### 2.4 Back (180°, for field walking)
- A bare left shoulder blade, and the braid is *not* visible from the back (it hangs in front). Instead, the tortoiseshell comb shows as a small warm shape behind her left ear.
- The vest has a deep scoop at the back to mid-shoulder-blade and is laced in gold cord. The sleeve's attachment ring shows on the right shoulder.

---

## 3. The Asymmetric Hallmark: the Verse-Sleeve

A single **white gauze sleeve** on the right arm, attached at the shoulder by a gold-thread cuff ring and trailing to the knee (0.95 m from shoulder seam to cuff tip). **One band of embroidery is added for each verse learned** (story sheet). It is the game's clearest piece of visible growth (pillar 5) and its clearest visible loss.

### 3.1 States
The sleeve is one mesh and one texture set. States are driven by a single shader uniform, `verse_count` (int, 0–7), plus one dissolve parameter. **Do not build separate meshes per state.**

| State | When | `verse_count` | Band added (from the shoulder downward) |
|---|---|---|---|
| S0 | Ch2 to Ch3 before the shrine | 0 | Blank gauze. Gold cuff ring only. |
| S1 | After Ilun (Ch3) | 1 | **Net-knot band**: a knotted-net lattice in `sea_blue_cloth` silk, with gold-thread knot points. |
| S2 | After Kahre (Ch5) | 2 | **Hammer-and-spark band**: stepped spark tiers in `lacquer_red` silk, with gold edges. |
| S3 | After Virel (Ch8) | 3 | **Kite-line band**: zigzag sailcloth panels in white-on-white satin stitch, with gold flame lines. |
| S4 | After Nhoa (Ch11) | 4 | **Root-and-mote band**: mangrove-root curls in `glimmer_bound`-tinted silk, with gold dots. |
| S5 | After Hesk (Ch12) | 5 | **Cord-knot band**: keth-style knot rows in `bone` silk, with gold wrap. |
| S6 | After Ethren (Ch13) | 6 | **Ring band**: interlocked rings in gold thread only (the only all-gold band, for Corran's ring). |
| S7 | After Kesh (Ch16); the Prologue and Ch19 | 7 | **Seven-mouth band**: seven open mouths, each stitched in the color of the earlier bands. |
| S8 | During and after the Letting (Ch21 onward) | 7 → dissolve | The sleeve **unravels into rising motes** (`glimmer_lift`), from the cuff upward over 6 s. After that, no sleeve: the bare right arm shows a faint gold-thread pressure mark at the shoulder. *(A proposal to Cinematics and Narrative. The story sheet says "the sleeve is gone"; this stages how it goes.)* |

**Band geometry:** each band is 9 cm tall with 3 cm of blank gauze between bands, starting 8 cm below the shoulder seam. Seven bands take up 8 + 7 × 9 + 6 × 3 = 89 cm, so the last band ends 6 cm above the cuff tip. Bands sit only on the outer face of the sleeve (an arc of 220°), so the inner face stays sheer.

**Material:** a single layer of gauze with alpha 0.55 (dithered, TAA-resolved, the same technique as hair) and a double layer at the cuff ring and the bands, where alpha is 0.95. Sheen color `gauze_white`, sheen roughness 0.5. Embroidered bands are opaque, raised by a 0.6 mm normal-map relief, and carry the embroidery and gold-thread mask channels (§4.2). Under rim light, the sheer gauze must glow: rendering adds a backscatter (transmission) term of 0.35 to the sleeve material.

**Secondary motion:** a spring-bone chain of 6 bones (shoulder to cuff), stiffness 0.35 and damping 0.6, plus a wind response of 0.6× the global wind uniform. In battle, the cast animation lifts the sleeve on a scripted arc. Don't rely on simulation for the hero pose.

---

## 4. Costume Layers and Materials

### 4.1 Layers (inner to outer)
| # | Piece | Material | Color callout | Mask channels | Notes |
|---|---|---|---|---|---|
| 1 | Under-bodice (a wrapped band top under the vest) | Fine cotton | `gauze_white` `#EBE7DF` | A sheen 0.3 | Visible at the scoop back and under the left arm opening. |
| 2 | Inner skirt | Cotton lawn, ankle length | `gauze_white` | A sheen 0.3 | Shows at the left wrap opening and the left hem. |
| 3 | Outer wrap-skirt | Dyed cotton, wrapped right over left | `sea_blue_cloth` `#3C78A8`, **dip-dyed** to `indigo_dye` `#2B3A6B` over the bottom 18 cm | R embroidery on a 4 cm hem band (a wave-tick border) · A sheen 0.4 | The asymmetric hem runs from mid-calf on the left to the ankle on the right. |
| 4 | Sash | Silk, 12 cm wide, knotted on the right hip, with two tails to mid-thigh | `sea_blue_cloth`, with a 1 cm gold-thread selvedge | G gold thread on the selvedge · A sheen 0.8 (silk) | The tails get a 4-bone chain each. |
| 5 | Vest | Black lacquered leather, high collar (6 cm), closes left of center with 3 shell toggles | `lacquer_black` `#1D1916`, with gold-leaf wave figures `gold_leaf` `#D4A437` | B lacquer (whole vest) · G gold leaf on the wave figures | Cut away at the left shoulder in a halter line. The right shoulder is covered and carries the sleeve ring. The gold figures take up about 18% of the vest area, weighted 70:30 to the right side. |
| 6 | Verse-sleeve | Gauze (§3) | `gauze_white`, with bands as listed | R embroidery · G gold thread · A sheen 0.5 | Attached by a gold-thread cuff ring at the right shoulder. |
| 7 | Arm and ankle wraps | Linen strips | `sand_cloth` `#C9B48E` | A sheen 0.2 | A left-forearm wrap from wrist to mid-forearm (the right forearm is under the sleeve). Ankle wraps above woven sandals. |
| 8 | Sandals | Woven palm fiber, with leather soles | `thatch` `#B08A52` | | |
| 9 | Hair hardware | 3 shell clasps on the braid, plus **her mother's tortoiseshell comb** behind the left ear | `bone` `#E6DAC0` · `tortoiseshell` `#6B3A1E` | B lacquer 0.6 on the comb (a polished shell) | The comb is the one warm brown accent near her face. |
| 10 | **Lantern-staff** (prop) | Dark hardwood shaft 1.95 m long and 3.2 cm in diameter. A brass open cage lantern (6 ribs, 16 cm tall) with an oil wick. Five bell-shells on cords hanging under the cage. | Shaft albedo `#3A2A20` (oiled wood) · cage `brass` `#B08D57` · bells `bone` · flame `oil_lamp` `#FFB16E` | B lacquer 0.3 on the shaft (oil finish) | When unlit, the cage is empty and dark. When lit (field at night and in the Ebbing), it gets an OmniLight3D at energy 0.8 with a range of 3 m, color `oil_lamp`. |

### 4.2 Shared mask packing (all heroes)
These are cross-role conventions for the cloth, skin, and hair shaders (M1-RND-04). Rhen and Toma use the same packing.

| Texture | R | G | B | A |
|---|---|---|---|---|
| `*_albedo` | sRGB albedo | | | Alpha (hair and gauze only) |
| `*_normal` | Tangent-space normal (OpenGL +Y) | | | — |
| `*_orm` | AO | Roughness | Metallic | — |
| **`*_clothmask`** | **Embroidery** (raised thread: sheen boost +0.3, roughness −0.1, adds the detail normal) | **Gold thread / gold leaf** (metallic 1.0, roughness 0.28, albedo forced to `gold_leaf`, anisotropic along the UV tangent) | **Lacquer** (clearcoat 1.0, clearcoat roughness 0.06, base roughness 0.35) | **Sheen / fuzz weight** (0 = leather or metal, 0.3 = cotton, 0.8 = silk) |
| `*_skinmask` | SSS thickness (0 thin, ears and nostrils, to 1 thick) | Cavity | Micro-roughness variation | Detail-normal weight |
| `*_hair` | Root-to-tip gradient | Strand ID (random 0–1) | Depth (for dithering order) | Alpha |
| `*_hairflow` | Flow / tangent direction (RG) | | | — |

**Why:** one cloth shader handles every costume in the game. Embroidery, gold thread, and lacquer are the three culturally specific finishes we lean on most (SPEC §8.2.6), so each gets a dedicated channel and they never compete with roughness or metallic maps.

---

## 5. Hair

- **Style:** black, very long hair, parted on the left. It is drawn back and braided into a **single three-strand side braid** that starts behind the left ear and falls over the front of the left shoulder to the hip (a braid length of 0.68 m). Three shell clasps sit at 0.20, 0.40, and 0.60 m. The braid ends in a 9 cm loose tail. Two face-framing strands (6–8 cm, uncut) are left free on the right temple.
- **Cards:** scalp cap cards in 3 layers (base, mid, and top flyaway), about 260 cards. The braid is built as 3 interleaved strand tubes of cards, 3 cards each across, along a Bezier spine with 40 segments. Loose tail: 30 cards. Flyaways: 40 thin cards (1–2 mm), alpha 0.4–0.7, concentrated at the crown and the braid surface, so the braid isn't a clean rope.
- **Strand texture atlas:** 2K, 16 strand clumps at varying widths (2–14 mm) with root-to-tip alpha taper.
- **Shading targets (Kajiya-Kay, M1-RND-04):** base color `hair_black` `#201A16`. Primary highlight: shift −0.08 along the tangent, exponent 120, tint `#E8D8C8` at 0.35. Secondary highlight: shift +0.12, exponent 40, tint `#8A5A3A` (warm, the color of light through the hair) at 0.5. Under noon sun, the primary band must read as a thin, cool-white ribbon. It must never become a broad grey sheen.
- **Motion:** braid chain of 8 bones (stiffness 0.5, gravity 1.0, collision capsules on the left clavicle and chest), front strands 2 bones each.
- **No hair physics on the scalp** (cards are bound to head bones).

---

## 6. Face

### 6.1 Face shape
- **Oval** with a soft, slightly narrow jaw. Cheekbones are moderately high and wide (widest point at 0.70 of the head width, 0.40 head heights below the vertex). The chin is small and rounded, and the forehead is moderately high (the hair is drawn back).
- **Eyes:** almond-shaped with a slight upward outer tilt (4°). A low single eyelid crease, partly hidden at the inner third. Iris `#3A2618` (very dark brown), with a lighter limbal ring of `#5A3A24` at the outer 15%. Scaled ×1.10 per §1.
- **Brows:** natural and fairly straight, slightly thicker at the head, tapering by the outer third. They are the main instrument of her worry.
- **Nose:** straight, with a soft rounded tip and a moderately narrow bridge.
- **Mouth:** medium width (0.40 of head width), with a full lower lip and a slight natural upturn at the corners. Even at rest, she looks about to smile.
- **Skin:** `skin_asha` `#B9876A` albedo, with a cooler, slightly olive undertone at the jaw and a warmer one across the nose and cheeks (an albedo variation of ±4%, from a procedural map). There are faint freckles across the nose bridge (12–20 dots, 0.8–1.5 mm, 8% darker), which reward close-ups. There is **no makeup**, except a single thin stroke of `gold_leaf` pigment along the right lower lash line in ceremonial scenes (the Ebbing, the Choir): a Cantor custom proposed by Art.

### 6.2 Shared face-shape set (all heroes; the target is about 30 expression shapes plus visemes)
Blendshape names are shared, so that `[emotion]` tags drive the same keys on every hero. The face rig can be blendshapes or bones (SPEC §7.3), but these names are the API.

- **Brows:** `brow_inner_up_L/R`, `brow_down_L/R`, `brow_outer_up_L/R`
- **Lids:** `lid_close_L/R` (blink), `lid_wide_L/R`, `lid_squint_L/R`
- **Cheeks and nose:** `cheek_raise_L/R`, `nose_sneer_L/R`
- **Mouth:** `mouth_smile_L/R`, `mouth_frown_L/R`, `mouth_stretch_L/R`, `mouth_dimple_L/R`, `mouth_press`, `mouth_pucker`, `lip_upper_up`, `lip_lower_down`
- **Jaw:** `jaw_open`, `jaw_clench`
- That is 32 shapes with L/R counted separately. Eye gaze uses bones (`eye_L`, `eye_R`) with lid-follow at 0.3.
- **Visemes (10):** `vis_rest`, `vis_aa`, `vis_e`, `vis_i`, `vis_o`, `vis_u`, `vis_mbp`, `vis_fv`, `vis_l`, `vis_st`. Lip-flap from text (SPEC §5.6) blends visemes at most 0.6 over the emotion pose.

### 6.3 Emotion tags mapped to Asha's face
The tags come from [`tech/dialogue_format.md`](../../tech/dialogue_format.md). Weights are 0–1. Unlisted shapes are 0. Where L and R differ, the values are given as L/R. **Asha's personal asymmetry:** her smile rises 10% higher on the left (`mouth_smile` L = R × 1.1). Her blend-in time is 0.25 s, slower than the party default of 0.18 s, because she arrives at emotions gently.

| Tag | Shape weights | Asha note |
|---|---|---|
| `neutral` | `mouth_smile` 0.08/0.07 | Her rest face is faintly warm. |
| `soft_smile` | `mouth_smile` 0.35/0.32, `cheek_raise` 0.15, `lid_squint` 0.10 | Her default in conversation. |
| `smile` | `mouth_smile` 0.70/0.64, `cheek_raise` 0.45, `lid_squint` 0.25, `lip_upper_up` 0.10 | **The protective smile:** in scenes where she is shielding someone, Cinematics adds `brow_inner_up` 0.25 with `@face`. The brows worry while the mouth smiles. This is the most important expression in her performance. |
| `laugh` | `mouth_smile` 0.90/0.82, `cheek_raise` 0.70, `jaw_open` 0.35, `lid_squint` 0.50, `brow_inner_up` 0.10 | Head tilts back 6°. Rare and real. |
| `worried` | `brow_inner_up` 0.60, `brow_down` 0.15, `mouth_press` 0.20, `mouth_frown` 0.15 | |
| `sad` | `brow_inner_up` 0.70, `lid_close` 0.25, `mouth_frown` 0.40 | Gaze drops 10°. |
| `grief` | `brow_inner_up` 1.00, `brow_down` 0.30, `lid_squint` 0.40, `mouth_frown` 0.60, `mouth_stretch` 0.30, `jaw_open` 0.15 | Reserved for Ch16 and the ending. Add a tear layer (a wet sheen on the lower lid, roughness 0.05). |
| `angry` | `brow_down` 0.70, `lid_squint` 0.30, `jaw_clench` 0.50, `mouth_press` 0.30 | No `nose_sneer` for Asha. Her anger is controlled. |
| `cold` | `brow_down` 0.15, `lid_close` 0.20, `mouth_press` 0.35 | Used for the Ch16 refusal: *the first time she doesn't smile while refusing.* Zero smile weight is the point. |
| `surprised` | `brow_inner_up` 0.60, `brow_outer_up` 0.80, `lid_wide` 0.55, `jaw_open` 0.25 | |
| `afraid` | `brow_inner_up` 0.90, `brow_outer_up` 0.40, `lid_wide` 0.65, `mouth_stretch` 0.45, `jaw_open` 0.15 | |
| `determined` | `brow_down` 0.35, `lid_squint` 0.15, `mouth_press` 0.40, `jaw_clench` 0.20 | The chin lifts 3°. |
| `tender` | `brow_inner_up` 0.30, `mouth_smile` 0.25/0.22, `lid_close` 0.20, `cheek_raise` 0.10 | Her scenes with Rhen and Toma, and the last scene with Imra. |
| `guilty` | `brow_inner_up` 0.40, `lid_close` 0.35, `mouth_press` 0.30 | Gaze down 15° and away 10°. |
| `exhausted` | `lid_close` 0.45, `brow_inner_up` 0.20, `jaw_open` 0.08, `mouth_frown` 0.10 | Head pitch −5°. Paired with joy in Cutscene B (add `mouth_smile` 0.4 via `@face`). |

**Cutscene A requirement** (act outline): the smile → stillness → smile beat. Blend from `smile` to `neutral` with the smile weight at 0.0, not the rest 0.08, over 0.12 s, hold for 0.5 s with a gaze shift to Rhen's lantern, then return to `smile` over 0.35 s. The stillness must be visibly colder than her rest face.

---

## 7. Color Callouts (from `palette.json`)

| Area | Swatch | Hex | Share of her silhouette |
|---|---|---|---|
| Gauze, under-layers | `gauze_white` | `#EBE7DF` | ~35% |
| Wrap-skirt, sash | `sea_blue_cloth` → `indigo_dye` | `#3C78A8` → `#2B3A6B` | ~28% |
| Vest | `lacquer_black` | `#1D1916` | ~12% |
| Skin | `skin_asha` | `#B9876A` | ~12% |
| Hair | `hair_black` | `#201A16` | ~6% |
| Gold (leaf and thread) | `gold_leaf` / `gold_leaf_hi` | `#D4A437` / `#F1D27A` | **≤4%** (keeps a group shot inside the 5% frame budget) |
| Staff, wraps, comb | oiled wood `#3A2A20`, `sand_cloth`, `tortoiseshell` | | ~3% |

**Value check:** her silhouette is about 40% light (gauze and white) and about 25% very dark (vest, hair, staff), which gives the strongest internal contrast in the party. That makes her the focal point of group shots by value alone.

---

## 8. Budgets (SPEC §7.3)

### 8.1 Triangles (LOD0 target 64k; the hard ceiling is 70k)
| Part | Triangles |
|---|---|
| Head and face (skin) | 9,000 |
| Eyes (2 × eyeball, cornea shell, tear line, occlusion shell) | 2,400 |
| Mouth (teeth, gums, tongue, mouth bag) | 2,000 |
| Lashes and brows (cards) | 900 |
| Visible body skin (neck, left shoulder and arm, hands, feet) | 9,000 |
| Hair cards (scalp, braid, tail, flyaways) and clasps and comb | 16,000 |
| Vest with collar and toggles | 5,000 |
| Wrap-skirt (2 layers) | 6,000 |
| Verse-sleeve | 4,000 |
| Sash and tails | 1,500 |
| Wraps and sandals | 1,700 |
| Lantern-staff (shaft, cage, 5 bells, cords) | 6,000 |
| **Total** | **63,500** |

**LODs:** LOD1 at 32k (used from 6 m, which covers the typical battle camera), LOD2 at 14k (from 15 m), and LOD3 at 5k (from 35 m). **LOD1 must keep the silhouette:** staff, sleeve, braid, and collar. Cut detail (flyaways, mouth interior, toggles), never shape. Hidden body under clothing is **deleted**, not counted.

### 8.2 Textures
| Set | Resolution | Maps | Texel target |
|---|---|---|---|
| Face and head | **4K** | albedo, normal, ORM, skinmask | ≥ 50 px/cm |
| Body | 2K | albedo, normal, ORM, skinmask | ≥ 10 px/cm |
| Costume atlas (vest, skirt, sash, sleeve, wraps) | **4K** | albedo (with alpha for the gauze), normal, ORM, clothmask | ≥ 11 px/cm. Sleeve bands at ≥ 20 px/cm (give them a larger UV share). |
| Hair | 2K | hair (packed), hairflow | — |
| Eyes | 1K | iris albedo, iris normal, sclera | — |
| Staff | 2K | albedo, normal, ORM, clothmask (B lacquer) | ≥ 8 px/cm |

**Storage:** 4K PNGs exceed the 5 MB per-binary cap (ADR 0005). Commit the **generators**, not the images. Textures are rebuilt in the pipeline from `assets_src/characters/asha/`, and only compressed imports (VRAM-compressed `.ctex` under `.godot/`, gitignored) exist locally until LFS is approved.

### 8.3 Shader notes for Rendering
- Skin: pre-integrated SSS with scatter color `#C8584A` and radius 2.5 mm, plus a painterly bias. The diffuse wrap is 0.15 and the micro-roughness is 0.42 to 0.5, so skin never looks wet.
- Eyes: a cornea refraction IOR of 1.376 and a visible caustic on the iris on the side opposite the light.
- Lacquer vest: clearcoat. It must show a crisp, dark mirror reflection of the sky, which is how lacquer reads as lacquer and not as plastic.

---

## 9. Modeling Notes for the Procedural Blender Build

Pipeline per SPEC §7.3: parametric base → sculpt-ready mesh → procedural cloth panels → bakes → material layers → Rigify → glTF → Godot import. All of this runs headless: `blender --background --python assets_src/characters/build_character.py -- --character asha`.

### 9.1 Parametric (driven by `assets_src/characters/asha/asha_params.json`)
- **Body:** height, head ratio, shoulder, waist, hip, limb lengths, neck length (§1 values), and a muscle tone of 0.35 out of 1. If the MPFB base is used (SPEC §16 Q2 default, logged in the CHR-01 ADR), it serves only as a topology donor, and every proportion is re-driven from this file.
- **Head:** eye scale 1.10, canthus offset, eye tilt 4°, jaw width, cheekbone height and width, chin, nose bridge width, lip fullness. Each is a named shape-key slider that the build applies at fixed values, so the face can be re-tuned without re-sculpting.
- **Costume:** sleeve length (0.95 m), band count and band height, collar height (6 cm), hem heights L/R, sash width, wrap overlap angle.
- **Hair:** braid length, strand count, clasp positions, card counts per layer.
- **Staff:** shaft length and diameter, cage rib count, bell count.

### 9.2 Costume panels (how they're built)
1. **Patterns as data.** Every garment is a set of flat 2D pattern pieces (polylines in cm, with seam pairs) in `asha_costume.json`, like a sewing pattern. The wrap-skirt is 2 trapezoids plus a waistband. The vest is a front, two backs, and a collar band. The sleeve is a tapered tube pattern with a cuff ring.
2. **Placement:** the script places pieces around the A-pose body on per-piece cylinders, joins the seams, and runs Blender cloth with pinned waistbands, collar, and cuff (40 frames, quality 8). It then **applies the result as the rest shape**. The simulation is a modeling tool only. The runtime uses bones.
3. **Thickness:** solidify gauze to 0 (single-sided, two-sided shading), cotton to 1.0 mm, leather to 2.5 mm, and the sash to 1.2 mm. Bevel the leather edges at 0.8 mm with 2 segments, so the vest catches a highlight line.
4. **Retopology:** shrinkwrap the simulated cloth onto a quad-dominant proxy generated from the pattern grid at 1.5 cm spacing. Pattern-grid topology gives clean UVs for free, because the UVs *are* the flat pattern.
5. **Detail for bakes only:** embroidery relief, gold-leaf wave figures, stitch lines (a 4 mm pitch), and leather grain are displaced on a subdivided high-poly copy and baked down (normal, AO, curvature) to the 4K atlas. The masks (§4.2) are written by the same script from the same vector motif data. **The motifs are authored as SVG-like path data in `assets_src/characters/asha/motifs/`, never painted.**
6. **The verse bands:** each band's motif is rasterized into the clothmask (R and G channels). A separate single-channel 512 px texture, `asha_sleeve_bandid`, stores the band index (0 = blank gauze, then n/7 for band *n*). The shader reveals band *n* when `verse_count ≥ n`. The S8 dissolve uses the same texture plus a noise map, running from the cuff upward.

### 9.3 Hand-tuned versus generated
- **Generated:** everything above, plus skin albedo variation, freckles, pores (a procedural micro-normal), and lash and brow cards.
- **Hand-tuned in script:** the 14 expression poses in §6.3 (as weight tables), the face landmark offsets, and the silhouette checks. Any manual Blender session must be replayed as script changes. If it can't be regenerated, it doesn't ship.

### 9.4 Rig (Rigify plus extra chains)
Braid (8), sleeve (6), sash tails (2 × 4), skirt (3 rings × 8, front-left split at the wrap opening), front hair strands (2 × 2), staff bells (5 × 1, physics at runtime), and lantern cage (1, sway). Export bones: deform bones only, named `DEF-*`. The face uses the shape keys from §6.2.

---

## 10. Open Questions
- **Reach-bands:** Low Reaches adults carry one band per voyage survived (bible §5.1). Asha has never sailed past Haluna's reef, so **her forearms are bare**. She earns her first band offscreen after the Ch4 ferry, shown from Ch5 on her left forearm, as a small visible growth beat, and a second band only in the ending dock shot (**approved by Narrative, [N-01](../../story/decisions_log.md)**). Band count: 0 in the slice, 1 from Ch5, 2 in `ending_dock`.
- **The gold lash stroke** is approved as the **gilt line** ([N-04](../../story/decisions_log.md)): a mask layer worn only at Order rites (Ch9, Ch13, Ch14, Ch16), never in the vertical slice or Act III. **The S8 sleeve unraveling** still needs Cinematics sign-off.

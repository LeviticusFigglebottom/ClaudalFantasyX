# Rhen Sallow: Design Sheet

Owner: Art Director (M1-ART-01). Build: Character Artist. Story source: [`story/characters/rhen_sallow.md`](../../story/characters/rhen_sallow.md).
Shared conventions (mask packing, face shapes, LOD rules, pipeline) are defined in [`asha.md`](asha.md) §4.2, §6.2, §8, and §9. This sheet lists only what differs.

**One-line read:** a lean, quick young man who leans forward as if about to leave. One long sleeve on the left that ends in a diving gauntlet, a bare right arm, a brass lantern bulb over his right shoulder, crossed hooks at the small of his back, and sun-bleached copper tips on short hair. Sun-faded teal, sand, and brass.

---

## 1. Proportions
| Measure | Value |
|---|---|
| Height | **1.77 m** |
| Head height | 0.237 m (**7.47 heads**) |
| Shoulder width | 1.95 heads (0.46 m). Lean swimmer's build: wide shoulders, narrow waist (1.15 heads). |
| Arm span | 1.03 × height (a diver's reach) |
| Eyes | Same ×1.10 rule as Asha (fissure 31 → 34 mm). Realistic IPD (64 mm). |
| Posture | **Forward lean of 4°** from the ankles, weight on the balls of the feet, chin slightly forward. Idle sway amplitude is 130% of the party default, and he shifts weight every 3–5 s. He is the opposite of Asha's stillness. |

## 2. Silhouette
- **Front:** an inverted triangle (shoulders to a narrow waist). The **lantern bulb** shows over the right shoulder (viewer's left) as a round shape about 14 cm in diameter that breaks the shoulder line. The left arm is a single dark column (sleeve plus gauntlet), and the right arm is a bare skin column. The tether coil makes a ring on the left hip.
- **Three-quarter (hero angle, his left toward camera):** the jacket is short (it ends at the lower ribs), so the waist and hips read clearly. The two reef-hook handles stick out past both hips behind him, at 30° on each side. The lantern shows above the far shoulder as a bright dot.
- **Profile:** the forward lean is obvious. The lantern makes a bump on the upper back, and the crossed hooks make an X in profile at the small of the back. The calf wraps thicken the lower leg.
- **Back:** the lantern on its strap across the right shoulder blade is the dominant shape, with the strap running diagonally to the left hip. The hooks are crossed below it. Read test: the lantern bulb and the crossed X must read at 64 px.

## 3. Asymmetric Hallmark: the Single-Sleeve Sea-Jacket and the Lantern
- **Sea-jacket:** short, sun-faded heavy cotton with a stand-up collar 3 cm high, open at the front. It has only a **left sleeve**, which runs long past the wrist into a fingerless **diving gauntlet** of oiled leather with brass rivets and a palm grip pad. The right side of the jacket ends in a raw, rolled armhole edge (cut off by hand, so the stitching is visible).
- **Right arm:** bare to the shoulder. A **faint, half-finished reach-band** sits on the upper forearm, 7 cm below the elbow. It's a 10 mm ring, the outline is complete, and only 40% of the fill is done (tattoo_ink at 60% opacity, slightly blurred with age).
- **Dace's diving lantern:** a brass frame (`brass`) with a salt-glass globe (`salt_glass`, transmission 0.7), 22 cm tall, clipped to a leather strap on the right shoulder blade. It is **unlit by default**. In dark dungeons it gets an OmniLight3D at energy 1.0 with a range of 5 m, color `oil_lamp`, and a 6 Hz flicker at ±6%. This flicker motif is also his Swell timing ring. The globe has 3 hairline cracks (they're in the normal map, and the light leaks through them).
- **The flame is oil** (resolved by Narrative, [N-02](../../story/decisions_log.md)): `oil_lamp` light behind salt-glass, never `glimmer_bound`, and it stays lit through the Unbinding. The housing is Saltwright work fitted with a wick by Dace.

## 4. Costume Layers and Materials
| # | Piece | Material | Color | Mask channels |
|---|---|---|---|---|
| 1 | Undershirt: a sleeveless wrap vest under the jacket | Thin cotton | `sand_cloth` `#C9B48E` | A 0.3 |
| 2 | Sea-jacket (left sleeve only) | Heavy cotton, sun-faded. The fade is stronger on the shoulders and the back (a procedural UV-space mask from the "sun direction"). | `faded_teal_cloth` `#5E9A96`, fading to 75% saturation at the shoulders | R embroidery: a thin current-song wave stitch along the hem (Dace's work, worn) · A 0.35 |
| 3 | Diving gauntlet | Oiled leather, with brass rivets | Leather `#5A3A26` · rivets `brass` | G on the rivets (as brass, metallic 1, roughness 0.4; use albedo `brass`, not gold) · A 0 |
| 4 | Short trousers to the knee | Canvas | `sand_cloth`, salt-stained (white tide-marks from a procedural mask, 2–3 lines) | A 0.3 |
| 5 | Belt with tether coil | Leather and rope. The rope coil is 18 cm in diameter, 8 turns. | Leather `#5A3A26` · rope `thatch` | — |
| 6 | Lantern strap | Leather, 4 cm wide | `#4A3020` | — |
| 7 | Calf wraps and wrapped sandals | Linen strips | `sand_cloth` | A 0.2 |
| 8 | Reef-hooks ×2 | Blades 28 cm long, hooked, with dark steel and wrapped grips | Steel `#5A6066`, metallic 1, roughness 0.35 · grip wrap `faded_teal_cloth` | — |

## 5. Hair
- **Style:** short (4–7 cm) and wind-ruffled, with the crown swept forward and to his left. Dark brown roots (`hair_dark_brown` `#2E1E14`) grade to sun-bleached copper tips (`hair_copper` `#A65A2A`) over the outer 40% of each strand. The bleaching is strongest at the crown and front.
- **Cards:** about 380 short cards in 3 layers, plus 30 flyaways. The tip gradient uses the hair texture's R channel (root to tip). Shading: primary highlight tint `#F0D8B8`, secondary highlight `#C86A30`. The secondary highlight carries the copper, so the tips glow in backlight.
- **Motion:** none on the scalp. A global wind response of 0.25 on the outer layer through vertex shader sway only.

## 6. Face
- **Shape:** a longer rectangle-oval, with a defined but not heavy jaw, a slightly pointed chin, and cheekbones lower and flatter than Asha's. There's a small scar through the left eyebrow (a 6 mm gap) from a dive.
- **Eyes:** slightly deep-set, with straight brows set close to the eyes. Iris `#4A3420` (dark amber-brown). Visible crow's-feet creases appear only under `smile` and `laugh` (he smiles a lot).
- **Nose:** a slightly bumped bridge (an old break) and a narrow tip.
- **Mouth:** wide (0.43 of head width), with thin upper and fuller lower lips. **His asymmetry is a crooked smile:** `mouth_smile` R = L × 1.25, and `mouth_dimple_R` 0.3 is added whenever `mouth_smile` > 0.3.
- **Skin:** `skin_rhen` `#A87556`. It's sun-darkened, with peeling-sun warmth across the nose and the tops of the ears (+6% redness), and salt-dry texture on the lips (roughness 0.6).
- **Blend timing:** 0.12 s (fast), with an 8% overshoot on smiles.

### Emotion tags mapped to Rhen's face
Rhen's tells: he **covers fear with a grin.** When a `.dlg` line is tagged `afraid` *and* he is joking, Cinematics uses `@face rhen smile` and layers `lid_wide` 0.4 and `brow_inner_up` 0.3 on top. The grin is too wide and the eyes betray it.

| Tag | Shape weights |
|---|---|
| `neutral` | All 0. The brows sit naturally low. |
| `soft_smile` | `mouth_smile` 0.28/0.35, `mouth_dimple_R` 0.1 |
| `smile` | `mouth_smile` 0.60/0.75, `cheek_raise` 0.40, `lid_squint` 0.30, `mouth_dimple_R` 0.3 |
| `laugh` | `mouth_smile` 0.85/1.00, `cheek_raise` 0.70, `jaw_open` 0.45, `lid_squint` 0.60 |
| `worried` | `brow_inner_up` 0.50, `brow_down` 0.25, `mouth_stretch` 0.15 |
| `sad` | `brow_inner_up` 0.55, `lid_close` 0.30, `mouth_frown` 0.30, `mouth_press` 0.20 |
| `grief` | `brow_inner_up` 0.95, `brow_down` 0.40, `lid_squint` 0.50, `mouth_frown` 0.55, `mouth_stretch` 0.40, `jaw_clench` 0.20 (he fights it) |
| `angry` | `brow_down` 0.85, `lid_squint` 0.35, `nose_sneer` 0.25, `lip_upper_up` 0.20, `jaw_clench` 0.40 |
| `cold` | `brow_down` 0.30, `mouth_press` 0.40, smile 0. Rare: Ch11, with Liss. |
| `surprised` | `brow_outer_up` 0.85, `brow_inner_up` 0.50, `lid_wide` 0.60, `jaw_open` 0.35 |
| `afraid` | `brow_inner_up` 0.85, `lid_wide` 0.70, `mouth_stretch` 0.50, `jaw_open` 0.20 |
| `determined` | `brow_down` 0.45, `jaw_clench` 0.35, `mouth_press` 0.30. Smile 0: the Act III "stops finishing jokes" face. |
| `tender` | `brow_inner_up` 0.25, `mouth_smile` 0.15/0.22, `lid_close` 0.15 |
| `guilty` | `brow_inner_up` 0.45, `mouth_press` 0.25, `mouth_smile` 0.10/0.20 (an apologetic half-smile). Gaze breaks away. |
| `exhausted` | `lid_close` 0.40, `jaw_open` 0.12, `brow_inner_up` 0.15 |

**Cutscene B requirement:** the slow recognition on "...where did you learn that?" Blend from `soft_smile` to `surprised` at 40% weight over 1.2 s (slow, as recognition dawns), then to `sad` at 30% while the smile decays to 0 over the line. No snap.

## 7. Color Callouts
| Area | Swatch | Share |
|---|---|---|
| Jacket | `faded_teal_cloth` `#5E9A96` | ~22% |
| Trousers, wraps, undershirt | `sand_cloth` `#C9B48E` | ~25% |
| Skin | `skin_rhen` `#A87556` | ~30% (the most skin in the party: bare right arm, open jacket, calves) |
| Leather | `#5A3A26` / `#4A3020` | ~12% |
| Brass (lantern, rivets) | `brass` `#B08D57` | ~4% |
| Hair | `hair_dark_brown` → `hair_copper` | ~5% |
| Steel | `#5A6066` | ~2% |

Rhen has **no gold and no lacquer.** He is the only principal without either, because he is not part of the sacred or ceremonial world. His metal is brass and steel.

## 8. Budgets
**LOD0 target: 58,500 triangles.** Head and face 9,000 · eyes 2,400 · mouth 2,000 · lashes and brows 900 · body skin 11,500 (bare right arm, chest opening, calves) · hair cards 9,000 · jacket 6,000 · gauntlet 3,000 · trousers 4,000 · belt, rope coil, and strap 3,000 · lantern 4,000 · reef-hooks 2,400 · wraps and sandals 1,300.
LOD1 is 30k, LOD2 13k, and LOD3 5k, at the same distances as Asha. LOD1 must keep the lantern bulb, the crossed hooks, the single sleeve, and the hair tips.
**Textures:** face 4K, body 2K, costume 4K atlas, hair 2K, props 2K (lantern and hooks share one), eyes 1K.

## 9. Modeling Notes (deltas from Asha §9)
- **Parametric:** forward-lean angle (in the idle pose library, not the bind pose), jacket length, sleeve length, the gauntlet's cuff height, rope coil turns, lantern size, sun-fade strength, and reach-band fill percentage (the ink fill value is a parameter, so a later scene could show it finished).
- **Jacket panels:** a front-left, a front-right, a back, the left sleeve, and the collar. The right armhole edge gets a rolled-hem bevel of 3 mm radius with stitch displacement in the high-poly only.
- **Sun-fade mask:** procedurally computed by baking a directional "sun exposure" from above and front (an AO-style bake from a light cone at 60° elevation). It drives saturation loss in the albedo generator.
- **Rig extras:** lantern (2 bones, a pendulum on the strap, stiffness 0.6), rope coil (1), jacket hem (5 bones around), and the left sleeve (3).

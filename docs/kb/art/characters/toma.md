# Toma Okeru: Design Sheet

Owner: Art Director (M1-ART-01). Build: Character Artist. Story source: [`story/characters/toma_okeru.md`](../../story/characters/toma_okeru.md).
Shared conventions are in [`asha.md`](asha.md) §4.2 (masks), §6.2 (face shapes), §8 (LOD rules), and §9 (pipeline). This sheet lists only what differs.

**One-line read:** the broadest shape in the party, planted in a wide stance. One huge red lacquer shell pauldron on the left with a bright chiselled scar where an emblem used to be, a bare right shoulder, a great round shield on his back, and a hooked spear. Red lacquer, indigo, bronze skin, and bone.

---

## 1. Proportions
| Measure | Value |
|---|---|
| Height | **1.89 m** |
| Head height | 0.252 m (**7.50 heads**) |
| Shoulder width | 2.30 heads (0.58 m), plus the pauldron, which adds 0.14 m on the left |
| Chest depth | 1.25 heads. A thick torso, a strong neck (neck width 0.62 of head width). |
| Waist / hip | 1.55 / 1.60 heads. Heavy but not fat. A fisher's and soldier's build. |
| Hands | 0.82 head (large but realistic) |
| Eyes | The ×1.10 rule (fissure 31 → 34 mm). IPD 65 mm. |
| Posture | **Stance width 1.4× shoulder width** in idle, knees soft, weight low. Idle sway amplitude is 70% of the party default. He settles, he doesn't fidget. |

## 2. Silhouette
- **Front:** a wide, heavy trapezoid. The **pauldron** on the left shoulder (viewer's right) is a large curved shell shape that raises his left shoulder line by 9 cm and extends it 14 cm outward. Behind him, the **tide-shield** rim shows past both sides of his torso as a disc (0.92 m in diameter). The spear (2.10 m) is usually grounded at his right side and rises above his head.
- **Three-quarter (hero angle, his left toward camera):** the pauldron dominates. The chiselled scar faces camera, a bright pale shape inside the red. The indigo sash makes a wide dark horizontal band at the waist (18 cm), the strongest horizontal in the party.
- **Profile:** a deep chest, the shield as a thick disc on the back (12 cm deep, domed), and the spear's hook visible at the top.
- **Back:** the **shield is the whole back**. Its layered turtle-shell scutes and lacquer rim read as a large patterned circle. Read test: a circle over a wide trapezoid at 64 px.

## 3. Asymmetric Hallmark: the Scarred Pauldron
- **Pauldron:** a Stillguard holdover. It's built from **layered shell plates** (5 overlapping lames, the top one the largest at 32 × 26 cm), lacquered in `lacquer_red`, aged to `lacquer_red_deep` at the edges and in the recesses, with gold-leaf piping 6 mm wide on the top lame's rim. It's strapped across the chest to a leather harness that runs under the right arm.
- **The chiselled scar:** where the Order's Level emblem was, there is now a roughly circular **chiselled-out area** (11 cm across) on the top lame. Chisel strokes have cut through the red lacquer to the **pale shell substrate** (`bone` `#E6DAC0`), with a ragged rim of chipped lacquer showing a thin black under-layer (`lacquer_black`) between the red and the bone. This is the **brightest value on his silhouette**, and it should catch the eye first. The stroke marks are radial and uneven, done by hand in anger. **No trace of the emblem's shape should remain.** Never show the Level on Toma, even faintly.
- **Bare right shoulder and arm:** with dense reach-bands on both forearms.
- **The prayer-cord mark:** a pale band of untanned skin 8 mm wide around the **left wrist**, from the Order prayer-cord he no longer wears. It's `skin_toma` lifted +12% in value, with a hard edge.

## 4. Costume Layers and Materials
| # | Piece | Material | Color | Mask channels |
|---|---|---|---|---|
| 1 | Sleeveless under-tunic, hip length, open at the right side | Heavy cotton | `bone` `#E6DAC0` (undyed), salt-yellowed at the collar | A 0.3 |
| 2 | Harness and pauldron strap | Leather, 5 cm, with bronze buckles | Leather `#4A3020` · buckles `bronze_patina` | G 0 (bronze is metallic via ORM, not gold) |
| 3 | Pauldron | Shell plates and lacquer (§3) | `lacquer_red` / `lacquer_red_deep` / `gold_leaf` piping / scar `bone` | B lacquer (all lames, except inside the scar) · G gold piping |
| 4 | Sash | Indigo cotton, 18 cm wide, wrapped 3 times, with the knot at the left front and tails to the knee | `indigo_dye` `#2B3A6B`, with an original white wave-tick stencil (resist-dye) at the tails | R embroidery 0 (the stencil is in the albedo) · A 0.35 |
| 5 | Wrapped trousers | Cotton, with shin-to-ankle wraps | `indigo_dye` at 70% value (faded) | A 0.3 |
| 6 | Footwear | Leather sandals with a reinforced sole | `#4A3020` | — |
| 7 | **Tide-shield** | Domed disc, 0.92 m across. 13 turtle-shell-pattern scutes (procedural, never a real species pattern copied) over a wood core, with a red lacquer rim band 7 cm wide and a bronze boss 14 cm across. | Scutes `tortoiseshell` `#6B3A1E` with `bone` mottling · rim `lacquer_red` · boss `bronze_patina` | B lacquer on the scutes (0.7) and rim (1.0) |
| 8 | Hooked boarding spear | Ash-wood shaft 2.10 m with a steel head and a 12 cm side hook | Shaft `timber_weathered` · steel `#5A6066` · a grip binding of `indigo_dye` cord | — |

## 5. Hair and Beard
- **Hair:** cropped close (8–12 mm) all over, with a slightly receding temple line. **Long strand cards are not suitable** at this length, so use a dense short-card layer of about 600 tiny cards (6–12 mm), plus a scalp albedo shadow (hair density baked into the scalp's skin albedo at 60%). Color `hair_black`.
- **Beard:** short (10–15 mm) and full along the jaw, with the cheeks clean above the line. About 900 short cards, plus the same scalp-shadow technique on the skin. There's a little grey at the chin (6% of strands use `#8A8478`), which is his age of 31 showing early.
- **Shading:** the primary highlight tint is `#D8CCC0` at a low 0.25 intensity, because cropped hair should read matte.

## 6. Face
- **Shape:** broad and square, with a strong jaw (jaw width 0.92 of cheekbone width), a heavy brow ridge, and a wide nose with a low bridge. His ears are slightly thickened (from Reefball and the Stillguard).
- **Eyes:** deep-set under the heavy brow, with steady, large irises (`#2A1A10`). The heavy brow means **his brows do most of the acting**, so his brow shapes get 15% more range than the other heroes (scale the `brow_*` deltas by 1.15).
- **Mouth:** wide, with a full lower lip mostly hidden by the beard. Smiles have to be read through `cheek_raise` and `lid_squint`, because the beard hides the mouth corners.
- **Skin:** `skin_toma` `#8A5A3E`, deep bronze, weathered. There are fine creases at the eye corners (a normal-map layer that is always on at 30% and goes to 100% under `smile`), and a faint old scar along the right jaw, hidden in the beard.
- **Blend timing:** 0.22 s, measured.

### Emotion tags mapped to Toma's face
His tells: **devotion is still** (as `neutral`, steady), and **his faith breaking is in the brows** (`brow_inner_up` held under a `determined` mouth). For the Ch15 Hollowmere scene, where his faith breaks among the people his order burned (ADR 0016; it was the Cistern), Cinematics should layer `brow_inner_up` 0.6 on `determined`.

| Tag | Shape weights (with the brow ×1.15 already applied) |
|---|---|
| `neutral` | All 0. |
| `soft_smile` | `cheek_raise` 0.25, `lid_squint` 0.15, `mouth_smile` 0.25 |
| `smile` | `cheek_raise` 0.55, `lid_squint` 0.35, `mouth_smile` 0.60 |
| `laugh` | `cheek_raise` 0.80, `lid_squint` 0.60, `mouth_smile` 0.85, `jaw_open` 0.40. Head back 8°. A big laugh, usually at Rhen. |
| `worried` | `brow_inner_up` 0.55, `brow_down` 0.30 |
| `sad` | `brow_inner_up` 0.70, `lid_close` 0.20, `mouth_frown` 0.25 |
| `grief` | `brow_inner_up` 1.00, `brow_down` 0.45, `lid_squint` 0.45, `mouth_frown` 0.50, `jaw_clench` 0.35 |
| `angry` | `brow_down` 0.95, `lid_squint` 0.25, `nose_sneer` 0.20, `jaw_clench` 0.60 |
| `cold` | `brow_down` 0.40, `lid_close` 0.15, `mouth_press` 0.45. The Stillguard face (Ch6, the Ch14 standoff). |
| `surprised` | `brow_outer_up` 0.75, `brow_inner_up` 0.45, `lid_wide` 0.45, `jaw_open` 0.20 |
| `afraid` | `brow_inner_up` 0.80, `lid_wide` 0.50, `jaw_open` 0.10. Rare: for Asha, never for himself. |
| `determined` | `brow_down` 0.50, `jaw_clench` 0.45, `mouth_press` 0.35 |
| `tender` | `brow_inner_up` 0.30, `cheek_raise` 0.20, `lid_close` 0.20 |
| `guilty` | `brow_inner_up` 0.60, `lid_close` 0.40, `mouth_press` 0.40. Gaze down 20°. His most important expression (the Ch15 confession). |
| `exhausted` | `lid_close` 0.40, `brow_inner_up` 0.20, `jaw_open` 0.10 |

## 7. Color Callouts
| Area | Swatch | Share |
|---|---|---|
| Sash, trousers | `indigo_dye` `#2B3A6B` | ~30% |
| Skin | `skin_toma` `#8A5A3E` | ~25% |
| Shield (seen from front, as a rim) | `tortoiseshell`, `lacquer_red` | ~10% from the front, ~60% from the back |
| Pauldron | `lacquer_red` / `lacquer_red_deep` | ~10% |
| Under-tunic | `bone` | ~12% |
| Leather, spear | `#4A3020`, `timber_weathered` | ~8% |
| Gold piping | `gold_leaf` | **≤1.5%** |
| Scar | `bone` | ~0.5% (a small shape, the brightest value) |

**Group-shot rule:** Toma carries the party's red. With Asha's gold and Toma's red together in one frame, the frame must still meet the palette limits (gold ≤ 5%, red ≤ 8%). At typical battle framing, Toma's red takes up about 2–3% of the frame.

## 8. Budgets
**LOD0 target: 66,000 triangles** (the heaviest hero, because of the shield). Head and face 9,000 · eyes 2,400 · mouth 2,000 · lashes and brows 900 · body skin 10,500 (right shoulder and arm, both forearms, neck, feet) · hair and beard cards 8,000 · under-tunic 3,000 · harness 1,500 · pauldron 4,500 · sash 3,500 · trousers and wraps 4,500 · sandals 1,000 · tide-shield 9,000 · spear 3,000 · buckles and boss detail 3,200.
LOD1 is 33k, LOD2 14k, and LOD3 5k. LOD1 keeps the shield disc, the pauldron outline, the scar, and the spear hook.
**Textures:** face 4K, body 2K, costume 4K atlas (tunic, sash, trousers, harness, pauldron), shield 2K (its own set: the scute pattern needs the space), spear 1K, hair 2K, eyes 1K.

## 9. Modeling Notes (deltas from Asha §9)
- **Parametric:** shoulder width, chest depth, pauldron lame count, sizes, and overlap, scar radius and stroke count, shield diameter, dome height, and scute count, spear length and hook size, sash width and wraps, reach-band count per forearm (**left 11, right 9**), and wrist-mark width.
- **Pauldron:** built procedurally as stacked, curved, solidified shell lames (each a lofted patch with a 6 mm thickness and 1.5 mm bevel), then a boolean "chisel" pass using a scatter of 40–60 wedge cutters inside the scar radius, at random depths to the substrate. The layer colors (red → black → bone) come from a **depth-from-surface bake**, so the stratigraphy is physically consistent.
- **Shield scutes:** a Voronoi pattern relaxed on the dome (13 cells) with raised growth-ring ridges (a procedural normal). The mottling uses noise in the albedo generator. Don't copy a real species' scute layout.
- **Reach-bands:** generated as rings on the forearm UV (bands 8–12 mm wide, 4–6 mm gaps), each with an original tick-pattern code (a seeded random sequence of short and long ticks per band). This is shared with every Low Reaches NPC through the same generator, with a different seed and count.
- **Rig extras:** sash tails (2 × 4), pauldron (1 bone with a 6° hinge on the strap), shield (fixed on the back, plus 1 bone for the battle unsling), and spear (a prop bone).

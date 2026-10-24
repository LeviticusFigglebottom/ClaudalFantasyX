# Character Shading (M1-RND-04)

This page covers the hero skin, hair, eye and cloth shaders (SPEC §7.3 and §8.2 items 4–6). Code lives in `game/shaders/character/`, the test stage in `game/levels/_tests/character_shading/`, the procedural test props in `assets_src/characters/shader_test/`, and the tests in `tests/unit/test_character_shading.gd`. The shared texture packing comes from [`art/characters/asha.md`](../art/characters/asha.md) §4.2. This page adds the shader-side contract that the Character stream authors against.

> **No number on this page was measured on a GPU.** Frames were rendered in software (Forward+ on Mesa lavapipe, ADR 0009). Every CPU timing below is labelled as such and **does not represent GPU cost**. The GPU figures are estimates from operation counts, ±50%, until the GPU runner exists (M1-QA-01).

## Files

| File | What it is |
|---|---|
| `character_brdf.gdshaderinc` | Shared maths: GGX (iso and aniso), Charlie sheen, the pre-integrated skin fit, Kajiya-Kay, interleaved-gradient dither, geometric specular AA, and normal-map helpers. |
| `character_wind.gdshaderinc` | Vertex wind sway driven by `hymn_wind` and `hymn_wind_time` plus vertex-colour weights. Used by hair and cloth. |
| `character_skin_body.gdshaderinc` + `character_skin{,_medium,_low}.gdshader` | Skin. |
| `character_hair_body.gdshaderinc` + `character_hair{,_medium,_low}.gdshader` | Hair cards. |
| `character_eye_body.gdshaderinc` + `character_eye{,_medium,_low}.gdshader` | Eyeball: sclera plus refracted iris. |
| `character_cornea.gdshader` | Wet cornea and tear-film shell (additive specular). One variant. |
| `character_eye_occlusion.gdshader` | Lid-shadow helper shell (multiply). One variant. |
| `character_tear_line.gdshader` | Tear meniscus and `grief` tear layer. One variant. |
| `character_cloth_body.gdshaderinc` + `character_cloth{,_medium,_low}.gdshader` | Opaque costume cloth: sheen, embroidery, gold, lacquer, verse bands. |
| `character_cloth_sheer{,_medium,_low}.gdshader` | The same body with `HYMN_CLOTH_SHEER`: gauze, two-sided, dithered alpha, transmission, the S8 dissolve. |
| `character_shader_tiers.json` + `character_shader_tiers.gd` (`CharacterShaderTiers`) | Maps graphics preset → tier → variant, and swaps materials. |

## Technique choices

### Skin: analytic pre-integrated SSS

The diffuse is pre-integrated subsurface scattering (Penner & Borshukov 2011), evaluated **analytically in `light()`**. Curvature comes from `fwidth()` of the interpolated vertex normal over `fwidth()` of the position. Each channel sees a differently blurred normal (red the smoothest). Sun penumbrae are shaped per channel so red bleeds into the shadow. Thin regions get a transmission lobe. Specular is a dual-lobe GGX at skin F0 0.028 (IOR 1.4).

**The fit.** `assets_src/characters/shader_test/preintegrated_skin_fit.py` integrates the d'Eon & Luebke six-Gaussian skin profile around a ring of radius R to build the reference LUT, and fits a hyperbolic soft ramp per channel:

```
D_c(x, u) = s_c (x + sqrt(x² + q_c²)) / (1 + sqrt(1 + q_c²)),  q_c = A u + B u²,  s_c = 1 + C u + D u²
x = N·L,  u = scatter_radius / R
```

Over u ∈ [0, 2] the maximum absolute error against the integrated LUT is **0.018 (red), 0.004 (green) and 0.010 (blue)**. At u = 0 the formula reduces exactly to the clamped cosine. A unit test checks that the shader constants equal the generator's `FIT_EXPECTED`, and that the fitted function wraps red furthest and is monotonic in N·L.

**Why this approach, considering Forward+ cost:**

| Option | Cost | Why not / why |
|---|---|---|
| Godot screen-space SSS (`SUBSURFACE_SCATTERING_STRENGTH`) | A full-screen separable blur over the diffuse buffer, with its quality set globally. Roughly 0.4–1.0 ms at 1440p (estimate). It is paid whenever any skin is on screen, even a battle-distance hero 200 px tall. | It doesn't run through a custom `light()` without double-scattering, it has no per-light penumbra control, and on the Low preset it would have to be switched off globally anyway. Not used. |
| Pre-integrated LUT texture | One extra sampler fetch per light per pixel, plus a 2D LUT asset under `assets/`. | It works, but the fit is within 0.02 of the LUT, costs about 12 ALU per light instead of a dependent fetch, and needs no binding, import settings or PROVENANCE row. |
| **Analytic pre-integrated (chosen)** | About 40–60 ALU per light (three blurred N·L terms, the fit, penumbra `pow`, transmission). No extra pass and no textures. | Its cost scales with pixels × clustered lights, so it is free when the hero is small. Low simply compiles it out. |

**Known limits:** curvature from derivatives is constant across each 2×2 pixel quad, so it needs smooth, well-tessellated heads (the 9k-triangle head budget is fine). Penumbra scattering applies only to directional lights, because `ATTENUATION` mixes distance falloff into omni and spot lights. There is no screen-space blur, so the fine scattering of pore-scale light (the "translucent glow" of real skin at close range) is approximated by blurring the normal, not simulated.

**Painterly option (SPEC §14 mitigation).** The `painterly` uniform (0 to 1) blends toward stylised shading. It applies a soft two-tone ramp around `painterly_terminator`, a warm band of `col_scatter` at the terminator, and a lavender shadow fill (`col_painterly_shadow`, never grey). `painterly_form` keeps some N·L shading inside the lit side. It also reduces pore detail by 70% and micro-roughness to zero, makes the highlight a single broader lobe at reduced strength, and adds +12% albedo saturation. The test material uses **0.2** ("slightly painterly", asha.md §1). At 1.0 a frontally lit face goes nearly flat. That is a usable stylised fallback, but it reads as cel shading, not paint (see the assessment below).

### Hair: Kajiya-Kay, two shifted lobes, temporal dither

Hair is shaded with Kajiya-Kay plus Scheuermann's shifted tangents, using two lobes:

- **Primary:** cool and narrow. Shift −0.08, exponent 120, `#E8D8C8` at 0.35.
- **Secondary:** warm and wider. Shift +0.12, exponent 40, `#8A5A3A`, broken up per strand by `secondary_sparkle`.

The tangent comes from the flow map (`tex_hairflow` RG in tangent space). Diffuse is Kajiya diffuse blended with wrapped Lambert. On High, a back-lit transmission lobe stands in for Marschner's TT path. It is gated by the shadow map (strands behind the head get nothing), weighted toward silhouettes and tips, and has a 35% multiple-scattering leak. Per-strand variation comes from the strand ID (value ±18%, hue, ±0.1 highlight shift) and from the root-to-tip gradient (root occlusion, the `col_root` → `col_tip` colour, and tip-weighted transmission). Highlight intensities are relative to a white Lambert surface facing the light.

**Coverage comparison** (measured on the backlit hair shot: 960×540, 30 vs 31 settle frames, TAA on). These are lavapipe frames: the image differences are valid, the costs are not GPU numbers.

| Technique | Frame-to-frame RMSE (linear) | Look after 30 TAA frames | Pipeline |
|---|---|---|---|
| **A. Temporal IGN dither + discard (chosen, Medium–Ultra)** | 0.0030 (p99 pixel 0.023) | Smoothest strands. The dither resolves into soft coverage. | Opaque. Depth pre-pass, SSAO, SSR, DOF, and shadows with the same coverage. No sorting. |
| B. Godot hashed alpha (`ALPHA_HASH_SCALE`) | 0.0026 | Visible static grain. Object-space stable, so TAA cannot average it. | Opaque. |
| C. Static IGN (`dither_temporal = false`) | 0.0023 | Visible ordered grain. | Opaque. |
| D. Alpha blend + `depth_prepass_alpha` | 0.0014 | Smooth, but card-order sorting errors show as dark streaks between layers. | Transparent pass: no SSAO or SSR on the hair, DOF depth from the pre-pass only, and overdraw is blended rather than depth-rejected. |
| E. Alpha-to-coverage | not tested | No preset uses MSAA (TAA or FSR2; Low moved from FXAA to TAA in M1-RND-07), so A2C would need MSAA just for hair. | Rejected. |

**A** has the highest frame-to-frame difference by design, because its pattern changes each frame and TAA integrates it. That difference stays well under the 0.008 screenshot threshold, and captures are bit-exact between runs (`--fixed-fps 60` makes `TIME` deterministic). The dither phase depends on `TIME` since process start. Capture runs one process per shot, so baselines don't depend on shot order. Captured inside a long-running process, the dithered gauze and hair would differ by up to about 0.015 RMSE. The **B channel of `*_hair`** decorrelates overlapping layers: each layer's threshold is offset by a golden-ratio multiple of its depth and strand ID, so two 50% layers cover 75% instead of sharing one pattern. **Low** uses alpha scissor at `alpha_cutoff` 0.35 instead: hard edges, no noise. This was decided when Low ran FXAA, which resolves no dither. Low has run TAA since M1-RND-07, and scissor stays (M1-RND-15): it is cheaper than the hashed path, it stays stable at Low's 30 fps target, where each frame moves further and TAA would leave a dither crawling or ghosting, and it still holds if a player sets AA to none or FXAA on Low.

### Eyes: object-space eyeball with parallax refraction, plus shells

- **Eyeball** (`character_eye*`). The sclera and iris are parametrised in the eye's object space, so the UVs are not used for the iris. The view ray refracts at a spherical cornea (IOR 1.376) and marches down to the iris plane through an anterior chamber of `anterior_depth_m`. The iris is looked up where that ray lands (Jimenez 2012). The iris normal is concave, and a caustic brightens the iris on the side opposite the light (asha.md §8.3). It also has a lighter limbal ring (`col_limbal`, the outer 15% for Asha), a dark limbus shadow ring, pupil dilation as a radial remap (the fibres stretch rather than slide), and wrapped sclera with a warm terminator.
- **Cornea shell** (`character_cornea`). An additive specular-only shell gives the wet look: Godot's sky and probe reflections plus one GGX lobe per light. The **wet highlight is kept stable under TAA** by four measures. (1) The normal is analytic (eyeball sphere blended into the corneal sphere), so tessellation never facets the highlight. (2) Geometric specular AA (Tokuyoshi & Kaplanyan 2019) widens roughness by the normal's screen-space variance. (3) A per-light `highlight_max` clamp keeps sub-pixel HDR spikes from fighting TAA's neighbourhood clamp. (4) The shell moves with the eyeball, whose motion vectors its pixels reuse.
- **Eye occlusion** (`character_eye_occlusion`). An unshaded multiply shell darkens the eye under the upper lid, the lower lid and the corners. The tint is warm `#4A2A22`, never grey. This is the single biggest cue against the stuck-on-eye read.
- **Tear line** (`character_tear_line`). This is the meniscus strip along the lower lid. `inst_tears` drives the grief tear layer (roughness 0.12 → 0.05, asha.md §6.3).
- **Low.** No refraction: the iris is read at the surface. No concave normal and no caustic.

### Cloth: one shader for every costume

The base layer is Lambert plus dielectric GGX plus **Charlie sheen** (Estevez & Kulla 2017, Neubelt visibility), with diffuse energy lost to the sheen. Sheen colour is tinted toward √albedo, so dyed fibres keep their hue at grazing angles. The cloth mask (asha.md §4.2) drives three more layers:

- **R, embroidery:** sheen +0.3, roughness −0.1, plus the tiled thread detail normal.
- **G, gold:** metallic 1, roughness 0.28, albedo forced to `col_gold`. It is **anisotropic GGX along the UV tangent**, rotated by `gold_tangent_rotation` (Burley D with matching Heitz visibility), and indirect light gets Godot's `ANISOTROPY` and `ANISOTROPY_FLOW`.
- **B, lacquer:** a **clear coat** (F0 0.04, roughness 0.06) over a 0.35-rough base. The coat uses the *geometric* normal, so leather grain shows under a mirror-smooth surface, and its Fresnel takes energy from everything beneath it. Indirect light reads `ROUGHNESS` as the top-most interface (coat on lacquer, leaf on gold), which gives lacquer its crisp, dark sky mirror (asha.md §8.3). Gold leaf sits on top of lacquer (`lacquer × (1 − gold)`). The three numbers are **material uniforms** (`lacquer_base_roughness`, `lacquer_coat_roughness`, `lacquer_coat_strength`); the shader defaults (0.35 / 0.06 / 1.0) are hard lacquerware such as a polished shell or a lacquered pauldron. **Lacquered leather** (Asha's vest, M1-CHR-04) sets base 0.55, coat 0.16, strength 0.55: the sky still mirrors as a broad, dark sheen, but a whole-garment coat at 0.06 reads as patent plastic on a large convex surface. Wear in the B mask (edges, folds) breaks it up further.

The sheer variant adds dithered alpha (as for hair), two-sided shading, diffuse transmission from behind plus a forward lobe (`transmission` 0.35, asha.md §3.1), and the S8 dissolve.

Indirect sheen is missing: Godot's ambient has no sheen term. Velvet-like edge glow appears only under direct lights.

## Quality tiers and presets

Tiers are compile-time variants (`game/shaders/README.md`). Every variant of a family declares **the same uniforms**, and a test enforces this, so switching tiers just swaps `ShaderMaterial.shader` and keeps every authored parameter.

| Preset (`graphics_presets.json`) | Character tier | Variant file |
|---|---|---|
| low | low | `*_low.gdshader` |
| medium | medium | `*_medium.gdshader` |
| high | high | `*.gdshader` |
| ultra | high | `*.gdshader`. The extra Ultra budget goes to native resolution, not to more character features. |

| | Low | Medium | High / Ultra |
|---|---|---|---|
| Skin diffuse | Wrapped Lambert plus a warm terminator band. **No SSS.** | Pre-integrated SSS, per-channel normal blur | Medium, plus sun-penumbra scattering and thin-region transmission |
| Skin detail | Base normal map only | Plus the pore detail normal | Plus micro-roughness variation |
| Skin specular | 1 GGX lobe | 1 GGX lobe | Dual GGX lobe |
| Hair coverage | Alpha scissor | Temporal dither | Temporal dither |
| Hair shading | **Primary lobe only**, no strand variation | Both lobes, strand jitter and sparkle | Medium plus back-lit transmission |
| Eye | Flat iris, no refraction, no caustic | Refraction, concave iris, caustic | Same as Medium |
| Cloth | Sheen, isotropic gold, lacquer as one sharp lobe, no detail normal, primary wind only; gauze uses alpha scissor | Plus clear coat, detail normal, secondary and flutter wind, dithered gauze | Plus anisotropic gold |
| Cornea, occlusion, tear line | Same at all tiers | | |

**Applying a tier.** Graphics settings can't edit materials, so whoever spawns a character, or reacts to a preset change, calls:

```gdscript
CharacterShaderTiers.apply_to_tree(character_root, CharacterShaderTiers.tier_for_preset(graphics_settings.preset_id))
```

This walks material overrides and surface materials, visits each material once, and is idempotent. Since M1-RND-19 it is **copy-on-swap**. A material that needs a new shader is duplicated first, unless it is a copy this function already made for the same root. Ownership is tagged by the `hymn_tier_owner` meta, which holds the root's and the copy's instance ids. The copy goes into the slot: `material_override`, the surface override, or the surface override slot for a mesh's own surface material. Shared `.tres` files, import-time overrides and meshes are never mutated, so two heroes sharing a material can sit at different tiers. Slots in one tree that shared a source also share its copy. A second call on the same root swaps those copies in place. A call on a different root, such as a subtree, copies again. `apply_tier` on its own still mutates in place, so callers use it only on materials they own. **Follow-up for the RND-05 owner:** fold the preset → tier column into `graphics_presets.json` and call this from `GraphicsSettings.apply_current`.

**Limits of the walk (M2-NIT-03, review-sweep-M on M1-RND-19).**
- **Overlays and next passes are not reached.** `GeometryInstance3D.material_overlay` and `Material.next_pass` chains are neither swapped nor copied, so a tiered hair shell or outline added as a next pass or an overlay would stay at its authored tier. Extend `apply_to_tree` before adding one. The docstring says the same.
- **Copies live as long as their instance.** A swap back to a material's source tier keeps the owned copy in the slot rather than restoring the shared source. That is harmless (same shader and parameters), but the per-instance copies are never released while the instance lives. When crowds use tiers, either restore the source on a swap back or accept one copy per tiered material per instance in the memory budget.

**Prewarm.** All 18 shaders are registered in `prewarm_materials.json`, scoped to the test stage, with a `tier` key. **Follow-up for the RND-06 owner:** have `ShaderPrewarm` skip entries whose tier isn't active. **Character stream:** add the hero's battle and dialogue scene paths when M1-CHR-02 lands.

## Map authoring requirements (Character stream)

The packing is asha.md §4.2. These are the shader-side details on top of it.

**Every map:** use PNG generated from source (ADR 0005 storage rules). Set **mipmaps on** in the `.import` file (`mipmaps/generate=true`). Headless imports don't auto-detect 3D use, and pores and hair alpha alias badly without mips. **Exception: id maps** (`*_bandid`, and any future map whose values are labels, not colours) are sampled with `filter_nearest` and imported with **mipmaps off** (`mipmaps/generate=false`): filtering or mip-averaging two ids invents the ids between them (band 7 next to blank 0 decodes as bands 1–6). Mark albedo as sRGB through the shader's `source_color`; never bake gamma into data maps. Normal maps are **tangent-space OpenGL (+Y green up)**. The shaders rebuild Z from XY, so RGTC (two-channel) compression is safe. **Tangents:** the hair flow, gold anisotropy and every normal map need them. Godot's importer generates MikkTSpace tangents (`meshes/ensure_tangents=true`, the default), which is what the test props use. Blender's exported tangents were not byte-stable between runs, which breaks reproducibility. Triangulate in the build script with a fixed rule and a sorted face order (see `new_object` in `build_shader_test_meshes.py`): bmesh operators order their output by pointer hashes.

| Map | Channels and ranges | Notes |
|---|---|---|
| `*_albedo` (skin) | sRGB. Keep values within the palette limits (`#1D1916`–`#EBE7DF`). | Leave `col_albedo` white when this map carries the colour, because it multiplies. |
| `*_normal` | Macro normal (wrinkles, lips, lid creases) | Pores do **not** go here; they come from the tiled detail map. |
| `*_orm` (skin) | R AO, **G roughness remapped into `roughness_min`–`roughness_max` (0.42–0.50)**, B ignored | Paint the T-zone toward 0 (oilier) and the cheeks toward 1. |
| `*_skinmask` | **R thickness:** 0 = thin (ear rims 0.1–0.2, nostril wings ~0.5, eyelids ~0.6), 1 = thick. **G cavity:** 1 = none, 0 = deep crease. It darkens albedo by `cavity_albedo` and occludes specular. **B micro-roughness:** 0.5 = neutral, ±0.5 maps to ±`micro_roughness` (0.06) at pore scale. **A detail weight:** 1 = full pores; lips ~0.35, lids ~0.5, scalp under the hair ~0.3. | Thickness also feeds transmission, so wrong values make ears and noses glow or stay dead. |
| Detail normal | A tileable pore and skin-line map. One tile covers **27.5 mm** of skin (the middle of 25–30 mm; pore spacing 0.5–1 mm). | Pores tile in UV space, so the head needs **uniform texel density across all its UV islands** (every island at the same mm of skin per UV unit, within ±10%; check it with a checker map before texturing), or the pore scale jumps at the seams. Then **`detail_tiling` = (mm of skin per UV unit) ÷ 27.5**. Example: a head unwrapped so one UV unit spans 440 mm of skin gives 440 ÷ 27.5 = **16** (the test bust's value). Too fine and the mips erase the pores; too coarse and the skin looks like orange peel. |
| `*_hair` | **R root→tip** (0 at the root along each card), **G strand ID** (random 0–1 per strand), **B depth/layer** (0 = innermost, near the scalp, to 1 = outer flyaways), **A alpha** with a root-to-tip taper | Cards: **V runs root (0) → tip (1)**. B is used for dither decorrelation and self-occlusion, so vary it per strand or per layer. Cards that share one atlas get per-layer B from **separate atlas regions per layer** (vertex colour is taken by wind). |
| `*_hairflow` | RG = strand direction in tangent space (0.5 = 0). Default strands run along +V. | **Vary it.** Per-clump lean (σ ≈ 0.14) and slow per-strand undulation (±0.12). A constant flow lights a flat sheet of hair all at once and reads as a broad bronze sheen. If there's no map, set `flow_strength = 0`. |
| Iris (`tex_iris`) | sRGB, **edge to edge = the iris disc**, pupil drawn at **radius 0.3** of the texture | It multiplies with `col_iris`, so keep the texture near white (0.4–1.0) with the structure in value. |
| `*_clothmask` | R embroidery, G gold, B lacquer, A sheen (0 leather or metal, 0.3 cotton, 0.8 silk). Soft 1–2 px edges. | Gold on lacquer: paint both. The shader puts the leaf on top. |
| `*_orm` (cloth) | R AO, G roughness (× `roughness_scale` 0.85), B metallic for non-gold metal (brass rivets, bronze) | Gold is the G mask, **not** ORM metallic. |
| `asha_sleeve_bandid` | One channel. **0 = blank gauze, n/7 for band n** (1–7). Cover the whole band rectangle on the outer 220°. | `verse_count` (int 0–7) reveals bands with n ≤ verse_count. Hidden bands fall back to `col_blank_gauze`, `blank_alpha` 0.55 and `blank_sheen` 0.5. **An id map:** the shader samples it nearest without mips; import it with `mipmaps/generate=false` (the exception above). Keep each band's region at least 2 texels wide so magnified edges stay on whole texels. |
| Sleeve UVs | **UV.y runs shoulder seam → cuff tip** inside [`sleeve_v_shoulder`, `sleeve_v_cuff`] | The S8 dissolve (`sleeve_dissolve` 0 → 1 over 6 s, driven by Cinematics) runs from the cuff upward along UV.y. Gauze albedo alpha is 0.55 single and 0.95 double (bands, cuff ring). |

**Geometry contracts:**

- **Eyes.** Eyeball, cornea shell, occlusion shell and tear line are **separate MeshInstance3D nodes** on a BoneAttachment3D of the eye bone. Their origin is at the eyeball centre, **+Z is the gaze** (Blender −Y), and scale is uniform. **Apply the object transform with the origin at the eyeball centre *before* parenting to the eye bone**: a bone-relative rotation baked into the mesh breaks the object-space iris. Set `eye_radius_m`, `iris_radius_m` and `cornea_radius_m` to the mesh (Asha: 13.2, 6.45 and 8.6 mm). The cornea shell is a sphere 0.2 mm out from the eyeball, with the corneal bulge in front. Turn off its cast shadow.
- **Eye-occlusion shell UVs:** U runs from the inner canthus (0) to the outer (1), V from the upper lid margin (0) to the lower (1). It sits about 1.7 mm off the eyeball, inside the lids.
- **Tear-line UVs:** U along the lower lid margin, V from the lid (0) to the eyeball (1).
- **Render priority** (transparent order): cornea 1, occlusion 2, tear line 3.
- **Lids** must rest on the eyeball, with geometry outside it everywhere. Any skin vertex inside the eyeball sphere lets the sclera poke through. The test prop does this with a lid "skirt" solved from the almond contour (`build_shader_test_meshes.py: add_lids`). The production head should model real lids.
- **Skin needs smooth vertex normals:** the curvature term reads them.
- **Vertex colours** carry wind weights on hair and cloth (next section). Meshes without vertex colours import as white, which means fully free. Set `wind_response = 0` on anything that must not sway.
- **Author them as float colours:** a Blender colour attribute of type **`FLOAT_COLOR`** on the **`POINT`** domain, made active and exported as glTF `COLOR_0` (`export_vertex_color="ACTIVE"`), as `build_shader_test_meshes.py:65` does. Never use a *Byte Color* attribute: Blender stores it sRGB-encoded and converts it on export, so a painted 0.5 weight or phase arrives as about 0.21.

## Wind (vertex colours carry weights)

`character_wind.gdshaderinc` uses the **same channel meanings as the vegetation convention** (M1-ENV-02: R primary, G secondary, B phase, A flutter) and the same 6 m/s reference wind. That way one `hymn_wind` moves palms, saltgrass and sleeves consistently.

| Channel | Meaning |
|---|---|
| R | Primary sway weight: 0 pinned (seam, waistband, collar, scalp) → 1 free (hem, cuff, tip). It leans downwind plus oscillates. |
| G | Secondary ripple: a wave travelling downwind through the garment (off on Low) |
| B | Phase 0–1: desynchronises panels, sash tails and clumps |
| A | Flutter along the normal: fast and small, for gauze (off on Low) |

All four channels are linear data (see "Author them as float colours" under Geometry contracts).

`wind_response` is the fraction of the global wind the mesh follows: Asha's sleeve 0.6, Rhen's outer hair 0.25, scalp cards 0 (the default for hair). Displacement happens in model space on the already-skinned vertex, so spring bones and wind add up. Drive it with `hymn_wind_time`, not `TIME`, so cutscenes can pause it.

## Verse-sleeve states (asha.md §3.1)

| State | `verse_count` | `sleeve_dissolve` |
|---|---|---|
| S0 | 0 | 0 |
| S1–S7 | 1–7 | 0 |
| S8 (the Letting) | 7 | 0 → 1 over 6 s from the cuff up, with a `glimmer_lift` edge (`col_dissolve_glow`, `dissolve_glow_energy` 4). Cinematics spawns the rising motes (GlimmerField) along the edge. |

After S8, hide the sleeve mesh. The faint gold pressure mark on the arm is a skin-albedo decal for the Character stream.

## Shadows on characters (M1-QA-05)

Measured on a GPU (docs/kb/qa/gpu/2026-10-23-qa-05-asha.md): the diagonal banding and blotchy self-shadowing on Asha's shadow-side cheek are the **shadow-terminator artefact**. Where smooth vertex normals disagree with flat triangles, the face shadows itself in steps that follow the triangles. It isn't the skin shader (detail normal, curvature and scatter off change nothing), and it isn't the CPU renderer (the GPU matches lavapipe).

- **Lights that key a face: `shadow_normal_bias` 2.5–3.0** (Godot default 1.0). At 3.0 Asha's full-body contact shadows still hold; there's no visible peter-panning.
- **Don't fight it with a shorter `directional_shadow_max_distance`.** Godot's normal bias scales with the shadow texel, so finer texels shrink the bias, and the stair-steps get sharper.
- The lasting fix is mesh density across the cheeks and jaw (Character).
- **Asha stage: 4.5 (M1-RND-20).** At 4.5 the smile corner is clean, and the nose, feet and staff contact shadows
  hold. The stage's key light has `directional_shadow_max_distance` 8 m.
- **The bias is in shadow texels, not metres.** Godot multiplies `shadow_normal_bias` by the cascade's texel size, so
  the same number pushes much further in a zone sun with long cascades. Match the *world* offset, not the number.
  - Haluna's sun (400 m, first split 0.04 = 16 m) has cascades about 10–20× coarser than the stage's at face range.
    At its own 1.0 its offset at a face is already larger than the stage's 4.5.
  - Measured (M1-RND-20 follow-up, `docs/kb/qa/gpu/2026-10-23-rnd-18-20-followups.md`): Asha's smile and neutral
    faces under Haluna's cascade settings show no corner stripe at bias 1.0. At 2.5 and 4.5 the nose shadow fades,
    and at 4.5 it's gone. **Keep zone suns at 1.0.**
  - What a zone sun can't do at dialogue range is resolve a face's own shadows at all: 16 m cascades blur the nose
    and cheek shadows away. Close-ups that need them need a dialogue key light with a short shadow range (a few
    metres, as the stage does) and bias 4.5 (M2 dialogue rig).

## Mouth interior (M1-RND-21, M1-RND-24)

The lips shadow an open mouth from every light, so with direct light alone the interior gets only ambient light and
goes near-black (M1-QA-05c fault 2, grief). Every hero's **mouth bag, teeth and tongue use the `mouth` family**
(`character_mouth{,_medium,_low}.gdshader`, body `character_mouth_body.gdshaderinc`). It's registered in
character_shader_tiers.json and the prewarm registry.

- **Material contract:** the values of the StandardMaterial3D it replaced.
  - `col_albedo` and `tex_albedo`.
  - `tex_orm`: R = occlusion, G = roughness.
  - `roughness`, with `roughness_from_orm` (0 = the uniform alone).
  - `specular` (F0 = 0.08 ×) and `ao_light_affect`.
- **Cavity bounce:** per light, the shader adds `col_cavity_bounce × cavity_bounce × LIGHT_COLOR / π`.
  - It's unshadowed, because the lips that bounce the light are lit even where the interior isn't.
  - It's faded by the baked occlusion (`mix(1, ao, cavity_occlusion)`), by how far the light is behind the face
    (`0.5 + 0.5 · L·V`, so a rim light from behind adds almost nothing), and, for positional lights, by the
    light's distance and cone falloff.
- **Unshadowed for every light type (M1-RND-24).** In Godot 4 a positional light's `ATTENUATION` is its distance and
  cone falloff *times its shadow*, and `light()` gets neither the light's position nor its range, so the shader
  can't rebuild the falloff alone. RND-21 used `ATTENUATION`, so a shadowed spot or omni key added no bounce.
  - **Directional lights:** their `ATTENUATION` is the shadow alone, so the base pass adds the bounce at reach 1
    (unchanged).
  - **Positional lights:** an additive second pass, `character_mouth_bounce.gdshader` (`blend_add`,
    `depth_draw_never`, `shadows_disabled`, `ambient_light_disabled`, `fog_disabled`), draws only their bounce.
    With shadows disabled, its `ATTENUATION` is exactly Godot's distance and cone falloff. Chosen over `reach =
    1.0` because the cone and range reach `light()` only through `ATTENUATION` (clustering culls by bounding
    volume, not per pixel), and because a distant key's energy is scaled for its falloff: dropping the falloff would over-light the mouth.
  - **Who attaches it:** `CharacterShaderTiers.apply_to_tree` gives every mouth-family material it reaches (an
    owned copy, never the `.tres`) the pass as its `next_pass`, copies the pass's parameters from it, and sets
    `cavity_bounce_pass` so the base pass leaves positional lights to the pass. The stages and
    `GraphicsRuntime.on_scene_entered` both call it, so every hero gets it. A material no tree walk reached keeps
    the old fallback (`ATTENUATION`, shadow included). Parameters are copied when the pass is attached: if you
    change a mouth parameter at runtime, change it on `next_pass` too.
  - **Drawn only where a positional light reaches the mouth (M1-RND-26, option a).** FSR2, the High
    preset's default upscaler, resolves the pixels under a transparent draw differently, even when that draw
    adds exactly nothing. Under directional light alone the pass made the teeth and interior edges of
    `asha_face_grief` softer: up to 74/255 on the mouth's pixels. So the pass stays on the material (meta
    `hymn_mouth_bounce`), but `next_pass` and `cavity_bounce_pass` are switched on only while a visible
    `OmniLight3D` or `SpotLight3D` has that mouth within its range (`CharacterShaderTiers.refresh_bounce_passes`).
    - `apply_to_tree` runs the check on every walk: zone entry and preset changes.
    - Call it again when a positional light near the cast appears, moves out of reach or goes. The underwater
      rig calls it when it builds Rhen's lantern.
    - With the pass hidden, the base pass keeps the positional bounce (the old shadowed fallback). That case
      only comes up for a light the check hasn't seen yet.
    - GPU (High, FSR2): under the directional key, the shipped frame's mouth pixels now match the no-pass frame
      within the capture's own run-to-run noise (max 21/255, mean 1.8, against 21 and 1.5 for two no-pass runs).
      Under a shadowed spot the pass still adds the bounce (mean 23.7/255 over the mouth, as before).
    - High captures aren't bit-repeatable here. FSR2 and TAA resolve the dithered hair, lashes and brows a little
      differently each run, so compare the mouth pixels (the probe's `mask` variant), not whole frames.
  - **Cost:** one extra additive draw of the three small mouth meshes per frame. It runs only for positional lights
    and does no texture work beyond the base pass's albedo and ORM fetches.
  - **No current shot changes.** Every Asha shot is lit by directional lights (asha_stage.tscn), and no other hero
    uses the family yet. The face stage with spot lights (`base_body_stage.tscn`) has no mouth materials. The pass
    matters for cutscene keys (M2-FP-10) and any spot- or omni-lit dialogue.
- **Every hero:** test_character_shading walks `assets/characters/*/materials/` and fails on any `mouth`, `teeth`
  or `tongue` material outside the family (Rhen and Toma, M2-CHR-01, inherit the rule).
  - Defaults: #C79A8C, 0.4, 0.5. A saturated lip red turned the teeth orange.
- **Tiers:** the bounce is on every tier. Low drops only the GGX lobe from lights.
- **Measured** on the GPU (`docs/kb/qa/gpu/2026-10-23-rnd-21-mouth-fill.md`), over the grief interior pixels:
  - The median luminance rises 0.0121 → 0.0174 (High) and 0.0121 → 0.0180 (Low).
  - The share below 0.01 halves: 0.30 → 0.16 (High) and 0.29 → 0.14 (Low).
  - Closed-mouth shots don't change.
- **The teeth still read khaki-brown,** even under a neutral bounce. That's the atlas teeth patch's albedo (QA-05c
  fault 3, M1-CHR-11), not this term.

## Cost estimates

**GPU (estimates from operation counts, not measured).** Per lit pixel, per light, compared with a StandardMaterial3D:

| Shader | High | Medium | Low | Texture fetches (fragment) |
|---|---|---|---|---|
| Skin | ~1.8× | ~1.4× | ~1.0× | 5 (4 on Low) |
| Hair | ~1.4× | ~1.2× | ~0.9× | 2 |
| Eye | ~1.3× | ~1.3× | ~0.8× | 2 |
| Cloth | ~2.2×: every layer is evaluated and masked, not branched | ~1.9× | ~1.4× | 6 |
| Cornea, occlusion, tear | Small transparent shells, a few hundred triangles each | | | 0 |

The real cost of a hero is **overdraw**, not ALU. Opaque dithered hair cards are rejected by the depth pre-pass, but the pre-pass and the shadow passes still rasterise every layer (2–4 deep), with `discard`. Estimated cost of one hero at 1440p on RTX 3060-class hardware: **0.4–0.9 ms** in a dialogue close-up filling about 40% of the screen, and **0.1–0.3 ms** at battle framing. Character-shading cost is not a risk to the §4.2 budgets. Hair overdraw and shadow casting from the cards are the items to measure first on the GPU runner.

**CPU (lavapipe, 4 shared vCPUs). Does not represent GPU cost.**

- Capture times for the four shots at 960×540, 30 frames: 43–110 s each.
- A full-screen-quad bench put every variant between 0.3× and 1.3× the StandardMaterial3D frame time. It was too noisy to rank the tiers, because parallel agents share the CPU (cloth Low even measured slower than High), so it isn't used for any decision here.

## Test stage and shots

`game/levels/_tests/character_shading/shading_test.tscn` (`CharacterShadingStage`):

- A neutral dark studio cyclorama under a muted dome, which is what the lacquer and cornea reflect.
- **Key:** the Ch2 Act I warm key `#FFB87B` (~3200 K, energy 2.4) from front-left above.
- **Rim:** the Ch3 dusk rim `#F2A64A` (~2700 K, energy 1.8) from behind-right.
- Wind globals pinned (and restored on exit).
- The procedural bust (head, ears, lids, eyes and shells, ~500 hair cards, lacquer collar) and the cloth set (indigo drape with embroidered band and gold thread, verse sleeve at S3, a second sleeve at S7 mid-dissolve).
- A side-by-side comparison rig where the right-hand bust gets the Low tier on duplicated materials.
- `tier` exported for previews.

| Shot (`tests/screenshots/shots.json`) | Camera | What it checks |
|---|---|---|
| `char_skin_eye_closeup` | `Cameras/SkinEye` | Pores, freckles, painterly 0.2, iris refraction and limbal ring, catch-light, lid occlusion |
| `char_hair_backlit` | `Cameras/HairBack` | Hair against the dusk rim: transmission glow, dither resolve, strand variation |
| `char_cloth_gold` | `Cameras/Cloth` | Charlie sheen on indigo, embroidery relief, gold thread, verse bands S1–S3 with S4+ hidden, gauze transmission, the S8 dissolve edge |
| `char_low_compare` | `Cameras/Compare` | High (left) against the Low tier (right) under identical light |

`Cameras/EyeMacro` and `Cameras/FaceFront` are extra framings for manual inspection and aren't in the manifest.

## Fidelity assessment (honest)

- **What works.** The eye is the strongest part:
  - Refraction gives the iris real depth as the view changes.
  - The limbal ring, catch-light, lid shadow and tear line together stop it reading as a painted ball.
  - Skin shows a soft, warm terminator, faint red penumbrae and pore-scale breakup that survives mipmapping.
  - Cloth has convincing sheen on dyed cotton, raised embroidery, lacquer with a dark mirror, and gold that glints along the thread.
  - Every verse band state works off one mesh and one uniform.
  - The hair dither resolves under TAA without sorting.
- **What the test frames can't prove.** The bust is a procedural ellipsoid with gaussian features. Its proportions (nose, mouth, ears, the seam where the lid skirt meets the face) are crude, and **the frames read as a mannequin, not a person**. That is a geometry and authoring gap, not a shader one, but it means **the uncanny-valley risk (SPEC §14) is still open**. It can only be judged on the M1-CHR-02 Asha head with sculpted forms, real maps, expression and motion.
- **Skin.** Without real albedo variation and a real curvature distribution, the skin reads waxy and slightly orange under the warm key. Pre-integration is subtle at a 2.5 mm scatter radius on gently curved areas. Most of the visible softness comes from the 0.15 wrap and the normal blur. The painterly slider works as a safety valve, but at 1.0 it is closer to cel shading than paint. A real painterly look needs authored colour zones in the albedo (warm nose and cheeks, cool jaw), not just a shading ramp.
- **Hair.**
  - With Asha's specified secondary lobe (0.5 × `#8A5A3A`), flat sheets of black hair read **bronze**. The test material uses 0.3, and flow-map variation matters more than any shader constant. **Proposal to the Art Director:** secondary 0.3 for black hair, and `#8A5A3A` adopted as the transmission colour.
  - Card stripes stay visible on the crown, where the test cards are coarse.
  - Dithered gauze still shows a faint screen-door grain after 30 TAA frames on lavapipe. A blue-noise or stratified per-frame pattern, or a GPU check of Godot's TAA history weighting, is the follow-up.
- **Eyes.** There's no sclera vein map yet, and the caustic is a stylised crescent, not a ray-traced focus.
- **Cloth.** Indirect sheen is missing (see above). Every layer is evaluated for every pixel, so branching on the masks is a later optimisation.
- **Not verified here:** GPU performance; driver compile and pipeline creation (headless only checks the front end); and behaviour under SDFGI, VoxelGI or volumetric fog with real zone lighting.

## Open items

| For | Item |
|---|---|
| Art | Approve or reject the hair secondary 0.3, transmission `#8A5A3A`, the warm eye-occlusion tint, the sclera colour `#DCD0C4`, and the painterly default 0.2. |
| Character (M1-CHR-02) | Author maps and geometry to the contracts above, and add the hero's scenes to the prewarm entries. |
| RND-05 | Move the preset → tier mapping into the presets data and call `CharacterShaderTiers.apply_to_tree` from settings apply. |
| RND-06 | Filter prewarm entries by the active tier. |
| QA (M1-QA-01) | Measure hero cost on a GPU, especially hair pre-pass and shadow overdraw. Re-approve these baselines on that runner. |
| Lead | The art README asks for an ADR on mask and vertex-colour packing. This page documents the cloth and hair vertex-colour convention and its alignment with vegetation, ready to cite. |

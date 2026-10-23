// Hymn of the Undertow: hero costume cloth (M1-RND-04, SPEC §8.2 item 6). Body shared by
// character_cloth{,_medium,_low}.gdshader (opaque, cull_back) and character_cloth_sheer{,_medium,
// _low}.gdshader (HYMN_CLOTH_SHEER: gauze, two-sided, dithered alpha, transmission, S8 dissolve).
// One shader for every costume in the game. Docs: docs/kb/tech/character_shading.md ("Cloth").
//
// Layers, all from the cloth mask (asha.md §4.2: R embroidery, G gold thread / leaf, B lacquer,
// A sheen):
//   base     Lambert + dielectric GGX (ORM roughness) + Charlie sheen (Estevez & Kulla 2017) with
//            weight A (0 leather/metal, 0.3 cotton, 0.8 silk)
//   R        embroidery: sheen +0.3, roughness -0.1, adds the tiled thread detail normal
//   G        gold thread / leaf: metallic 1, roughness 0.28, albedo forced to col_gold, anisotropic
//            GGX along the UV tangent (rotated by gold_tangent_rotation)
//   B        lacquer: clear coat (roughness 0.06, F0 0.04) over a base of roughness 0.35. The coat
//            uses the geometric normal, so leather grain shows under a mirror-smooth surface.
// Verse-sleeve (asha.md §3): tex_band_id stores n / 7 for band n (0 = blank gauze); band n shows
// when verse_count >= n, otherwise the pixel reverts to blank gauze. sleeve_dissolve (sheer
// only) unravels the sleeve from the cuff up with a glimmer_lift edge (S8).
// Tiers: LOW = sheen + isotropic gold, lacquer as a single low-roughness lobe, no detail normal,
// primary wind only, alpha scissor for gauze. MEDIUM = + clear coat, detail normal, dithered
// gauze. HIGH/ULTRA = + anisotropic gold.

#ifndef HYMN_CHARACTER_CLOTH_BODY_GDSHADERINC
#define HYMN_CHARACTER_CLOTH_BODY_GDSHADERINC

#include "res://game/shaders/character/character_brdf.gdshaderinc"
#include "res://game/shaders/character/character_wind.gdshaderinc"

// Band ids are stored as n / HYMN_VERSE_BANDS (asha.md §9.2 step 6).
#define HYMN_VERSE_BANDS 7.0
// Dielectric F0 of fibres, leather and lacquer resin (IOR ~1.5).
#define HYMN_CLOTH_F0 0.04
// Godot's SPECULAR input maps F0 = 0.08 * SPECULAR.
#define HYMN_CLOTH_SPECULAR (HYMN_CLOTH_F0 / 0.08)
#define HYMN_CLOTH_DITHER_FPS 60.0
#define HYMN_CLOTH_EMBROIDERY_SHEEN 0.3 // asha.md §4.2
#define HYMN_CLOTH_EMBROIDERY_ROUGHNESS 0.1

group_uniforms base;
uniform vec4 col_albedo : source_color = vec4(1.0);
uniform sampler2D tex_albedo : source_color, hint_default_white, filter_linear_mipmap_anisotropic;
uniform sampler2D tex_normal : hint_normal, filter_linear_mipmap_anisotropic;
uniform float normal_strength : hint_range(0.0, 2.0) = 1.0;
uniform sampler2D tex_orm : hint_default_white, filter_linear_mipmap_anisotropic;
uniform float roughness_scale : hint_range(0.0, 2.0) = 0.85;
uniform sampler2D tex_cloth_mask : hint_default_black, filter_linear_mipmap_anisotropic;
group_uniforms;

group_uniforms sheen;
uniform vec4 col_sheen : source_color = vec4(0.922, 0.906, 0.875, 1.0); // gauze_white #EBE7DF
uniform float sheen_tint : hint_range(0.0, 1.0) = 0.7; // 0 = col_sheen, 1 = sqrt(albedo)
uniform float sheen_roughness : hint_range(0.05, 1.0) = 0.5; // asha.md §3.1
uniform float sheen_intensity : hint_range(0.0, 4.0) = 1.0;
group_uniforms;

group_uniforms embroidery;
uniform sampler2D tex_detail_normal : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform float detail_tiling : hint_range(1.0, 512.0) = 64.0;
uniform float detail_strength : hint_range(0.0, 2.0) = 0.8;
group_uniforms;

group_uniforms gold;
uniform vec4 col_gold : source_color = vec4(0.831, 0.643, 0.216, 1.0); // gold_leaf #D4A437
uniform float gold_roughness : hint_range(0.02, 1.0) = 0.28; // asha.md §4.2
uniform float gold_anisotropy : hint_range(0.0, 0.95) = 0.65; // thread runs along the tangent
uniform float gold_tangent_rotation : hint_range(-3.1416, 3.1416) = 0.0;
group_uniforms;

group_uniforms lacquer;
uniform float lacquer_base_roughness : hint_range(0.02, 1.0) = 0.35; // asha.md §4.2
uniform float lacquer_coat_roughness : hint_range(0.0, 0.5) = 0.06;
uniform float lacquer_coat_strength : hint_range(0.0, 1.0) = 1.0;
group_uniforms;

group_uniforms verse_sleeve;
// An id map, not an image: nearest, no mipmaps. Bilinear or mip averaging between band 7 and blank 0
// makes the in-between ids 1-6 and leaks hidden bands (M1-RND-09; character_shading.md map table).
uniform sampler2D tex_band_id : hint_default_black, filter_nearest;
uniform int verse_count : hint_range(0, 7) = 7;
uniform vec4 col_blank_gauze : source_color = vec4(0.922, 0.906, 0.875, 1.0); // gauze_white
uniform float blank_alpha : hint_range(0.0, 1.0) = 0.55; // asha.md §3.1
uniform float blank_sheen : hint_range(0.0, 1.0) = 0.5;
group_uniforms;

#ifdef HYMN_CLOTH_SHEER
group_uniforms sheer;
uniform float transmission : hint_range(0.0, 1.0) = 0.35; // asha.md §3.1 backscatter
uniform float transmission_forward_power : hint_range(1.0, 16.0) = 4.0;
uniform float alpha_cutoff : hint_range(0.05, 0.95) = 0.35; // Low: alpha scissor
uniform bool dither_temporal = true;
uniform float sleeve_dissolve : hint_range(0.0, 1.0) = 0.0; // S8: 0 intact .. 1 gone
uniform float sleeve_v_shoulder : hint_range(0.0, 1.0) = 0.0; // UV.y at the shoulder seam
uniform float sleeve_v_cuff : hint_range(0.0, 1.0) = 1.0; // UV.y at the cuff tip
uniform float dissolve_noise : hint_range(0.0, 1.0) = 0.35;
uniform float dissolve_noise_scale : hint_range(1.0, 64.0) = 14.0;
uniform float dissolve_edge : hint_range(0.0, 0.3) = 0.06;
uniform vec4 col_dissolve_glow : source_color = vec4(1.0, 0.914, 0.722, 1.0); // glimmer_lift #FFE9B8
uniform float dissolve_glow_energy : hint_range(0.0, 16.0) = 4.0;
group_uniforms;
#endif

varying vec4 v_layers; // x embroidery, y gold, z lacquer (without gold), w sheen weight
varying vec3 v_geo_normal;
varying vec3 v_gold_t;
varying float v_base_rough;

void vertex() {
	VERTEX += hymn_char_wind_offset(VERTEX, NORMAL, COLOR, MODEL_MATRIX);
}

void fragment() {
	vec4 albedo = texture(tex_albedo, UV) * col_albedo;
	vec4 mask = texture(tex_cloth_mask, UV);
	vec4 orm = texture(tex_orm, UV);
	vec3 n = hymn_char_unpack_normal(texture(tex_normal, UV).rg, normal_strength);

	// Verse-sleeve: hide bands above the current verse count.
	float band = floor(texture(tex_band_id, UV).r * HYMN_VERSE_BANDS + 0.5);
	float hidden = step(float(verse_count) + 0.5, band);
	albedo = mix(albedo, vec4(col_blank_gauze.rgb, blank_alpha), hidden);
	mask = mix(mask, vec4(0.0, 0.0, 0.0, blank_sheen), hidden);
	n = normalize(mix(n, vec3(0.0, 0.0, 1.0), hidden));

	float emb = mask.r;
	float gold = mask.g;
	float lacquer = mask.b * (1.0 - gold); // leaf sits on top of the lacquer
	float sheen = clamp(mask.a + HYMN_CLOTH_EMBROIDERY_SHEEN * emb, 0.0, 1.0);
#if HYMN_QUALITY >= HYMN_QUALITY_MEDIUM
	vec3 nd = hymn_char_unpack_normal(texture(tex_detail_normal, UV * detail_tiling).rg, detail_strength * emb);
	n = hymn_char_blend_rnm(n, nd);
#endif
	NORMAL_MAP = hymn_char_pack_normal(n);
	NORMAL_MAP_DEPTH = 1.0;

#ifdef HYMN_CLOTH_SHEER
	float a = albedo.a;
#if HYMN_QUALITY >= HYMN_QUALITY_MEDIUM
	float frame = dither_temporal ? floor(TIME * HYMN_CLOTH_DITHER_FPS) : 0.0;
	if (a < mix(HYMN_EPSILON, 1.0, hymn_char_ign(FRAGCOORD.xy, frame))) {
		discard;
	}
#else
	ALPHA = a;
	ALPHA_SCISSOR_THRESHOLD = alpha_cutoff;
#endif
	if (sleeve_dissolve > 0.0) {
		float along = clamp((UV.y - sleeve_v_shoulder) / (sleeve_v_cuff - sleeve_v_shoulder), 0.0, 1.0);
		float field = (1.0 - along) + hymn_fbm2(UV * dissolve_noise_scale, 3, 2.0, 0.5) * dissolve_noise;
		float cut = sleeve_dissolve * (1.0 + dissolve_noise + dissolve_edge);
		if (field < cut - dissolve_edge) {
			discard;
		}
		float edge = 1.0 - clamp((field - (cut - dissolve_edge)) / max(dissolve_edge, HYMN_EPSILON), 0.0, 1.0);
		EMISSION = col_dissolve_glow.rgb * (dissolve_glow_energy * edge * edge);
	}
#endif

	float rough = clamp(orm.g * roughness_scale - HYMN_CLOTH_EMBROIDERY_ROUGHNESS * emb, 0.03, 1.0);
	rough = mix(rough, lacquer_base_roughness, lacquer);
	ALBEDO = mix(albedo.rgb, col_gold.rgb, gold);
	METALLIC = max(orm.b, gold);
	AO = orm.r;
	SPECULAR = HYMN_CLOTH_SPECULAR;
	// Indirect light sees the top-most interface: the coat on lacquer, the leaf on gold.
	ROUGHNESS = mix(mix(rough, gold_roughness, gold), lacquer_coat_roughness, lacquer * lacquer_coat_strength);
#if HYMN_QUALITY >= HYMN_QUALITY_HIGH
	vec2 flow = vec2(cos(gold_tangent_rotation), sin(gold_tangent_rotation));
	ANISOTROPY = gold * gold_anisotropy;
	ANISOTROPY_FLOW = flow;
	v_gold_t = normalize(TANGENT * flow.x + BINORMAL * flow.y);
#else
	v_gold_t = TANGENT;
#endif
	v_layers = vec4(emb, gold, lacquer, sheen);
	v_geo_normal = NORMAL;
	v_base_rough = rough;
}

void light() {
	float ndl = max(dot(NORMAL, LIGHT), 0.0);
	float gold = v_layers.y;
	float lacquer = v_layers.z * lacquer_coat_strength;
	vec3 f0 = vec3(HYMN_CLOTH_F0);

	// Sheen lobe and the matching diffuse energy loss.
	// Dyed fibres scatter their own colour at grazing angles: tint toward sqrt(albedo) (brighter, same hue).
	vec3 sheen_col = mix(col_sheen.rgb, sqrt(ALBEDO), sheen_tint) * (v_layers.w * sheen_intensity * (1.0 - gold));
	vec3 sheen = hymn_char_sheen_lobe(NORMAL, VIEW, LIGHT, sheen_col, sheen_roughness);
	float diffuse_scale = hymn_char_sheen_albedo_scale(sheen_col);

	// Base specular: dielectric, or gold (metal, F0 = gold albedo).
	vec3 spec_d = hymn_char_ggx_lobe(NORMAL, VIEW, LIGHT, v_base_rough, f0);
#if HYMN_QUALITY >= HYMN_QUALITY_HIGH
	vec3 t = normalize(v_gold_t - NORMAL * dot(NORMAL, v_gold_t));
	vec3 b = cross(NORMAL, t);
	float ag = max(gold_roughness * gold_roughness, HYMN_CHAR_MIN_ALPHA);
	float at = max(ag * (1.0 + gold_anisotropy), HYMN_CHAR_MIN_ALPHA);
	float ab = max(ag * (1.0 - gold_anisotropy), HYMN_CHAR_MIN_ALPHA);
	vec3 spec_g = hymn_char_ggx_aniso_lobe(NORMAL, t, b, VIEW, LIGHT, at, ab, col_gold.rgb);
#else
	vec3 spec_g = hymn_char_ggx_lobe(NORMAL, VIEW, LIGHT, gold_roughness, col_gold.rgb);
#endif
	vec3 spec = mix(spec_d, spec_g, gold);

	float coat_t = 1.0;
#if HYMN_QUALITY >= HYMN_QUALITY_MEDIUM
	// Clear coat on lacquer: its Fresnel takes energy from everything under it.
	vec3 ng = normalize(v_geo_normal);
	float fc = hymn_char_f_schlick1(HYMN_CLOTH_F0, max(dot(ng, VIEW), 0.0)) * lacquer;
	coat_t = 1.0 - fc;
	vec3 coat = hymn_char_ggx_lobe(ng, VIEW, LIGHT, lacquer_coat_roughness, f0) * lacquer;
	spec = spec * coat_t + coat;
#else
	// Low: the lacquer is one sharp lobe on the shading normal.
	spec = mix(spec, hymn_char_ggx_lobe(NORMAL, VIEW, LIGHT, lacquer_coat_roughness, f0), lacquer);
#endif

	float diffuse = ndl * diffuse_scale * coat_t * ATTENUATION;
#ifdef HYMN_CLOTH_SHEER
	// Sheer gauze glows under rim light: diffuse transmission from behind plus a forward lobe.
	// A single gauze layer shadows itself in the shadow map, so most of that shadow is ignored.
	float behind = max(-dot(NORMAL, LIGHT), 0.0);
	float forward = pow(clamp(dot(VIEW, -LIGHT), 0.0, 1.0), transmission_forward_power);
	diffuse += (0.5 * behind + forward) * transmission * mix(ATTENUATION, 1.0, 0.7);
#endif
	DIFFUSE_LIGHT += vec3(diffuse) * LIGHT_COLOR / PI;
	SPECULAR_LIGHT += (spec + sheen) * ATTENUATION * LIGHT_COLOR * SPECULAR_AMOUNT;
}

#endif

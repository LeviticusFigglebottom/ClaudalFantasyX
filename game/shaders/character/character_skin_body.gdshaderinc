// Hymn of the Undertow: hero skin (M1-RND-04, SPEC §8.2 item 4). Body shared by the tier
// wrappers character_skin{,_medium,_low}.gdshader. Docs: docs/kb/tech/character_shading.md.
//
// Technique: pre-integrated diffuse SSS (Penner & Borshukov 2011) evaluated analytically in
// light() (no LUT, no extra pass), curvature from screen-space derivatives of the geometric normal,
// per-channel normal blurring, penumbra scattering for the sun, thin-region transmission, a
// dual-lobe GGX specular, a tiled pore detail normal and pore-level micro-roughness from the skin
// mask, plus a `painterly` blend toward stylised shading (SPEC §14 mitigation).
//
// Tiers (HYMN_QUALITY): LOW = wrapped Lambert + warm terminator, one GGX lobe, no detail normal.
// MEDIUM = pre-integrated SSS + detail normal, one GGX lobe. HIGH/ULTRA = everything.
//
// Maps (asha.md §4.2): tex_albedo sRGB; tex_normal tangent-space OpenGL +Y; tex_orm = AO,
// roughness (remapped into roughness_min..roughness_max), metallic (ignored on skin);
// tex_skin_mask = R SSS thickness (0 thin .. 1 thick), G cavity (0 deep .. 1 none),
// B micro-roughness variation (0.5 neutral), A detail-normal weight.

#ifndef HYMN_CHARACTER_SKIN_BODY_GDSHADERINC
#define HYMN_CHARACTER_SKIN_BODY_GDSHADERINC

#include "res://game/shaders/character/character_brdf.gdshaderinc"

// Godot reconstructs Z from the encoded XY of NORMAL_MAP; depth 1 keeps our blended normal as is.
#define HYMN_SKIN_NORMAL_MAP_DEPTH 1.0
// Curvature from fwidth() is in 1/m; scatter radii are authored in mm.
#define HYMN_MM_TO_M 0.001

group_uniforms albedo;
uniform vec4 col_albedo : source_color = vec4(1.0); // tint on tex_albedo (untextured: set skin_asha #B9876A)
uniform sampler2D tex_albedo : source_color, hint_default_white, filter_linear_mipmap_anisotropic;
uniform float cavity_albedo : hint_range(0.0, 1.0) = 0.35; // how much cavity darkens albedo
group_uniforms;

group_uniforms normals;
uniform sampler2D tex_normal : hint_normal, filter_linear_mipmap_anisotropic;
uniform float normal_strength : hint_range(0.0, 2.0) = 1.0;
uniform sampler2D tex_detail_normal : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform float detail_tiling : hint_range(1.0, 256.0) = 48.0; // detail repeats per UV unit
uniform float detail_strength : hint_range(0.0, 2.0) = 0.6;
group_uniforms;

group_uniforms surface;
uniform sampler2D tex_orm : hint_default_white, filter_linear_mipmap_anisotropic;
uniform sampler2D tex_skin_mask : hint_default_white, filter_linear_mipmap_anisotropic;
uniform float roughness_min : hint_range(0.05, 1.0) = 0.42; // asha.md §8.3: never wet
uniform float roughness_max : hint_range(0.05, 1.0) = 0.5;
uniform float micro_roughness : hint_range(0.0, 0.3) = 0.06; // +/- around the macro value
uniform float wet_roughness : hint_range(0.02, 0.5) = 0.12; // reached at inst_wetness = 1
uniform float cavity_specular : hint_range(0.0, 1.0) = 0.8; // specular occlusion from cavity
uniform float specular_scale : hint_range(0.0, 2.0) = 1.0;
uniform float lobe_roughness_a : hint_range(0.3, 1.0) = 1.0; // dual lobe (multiplies roughness)
uniform float lobe_roughness_b : hint_range(1.0, 2.5) = 1.6;
uniform float lobe_mix : hint_range(0.0, 1.0) = 0.2; // weight of the rough lobe B
group_uniforms;

group_uniforms scattering;
uniform vec4 col_scatter : source_color = vec4(0.784, 0.345, 0.29, 1.0); // asha.md §8.3 #C8584A
uniform float scatter_radius_mm : hint_range(0.1, 10.0) = 2.5;
uniform float sss_strength : hint_range(0.0, 1.0) = 1.0;
uniform float curvature_scale : hint_range(0.0, 4.0) = 1.0;
uniform float diffuse_wrap : hint_range(0.0, 0.5) = 0.15; // asha.md §8.3
uniform float normal_blur : hint_range(0.0, 1.0) = 0.6; // diffuse sees a softer normal (red most)
uniform float shadow_scatter : hint_range(0.0, 3.0) = 1.0; // red bleeding into sun penumbrae
uniform float transmission_strength : hint_range(0.0, 2.0) = 0.6; // thin regions, back-lit
uniform float transmission_power : hint_range(1.0, 16.0) = 3.0;
uniform float transmission_distortion : hint_range(0.0, 1.0) = 0.25;
uniform float transmission_shadow_leak : hint_range(0.0, 1.0) = 0.6; // self-shadow ignored when thin
group_uniforms;

group_uniforms painterly;
// 0 = physically based; 1 = stylised (soft two-tone ramp, warm terminator band, tinted shadow
// fill, fewer pores, one softer highlight). Asha's sheet asks for "slightly painterly".
uniform float painterly : hint_range(0.0, 1.0) = 0.0;
uniform float painterly_terminator : hint_range(-0.5, 0.5) = 0.02;
uniform float painterly_softness : hint_range(0.02, 1.0) = 0.3;
uniform float painterly_band : hint_range(0.0, 1.0) = 0.35; // warm terminator band strength
uniform float painterly_form : hint_range(0.0, 1.0) = 0.4; // how much N.L shading survives in the lit side
uniform vec4 col_painterly_shadow : source_color = vec4(0.42, 0.353, 0.431, 1.0); // lavender #6B5A6E
uniform float painterly_shadow_fill : hint_range(0.0, 0.5) = 0.1;
uniform float painterly_specular : hint_range(0.0, 1.0) = 0.6;
group_uniforms;

instance uniform float inst_wetness : hint_range(0.0, 1.0) = 0.0; // rain / sea spray / tears

varying vec3 v_geo_normal;
varying float v_curv_u;
varying float v_thickness;
varying float v_cavity;

vec3 skin_scatter_weights() {
	vec3 c = col_scatter.rgb;
	return c / max(max(c.r, c.g), max(c.b, HYMN_EPSILON));
}

void fragment() {
	vec4 albedo = texture(tex_albedo, UV) * col_albedo;
	vec4 orm = texture(tex_orm, UV);
	vec4 mask = texture(tex_skin_mask, UV);
	vec3 n = hymn_char_unpack_normal(texture(tex_normal, UV).rg, normal_strength);
#if HYMN_QUALITY >= HYMN_QUALITY_MEDIUM
	float detail_w = mask.a * detail_strength * (1.0 - 0.7 * painterly);
	vec3 nd = hymn_char_unpack_normal(texture(tex_detail_normal, UV * detail_tiling).rg, detail_w);
	n = hymn_char_blend_rnm(n, nd);
#endif
	NORMAL_MAP = hymn_char_pack_normal(n);
	NORMAL_MAP_DEPTH = HYMN_SKIN_NORMAL_MAP_DEPTH;

	float cavity = mask.g;
	vec3 base = albedo.rgb * mix(1.0, cavity, cavity_albedo);
	ALBEDO = hymn_saturate_color(base, 1.0 + 0.12 * painterly);

	float r = mix(roughness_min, roughness_max, orm.g);
#if HYMN_QUALITY >= HYMN_QUALITY_HIGH
	r += (mask.b - 0.5) * 2.0 * micro_roughness * (1.0 - painterly);
#endif
	r = mix(r, wet_roughness, inst_wetness);
	ROUGHNESS = clamp(r, 0.02, 1.0);
	METALLIC = 0.0;
	SPECULAR = HYMN_CHAR_SKIN_SPECULAR * mix(1.0, cavity, cavity_specular) * specular_scale;
	AO = orm.r;

	v_geo_normal = NORMAL;
	v_thickness = mask.r;
	v_cavity = mix(1.0, cavity, cavity_specular);
#if HYMN_QUALITY >= HYMN_QUALITY_MEDIUM
	// Curvature (1/m) of the interpolated vertex normal. Constant across a 2x2 quad, which is
	// invisible on a smooth head but would show on faceted low-poly geometry.
	float curv = length(fwidth(NORMAL)) / max(length(fwidth(VERTEX)), HYMN_EPSILON);
	v_curv_u = clamp(curv * scatter_radius_mm * HYMN_MM_TO_M * curvature_scale, 0.0, HYMN_SKIN_PREINT_U_MAX);
#else
	v_curv_u = 0.0;
#endif
}

void light() {
	vec3 ng = normalize(v_geo_normal);
	vec3 w = skin_scatter_weights();
	float ndl = dot(NORMAL, LIGHT);
	vec3 d;
#if HYMN_QUALITY >= HYMN_QUALITY_MEDIUM
	// Per-channel diffuse normal: red sees the smoothest surface, blue nearly the mapped one.
	vec3 blur = clamp(normal_blur * sss_strength * w, 0.0, 1.0);
	vec3 x = vec3(
			dot(normalize(mix(NORMAL, ng, blur.r)), LIGHT),
			dot(normalize(mix(NORMAL, ng, blur.g)), LIGHT),
			dot(normalize(mix(NORMAL, ng, blur.b)), LIGHT));
	x = (x + diffuse_wrap) / (1.0 + diffuse_wrap);
	vec3 lambert = max(x, vec3(0.0));
	vec3 pre = hymn_char_preint_skin(x, v_curv_u);
	d = lambert + (pre - lambert) * w * sss_strength;
#else
	float xw = hymn_char_wrap(ndl, diffuse_wrap);
	vec3 x = vec3(xw);
	// Cheap stand-in for scattering: a warm band at the terminator.
	d = vec3(xw) + col_scatter.rgb * (0.25 * sss_strength * clamp(1.0 - abs(ndl) * 3.0, 0.0, 1.0));
#endif
	vec3 att = vec3(ATTENUATION);
#if HYMN_QUALITY >= HYMN_QUALITY_HIGH
	if (LIGHT_IS_DIRECTIONAL) {
		// Penumbra scattering: shape the shadow edge per channel so red bleeds into it.
		att = pow(vec3(ATTENUATION), vec3(1.0) / (vec3(1.0) + shadow_scatter * sss_strength * w));
	}
#endif
	// Painterly: a soft two-tone ramp with a warm band at the terminator and a tinted fill.
	float s = smoothstep(painterly_terminator - painterly_softness, painterly_terminator + painterly_softness, x.g);
	// Keep some form inside the lit side so a frontal key does not flatten the face.
	float form = mix(1.0, clamp(x.g, 0.0, 1.0), painterly_form);
	vec3 paint = vec3(s * form) + col_scatter.rgb * (painterly_band * 4.0 * s * (1.0 - s));
	d = mix(d, paint, painterly);
	vec3 fill = col_painterly_shadow.rgb * ((1.0 - s) * painterly_shadow_fill * painterly);
	DIFFUSE_LIGHT += (d * att + fill * ATTENUATION) * LIGHT_COLOR / PI;

#if HYMN_QUALITY >= HYMN_QUALITY_HIGH
	// Transmission through thin regions (ears, nostrils), seen against the light.
	float thin = 1.0 - v_thickness;
	vec3 lt = normalize(LIGHT + ng * transmission_distortion);
	float back = pow(clamp(dot(VIEW, -lt), 0.0, 1.0), transmission_power);
	float t_att = mix(ATTENUATION, 1.0, thin * transmission_shadow_leak);
	DIFFUSE_LIGHT += col_scatter.rgb * (back * thin * transmission_strength * t_att) * LIGHT_COLOR / PI;
#endif

	vec3 f0 = vec3(HYMN_CHAR_SKIN_F0);
#if HYMN_QUALITY >= HYMN_QUALITY_HIGH
	vec3 lobe_b = hymn_char_ggx_lobe(NORMAL, VIEW, LIGHT, ROUGHNESS * lobe_roughness_b, f0);
	vec3 spec = hymn_char_ggx_lobe(NORMAL, VIEW, LIGHT, ROUGHNESS * lobe_roughness_a, f0) * (1.0 - lobe_mix)
			+ lobe_b * lobe_mix;
	// Painterly: the softer lobe takes over, so the highlight reads as a broad stroke.
	spec = mix(spec, lobe_b, painterly * 0.5);
#else
	vec3 spec = hymn_char_ggx_lobe(NORMAL, VIEW, LIGHT, ROUGHNESS, f0);
#endif
	spec *= v_cavity * specular_scale * mix(1.0, painterly_specular, painterly);
	SPECULAR_LIGHT += spec * ATTENUATION * LIGHT_COLOR * SPECULAR_AMOUNT;
}

#endif

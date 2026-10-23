// Hymn of the Undertow: cornea / tear-film shell over the eyeball (M1-RND-04). One variant for
// every tier (it is a few hundred triangles of additive specular). Docs:
// docs/kb/tech/character_shading.md ("Eyes").
//
// Geometry contract: same object space as the eyeball (origin at the eyeball centre, +Z = gaze),
// a sphere slightly larger than the eyeball with the corneal bulge in front. The shell adds only
// reflected light: Godot's sky / probe / SSR-free reflections through SPECULAR and ROUGHNESS, plus
// one GGX lobe per light from light(). Its diffuse is zero, so additive blending is exact enough
// (the transmitted 1 - F ~ 0.97 of the iris is drawn by the eyeball underneath).
//
// TAA stability of the wet highlight:
//  1. the normal is analytic (sphere + corneal cap), so tessellation never facets the highlight;
//  2. roughness is widened by geometric specular AA on that normal (Tokuyoshi & Kaplanyan 2019);
//  3. each light's highlight is clamped to highlight_max, so a sub-pixel HDR spike cannot fight
//     TAA's neighbourhood clamp and flicker;
//  4. it moves with the eyeball, whose motion vectors the shell's pixels reuse.
shader_type spatial;
render_mode blend_add, depth_draw_never, cull_back, shadows_disabled, specular_schlick_ggx;

#include "res://game/shaders/character/character_brdf.gdshaderinc"

group_uniforms geometry;
uniform float eye_radius_m : hint_range(0.008, 0.02) = 0.0132; // match the eyeball
uniform float iris_radius_m : hint_range(0.004, 0.01) = 0.00645;
uniform float cornea_radius_m : hint_range(0.005, 0.012) = 0.0086; // 7.8 mm x 1.10
group_uniforms;

group_uniforms wet;
uniform float roughness : hint_range(0.0, 0.5) = 0.04;
uniform float wet_strength : hint_range(0.0, 2.0) = 1.0; // grief: raise slightly with the tear layer
uniform float highlight_max : hint_range(0.5, 64.0) = 12.0; // per-light clamp, in light-colour units
uniform float spec_aa : hint_range(0.0, 1.0) = 1.0;
group_uniforms;

varying vec3 v_obj_pos;
varying float v_rough;

// Unit normal of the eye surface: the eyeball sphere, blended into the corneal sphere, whose
// centre sits on the axis so the two meet at the limbus.
vec3 eye_surface_normal(vec3 p) {
	float zl = sqrt(max(eye_radius_m * eye_radius_m - iris_radius_m * iris_radius_m, 0.0));
	float zc = zl - sqrt(max(cornea_radius_m * cornea_radius_m - iris_radius_m * iris_radius_m, 0.0));
	vec3 n_ball = normalize(p);
	vec3 n_cornea = normalize(p - vec3(0.0, 0.0, zc));
	float k = smoothstep(1.15, 0.95, length(p.xy) / iris_radius_m) * step(0.0, p.z);
	return normalize(mix(n_ball, n_cornea, k));
}

void vertex() {
	v_obj_pos = VERTEX;
}

void fragment() {
	vec3 n_obj = eye_surface_normal(v_obj_pos);
	NORMAL = normalize(mat3(VIEW_MATRIX) * (mat3(MODEL_MATRIX) * n_obj));
	float r = mix(roughness, hymn_char_spec_aa_roughness(NORMAL, roughness), spec_aa);
	v_rough = r;
	ALBEDO = vec3(0.0);
	METALLIC = 0.0;
	ROUGHNESS = r;
	SPECULAR = HYMN_CHAR_CORNEA_F0 / 0.08 * wet_strength;
	ALPHA = 1.0;
}

void light() {
	vec3 s = hymn_char_ggx_lobe(NORMAL, VIEW, LIGHT, v_rough, vec3(HYMN_CHAR_CORNEA_F0)) * wet_strength;
	SPECULAR_LIGHT += min(s * ATTENUATION * LIGHT_COLOR * SPECULAR_AMOUNT, vec3(highlight_max));
}

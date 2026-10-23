// Hymn of the Undertow: hero eyeball (sclera + iris) (M1-RND-04, SPEC §7.3 "separate cornea and
// refraction shader"). Body shared by character_eye{,_medium,_low}.gdshader. The wet surface is a
// separate shell (character_cornea.gdshader); lid shadow and the tear meniscus are helpers
// (character_eye_occlusion.gdshader, character_tear_line.gdshader).
// Docs: docs/kb/tech/character_shading.md ("Eyes").
//
// Geometry contract: the eyeball is its own MeshInstance3D (parented to a BoneAttachment3D on the
// eye bone), origin at the eyeball centre, +Z = gaze, uniform scale. Everything is parametrised
// in object space from eye_radius_m / iris_radius_m, so the mesh UVs are not used for the iris.
//
// Refraction: the view ray refracts at the cornea (IOR 1.376) and travels down to the iris plane
// through the anterior chamber; the iris is looked up where that ray lands (parallax offset,
// Jimenez 2012). The iris is lit with a concave normal and gets a caustic on the side away from
// the light (asha.md §8.3). LOW: no refraction, flat iris, no caustic.

#ifndef HYMN_CHARACTER_EYE_BODY_GDSHADERINC
#define HYMN_CHARACTER_EYE_BODY_GDSHADERINC

#include "res://game/shaders/character/character_brdf.gdshaderinc"

// Smallest |z| of the refracted ray used for the parallax divide (grazing views).
#define HYMN_EYE_MIN_RAY_Z 0.2
// Texture convention: tex_iris covers the iris disc edge to edge, with its pupil at this radius.
#define HYMN_EYE_TEX_PUPIL 0.3

group_uniforms geometry;
uniform float eye_radius_m : hint_range(0.008, 0.02) = 0.0132; // 12 mm x 1.10 (asha.md §1)
uniform float iris_radius_m : hint_range(0.004, 0.01) = 0.00645; // 12.9 mm iris (asha.md §1)
uniform float pupil_radius : hint_range(0.1, 0.7) = 0.36; // fraction of the iris radius
uniform float pupil_dilation : hint_range(-1.0, 1.0) = 0.0; // cinematics: fear +, bright light -
group_uniforms;

group_uniforms iris;
uniform vec4 col_iris : source_color = vec4(0.227, 0.149, 0.094, 1.0); // Asha #3A2618
uniform sampler2D tex_iris : source_color, hint_default_white, filter_linear_mipmap_anisotropic;
uniform vec4 col_limbal : source_color = vec4(0.353, 0.227, 0.141, 1.0); // Asha #5A3A24
uniform float limbal_width : hint_range(0.0, 0.5) = 0.15; // outer fraction of the iris
uniform float limbus_softness : hint_range(0.005, 0.2) = 0.06;
uniform float limbus_shadow : hint_range(0.0, 1.0) = 0.45; // dark ring where iris meets sclera
uniform vec4 col_pupil : source_color = vec4(0.03, 0.025, 0.022, 1.0);
uniform float ior : hint_range(1.0, 1.6) = 1.376; // asha.md §8.3
uniform float anterior_depth_m : hint_range(0.0, 0.006) = 0.0028;
uniform float iris_concavity : hint_range(0.0, 2.0) = 0.6;
uniform float caustic_strength : hint_range(0.0, 4.0) = 1.2;
uniform float caustic_power : hint_range(1.0, 8.0) = 2.5;
group_uniforms;

group_uniforms sclera;
uniform vec4 col_sclera : source_color = vec4(0.863, 0.816, 0.769, 1.0); // #DCD0C4, warm, under the albedo ceiling
uniform sampler2D tex_sclera : source_color, hint_default_white, filter_linear_mipmap_anisotropic;
uniform vec4 col_sclera_scatter : source_color = vec4(0.784, 0.416, 0.353, 1.0); // #C86A5A
uniform float sclera_wrap : hint_range(0.0, 1.0) = 0.35;
// Only for eyes rendered without the cornea shell (e.g. distant LODs): adds the wet lobe here.
uniform float self_specular : hint_range(0.0, 1.0) = 0.0;
group_uniforms;

varying vec3 v_obj_pos;
varying vec3 v_cam_obj;
varying vec3 v_ex;
varying vec3 v_ey;
varying vec3 v_ez;
varying vec3 v_iris; // xy = refracted iris position / iris radius, z = iris mask

void vertex() {
	v_obj_pos = VERTEX;
	v_cam_obj = (inverse(MODEL_MATRIX) * vec4(CAMERA_POSITION_WORLD, 1.0)).xyz;
	v_ex = normalize((MODELVIEW_MATRIX * vec4(1.0, 0.0, 0.0, 0.0)).xyz);
	v_ey = normalize((MODELVIEW_MATRIX * vec4(0.0, 1.0, 0.0, 0.0)).xyz);
	v_ez = normalize((MODELVIEW_MATRIX * vec4(0.0, 0.0, 1.0, 0.0)).xyz);
}

void fragment() {
	vec3 p = v_obj_pos;
	float r_i = iris_radius_m;
	float rr_surface = length(p.xy) / r_i;
	vec2 q = p.xy;
	float front = step(0.0, p.z);
#if HYMN_QUALITY >= HYMN_QUALITY_MEDIUM
	// Refract at the (spherical) cornea and march to the iris plane.
	float big_r = eye_radius_m;
	float z_iris = sqrt(max(big_r * big_r - r_i * r_i, 0.0));
	vec3 v = normalize(v_cam_obj - p);
	vec3 rd = refract(-v, normalize(p), 1.0 / ior);
	float h = anterior_depth_m * clamp((p.z - z_iris) / max(big_r - z_iris, HYMN_EPSILON), 0.0, 1.0);
	vec2 q_refr = p.xy + rd.xy * (h / max(-rd.z, HYMN_EYE_MIN_RAY_Z));
	float cornea = 1.0 - smoothstep(1.0, 1.12, rr_surface);
	q = mix(p.xy, q_refr, cornea * front);
#endif
	float r = length(q) / r_i;
	float iris_mask = (1.0 - smoothstep(1.0 - limbus_softness, 1.0 + limbus_softness, r)) * front;

	// Pupil dilation remaps the iris radially so the texture's fibres stretch, not slide.
	float pupil_r = clamp(pupil_radius * (1.0 + 0.5 * pupil_dilation), 0.05, 0.9);
	float t = clamp((r - pupil_r) / max(1.0 - pupil_r, HYMN_EPSILON), 0.0, 1.0);
	float r_tex = mix(HYMN_EYE_TEX_PUPIL, 1.0, t);
	vec2 dir = r > HYMN_EPSILON ? q / (r * r_i) : vec2(0.0);
	vec2 iris_uv = vec2(0.5) + dir * (0.5 * r_tex) * vec2(1.0, -1.0);
	vec3 iris = texture(tex_iris, iris_uv).rgb * col_iris.rgb;
	iris = mix(iris, col_limbal.rgb, smoothstep(1.0 - limbal_width, 1.0, r) * step(r, 1.0 + limbus_softness));
	iris = mix(col_pupil.rgb, iris, smoothstep(pupil_r - 0.03, pupil_r + 0.03, r));

	vec3 sclera = texture(tex_sclera, UV).rgb * col_sclera.rgb;
	float ring = exp(-pow((rr_surface - 1.0) / max(limbus_softness * 2.0, HYMN_EPSILON), 2.0)) * front;
	sclera *= 1.0 - limbus_shadow * ring;
	ALBEDO = mix(sclera, iris * (1.0 - 0.5 * limbus_shadow * ring), iris_mask);
	ROUGHNESS = 0.3;
	SPECULAR = 0.0; // the cornea shell carries the wet reflection
	METALLIC = 0.0;

#if HYMN_QUALITY >= HYMN_QUALITY_MEDIUM
	// Concave iris: its normal tilts toward the optical axis, so the side away from the light
	// receives more light, like a real iris under a convex cornea.
	vec3 n_obj = normalize(vec3(-q * iris_concavity / r_i, 1.0));
	vec3 n_view = normalize(mat3(VIEW_MATRIX) * (mat3(MODEL_MATRIX) * n_obj));
	NORMAL = normalize(mix(NORMAL, n_view, iris_mask));
#endif
	v_iris = vec3(q / r_i, iris_mask);
}

void light() {
	float ndl = dot(NORMAL, LIGHT);
	float iris_mask = v_iris.z;
	// Sclera: wrapped, with a warm terminator (it is a translucent, vascular tissue).
	float ws = hymn_char_wrap(ndl, sclera_wrap);
	vec3 sclera_d = vec3(ws) + col_sclera_scatter.rgb * (0.3 * clamp(1.0 - abs(ndl) * 2.5, 0.0, 1.0));
	vec3 iris_d = vec3(max(ndl, 0.0));
#if HYMN_QUALITY >= HYMN_QUALITY_MEDIUM
	// Caustic: the cornea focuses light onto the iris on the side opposite the light.
	vec2 lp = vec2(dot(LIGHT, v_ex), dot(LIGHT, v_ey));
	float lz = clamp(dot(LIGHT, v_ez), 0.0, 1.0);
	float side = length(lp);
	vec2 pos = v_iris.xy;
	float across = side > HYMN_EPSILON && length(pos) > HYMN_EPSILON ? dot(normalize(pos), -lp / side) : 0.0;
	float caustic = pow(clamp(across, 0.0, 1.0), caustic_power) * smoothstep(0.2, 0.85, length(pos)) * side * lz;
	iris_d += vec3(caustic * caustic_strength);
#endif
	vec3 d = mix(sclera_d, iris_d, iris_mask);
	DIFFUSE_LIGHT += d * ATTENUATION * LIGHT_COLOR / PI;
	if (self_specular > 0.0) {
		SPECULAR_LIGHT += hymn_char_ggx_lobe(NORMAL, VIEW, LIGHT, 0.12, vec3(HYMN_CHAR_CORNEA_F0)) * self_specular
				* ATTENUATION * LIGHT_COLOR * SPECULAR_AMOUNT;
	}
}

#endif

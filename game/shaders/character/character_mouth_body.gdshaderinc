// Hymn of the Undertow: hero mouth interior (the mouth bag, teeth and tongue) (M1-RND-21). Body shared
// by character_mouth{,_medium,_low}.gdshader. Docs: docs/kb/tech/character_shading.md ("Mouth interior").
//
// The lips shadow the open mouth from every light, so with direct light alone the interior gets only
// ambient and goes near-black in grief (M1-QA-05c fault 2). A real mouth is lit by light bounced off
// the lit lips, teeth and cheeks. The cavity bounce gives that back: per light, unshadowed, tinted
// by the lit lip colour, faded by the baked occlusion (deeper is darker) and by how far the light is
// behind the face (a rim light from behind lights no lips the camera sees). Every hero's mouth,
// teeth and tongue use this family, so the term reaches every hero.
//
// Unshadowed means unshadowed for every light type (M1-RND-24). A directional light's ATTENUATION is its
// shadow alone, so the bounce takes 1 here. A positional light's ATTENUATION is its distance and cone
// falloff times its shadow, and light() gets no distance to rebuild the falloff from, so the
// positional bounce is drawn by a second, additive pass (character_mouth_bounce.gdshader, render_mode
// shadows_disabled): there ATTENUATION is the falloff alone. CharacterShaderTiers.apply_to_tree
// attaches that pass to every mouth-family material it sees and sets cavity_bounce_pass, which moves
// the positional bounce out of this pass. Without the pass (a material no tree walk reached) the
// positional bounce falls back to ATTENUATION here, shadow included.
//
// Material contract: the same names as the StandardMaterial3D values it replaces (albedo,
// roughness, specular, AO with ao_light_affect); tex_orm R = occlusion, G = roughness (the head
// bake). LOW: no specular lobe from lights (diffuse and the bounce only).

#ifndef HYMN_CHARACTER_MOUTH_BODY_GDSHADERINC
#define HYMN_CHARACTER_MOUTH_BODY_GDSHADERINC

#include "res://game/shaders/character/character_brdf.gdshaderinc"

uniform vec4 col_albedo : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform sampler2D tex_albedo : source_color, hint_default_white, filter_linear_mipmap_anisotropic;
// R = occlusion, G = roughness (multiplied by `roughness`).
uniform sampler2D tex_orm : hint_default_white, filter_linear_mipmap_anisotropic;
uniform float roughness : hint_range(0.0, 1.0) = 1.0;
// 1 = roughness x tex_orm G (the teeth); 0 = the uniform alone (a map whose G is not this surface's).
uniform float roughness_from_orm : hint_range(0.0, 1.0) = 1.0;
// Godot's SPECULAR (F0 = 0.08 x this), as StandardMaterial3D's metallic_specular.
uniform float specular : hint_range(0.0, 1.0) = 0.5;
// How much the baked occlusion also dims direct light (0 = ambient only), as ao_light_affect.
uniform float ao_light_affect : hint_range(0.0, 1.0) = 0.0;

group_uniforms cavity;
// Colour of the light the lit lips, cheeks and teeth bounce into the mouth: a pale, desaturated lip
// tone (#C79A8C). A saturated lip red turned the teeth orange (GPU, M1-RND-21).
uniform vec4 col_cavity_bounce : source_color = vec4(0.780, 0.604, 0.549, 1.0);
// Share of each light's irradiance that comes back into the cavity as bounce. 0 = off.
uniform float cavity_bounce : hint_range(0.0, 1.0) = 0.4;
// How much the baked occlusion fades the bounce (1 = fully: the deepest bag gets none). The lips sit
// right over the opening, so the first centimetre behind them still sees them lit.
uniform float cavity_occlusion : hint_range(0.0, 1.0) = 0.5;
// True when the unshadowed bounce pass is attached (next_pass): positional lights' bounce is drawn
// there, not here (M1-RND-24). Set by CharacterShaderTiers; leave it off in authored materials.
uniform bool cavity_bounce_pass = false;
group_uniforms;

varying float v_occlusion;

void fragment() {
	vec4 orm = texture(tex_orm, UV);
	ALBEDO = col_albedo.rgb * texture(tex_albedo, UV).rgb;
	ROUGHNESS = clamp(roughness * mix(1.0, orm.g, roughness_from_orm), 0.0, 1.0);
	SPECULAR = specular;
	METALLIC = 0.0;
	AO = orm.r;
	AO_LIGHT_AFFECT = ao_light_affect;
	v_occlusion = orm.r;
}

// The cavity bounce of one light at full reach: tinted by the lit lip colour, faded by the baked
// occlusion and by how far the light is behind the face (a rim from behind lights no lips in view).
vec3 hymn_cavity_bounce(vec3 light_dir, vec3 view, vec3 light_color) {
	float facing = clamp(0.5 + 0.5 * dot(light_dir, view), 0.0, 1.0);
	return col_cavity_bounce.rgb * (cavity_bounce * mix(1.0, v_occlusion, cavity_occlusion) * facing) * light_color / PI;
}

#ifdef HYMN_MOUTH_BOUNCE_PASS
// The additive bounce pass (M1-RND-24): shadows_disabled, so a positional light's ATTENUATION is its
// distance and cone falloff alone. Directional lights' bounce stays in the base pass.
void light() {
	if (!LIGHT_IS_DIRECTIONAL) {
		DIFFUSE_LIGHT += hymn_cavity_bounce(LIGHT, VIEW, LIGHT_COLOR) * ATTENUATION;
	}
}
#else
void light() {
	float ndl = dot(NORMAL, LIGHT);
	DIFFUSE_LIGHT += max(ndl, 0.0) * ATTENUATION * LIGHT_COLOR / PI;
	// Cavity bounce, unshadowed (the lips that bounce it are lit even where the interior is not). A
	// directional light's ATTENUATION is only its shadow: reach 1. A positional light's bounce is in
	// the bounce pass when it is attached; otherwise ATTENUATION, which includes the shadow (fallback).
	float reach = LIGHT_IS_DIRECTIONAL ? 1.0 : (cavity_bounce_pass ? 0.0 : ATTENUATION);
	DIFFUSE_LIGHT += hymn_cavity_bounce(LIGHT, VIEW, LIGHT_COLOR) * reach;
#if HYMN_QUALITY >= HYMN_QUALITY_MEDIUM
	SPECULAR_LIGHT += hymn_char_ggx_lobe(NORMAL, VIEW, LIGHT, ROUGHNESS, vec3(0.08 * specular)) * ATTENUATION
			* LIGHT_COLOR * SPECULAR_AMOUNT;
#endif
}
#endif

#endif

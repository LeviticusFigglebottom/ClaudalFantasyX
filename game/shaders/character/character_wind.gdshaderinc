// Hymn of the Undertow: character cloth / hair wind sway (M1-RND-04). Vertex stage only; works in
// model space on the already-skinned VERTEX, so spring bones and sway add up.
//
// Vertex-colour weights (the shared rule: vertex colours carry weights). Same channel meanings as
// the vegetation convention (game/shaders/vegetation/vegetation_wind.gdshaderinc, M1-ENV-02):
//   COLOR.r primary sway weight   (0 = pinned at seam/waistband/collar/scalp .. 1 = free hem/cuff/tip)
//   COLOR.g secondary ripple      (0 .. 1: travelling wave along the garment)          (not on Low)
//   COLOR.b phase 0..1            (desynchronises panels, sash tails, card clumps)
//   COLOR.a flutter weight        (0 .. 1: fast, small motion along the normal; gauze)  (not on Low)
// A mesh exported without vertex colours gets Godot's default white (1, 1, 1, 1) = fully free, so
// meshes that must not sway set wind_response = 0 or paint the weights.
// Driven by the globals hymn_wind (xyz = direction * m/s, w = gust 0..1) and hymn_wind_time (s).
// Docs: docs/kb/tech/character_shading.md ("Wind").
//   #include "res://game/shaders/character/character_wind.gdshaderinc"

#ifndef HYMN_CHARACTER_WIND_GDSHADERINC
#define HYMN_CHARACTER_WIND_GDSHADERINC

#include "res://game/shaders/include/common.gdshaderinc"
#include "res://game/shaders/include/globals.gdshaderinc"

// Wind speed (m/s) at which wind_response is reached. Same reference as vegetation (Haluna trade
// wind, haluna.md §1.1) so one global wind moves plants and costumes consistently.
#define HYMN_CHAR_REFERENCE_WIND_MS 6.0
// Ratio between the two sway sines (irrational-ish so the sum never visibly repeats).
#define HYMN_CHAR_SWAY_RATIO 2.31
// Gust noise period along the clock (s); gusts arrive every few seconds.
#define HYMN_CHAR_GUST_PERIOD_S 3.7

// An including body may set its own default before the include (hair: 0, scalp cards are bound).
#ifndef HYMN_CHAR_WIND_RESPONSE_DEFAULT
#define HYMN_CHAR_WIND_RESPONSE_DEFAULT 0.6
#endif

group_uniforms wind;
// Fraction of the global wind this mesh follows. Asha's sleeve 0.6, Rhen's outer hair layer 0.25.
uniform float wind_response : hint_range(0.0, 2.0) = HYMN_CHAR_WIND_RESPONSE_DEFAULT;
uniform float sway_amplitude_m : hint_range(0.0, 0.3) = 0.05; // hem displacement at reference wind
uniform float sway_frequency_hz : hint_range(0.05, 3.0) = 0.45;
uniform float ripple_amplitude_m : hint_range(0.0, 0.1) = 0.012;
uniform float ripple_wavelength_m : hint_range(0.05, 2.0) = 0.35;
uniform float ripple_frequency_hz : hint_range(0.1, 6.0) = 1.3;
uniform float flutter_amplitude_m : hint_range(0.0, 0.02) = 0.003;
uniform float flutter_frequency_hz : hint_range(0.5, 20.0) = 7.0;
group_uniforms;

// Returns the model-space displacement for one vertex. `model_pos`/`model_normal` are VERTEX and
// NORMAL, `weights` is COLOR, `model` is MODEL_MATRIX.
vec3 hymn_char_wind_offset(vec3 model_pos, vec3 model_normal, vec4 weights, mat4 model) {
	vec3 wv = hymn_wind.xyz;
	float speed = length(wv);
	if (speed < HYMN_EPSILON || wind_response <= 0.0) {
		return vec3(0.0);
	}
	vec3 dir_w = wv / speed;
	float strength = speed / HYMN_CHAR_REFERENCE_WIND_MS * wind_response;
	float t = hymn_wind_time;
	vec3 origin = model[3].xyz;
	float phase = (weights.b + hymn_hash12(origin.xz)) * HYMN_TAU;
	// Gusts: slow 1D noise along the clock, scaled by the global gust strength.
	float g = hymn_value_noise2(vec2(t / HYMN_CHAR_GUST_PERIOD_S, phase));
	float gust = 1.0 + clamp(hymn_wind.w, 0.0, 1.0) * (g - 0.5) * 1.6;
	float k = strength * gust;
	float osc = 0.65 * sin(t * sway_frequency_hz * HYMN_TAU + phase)
			+ 0.35 * sin(t * sway_frequency_hz * HYMN_CHAR_SWAY_RATIO * HYMN_TAU + phase * 2.0);
	// Primary: lean downwind (half the amplitude) plus an oscillation around that lean.
	vec3 disp_w = dir_w * (sway_amplitude_m * (0.5 + 0.5 * osc) * weights.r * k);
	vec3 world_pos = (model * vec4(model_pos, 1.0)).xyz;
#if HYMN_QUALITY > HYMN_QUALITY_LOW
	// Secondary: a wave travelling downwind through the garment, mostly across the wind.
	float wave = sin(dot(world_pos, dir_w) / ripple_wavelength_m * HYMN_TAU - t * ripple_frequency_hz * HYMN_TAU
			+ phase);
	vec3 across = normalize(cross(dir_w, vec3(0.0, 1.0, 0.0)) + vec3(0.0, 0.3, 0.0));
	disp_w += across * (ripple_amplitude_m * wave * weights.g * k);
#endif
	mat3 to_model = inverse(mat3(model));
	vec3 disp = to_model * disp_w;
#if HYMN_QUALITY > HYMN_QUALITY_LOW
	// Flutter: fast, small, along the surface normal (model space already).
	float fl = sin(t * flutter_frequency_hz * HYMN_TAU + phase * 3.0 + dot(world_pos, vec3(9.1, 5.3, 7.7)));
	disp += model_normal * (flutter_amplitude_m * fl * weights.a * k);
#endif
	return disp;
}

#endif

// Hymn of the Undertow: nacre inlay (mother-of-pearl bands) of the Shell Shrine (M2-ENV-03, haluna.md §3.3).
// Base `bone` with a thin-film hue shift by view angle (±40° at 0.3 strength, the brief's optional
// request), and, per instance, a faint WATER shimmer while water runs over it: caustic lines that
// drift with hymn_wind_time, a wet sheen. No glimmer: the light here is sunlight through water.
// inst_shimmer is per GeometryInstance3D (0 dry .. 1 water running), so one material serves every
// channel. One variant serves every tier: a handful of value-noise taps, no loops.
shader_type spatial;
render_mode cull_back;

#include "res://game/shaders/include/common.gdshaderinc"
#include "res://game/shaders/include/globals.gdshaderinc"

// Thin-film hue rotation is around the RGB grey axis (Rodrigues; 1/sqrt(3) per channel).
#define NACRE_GREY_AXIS vec3(0.57735027)

group_uniforms nacre;
uniform vec4 col_base : source_color = vec4(0.902, 0.855, 0.753, 1.0); // bone #E6DAC0
uniform float iridescence : hint_range(0.0, 1.0) = 0.3;
uniform float hue_shift_deg : hint_range(0.0, 90.0) = 40.0;
uniform float band_scale_per_m : hint_range(0.5, 40.0) = 9.0; // growth bands across the inlay
uniform float band_contrast : hint_range(0.0, 0.5) = 0.12;
uniform float roughness_dry : hint_range(0.0, 1.0) = 0.3;
uniform float specular_value : hint_range(0.0, 1.0) = 0.6;
group_uniforms;

group_uniforms shimmer;
instance uniform float inst_shimmer : hint_range(0.0, 1.0) = 0.0;
uniform vec4 col_shimmer : source_color = vec4(0.82, 0.93, 0.92, 1.0); // sunlit water, pale aqua-white
uniform float shimmer_energy : hint_range(0.0, 2.0) = 0.35;
uniform float shimmer_scale_per_m : hint_range(0.5, 20.0) = 5.0;
uniform float shimmer_speed : hint_range(0.0, 4.0) = 0.6;
uniform float shimmer_sharpness : hint_range(1.0, 16.0) = 6.0;
uniform float roughness_wet : hint_range(0.0, 1.0) = 0.06;
uniform float wet_darken : hint_range(0.0, 1.0) = 0.8;
group_uniforms;

varying vec3 v_world_pos;

void vertex() {
	v_world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

vec3 hue_rotate(vec3 c, float angle) {
	float cs = cos(angle);
	vec3 k = NACRE_GREY_AXIS;
	return c * cs + cross(k, c) * sin(angle) + k * dot(k, c) * (1.0 - cs);
}

// Caustic lines: the ridges of two drifting value-noise fields (|n - 0.5| near 0 is a bright line).
float caustic(vec3 p, float t) {
	vec2 q = p.xz * shimmer_scale_per_m + vec2(p.y * shimmer_scale_per_m * 0.5);
	float a = hymn_value_noise2(q + vec2(t * shimmer_speed, -t * shimmer_speed * 0.7));
	float b = hymn_value_noise2(q * 1.37 + vec2(-t * shimmer_speed * 0.8, t * shimmer_speed * 0.5) + 11.3);
	float la = pow(1.0 - abs(a - 0.5) * 2.0, shimmer_sharpness);
	float lb = pow(1.0 - abs(b - 0.5) * 2.0, shimmer_sharpness);
	return la * lb * 4.0 + 0.25 * (la + lb);
}

void fragment() {
	float ndv = clamp(dot(NORMAL, VIEW), 0.0, 1.0);
	float bands = hymn_value_noise2(v_world_pos.xz * band_scale_per_m + v_world_pos.y * band_scale_per_m);
	vec3 base = col_base.rgb * (1.0 - band_contrast + band_contrast * 2.0 * bands);
	// Thin film: the hue swings with the view angle (grazing = the full shift), weighted by `iridescence`.
	float film = (1.0 - ndv) * 2.0 - 1.0 + (bands - 0.5) * 0.6;
	vec3 shifted = hue_rotate(base, radians(hue_shift_deg) * film);
	vec3 albedo = mix(base, shifted, iridescence);
	float wet = clamp(inst_shimmer, 0.0, 1.0);
	ALBEDO = albedo * mix(1.0, wet_darken, wet);
	ROUGHNESS = mix(roughness_dry, roughness_wet, wet);
	SPECULAR = specular_value;
	EMISSION = col_shimmer.rgb * caustic(v_world_pos, hymn_wind_time) * shimmer_energy * wet;
}

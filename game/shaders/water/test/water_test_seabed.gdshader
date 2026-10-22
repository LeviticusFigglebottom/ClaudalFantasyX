// Test-only (M1-RND-01 water test scene): lagoon sand. Not a production terrain shader; the
// Environment role's stone/sand kit (SPEC §8.2 item 7) replaces it. World-space, no textures.
shader_type spatial;
render_mode cull_back;

#include "res://game/shaders/include/common.gdshaderinc"

// palette.json: sand_dry #EFDDB4, sand_wet #B59D74, vegetation_shadow #1E4A3A, coral_weathered #B9AE98.
uniform vec3 col_dry : source_color = vec3(0.937, 0.867, 0.706);
uniform vec3 col_wet : source_color = vec3(0.710, 0.616, 0.455);
uniform vec3 col_grass : source_color = vec3(0.118, 0.290, 0.227);
uniform vec3 col_rubble : source_color = vec3(0.725, 0.682, 0.596);
// Lagoon floor: white coral sand (palette mortar #E6E1D6 is the nearest neutral swatch).
uniform vec3 col_lagoon_floor : source_color = vec3(0.902, 0.882, 0.839);
uniform float underwater_albedo : hint_range(0.0, 1.0) = 0.92;
uniform float water_level_m = 0.0;
uniform float capillary_band_m : hint_range(0.0, 2.0) = 0.35;
uniform float grass_depth_lo_m = 0.9;
uniform float grass_depth_hi_m = 3.5;
uniform float grass_cover : hint_range(0.0, 1.0) = 0.42;
uniform float grass_scale_per_m = 0.11;
uniform float ripple_period_m : hint_range(0.05, 2.0) = 0.6;
uniform float ripple_strength : hint_range(0.0, 1.0) = 0.25;
uniform float variation_scale_per_m = 0.35;

varying vec3 v_world;

void vertex() {
	v_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec3 p = v_world;
	float var_n = hymn_fbm2(p.xz * variation_scale_per_m, 4, 2.0, 0.5);
	float above = p.y - water_level_m;
	float wet = 1.0 - smoothstep(0.0, capillary_band_m, above);
	vec3 sand = mix(col_dry, col_wet, wet);
	if (above < 0.0) {
		sand = mix(col_wet, col_lagoon_floor * underwater_albedo, smoothstep(0.0, -0.4, above));
	}
	sand *= 0.88 + 0.24 * var_n;
	float depth = -above;
	float band = smoothstep(grass_depth_lo_m, grass_depth_lo_m + 0.5, depth)
			* (1.0 - smoothstep(grass_depth_hi_m, grass_depth_hi_m + 1.0, depth));
	float g = hymn_fbm2(p.xz * grass_scale_per_m + vec2(3.1, 7.7), 4, 2.0, 0.5);
	float grass = smoothstep(1.0 - grass_cover, 1.0 - grass_cover + 0.08, g) * band;
	float rubble = smoothstep(0.62, 0.7, hymn_fbm2(p.xz * 0.6 + vec2(11.0), 3, 2.0, 0.5))
			* smoothstep(1.5, 3.0, depth);
	vec3 alb = mix(sand, col_rubble * (0.7 + 0.3 * var_n), rubble);
	alb = mix(alb, col_grass * (0.8 + 0.4 * var_n), grass);
	// Wind-built sand ripples: a warped sine ridge field (normal only).
	vec2 warp = vec2(hymn_value_noise2(p.xz * 0.5), hymn_value_noise2(p.xz * 0.5 + 9.0));
	float ph = HYMN_TAU * (p.z + p.x * 0.3 + warp.x * 0.6) / ripple_period_m;
	// Fade ripples out before they alias (phase change per pixel approaching half a cycle).
	float alias = 1.0 - smoothstep(0.15, 0.4, fwidth(ph) / HYMN_TAU);
	float slope = cos(ph) * ripple_strength * alias * (1.0 - grass) * smoothstep(0.0, -0.2, above);
	vec3 n_world = normalize(vec3(slope * 0.3, 1.0, slope));
	ALBEDO = alb;
	ROUGHNESS = mix(0.95, 0.45, wet * step(0.0, above));
	NORMAL = normalize(mix(NORMAL, (VIEW_MATRIX * vec4(n_world, 0.0)).xyz, 0.5));
}

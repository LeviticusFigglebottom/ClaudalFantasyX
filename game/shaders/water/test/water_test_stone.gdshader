// Test-only (M1-RND-01 water test scene): drowned-ruin coral-limestone. A stand-in for the
// Environment stone/weathering shader (SPEC §8.2 item 7): world-space fBm, tide-line salt band,
// capillary wet band, algae below the waterline. No textures.
shader_type spatial;
render_mode cull_back;

#include "res://game/shaders/include/common.gdshaderinc"

// palette.json: coral_block #E8DCC4, coral_weathered #B9AE98, vegetation_shadow #1E4A3A,
// mortar #E6E1D6 (salt crust).
uniform vec3 col_fresh : source_color = vec3(0.910, 0.863, 0.769);
uniform vec3 col_weathered : source_color = vec3(0.725, 0.682, 0.596);
uniform vec3 col_algae : source_color = vec3(0.118, 0.290, 0.227);
uniform vec3 col_salt : source_color = vec3(0.902, 0.882, 0.839);
uniform float water_level_m = 0.0;
uniform float tide_high_m = 0.9;
uniform float capillary_band_m : hint_range(0.0, 2.0) = 0.25;
uniform float algae_strength : hint_range(0.0, 1.0) = 0.55;
uniform float scale_per_m = 1.3;
uniform float bump_strength : hint_range(0.0, 2.0) = 0.6;
uniform float wet_darkening : hint_range(0.0, 1.0) = 0.55;

varying vec3 v_world;
varying vec3 v_world_normal;

void vertex() {
	v_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	v_world_normal = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

// Cheap triplanar blend of 2D fBm (value + gradient via finite difference is too costly here).
float tri_fbm(vec3 p, vec3 n) {
	vec3 w = pow(abs(n), vec3(4.0));
	w /= dot(w, vec3(1.0));
	return w.x * hymn_fbm2(p.zy, 4, 2.0, 0.5) + w.y * hymn_fbm2(p.xz, 4, 2.0, 0.5)
			+ w.z * hymn_fbm2(p.xy, 4, 2.0, 0.5);
}

void fragment() {
	vec3 p = v_world * scale_per_m;
	vec3 n = normalize(v_world_normal);
	float f = tri_fbm(p, n);
	float pits = tri_fbm(p * 3.7 + 5.0, n);
	vec3 alb = mix(col_fresh, col_weathered, smoothstep(0.45, 0.8, f));
	alb *= 0.8 + 0.3 * pits;
	float h = v_world.y - water_level_m;
	// Salt crust in the splash band between mean sea level and high water.
	float salt = smoothstep(0.0, 0.15, h) * (1.0 - smoothstep(tide_high_m - 0.3, tide_high_m, h));
	alb = mix(alb, col_salt, salt * smoothstep(0.45, 0.6, pits) * 0.6);
	float wet = 1.0 - smoothstep(0.0, capillary_band_m, h);
	// Algae and darkening below the waterline.
	float algae = smoothstep(0.0, -0.3, h) * algae_strength * smoothstep(0.3, 0.6, f);
	alb = mix(alb, col_algae, algae);
	alb *= 1.0 - wet_darkening * wet;
	// Bump: finite-difference tangent-free perturbation from the pit field.
	vec3 e = vec3(0.04, 0.0, 0.0);
	float bx = tri_fbm(p * 3.7 + 5.0 + e.xyy, n) - pits;
	float by = tri_fbm(p * 3.7 + 5.0 + e.yxy, n) - pits;
	float bz = tri_fbm(p * 3.7 + 5.0 + e.yyx, n) - pits;
	vec3 g = vec3(bx, by, bz) / e.x;
	vec3 nb = normalize(n - (g - dot(g, n) * n) * bump_strength * 0.05);
	ALBEDO = alb;
	ROUGHNESS = mix(0.85, 0.25, wet);
	NORMAL = normalize((VIEW_MATRIX * vec4(nb, 0.0)).xyz);
}

// Test-scene scenery only (M1-ENV-02): a dry-to-wet sand strip for the vegetation test. Not a
// production terrain shader; the beach/terrain material belongs to M1-ENV-01 and later tasks.
shader_type spatial;

#include "res://game/shaders/include/common.gdshaderinc"

uniform vec4 col_dry : source_color = vec4(0.937, 0.867, 0.706, 1.0); // palette sand_dry #EFDDB4
uniform vec4 col_wet : source_color = vec4(0.71, 0.616, 0.455, 1.0); // palette sand_wet #B59D74
uniform vec4 col_debris : source_color = vec4(0.494, 0.416, 0.333, 1.0); // timber_weathered #7E6A55
uniform float shore_x_m = 8.0; // world X of the waterline
uniform float wet_band_m : hint_range(0.0, 20.0) = 4.5;
uniform float ripple_scale : hint_range(0.0, 8.0) = 1.6;
uniform float ripple_strength : hint_range(0.0, 2.0) = 0.35;

varying vec3 v_world_pos;

void vertex() {
	v_world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec2 p = v_world_pos.xz;
	float broad = hymn_fbm2(p * 0.08, 4, 2.0, 0.5);
	float fine = hymn_fbm2(p * 3.0, 3, 2.0, 0.5);
	float wet = smoothstep(shore_x_m - wet_band_m * (0.6 + 0.8 * broad), shore_x_m, v_world_pos.x);
	vec3 albedo = mix(col_dry.rgb, col_wet.rgb, wet);
	albedo *= 0.9 + 0.16 * broad + 0.08 * (fine - 0.5);
	float debris = smoothstep(0.78, 0.86, hymn_fbm2(p * 1.4 + vec2(5.3, 1.7), 3, 2.0, 0.5));
	albedo = mix(albedo, col_debris.rgb, debris * 0.6 * (1.0 - wet));
	ALBEDO = albedo;
	ROUGHNESS = mix(0.95, 0.35, wet);
	SPECULAR = 0.35;
	vec3 rip = hymn_value_noise2_d(vec2(p.x * ripple_scale * 0.6, p.y * ripple_scale * 0.25));
	vec3 grain = hymn_value_noise2_d(p * 14.0);
	vec2 slope = rip.yz * ripple_strength * 0.1 + grain.yz * 0.01;
	NORMAL_MAP = normalize(vec3(-slope.x, -slope.y, 1.0)) * 0.5 + 0.5;
}

// Test-scene scenery only (M1-ENV-02): a flat stand-in sea so the vegetation shots have a horizon.
// The real ocean and shallows shader is M1-RND-01; nothing outside this test scene may use this.
shader_type spatial;

#include "res://game/shaders/include/common.gdshaderinc"

uniform vec4 col_shallow : source_color = vec4(0.247, 0.816, 0.788, 1.0); // turquoise_shallow #3FD0C9
uniform vec4 col_lagoon : source_color = vec4(0.122, 0.639, 0.651, 1.0); // lagoon_teal #1FA3A6
uniform vec4 col_reef : source_color = vec4(0.082, 0.412, 0.627, 1.0); // reef_blue #1569A0
uniform float shore_x_m = 8.0;
uniform float shallow_width_m = 30.0;
uniform float lagoon_width_m = 140.0;

varying vec3 v_world_pos;

void vertex() {
	v_world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	float d = max(0.0, v_world_pos.x - shore_x_m);
	vec3 c = mix(col_shallow.rgb, col_lagoon.rgb, smoothstep(0.0, shallow_width_m, d));
	c = mix(c, col_reef.rgb, smoothstep(shallow_width_m, lagoon_width_m, d));
	float n = hymn_fbm2(v_world_pos.xz * 0.15, 3, 2.0, 0.5);
	ALBEDO = c * (0.85 + 0.2 * n);
	ROUGHNESS = 0.08;
	SPECULAR = 0.5;
	vec3 w = hymn_value_noise2_d(v_world_pos.xz * vec2(0.6, 0.35));
	NORMAL_MAP = normalize(vec3(-w.y * 0.08, -w.z * 0.08, 1.0)) * 0.5 + 0.5;
}

// Test-only shader: exercises every helper in common.gdshaderinc so the headless compile check in
// tests/unit/test_shader_prewarm.gd type-checks the whole include, and gives the shader-prewarm
// registry one real material to warm. Not used by any game scene.
shader_type spatial;
render_mode cull_disabled;

#include "res://game/shaders/include/common.gdshaderinc"

group_uniforms surface;
uniform vec3 col_tint : source_color = vec3(0.1, 0.55, 0.6);
uniform float noise_scale : hint_range(0.1, 32.0) = 4.0;
uniform int noise_octaves : hint_range(1, 8) = 5;
uniform float noise_lacunarity : hint_range(1.0, 4.0) = 2.0;
uniform float noise_gain : hint_range(0.0, 1.0) = 0.5;
group_uniforms;

varying vec3 v_world_pos;

void vertex() {
	v_world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec3 p = v_world_pos * noise_scale;
	float n2 = hymn_fbm2(p.xy, noise_octaves, noise_lacunarity, noise_gain);
	float n3 = hymn_fbm3(p, noise_octaves, noise_lacunarity, noise_gain);
	vec3 flow = hymn_curl_fbm3(p, noise_octaves, noise_lacunarity, noise_gain) + hymn_curl_noise3(p);
	vec2 flow2 = hymn_curl_noise2(p.xy);
	float h = hymn_hash12(UV) + hymn_hash33(p).x + hymn_hash_cell22(floor(p.xy)).y + hymn_hash_cell33(floor(p)).z;
	vec3 hsv = hymn_rgb_to_hsv(hymn_srgb_to_linear(col_tint));
	hsv.x = fract(hsv.x + flow.x * 0.05 + flow2.y * 0.05);
	vec3 base = hymn_hsv_to_rgb(hsv);
	vec3 lab = hymn_linear_srgb_to_oklab(base);
	lab.x *= mix(0.8, 1.2, n2 * n3);
	vec3 graded = hymn_saturate_color(hymn_oklab_to_linear_srgb(lab), 1.0 + h * 0.01);
	ALBEDO = graded;
	ROUGHNESS = mix(0.4, 0.6, clamp(hymn_luminance(hymn_linear_to_srgb(graded)), 0.0, 1.0));
}

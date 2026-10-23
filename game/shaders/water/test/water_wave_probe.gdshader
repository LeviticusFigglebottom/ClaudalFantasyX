// Test-only (M1-RND-01): evaluates the shared Gerstner include on the GPU so the parity probe
// (game/levels/_tests/water/wave_parity_probe.gd) can read the results back and compare them
// with GerstnerWaves (GDScript). One pixel = one rest point on a grid.
shader_type canvas_item;
render_mode blend_disabled, unshaded;

#include "res://game/shaders/water/water_waves.gdshaderinc"

uniform vec2 origin_m = vec2(0.0);
uniform float spacing_m = 1.0;
uniform float time_s = 0.0;
// 0: rgb = displacement (m). 1: rgb = normal, a = Jacobian.
uniform int channel = 0;

void fragment() {
	vec2 p0 = origin_m + floor(FRAGCOORD.xy) * spacing_m;
	vec3 disp;
	vec3 n;
	float jac;
	hymn_water_gerstner(p0, time_s, 0.0, 0.0, disp, n, jac);
	COLOR = channel == 0 ? vec4(disp, 1.0) : vec4(n, jac);
}

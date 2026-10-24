// Hymn of the Undertow: the Reefball water sphere, MULTIPLY pass (M3-RND-01). Body: water_sphere.gdshaderinc.
// A full-screen quad (WaterSphereRig) drawn after everything else: the frame times the water's transmittance along
// each ray's path through the ball, and the meniscus line where a camera's lens meets the wall.
shader_type spatial;
render_mode blend_mul, unshaded, cull_disabled, depth_test_disabled, depth_draw_never, fog_disabled, shadows_disabled;

#include "res://game/shaders/water/sphere/water_sphere.gdshaderinc"

uniform sampler2D depth_tex : hint_depth_texture, filter_nearest, repeat_disable;

void vertex() {
	// The quad's corners (+-0.5) to the whole clip-space screen.
	POSITION = vec4(VERTEX.xy * 2.0, 0.5, 1.0);
}

void fragment() {
	vec3 rd;
	float path_m;
	float depth_m;
	float meniscus;
	bool wet = sphere_ray(
			SCREEN_UV, depth_tex, INV_PROJECTION_MATRIX, INV_VIEW_MATRIX, CAMERA_POSITION_WORLD, rd, path_m, depth_m, meniscus);
	vec3 tr = wet ? sphere_transmittance(path_m) : vec3(1.0);
	ALBEDO = tr * (1.0 - 0.45 * meniscus);
}

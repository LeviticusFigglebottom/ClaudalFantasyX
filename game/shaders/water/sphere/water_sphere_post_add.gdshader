// Hymn of the Undertow: the Reefball water sphere, ADD pass (M3-RND-01). Body: water_sphere.gdshaderinc.
// A full-screen quad (WaterSphereRig) drawn after the multiply pass: the light the water scatters toward the camera.
shader_type spatial;
render_mode blend_add, unshaded, cull_disabled, depth_test_disabled, depth_draw_never, fog_disabled, shadows_disabled;

#include "res://game/shaders/water/sphere/water_sphere.gdshaderinc"

uniform sampler2D depth_tex : hint_depth_texture, filter_nearest, repeat_disable;

void vertex() {
	POSITION = vec4(VERTEX.xy * 2.0, 0.5, 1.0);
}

void fragment() {
	vec3 rd;
	float path_m;
	float depth_m;
	float meniscus;
	bool wet = sphere_ray(
			SCREEN_UV, depth_tex, INV_PROJECTION_MATRIX, INV_VIEW_MATRIX, CAMERA_POSITION_WORLD, rd, path_m, depth_m, meniscus);
	ALBEDO = wet ? sphere_inscatter(sphere_transmittance(path_m), rd, depth_m) : vec3(0.0);
}

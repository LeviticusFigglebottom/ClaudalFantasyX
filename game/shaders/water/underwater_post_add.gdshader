// Hymn of the Undertow: the underwater post, ADD pass (M2-RND-02). Body: underwater_post.gdshaderinc.
// A full-screen quad (UnderwaterRig) drawn after everything else.
shader_type spatial;
render_mode blend_add, unshaded, cull_disabled, depth_test_disabled, depth_draw_never, fog_disabled, shadows_disabled;

#define UNDERWATER_PASS_ADD
#include "res://game/shaders/water/underwater_post.gdshaderinc"

void vertex() {
	// The quad's corners (+-0.5) to the whole clip-space screen.
	POSITION = vec4(VERTEX.xy * 2.0, 0.5, 1.0);
}

void fragment() {
	float path_m;
	vec3 rd;
	float depth_m;
	float meniscus;
	bool under = underwater_ray(
			SCREEN_UV, INV_PROJECTION_MATRIX, INV_VIEW_MATRIX, CAMERA_POSITION_WORLD, path_m, rd, depth_m, meniscus);
	vec3 tr = under ? underwater_transmittance(path_m) : vec3(1.0);
	ALBEDO = under ? underwater_inscatter(tr, rd, depth_m) : vec3(0.0);
}

// Hymn of the Undertow: the underwater post, MUL pass (M2-RND-02). Body: underwater_post.gdshaderinc.
// A full-screen quad (UnderwaterRig) drawn after everything else.
shader_type spatial;
render_mode blend_mul, unshaded, cull_disabled, depth_test_disabled, depth_draw_never, fog_disabled, shadows_disabled;

#define UNDERWATER_PASS_MUL
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
	float cover;
	bool under = underwater_ray(
			SCREEN_UV, INV_PROJECTION_MATRIX, INV_VIEW_MATRIX, CAMERA_POSITION_WORLD, path_m, rd, depth_m, meniscus, cover);
	vec3 tr = under ? mix(vec3(1.0), underwater_transmittance(path_m), cover) : vec3(1.0);
	// The meniscus: a thin dark line where the lens crosses the surface.
	ALBEDO = tr * (1.0 - 0.45 * meniscus);
}

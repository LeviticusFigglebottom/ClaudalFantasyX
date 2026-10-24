// Hymn of the Undertow: the Undertow's raymarched body (M1-RND-03). Medium, High and Ultra tiers;
// Low draws undertow_shell.gdshader instead. Docs: docs/kb/tech/undertow.md.
//
// Drawn on a proxy cylinder that bounds the storm, BACK faces only (cull_front), so it works with the
// camera outside or inside the storm. The ray is clipped analytically to the bounding cylinder and
// the slab [sea level, top], and against the OPAQUE depth buffer by hand (depth_test_disabled): the
// ocean is a transparent material and is not in that buffer, so the sea-level slab stands in for it.
// Sort it after the water (render_priority, undertow.json "render_priority").
//
// A variant defines before including this file:
//   UNDERTOW_MAX_STEPS      compile-time cap on march_steps
//   UNDERTOW_LIGHT_SAMPLES  sun-ward optical-depth samples per step
//   UNDERTOW_LIGHT_NOISE    1 = those samples include noise, 0 = envelope only
//   UNDERTOW_CURL           1 = curl-noise domain warp (turbulence), 0 = none
//   UNDERTOW_OCTAVES        fBm octaves of the cloud noise
//   UNDERTOW_BILLOW_SHADE   1 = sun-ward derivative shading of the surface billows, 0 = none

render_mode blend_premul_alpha, unshaded, cull_front, depth_draw_never, depth_test_disabled, fog_disabled,
		shadows_disabled;

#include "res://game/shaders/include/globals.gdshaderinc"

// Baked noise lattice (M1-RND-10): texel (x, y, z) = hymn_pcg3d(x, y, z) in RGB plus a fourth hash in
// A, tileable (assets_src/vfx/undertow/bake_noise3d.py). UndertowStorm binds it from undertow.json
// "noise". One trilinear fetch at a quintic-remapped coordinate is hymn_value_noise3's quintic
// interpolation of the same lattice, at the cost of a texture fetch instead of eight PCG3D hashes.
// The cloud fields use it; the wounds keep hashing (undertow_common.gdshaderinc), so the rents stay
// exactly where they were: their fields span only a few lattice cells, where wrapping shows.
uniform highp sampler3D noise_tex : filter_linear, repeat_enable;
#include "res://game/shaders/undertow/undertow_body_uniforms.gdshaderinc"

uniform sampler2D depth_tex : hint_depth_texture, filter_nearest, repeat_disable;

#include "res://game/shaders/undertow/undertow_body_march.gdshaderinc"

void fragment() {
	vec3 world = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec3 ro = undertow_local(CAMERA_POSITION_WORLD);
	vec3 rd = normalize(world - CAMERA_POSITION_WORLD);
	float depth = texture(depth_tex, SCREEN_UV).r;
	float t_opaque = UNDERTOW_FAR_M;
	if (depth > UNDERTOW_SKY_DEPTH) {
		vec4 v = INV_PROJECTION_MATRIX * vec4(SCREEN_UV * 2.0 - 1.0, depth, 1.0);
		t_opaque = length(v.xyz / v.w);
	}
	float t_mean;
	vec4 body = undertow_march(ro, rd, t_opaque, FRAGCOORD.xy, t_mean);
	if (body.a < 0.0) {
		discard;
	}
	ALBEDO = body.rgb;
	ALPHA = body.a;
}

// Hymn of the Undertow: the underwater post (M2-RND-02). Docs: docs/kb/tech/underwater.md.
// Two full-screen passes share this include. UNDERWATER_PASS_MUL multiplies the frame by the water's
// per-channel transmittance; UNDERWATER_PASS_ADD adds the in-scattered light. Neither reads the screen
// texture, so everything drawn before them (the surface's underside, motes, glass) is absorbed too.
//
// Per pixel: the view ray starts underwater when its lens point (lens_m along it) is below the wavy surface (the
// same Gerstner sum as the water, water_waves.gdshaderinc). So a half-submerged camera gets a clean
// waterline across the lens, with a thin meniscus band, and crossing the surface never pops. A ray
// starting above water is left alone: the water surface draws the above-water look itself.

#include "res://game/shaders/include/globals.gdshaderinc"
#include "res://game/shaders/water/water_waves.gdshaderinc"

// Reverse-Z: a depth of 0 is the sky (no opaque surface).
#define UNDERWATER_SKY_DEPTH 1e-7
#define UNDERWATER_EPSILON 1e-4

uniform sampler2D depth_tex : hint_depth_texture, filter_nearest, repeat_disable;
// Water rest plane (world Y) and the water's time base (hymn_wind_time * time_scale), from UnderwaterRig.
uniform float water_rest_y = 0.0;
uniform float water_time_scale = 1.0;
// false (Low): a flat surface at water_rest_y (no wave sum per pixel).
uniform bool use_waves = true;
// -ln(transmit colour) / transmit distance, per channel (per metre).
uniform vec3 sigma = vec3(0.28, 0.11, 0.1);
uniform vec3 col_scatter : source_color = vec3(0.05, 0.63, 0.58);
uniform vec3 col_deep : source_color = vec3(0.002, 0.01, 0.024);
uniform float scatter_strength = 0.85;
uniform float depth_falloff_m = 22.0;
uniform float down_darkening = 0.6;
uniform float meniscus_m = 0.03;
// The waterline is tested this far along each ray, not at the near plane (a few cm tall): a camera within
// about lens_m x tan(fov / 2) of the surface shows the split, and it sweeps smoothly as the camera crosses.
uniform float lens_m = 0.25;
uniform float max_distance_m = 400.0;
// How much the in-scatter's light level follows the camera's own depth (the rest: the path's middle).
// Scattered light mostly comes from near the camera; the middle of a long ray to the deep reef is dark.
uniform float camera_light_weight = 0.7;
// The scene's daylight over a noon sun (UnderwaterRig): a night dive's water is dark.
uniform float light_level = 1.0;

float underwater_surface_y(vec2 xz) {
	if (!use_waves) {
		return water_rest_y;
	}
	vec3 disp;
	vec3 n;
	float jac;
	hymn_water_gerstner(xz, hymn_wind_time * water_time_scale, 0.0, 0.0, disp, n, jac);
	return water_rest_y + disp.y;
}

// Fills in the ray through this pixel: whether it starts underwater, the length of water it crosses,
// its world direction, and how far below the surface it travels on average (for the light level).
// Returns false when the ray starts above water.
bool underwater_ray(
		vec2 screen_uv, mat4 inv_proj, mat4 inv_view, vec3 cam, out float path_m, out vec3 rd, out float depth_m,
		out float meniscus) {
	vec2 ndc = screen_uv * 2.0 - 1.0;
	vec4 near_v = inv_proj * vec4(ndc, 1.0, 1.0);
	rd = normalize((inv_view * vec4(near_v.xyz / near_v.w, 1.0)).xyz - cam);
	vec3 near_w = cam + rd * lens_m;
	float surf = underwater_surface_y(near_w.xz);
	meniscus = 1.0 - smoothstep(0.0, meniscus_m, abs(near_w.y - surf));
	if (near_w.y > surf) {
		path_m = 0.0;
		depth_m = 0.0;
		return false;
	}
	float depth = texture(depth_tex, screen_uv).r;
	float t_scene = max_distance_m;
	if (depth > UNDERWATER_SKY_DEPTH) {
		vec4 v = inv_proj * vec4(ndc, depth, 1.0);
		t_scene = min(length(v.xyz / v.w), max_distance_m);
	}
	// Where a rising ray leaves the water: the rest plane, then one refinement on the waves.
	float t_exit = max_distance_m;
	if (rd.y > UNDERWATER_EPSILON) {
		t_exit = (water_rest_y - near_w.y) / rd.y;
		vec3 p = near_w + rd * t_exit;
		t_exit = max((underwater_surface_y(p.xz) - near_w.y) / rd.y, 0.0);
	}
	path_m = min(t_scene, t_exit);
	vec3 mid = near_w + rd * (0.5 * path_m);
	depth_m = mix(max(water_rest_y - mid.y, 0.0), max(water_rest_y - cam.y, 0.0), camera_light_weight);
	return true;
}

// Per-channel transmittance over `path_m` of water.
vec3 underwater_transmittance(float path_m) {
	return exp(-sigma * path_m);
}

// Light scattered toward the camera along the ray: the scatter colour near the surface, darkening with
// depth and when looking down, times (1 - transmittance).
vec3 underwater_inscatter(vec3 transmittance, vec3 rd, float depth_m) {
	float light = exp(-depth_m / depth_falloff_m);
	vec3 tint = mix(col_scatter, col_deep, clamp(-rd.y * down_darkening, 0.0, 1.0) * 0.6 + (1.0 - light) * 0.4);
	return tint * scatter_strength * light * light_level * (vec3(1.0) - transmittance);
}

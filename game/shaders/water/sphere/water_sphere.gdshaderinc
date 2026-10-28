// Hymn of the Undertow: the Reefball water sphere (M3-RND-01). Docs: docs/kb/tech/water_sphere.md.
// Shared by the sphere's two full-screen passes (water_sphere_post_mul / _add) and its surface. A ball of water of
// sphere_radius_m at sphere_center, held in the air (SPEC §6.10); flattened by sphere_flatten (the vertical
// semi-axis over the radius) it is the Tamsule Bell's held drop (M3-RND-26, a 14.0 x 11.5 m spheroid). Every view ray's water is the part of it inside the
// ball, from max(entry, the lens point) to min(exit, the opaque scene): one rule for a camera outside the ball (the
// ball absorbs what's behind and inside it), inside it (the underwater look to the wall) and crossing its wall.

#include "res://game/shaders/include/globals.gdshaderinc"

// Reverse-Z: a depth of 0 is the sky (no opaque surface).
#define SPHERE_SKY_DEPTH 1e-7
#define SPHERE_FAR_M 1e6

uniform vec3 sphere_center = vec3(0.0, 20.0, 0.0);
uniform float sphere_radius_m = 16.0;
// The vertical semi-axis over the horizontal radius (1: a ball).
uniform float sphere_flatten = 1.0;
// -ln(transmit colour) / transmit distance, per channel (per metre).
uniform vec3 sigma = vec3(0.107, 0.025, 0.024);
uniform vec3 col_scatter : source_color = vec3(0.013, 0.366, 0.381);
uniform vec3 col_deep : source_color = vec3(0.004, 0.068, 0.091);
uniform float scatter_strength = 0.45;
// In-scatter darkens with depth below the ball's top over this distance.
uniform float depth_falloff_m = 30.0;
uniform float down_darkening = 0.5;
// The lens point: the wall is tested this far along each ray, so a camera at the wall gets a clean split.
uniform float lens_m = 0.25;
uniform float meniscus_px = 1.5;
// The scene's daylight over a noon sun (WaterSphereRig): a night match's water is dark.
uniform float light_level = 1.0;

vec3 sphere_axes() {
	return vec3(sphere_radius_m, sphere_radius_m * sphere_flatten, sphere_radius_m);
}

// The ray's entry and exit distances through the ball (t0 > t1: a miss), solved in the space where it's a unit ball
// (the distances along rd stay world metres).
vec2 sphere_hit(vec3 ro, vec3 rd) {
	vec3 inv = 1.0 / sphere_axes();
	vec3 oc = (ro - sphere_center) * inv;
	vec3 d = rd * inv;
	float a = dot(d, d);
	float b = dot(oc, d);
	float c = dot(oc, oc) - 1.0;
	float h = b * b - a * c;
	if (h < 0.0) {
		return vec2(SPHERE_FAR_M, -SPHERE_FAR_M);
	}
	h = sqrt(h);
	return vec2((-b - h) / a, (-b + h) / a);
}

// Metres inside the wall (< 0 outside): exact for a ball, scaled by the shorter axis for a flattened drop.
float sphere_inside_m(vec3 p) {
	return (1.0 - length((p - sphere_center) / sphere_axes())) * sphere_radius_m * min(sphere_flatten, 1.0);
}

// The wall's outward normal at (or near) p.
vec3 sphere_normal(vec3 p) {
	vec3 ax = sphere_axes();
	return normalize((p - sphere_center) / (ax * ax));
}

float sphere_top_y() {
	return sphere_center.y + sphere_radius_m * sphere_flatten;
}

// The view ray through this pixel: its world direction, the metres of water it crosses, the mean depth of that
// water below the ball's top (for the light level), and the meniscus line where the lens meets the wall.
// Returns false when the ray crosses no water.
bool sphere_ray(
		vec2 screen_uv, sampler2D depth_tex, mat4 inv_proj, mat4 inv_view, vec3 cam, out vec3 rd, out float path_m,
		out float depth_m, out float meniscus) {
	vec2 ndc = screen_uv * 2.0 - 1.0;
	vec4 near_v = inv_proj * vec4(ndc, 1.0, 1.0);
	rd = normalize((inv_view * vec4(near_v.xyz / near_v.w, 1.0)).xyz - cam);
	// Pixels from the lens point to the wall (signed: > 0 inside), for the meniscus line (before any branch).
	float inside_m = sphere_inside_m(cam + rd * lens_m);
	float px = inside_m / max(fwidth(inside_m), 1e-8);
	meniscus = 1.0 - smoothstep(0.0, meniscus_px, abs(px));
	vec2 t = sphere_hit(cam, rd);
	float depth = texture(depth_tex, screen_uv).r;
	float t_scene = SPHERE_FAR_M;
	if (depth > SPHERE_SKY_DEPTH) {
		vec4 v = inv_proj * vec4(ndc, depth, 1.0);
		t_scene = length(v.xyz / v.w);
	}
	float t_in = max(t.x, lens_m);
	float t_out = min(t.y, t_scene);
	path_m = max(t_out - t_in, 0.0);
	vec3 mid = cam + rd * (0.5 * (t_in + t_out));
	depth_m = max(sphere_top_y() - mid.y, 0.0);
	return path_m > 0.0;
}

vec3 sphere_transmittance(float path_m) {
	return exp(-sigma * path_m);
}

// Light scattered toward the camera along the water: the scatter colour near the top, darkening toward the deep
// colour with depth and when looking down, times (1 - transmittance).
vec3 sphere_inscatter(vec3 transmittance, vec3 rd, float depth_m) {
	float light = exp(-depth_m / depth_falloff_m);
	vec3 tint = mix(col_scatter, col_deep, clamp(-rd.y * down_darkening, 0.0, 1.0) * 0.6 + (1.0 - light) * 0.4);
	return tint * scatter_strength * light * light_level * (vec3(1.0) - transmittance);
}

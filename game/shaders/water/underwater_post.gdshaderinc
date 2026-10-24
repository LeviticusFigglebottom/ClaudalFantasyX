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
// The meniscus: a dark line this many pixels each side of the waterline (screen space, so it stays one thin
// continuous line at any distance; M2-RND-09 item 6).
uniform float meniscus_px = 1.5;
// The waterline is tested this far along each ray, not at the near plane (a few cm tall): a camera within
// about lens_m x tan(fov / 2) of the surface shows the split, and it sweeps smoothly as the camera crosses.
uniform float lens_m = 0.25;
uniform float max_distance_m = 400.0;
// How much the in-scatter's light level follows the camera's own depth (the rest: the path's middle).
// Scattered light mostly comes from near the camera; the middle of a long ray to the deep reef is dark.
uniform float camera_light_weight = 0.7;
// The scene's daylight over a noon sun (UnderwaterRig): a night dive's water is dark.
uniform float light_level = 1.0;
// Night sea-glow in the water column (colour script rule 3, M2-RND-09): emission at the zone's sea-glow
// energy, independent of the light level, so a night dive is dark but teal, not black.
uniform vec3 col_sea_glow : source_color = vec3(0.012, 0.147, 0.184);
uniform float sea_glow_energy = 0.0;
// Rhen's lantern halo (M2-RND-09 item 4): single scattering of the lamp's light along the ray, absorbed
// from the lamp to each point and from that point to the camera, marched over the part of the ray within
// the lamp's range. Volumetric fog can't do this: the post absorbs fog light over the whole path to the
// background, which strips the lamp's red and turns the halo green. lamp_color is linear x energy (0 = none).
uniform vec3 lamp_pos = vec3(0.0);
uniform vec3 lamp_color = vec3(0.0);
uniform float lamp_range_m = 9.0;
uniform float lamp_attenuation = 1.4;
uniform float lamp_core_m = 0.6;
uniform float lamp_scatter = 0.05;
uniform int lamp_steps = 16;
// The halo's absorption over the water's (Art, M2-ART-02: the oil lamp is the game's last warm light and
// must read warm; physics yields to that, so the halo loses less red than the scene behind it).
uniform float lamp_absorption = 1.0;

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
// `cover` is how much of the pixel starts underwater (antialiased across the waterline, from the lens
// point's height over the surface in pixels), and `meniscus` the thin line along it.
// Returns false when the ray starts above water.
bool underwater_ray(
		vec2 screen_uv, mat4 inv_proj, mat4 inv_view, vec3 cam, out float path_m, out vec3 rd, out float depth_m,
		out float meniscus, out float cover) {
	vec2 ndc = screen_uv * 2.0 - 1.0;
	vec4 near_v = inv_proj * vec4(ndc, 1.0, 1.0);
	rd = normalize((inv_view * vec4(near_v.xyz / near_v.w, 1.0)).xyz - cam);
	vec3 near_w = cam + rd * lens_m;
	float below = underwater_surface_y(near_w.xz) - near_w.y;
	// Pixels below the waterline (derivatives before any branch).
	float px = below / max(fwidth(below), UNDERWATER_EPSILON * UNDERWATER_EPSILON);
	cover = clamp(px + 0.5, 0.0, 1.0);
	meniscus = 1.0 - smoothstep(0.0, meniscus_px, abs(px));
	if (cover <= 0.0) {
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

// The lantern's in-scattered light along the ray from `origin` (direction rd) over path_m of water.
vec3 underwater_lamp_halo(vec3 origin, vec3 rd, float path_m) {
	if (dot(lamp_color, lamp_color) <= 0.0 || lamp_steps <= 0) {
		return vec3(0.0);
	}
	// The ray's segment inside the lamp's range sphere.
	vec3 oc = origin - lamp_pos;
	float b = dot(oc, rd);
	float c = dot(oc, oc) - lamp_range_m * lamp_range_m;
	float h = b * b - c;
	if (h <= 0.0) {
		return vec3(0.0);
	}
	h = sqrt(h);
	float t0 = max(-b - h, 0.0);
	float t1 = min(-b + h, path_m);
	if (t1 <= t0) {
		return vec3(0.0);
	}
	float dt = (t1 - t0) / float(lamp_steps);
	vec3 sum = vec3(0.0);
	for (int i = 0; i < lamp_steps; i++) {
		float t = t0 + (float(i) + 0.5) * dt;
		float d = length(origin + rd * t - lamp_pos);
		float fall = pow(max(1.0 - d / lamp_range_m, 0.0), lamp_attenuation) / (1.0 + (d * d) / (lamp_core_m * lamp_core_m));
		sum += fall * exp(-sigma * lamp_absorption * (t + d));
	}
	return lamp_color * lamp_scatter * sum * dt;
}

// Light scattered toward the camera along the ray: the scatter colour near the surface, darkening with
// depth and when looking down, times (1 - transmittance).
vec3 underwater_inscatter(vec3 transmittance, vec3 rd, float depth_m) {
	float light = exp(-depth_m / depth_falloff_m);
	vec3 tint = mix(col_scatter, col_deep, clamp(-rd.y * down_darkening, 0.0, 1.0) * 0.6 + (1.0 - light) * 0.4);
	vec3 glow = col_sea_glow * sea_glow_energy;
	return (tint * scatter_strength * light * light_level + glow) * (vec3(1.0) - transmittance);
}

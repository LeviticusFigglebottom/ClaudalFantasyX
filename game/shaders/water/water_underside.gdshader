// Hymn of the Undertow: the water surface seen from below (M2-RND-02). Docs: docs/kb/tech/underwater.md.
// Drawn by UnderwaterRig on a copy of the water's surface mesh, BACK faces only: invisible from above,
// it is the underside from below. The vertex stage is the water's own (water_surface_body.gdshaderinc,
// world_vertex_coords, the same Gerstner sum and LOD fade), so the two surfaces never part.
// Optics: a ray leaves the water only within the critical angle (asin(1/ior), 48.6 deg from straight up):
// - inside that Snell window the surface is mostly clear, with a sky tint, so the world above shows
//   through;
// - outside it, total internal reflection: the underside mirrors the water's own deep colour.
// The underwater post then absorbs it along the path, as everything else. Fog stays on: the god rays'
// volumetric fog in front of the surface must cover it.
shader_type spatial;
render_mode blend_mix, unshaded, cull_front, depth_draw_never, world_vertex_coords, shadows_disabled;

#include "res://game/shaders/include/globals.gdshaderinc"
#include "res://game/shaders/water/water_waves.gdshaderinc"

uniform float water_time_scale = 1.0;
uniform float lod_fade_wavelengths = 60.0;
uniform vec3 col_window : source_color = vec3(0.027, 0.212, 0.672);
uniform vec3 col_tir : source_color = vec3(0.004, 0.068, 0.091);
uniform float ior = 1.333;
uniform float window_soft_deg = 5.0;
uniform float window_alpha = 0.35;
uniform float tir_alpha = 0.9;
// The refracted sun inside the window: a disc and a halo (straight up the sun sits at asin(sin(z) / ior)).
uniform float sun_disc = 6.0;
uniform float sun_halo = 0.8;
// The scene's daylight over a noon sun (UnderwaterRig): the window and the reflection darken at night.
uniform float light_level = 1.0;
// The reflection's gain over col_tir (M2-RND-09: deep_teal_shadow, kept at about its old on-screen value),
// and the night sea-glow it reflects (the water column's own emission, independent of the light level).
uniform float tir_gain = 1.0;
// The underwater post's lens distance (M2-RND-09 item 6): a ray that meets the surface nearer than its lens
// point is one the post treats as above water, so the underside must not draw there either. Otherwise a
// camera just under a crest saw TIR across the whole upper frame instead of the air.
uniform float lens_m = 0.25;
uniform vec3 col_sea_glow : source_color = vec3(0.012, 0.147, 0.184);
uniform float sea_glow_energy = 0.0;

varying vec3 v_normal_w;

void vertex() {
	vec3 rest = VERTEX;
	float dist = length(rest.xz - CAMERA_POSITION_WORLD.xz);
	vec3 disp;
	vec3 n;
	float jac;
	hymn_water_gerstner(rest.xz, hymn_wind_time * water_time_scale, dist, lod_fade_wavelengths, disp, n, jac);
	VERTEX = rest + disp;
	v_normal_w = n;
}

void fragment() {
	vec3 world = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	if (length(world - CAMERA_POSITION_WORLD) < lens_m) {
		discard;
	}
	vec3 rd = normalize(world - CAMERA_POSITION_WORLD);
	float cos_t = dot(rd, normalize(v_normal_w));
	float crit = asin(1.0 / ior);
	float soft = radians(window_soft_deg);
	// 1 inside the Snell window, 0 in total internal reflection, soft at the rim.
	float inside = smoothstep(cos(crit + soft), cos(max(crit - soft, 0.0)), cos_t);
	// Where the sun is seen from below: sunlight refracted down through this point, reversed.
	vec3 n = normalize(v_normal_w);
	vec3 down = refract(-normalize(hymn_sun_direction), n, 1.0 / ior);
	float to_sun = max(dot(rd, -down), 0.0);
	float sun = (sun_disc * pow(to_sun, 900.0) + sun_halo * pow(to_sun, 24.0)) * inside;
	ALBEDO = (mix(col_tir * tir_gain, col_window, inside) + vec3(sun)) * light_level + col_sea_glow * sea_glow_energy * (1.0 - inside);
	ALPHA = clamp(mix(tir_alpha, window_alpha, inside) + sun, 0.0, 1.0);
}

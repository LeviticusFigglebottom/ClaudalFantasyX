// Hymn of the Undertow: the Reefball water sphere, ADD pass (M3-RND-01). Body: water_sphere.gdshaderinc.
// A full-screen quad (WaterSphereRig) drawn after the multiply pass: the light the water scatters toward the camera,
// and at night the water column's sea-glow (M3-RND-05, colour script rule 3: glimmer.gdshaderinc's, with its slow
// noise, at the zone's energy or the rig's own, times sea_glow_strength as the underwater look's).
shader_type spatial;
render_mode blend_add, unshaded, cull_disabled, depth_test_disabled, depth_draw_never, fog_disabled, shadows_disabled;

#include "res://game/shaders/water/sphere/water_sphere.gdshaderinc"
#include "res://game/shaders/include/glimmer.gdshaderinc"
#include "res://game/shaders/water/sphere/water_sphere_caustics.gdshaderinc"

uniform sampler2D depth_tex : hint_depth_texture, filter_nearest, repeat_disable;
// The rig's own sea-glow energy (0: the zone's hymn_zone_sea_glow), and the water column's gain over it.
uniform float sea_glow_energy = 0.0;
uniform float sea_glow_strength = 1.8;
// The bound light the water holds (M3-RND-26, the Tamsule Bell's drop: glimmer_bound, steady, colour script rule 2):
// colour x energy, times (1 - transmittance), independent of the light level. 0: none.
uniform vec3 bound_glow_color : source_color = vec3(0.0);
uniform float bound_glow_energy = 0.0;

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
	vec3 under = sphere_under_light(SCREEN_UV, texture(depth_tex, SCREEN_UV).r, INV_PROJECTION_MATRIX, INV_VIEW_MATRIX);
	if (!wet) {
		ALBEDO = under;
	} else {
		vec3 tr = sphere_transmittance(path_m);
		// The glow's noise patches drift over the ball's middle along the ray (the scene depth doesn't move them).
		vec2 t = sphere_hit(CAMERA_POSITION_WORLD, rd);
		vec3 mid = CAMERA_POSITION_WORLD + rd * (0.5 * (max(t.x, 0.0) + t.y));
		float energy = hymn_sea_glow_energy(hymn_sea_glow_zone(sea_glow_energy)) * sea_glow_strength;
		// The column builds up along the ray's water (glimmer.gdshaderinc: up to twice the surface glow).
		vec3 glow = hymn_sea_glow(mid, hymn_wind_time, energy, path_m);
		vec3 bound = bound_glow_color * bound_glow_energy;
		ALBEDO = sphere_inscatter(tr, rd, depth_m) + (glow + bound) * (vec3(1.0) - tr) + under * tr;
	}
}

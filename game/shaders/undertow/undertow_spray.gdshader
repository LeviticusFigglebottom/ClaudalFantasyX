// Hymn of the Undertow: spray skirt where the sea is torn up into the wall (M1-RND-03), every tier.
// Docs: docs/kb/tech/undertow.md. Drawn on a unit open cylinder (radius 1, height 1, centred) that
// the vertex shader maps to a curtain of radius spray_radius_m and height spray_height_m around the
// eye, in storm-local model space (the MeshInstance3D sits at storm_center).
shader_type spatial;
render_mode blend_mix, unshaded, cull_disabled, depth_draw_never, fog_disabled, shadows_disabled;

#include "res://game/shaders/include/globals.gdshaderinc"
#include "res://game/shaders/undertow/undertow_common.gdshaderinc"

#define UNDERTOW_SPRAY_OFFSET vec3(23.9, -3.3, 61.7)
// Unit cylinder: VERTEX.y runs from -0.5 to 0.5.
#define UNDERTOW_UNIT_HALF 0.5

group_uniforms spray;
uniform float spray_radius_m : hint_range(10.0, 40000.0) = 4300.0;
uniform float spray_height_m : hint_range(1.0, 5000.0) = 650.0;
uniform float spray_scale_m : hint_range(1.0, 5000.0) = 300.0;
uniform float spray_rise_m_s : hint_range(0.0, 100.0) = 14.0;
uniform float spray_density : hint_range(0.0, 1.0) = 0.6;
uniform vec3 col_spray : source_color = vec3(0.855, 0.922, 0.905);
uniform vec3 col_sun : source_color = vec3(0.888, 0.381, 0.069);
uniform float sun_energy : hint_range(0.0, 16.0) = 1.0;
uniform vec3 col_ambient_top : source_color = vec3(0.159, 0.209, 0.271);
uniform float ambient_energy : hint_range(0.0, 8.0) = 1.0;
uniform vec3 col_haze : source_color = vec3(0.35, 0.3, 0.32);
uniform float haze_visibility_m : hint_range(100.0, 200000.0) = 26000.0;
group_uniforms;

varying vec3 v_local;
varying float v_h;

void vertex() {
	float h = VERTEX.y + UNDERTOW_UNIT_HALF;
	vec2 dir = normalize(VERTEX.xz);
	VERTEX = vec3(dir.x * spray_radius_m, h * spray_height_m * storm_intensity, dir.y * spray_radius_m);
	NORMAL = vec3(dir.x, 0.0, dir.y);
	v_local = VERTEX;
	v_h = h;
}

void fragment() {
	vec3 p = v_local;
	float ta;
	float tb;
	float wa;
	undertow_phases(ta, tb, wa);
	vec3 pa = undertow_flow_point(p, ta) + vec3(0.0, (updraft_m_s - spray_rise_m_s) * ta, 0.0);
	vec3 pb = undertow_flow_point(p, tb) + vec3(0.0, (updraft_m_s - spray_rise_m_s) * tb, 0.0);
	float na = hymn_fbm3(pa / spray_scale_m + UNDERTOW_SPRAY_OFFSET, 3, 2.0, 0.5);
	float nb = hymn_fbm3(pb / spray_scale_m + UNDERTOW_SPRAY_OFFSET, 3, 2.0, 0.5);
	float n = mix(nb, na, wa);
	float fade = (1.0 - v_h) * (1.0 - v_h) * smoothstep(0.0, 0.04, v_h);
	float a = smoothstep(0.35, 0.75, n) * fade * spray_density * storm_intensity;
	vec3 L = normalize(hymn_sun_direction + vec3(0.0, HYMN_EPSILON, 0.0));
	vec3 lit = col_spray * (col_sun * sun_energy * (0.25 + 0.5 * max(L.y, 0.0)) + col_ambient_top * ambient_energy);
	lit += undertow_lightning(p) * 0.6;
	float dist = length(p + storm_center - CAMERA_POSITION_WORLD);
	float haze = 1.0 - exp(-dist / haze_visibility_m);
	ALBEDO = mix(lit, col_haze, haze);
	ALPHA = clamp(a, 0.0, 1.0);
}

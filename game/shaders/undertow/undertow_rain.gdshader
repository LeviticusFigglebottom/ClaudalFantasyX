// Hymn of the Undertow: near-field rain around the camera under the storm (M2-RND-05). Docs:
// docs/kb/tech/undertow.md ("Storm events"). Drawn on a unit open cylinder (radius 1, height 1,
// centred) that UndertowRain keeps on the camera; each layer is a curtain of rain_radius_m. Streaks
// fall at rain_fall_m_s on the storm clock (never TIME), slanted by the wind toward the storm.
shader_type spatial;
render_mode blend_mix, unshaded, cull_disabled, depth_draw_never, shadows_disabled;

#include "res://game/shaders/include/common.gdshaderinc"

#define UNDERTOW_RAIN_OFFSET vec3(3.1, -12.7, 21.9)
// Unit cylinder: VERTEX.y runs from -0.5 to 0.5.
#define UNDERTOW_UNIT_HALF 0.5

group_uniforms rain;
uniform float rain_amount : hint_range(0.0, 1.0) = 0.0;
uniform float rain_radius_m : hint_range(0.5, 200.0) = 6.0;
uniform float rain_height_m : hint_range(1.0, 400.0) = 36.0;
uniform float rain_fall_m_s : hint_range(0.0, 40.0) = 9.0;
// Sideways lean of the streaks (m across per m down).
uniform float rain_slant : hint_range(-2.0, 2.0) = 0.25;
uniform float rain_streak_m : hint_range(0.05, 20.0) = 1.6;
uniform float rain_drop_m : hint_range(0.005, 1.0) = 0.035;
uniform float rain_density : hint_range(0.0, 1.0) = 0.55;
uniform float rain_alpha : hint_range(0.0, 1.0) = 0.22;
// M2-RND-10: each column's streak length varies by +- rain_length_var, and rain_softness (0 crisp streaks,
// 1 a veil) widens the streak's edge, so the outer layers read as sheets of rain rather than scratches.
uniform float rain_length_var : hint_range(0.0, 0.9) = 0.0;
uniform float rain_softness : hint_range(0.0, 1.0) = 0.0;
uniform float rain_time_s = 0.0;
uniform vec3 col_rain : source_color = vec3(0.48, 0.53, 0.58);
group_uniforms;

varying vec2 v_sheet;

void vertex() {
	float h = VERTEX.y;
	vec2 dir = normalize(VERTEX.xz);
	VERTEX = vec3(dir.x * rain_radius_m, h * rain_height_m, dir.y * rain_radius_m);
	// Sheet coordinates (m): around the curtain and down it.
	v_sheet = vec2(atan(dir.y, dir.x) * rain_radius_m, (UNDERTOW_UNIT_HALF - h) * rain_height_m);
}

void fragment() {
	vec2 q = v_sheet;
	q.y -= rain_fall_m_s * rain_time_s;
	q.x += q.y * rain_slant;
	float column = floor(q.x / rain_drop_m);
	float drop = hymn_hash12(vec2(column, rain_radius_m));
	float len_m = rain_streak_m * (1.0 + rain_length_var * (2.0 * hymn_hash12(vec2(column, 7.3)) - 1.0));
	float streak = hymn_value_noise2(vec2(column * 1.37, (q.y + drop * 97.0) / len_m));
	float on = step(1.0 - rain_density, drop) * smoothstep(0.55 - 0.4 * rain_softness, 0.85, streak);
	float edge = smoothstep(0.0, 0.15, UV.y) * smoothstep(0.0, 0.15, 1.0 - UV.y);
	ALBEDO = col_rain;
	ALPHA = clamp(on * rain_alpha * rain_amount * edge, 0.0, 1.0);
}

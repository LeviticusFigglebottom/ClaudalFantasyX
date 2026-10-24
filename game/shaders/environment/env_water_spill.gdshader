// Hymn of the Undertow: a falling sheet of water (M2-ENV-03): the Shell Shrine's basin lips and spring
// spout pouring into the channels (haluna.md S04). The ribbon's UV.x runs across the sheet (0..1), UV.y
// down the fall (0 at the lip .. 1 where it lands). Streaks run down with hymn_wind_time; the sheet
// thins and breaks up toward its edges and its foot. Alpha-blended, both faces, no depth write.
shader_type spatial;
render_mode blend_mix, cull_disabled, depth_draw_never, specular_schlick_ggx;

#include "res://game/shaders/include/common.gdshaderinc"
#include "res://game/shaders/include/globals.gdshaderinc"

group_uniforms sheet;
uniform vec4 col_water : source_color = vec4(0.62, 0.86, 0.84, 1.0);
uniform vec4 col_foam : source_color = vec4(0.93, 0.96, 0.95, 1.0);
uniform float opacity : hint_range(0.0, 1.0) = 0.55;
uniform float fall_speed_m_s : hint_range(0.0, 6.0) = 2.4;
uniform float streak_scale : hint_range(1.0, 40.0) = 14.0;
uniform float streak_stretch : hint_range(0.05, 1.0) = 0.18;
uniform float foot_foam : hint_range(0.0, 1.0) = 0.6;
uniform float roughness_value : hint_range(0.0, 1.0) = 0.08;
uniform float emission_energy : hint_range(0.0, 1.0) = 0.06;
group_uniforms;

void fragment() {
	float t = hymn_wind_time * fall_speed_m_s;
	vec2 q = vec2(UV.x * streak_scale, (UV.y - t) * streak_scale * streak_stretch);
	float streak = hymn_value_noise2(q) * 0.65 + hymn_value_noise2(q * 2.3 + 7.1) * 0.35;
	float edge = smoothstep(0.0, 0.18, UV.x) * smoothstep(1.0, 0.82, UV.x);
	float foot = smoothstep(0.55, 1.0, UV.y);
	float foam = foot * foot_foam * smoothstep(0.45, 0.8, streak);
	ALBEDO = mix(col_water.rgb, col_foam.rgb, foam);
	ROUGHNESS = roughness_value;
	SPECULAR = 0.5;
	EMISSION = col_water.rgb * emission_energy * (0.5 + streak);
	ALPHA = clamp(opacity * edge * (0.55 + 0.6 * streak) * (1.0 - foot * 0.4) + foam * 0.3, 0.0, 1.0);
}

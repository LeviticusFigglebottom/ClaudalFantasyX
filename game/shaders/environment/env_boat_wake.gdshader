// Hymn of the Undertow: a moving boat's wake (M3-ENV-1000, brine_shoals.md §2): the Order's skiffs and the
// vendor boats leave one; Sefir's barge never does (ADR 0017 (a)). The Brine Shoals kit's boat_wake ribbons:
// UV.x across a ribbon (0..1), UV.y along the wake (0 at the stern .. 1 at its tail), UV2.x 0 on the Kelvin arms
// and 1 on the churned centre track. Foam streaks drift back with hymn_wind_time at the boat's speed; the wake
// fades toward its tail and its ribbons' edges. speed_m_s 0 hides it (a moored boat). Alpha-blended, no depth write.
shader_type spatial;
render_mode blend_mix, cull_disabled, depth_draw_never, specular_schlick_ggx;

#include "res://game/shaders/include/common.gdshaderinc"
#include "res://game/shaders/include/globals.gdshaderinc"

group_uniforms wake;
uniform vec4 col_foam : source_color = vec4(0.92, 0.94, 0.92, 1.0);
uniform vec4 col_churn : source_color = vec4(0.62, 0.72, 0.68, 1.0);
uniform float opacity : hint_range(0.0, 1.0) = 0.7;
uniform float speed_m_s : hint_range(0.0, 6.0) = 1.6;
uniform float full_speed_m_s : hint_range(0.5, 6.0) = 1.6;
uniform float wake_length_m : hint_range(1.0, 40.0) = 16.0;
uniform float streak_scale : hint_range(1.0, 40.0) = 9.0;
uniform float tail_fade : hint_range(0.05, 1.0) = 0.55;
uniform float roughness_value : hint_range(0.0, 1.0) = 0.35;
group_uniforms;

void fragment() {
	float strength = clamp(speed_m_s / full_speed_m_s, 0.0, 1.0);
	float along = UV.y * wake_length_m;
	vec2 q = vec2(UV.x * 3.0 + UV2.x * 11.0, (along + hymn_wind_time * speed_m_s) * streak_scale / wake_length_m);
	float n = hymn_value_noise2(q) * 0.6 + hymn_value_noise2(q * 2.7 + 3.1) * 0.4;
	// Arms: a crest line along the middle of the ribbon; the track: churn across all of it.
	float across = abs(UV.x - 0.5) * 2.0;
	float crest = mix(1.0 - smoothstep(0.0, 0.85, across), 1.0 - smoothstep(0.4, 1.0, across), UV2.x);
	float tail = 1.0 - smoothstep(1.0 - tail_fade, 1.0, UV.y);
	float head = smoothstep(0.0, 0.03, UV.y);
	float foam = crest * tail * head * smoothstep(0.35, 0.75, n + 0.25 * (1.0 - UV.y));
	ALBEDO = mix(col_churn.rgb, col_foam.rgb, smoothstep(0.2, 0.7, foam));
	ROUGHNESS = roughness_value;
	SPECULAR = 0.4;
	ALPHA = clamp(opacity * strength * foam, 0.0, 1.0);
}

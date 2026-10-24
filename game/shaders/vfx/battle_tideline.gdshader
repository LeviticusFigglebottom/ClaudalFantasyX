// Hymn of the Undertow: the encounter stinger's tide line (M2-BPR-05). Docs: docs/kb/tech/battle_presentation.md,
// "Encounter transition". Drawn full screen by BattleStinger (game/flow/battle_stinger.gd) over the frozen field,
// before SceneRouter's fade: a band of dark water rises from the bottom edge to `crest` of the screen as `progress`
// goes 0 -> 1. Its surface is a slow two-sine swell with a thin foam crest; the field under it ripples (a small
// sideways refraction) and sinks into a teal-to-abyss gradient; the field above it dims and loses its colour.
// Every value comes from game/data/flow/battle_transition.json. At progress 0 the output is the screen unchanged.
shader_type canvas_item;

const float TAU_ = 6.28318530718;
// Rec.709 relative luminance (the palette's luminance_linear uses the same weights).
const vec3 LUMA = vec3(0.2126, 0.7152, 0.0722);

uniform sampler2D screen_tex : hint_screen_texture, repeat_disable, filter_linear;
uniform float progress : hint_range(0.0, 1.0) = 0.0;
// Seconds since the stinger started (BattleStinger drives it, so the swell is frame-exact in captures).
uniform float phase = 0.0;
uniform float crest = 0.62;
uniform float wave_amplitude = 0.014;
uniform float wave_frequency = 2.6;
uniform float wave_speed = 0.45;
uniform float wave_detail = 2.3;
uniform float wave_detail_weight = 0.35;
uniform float foam_width = 0.008;
uniform float foam_alpha = 0.28;
uniform float water_alpha_top = 0.5;
uniform float water_alpha = 0.82;
uniform float refract = 0.004;
uniform float refract_frequency = 9.0;
uniform float dim = 0.32;
uniform float desaturate = 0.55;
uniform vec4 water_deep : source_color = vec4(0.024, 0.102, 0.169, 1.0);
uniform vec4 water_edge : source_color = vec4(0.055, 0.290, 0.333, 1.0);
uniform vec4 foam : source_color = vec4(0.933, 0.965, 0.957, 1.0);

void fragment() {
	vec2 uv = SCREEN_UV;
	float t = phase * wave_speed;
	float swell = sin((uv.x * wave_frequency + t) * TAU_) * (1.0 - wave_detail_weight)
		+ sin((uv.x * wave_frequency * wave_detail - t) * TAU_) * wave_detail_weight;
	float line = 1.0 - crest * progress + swell * wave_amplitude * progress;
	// > 0 under the water, in screen fractions.
	float depth = uv.y - line;

	vec3 field = texture(screen_tex, uv).rgb;
	vec3 grey = vec3(dot(field, LUMA));
	vec3 above = mix(field, grey, desaturate * progress) * (1.0 - dim * progress);

	vec2 bent = uv + vec2(sin((uv.y * refract_frequency + t) * TAU_) * refract * progress, 0.0);
	vec3 seen = texture(screen_tex, bent).rgb;
	float down = clamp(depth / max(1.0 - line, 1e-4), 0.0, 1.0);
	vec3 water = mix(water_edge.rgb, water_deep.rgb, down);
	vec3 below = mix(seen, water, mix(water_alpha_top, water_alpha, down));

	float risen = step(1e-4, progress);
	float under = smoothstep(-foam_width, foam_width, depth) * risen;
	vec3 col = mix(above, below, under);
	float crest_line = 1.0 - smoothstep(0.0, foam_width, abs(depth));
	col = mix(col, foam.rgb, crest_line * foam_alpha * risen);
	COLOR = vec4(col, 1.0);
}

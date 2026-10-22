shader_type canvas_item;
// Full-screen scrim behind result screens: night_sky deepening softly toward the edges, so the
// battlefield stays visible in the middle while the panel reads clearly. `amount` fades it in.

uniform vec4 tint : source_color = vec4(0.02, 0.039, 0.078, 0.55);
uniform float center_alpha = 0.55;
uniform float inner = 0.25;
uniform float outer = 1.1;
uniform float amount : hint_range(0.0, 1.0) = 1.0;

void fragment() {
	vec2 p = (UV - 0.5) * vec2(1.7778, 1.0) * 2.0;
	float edge = smoothstep(inner, outer, length(p));
	COLOR = vec4(tint.rgb, tint.a * mix(center_alpha, 1.0, edge) * amount);
}

shader_type canvas_item;
// Lamplight seen through water (ADR 0033): thin, slowly drifting caustic lines over a menu's
// backdrop, brightest in the upper middle and fading toward the edges and the bottom, so the
// panels above stay the brightest thing on screen. `phase` is advanced by CausticBackdrop from
// its own elapsed time (so --fixed-fps captures are deterministic), and holds still under reduced
// motion. `tint` carries the colour and the strongest alpha.

uniform vec4 tint : source_color = vec4(0.435, 0.878, 0.847, 0.07);
uniform float phase = 0.0;
uniform float scale = 5.5;
uniform float sharpness = 9.0;

float ridge(vec2 p) {
	float a = sin(p.x + sin(p.y * 0.8 + phase * 0.7) * 1.3);
	float b = sin(p.y * 1.1 + sin(p.x * 0.9 - phase * 0.5) * 1.5);
	float c = sin((p.x + p.y) * 0.7 + phase * 0.3);
	float v = (a + b + c) / 3.0;
	return pow(1.0 - abs(v), sharpness);
}

void fragment() {
	vec2 p = UV * vec2(1.7778, 1.0) * scale;
	float lines = ridge(p) * 0.65 + ridge(p * 1.9 + vec2(3.1, 1.7)) * 0.35;
	vec2 q = (UV - vec2(0.5, 0.35)) * vec2(1.7778, 1.0);
	float falloff = 1.0 - smoothstep(0.15, 1.15, length(q));
	COLOR = vec4(tint.rgb, tint.a * lines * falloff);
}

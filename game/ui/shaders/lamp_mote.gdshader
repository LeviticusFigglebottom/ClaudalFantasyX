shader_type canvas_item;
// The lamp mote (docs/kb/art/ui.md §3): a soft ui_focus glow with a gold core that "breathes".
// `phase` is driven by script time (not TIME) so screenshot captures stay deterministic.

uniform vec4 glow_color : source_color = vec4(0.435, 0.878, 0.847, 0.9);
uniform vec4 core_color : source_color = vec4(0.851, 0.706, 0.353, 1.0);
uniform float core_radius = 0.28;
uniform float core_soft = 0.12;
uniform float alpha_min = 0.75;
// 0..1 position in the breathing cycle; 1.0 alpha when breathing is off.
uniform float phase = 0.25;
uniform bool breathing = true;

void fragment() {
	vec2 p = UV * 2.0 - 1.0;
	float d = length(p);
	float glow = 1.0 - smoothstep(0.0, 1.0, d);
	glow *= glow;
	float core = 1.0 - smoothstep(core_radius, core_radius + core_soft, d);
	float breath = breathing ? mix(alpha_min, 1.0, 0.5 + 0.5 * sin(phase * TAU)) : 1.0;
	vec3 rgb = mix(glow_color.rgb, core_color.rgb, core);
	float a = max(glow * glow_color.a, core * core_color.a);
	COLOR = vec4(rgb, a * breath);
}

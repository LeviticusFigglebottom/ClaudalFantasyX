shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_never, cull_disabled, shadows_disabled;
// Target highlight ring on the ground (docs/kb/art/ui.md §6.4): a thin ring at `radius` with a
// soft inner gradient, six notch gaps so it is never a plain circle, rotating at 12°/s.
// Drawn on a flat quad whose UV spans [-extent, extent] metres. `spin` (radians) comes from
// script time so captures stay deterministic.

uniform vec4 ring_color : source_color = vec4(0.435, 0.878, 0.847, 1.0);
uniform float radius = 0.7;
uniform float line_width = 0.06;
uniform float inner_soft = 0.25;
uniform float extent = 1.2;
uniform float notches = 6.0;
uniform float notch_fraction = 0.12;
uniform float spin = 0.0;
uniform float intensity = 1.0;
uniform float inner_alpha = 0.35;
uniform float notch_soft = 0.02;

void fragment() {
	vec2 p = (UV * 2.0 - 1.0) * extent;
	float d = length(p);
	float half_w = line_width * 0.5;
	float aa = fwidth(d) * 1.5;
	float line = 1.0 - smoothstep(half_w - aa, half_w + aa, abs(d - radius));
	float inner = smoothstep(radius - inner_soft, radius, d) * step(d, radius) * inner_alpha;
	float ang = atan(p.y, p.x) + spin;
	float cell = fract(ang / TAU * notches);
	float gap = smoothstep(0.0, notch_soft, cell) * (1.0 - smoothstep(notch_fraction - notch_soft, notch_fraction, cell));
	float notch = 1.0 - gap;
	float a = max(line * notch, inner) * intensity;
	ALBEDO = ring_color.rgb;
	ALPHA = a * ring_color.a;
}

// Hymn of the Undertow: Ilun's Floodnet over the flood (M2-RND-04). Docs: docs/kb/tech/battle_vfx.md.
// Bound light (glimmer_bound): a steady net of caustic-like threads on the water. It never drifts or trails;
// it only fades in, holds and fades out (alpha, from BattleBossVfx). color_script.md rule 1, bound.
shader_type spatial;
render_mode blend_add, unshaded, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;

uniform vec3 color : source_color = vec3(0.31, 0.702, 0.69);
uniform float alpha = 0.0;
uniform float energy = 1.2;
uniform float half_m = 10.0;
uniform float cell_m = 1.1;
uniform float thread = 10.0;

float threads(vec2 p) {
	float a = 1.0 - abs(sin(p.x));
	float b = 1.0 - abs(sin(p.y));
	return pow(max(a, b), thread);
}

void fragment() {
	vec2 p = (UV - 0.5) * 2.0 * half_m;
	float r = length(p);
	// Two nets at 0 and 60 degrees, warped by each other: the knots read as a woven mesh, not a grid.
	vec2 q = p / cell_m;
	vec2 q2 = mat2(vec2(0.5, -0.866), vec2(0.866, 0.5)) * q;
	float net = threads(q + 0.35 * sin(q2.yx)) * 0.6 + threads(q2 + 0.35 * sin(q.yx)) * 0.6;
	float fade = 1.0 - smoothstep(half_m * 0.55, half_m, r);
	ALBEDO = color * energy * min(net, 1.0) * fade * alpha;
	ALPHA = 1.0;
}

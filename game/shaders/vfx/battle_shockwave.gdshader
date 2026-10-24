// Hymn of the Undertow: the Drownbell's toll shockwave (M2-RND-04). Docs: docs/kb/tech/battle_vfx.md.
// A flat quad over the water; BattleBossVfx grows radius_m and fades alpha. A bright leading edge, a soft
// trailing wash, and a slight ripple around the ring so it reads as water, not a decal.
shader_type spatial;
render_mode blend_add, unshaded, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;

uniform vec3 color : source_color = vec3(0.855, 0.922, 0.906);
uniform float radius_m = 1.0;
uniform float width_m = 0.35;
uniform float wash_m = 1.6;
uniform float alpha = 1.0;
// Half the quad's side, in metres (UV 0..1 spans -half_m..half_m).
uniform float half_m = 12.0;
uniform float ripple = 0.08;
uniform float ripple_count = 23.0;

void fragment() {
	vec2 p = (UV - 0.5) * 2.0 * half_m;
	float r = length(p);
	float ang = atan(p.y, p.x);
	float wobble = 1.0 + ripple * sin(ang * ripple_count) * sin(ang * 7.0 + radius_m);
	float d = r - radius_m * wobble;
	float edge = exp(-(d * d) / max(width_m * width_m, 1e-4));
	float wash = d < 0.0 ? exp(d / max(wash_m, 1e-3)) * 0.25 : 0.0;
	float a = (edge + wash) * alpha * (1.0 - smoothstep(half_m * 0.85, half_m, r));
	ALBEDO = color * a;
	ALPHA = 1.0;
}

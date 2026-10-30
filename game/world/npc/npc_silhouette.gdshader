shader_type spatial;
// A person drawn as one glowing silhouette (M3-HER-1142: the figure in Corrow's storm wall, act1_ch08 W22, "a
// single cyan silhouette"). Unshaded: no face, cloth or skin reads, only the shape. The rim (fresnel) burns brighter
// than the core so the outline holds against the storm; the body fades toward its feet as if it stood in the water.
// A depth prepass keeps only the nearest surface, so the costume's inner layers never show through: one shape.
// No TIME: a still frame renders the same on every run (screenshots).
render_mode unshaded, cull_back, depth_prepass_alpha, shadows_disabled, fog_disabled;

uniform vec4 glow : source_color = vec4(0.373, 0.839, 0.878, 1.0);
// Core and rim brightness (HDR multipliers of `glow`) and opacity.
uniform float core_energy = 0.55;
uniform float rim_energy = 2.4;
uniform float rim_power = 2.2;
uniform float core_alpha = 0.62;
// The height (model space, metres from the soles) over which the body fades in from nothing.
uniform float feet_fade_m = 0.55;

varying float height_m;

void vertex() {
	height_m = VERTEX.y;
}

void fragment() {
	float rim = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), rim_power);
	float feet = smoothstep(0.0, feet_fade_m, height_m);
	ALBEDO = glow.rgb * mix(core_energy, rim_energy, rim);
	ALPHA = clamp(mix(core_alpha, 1.0, rim) * feet, 0.0, 1.0);
}

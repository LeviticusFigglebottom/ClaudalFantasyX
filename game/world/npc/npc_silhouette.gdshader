shader_type spatial;
// A person drawn as one glowing silhouette (M3-HER-1142: the figure in Corrow's storm wall, act1_ch08 W22, "a
// single cyan silhouette"). Unshaded: no face, cloth or skin reads, only the shape. The rim (fresnel) burns brighter
// than the core so the outline holds against the storm; the body fades toward its feet as if it stood in the water.
// A depth prepass keeps only the nearest surface, so the costume's inner layers never show through: one shape.
// Under the glow the body keeps its surface (the PC's real-GPU pass 3: up close it read as a featureless mannequin): its
// own albedo's brightness (cloth folds, seams, the face), its occlusion (crevices darker) and its normal map (the rim
// breaks along folds), plus sea-wear: faint brine tide lines and drip streaks down the cloth.
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
// The surface's own maps (NpcSilhouette copies them from the material each surface wore).
uniform sampler2D tex_albedo : source_color, hint_default_white, filter_linear_mipmap;
uniform sampler2D tex_normal : hint_normal, filter_linear_mipmap;
uniform sampler2D tex_orm : hint_default_white, filter_linear_mipmap;
// How much the albedo's brightness shades the core (0 flat .. 1 full), and the occlusion's darkening.
uniform float detail = 1.0;
uniform float cavity = 0.7;
// Sea-wear: brine tide lines (per metre of height) and drip streaks (columns per metre round the body).
uniform float wear = 0.5;
uniform float tide_lines_per_m = 3.0;
uniform float drips_per_m = 18.0;

varying vec3 model_pos;

float hash1(float x) {
	return fract(sin(x * 127.1) * 43758.5453);
}

void vertex() {
	model_pos = VERTEX;
}

void fragment() {
	vec3 nm = texture(tex_normal, UV).rgb * 2.0 - 1.0;
	vec3 n = normalize(TANGENT * nm.x + BINORMAL * nm.y + NORMAL * max(nm.z, 0.2));
	float rim = pow(1.0 - clamp(dot(n, VIEW), 0.0, 1.0), rim_power);
	float feet = smoothstep(0.0, feet_fade_m, model_pos.y);
	float luma = dot(texture(tex_albedo, UV).rgb, vec3(0.299, 0.587, 0.114));
	float shade = mix(1.0, 0.3 + 1.4 * luma, detail) * mix(1.0, texture(tex_orm, UV).r, cavity);
	float band = abs(fract(model_pos.y * tide_lines_per_m) - 0.5);
	float tide = smoothstep(0.47, 0.5, band);  // a thin bright brine line where the water stood
	float column = floor((model_pos.x + model_pos.z) * drips_per_m);
	float drip = step(0.72, hash1(column)) * smoothstep(0.0, 0.6, fract(model_pos.y * 1.7 + hash1(column + 7.0)));
	float core = core_energy * shade * (1.0 - wear * 0.6 * drip) + core_energy * wear * tide;
	ALBEDO = glow.rgb * mix(core, rim_energy, rim);
	ALPHA = clamp(mix(core_alpha, 1.0, rim) * feet, 0.0, 1.0);
}

// Hymn of the Undertow: carved wake-shells on the Pilgrim's Wake wall (M1-ENV-01, haluna.md §1.2).
// Each shell maps into one cell of shell_glyph.png (R = carved name glyph, G = radial rib relief).
// UV2.y = age (0 newest, whitest .. 1 oldest: salt-grey, worn glyph); COLOR.a = wear.
// One variant serves every tier: four texture fetches, no loops.
shader_type spatial;
render_mode cull_back;

group_uniforms surface;
uniform sampler2D tex_glyph : hint_default_black, filter_linear_mipmap_anisotropic, repeat_disable;
uniform vec4 col_new : source_color = vec4(0.922, 0.906, 0.875, 1.0); // gauze_white #EBE7DF (albedo ceiling)
uniform vec4 col_old : source_color = vec4(0.725, 0.682, 0.596, 1.0); // coral_stone_weathered #B9AE98
uniform vec4 col_glyph : source_color = vec4(0.42, 0.36, 0.30, 1.0); // carved groove, shadowed
uniform float glyph_depth : hint_range(0.0, 1.0) = 0.75;
uniform float rib_strength : hint_range(0.0, 2.0) = 0.6;
uniform float roughness_value : hint_range(0.0, 1.0) = 0.55;
uniform float ao_strength : hint_range(0.0, 1.0) = 0.7;
group_uniforms;

void fragment() {
	vec4 g = texture(tex_glyph, UV);
	float age = clamp(UV2.y, 0.0, 1.0);
	float glyph = g.r * mix(1.0, 0.45, age); // old names wear shallow
	vec3 shell = mix(col_new.rgb, col_old.rgb, age * age);
	shell *= 0.9 + 0.1 * g.g;
	ALBEDO = mix(shell, col_glyph.rgb, glyph * glyph_depth);
	// Ribs as a normal tilt across the fan: derivative of the rib relief in UV space.
	vec2 texel = vec2(1.0) / vec2(textureSize(tex_glyph, 0));
	float gx = texture(tex_glyph, UV + vec2(texel.x, 0.0)).g - texture(tex_glyph, UV - vec2(texel.x, 0.0)).g;
	NORMAL_MAP = vec3(clamp(0.5 - gx * rib_strength * 2.0, 0.0, 1.0), 0.5, 1.0);
	ROUGHNESS = roughness_value + 0.25 * age;
	SPECULAR = 0.45;
	AO = mix(1.0, UV2.x, ao_strength);
}

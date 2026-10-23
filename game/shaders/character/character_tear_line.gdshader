// Hymn of the Undertow: tear-line helper (M1-RND-04). The wet meniscus along the lower lid margin,
// and the `grief` tear layer (asha.md §6.3: a wet sheen on the lower lid, roughness 0.05).
// One variant, all tiers; built-in GGX lighting (no light()). Docs:
// docs/kb/tech/character_shading.md ("Eyes").
//
// UV contract: U along the lid margin (inner canthus 0 .. outer 1), V across the strip (lid 0 ..
// eyeball 1). Instance uniform inst_tears (0..1) is driven by the emotion system.
shader_type spatial;
render_mode blend_mix, depth_draw_never, cull_back, shadows_disabled, specular_schlick_ggx;

#include "res://game/shaders/character/character_brdf.gdshaderinc"

group_uniforms tear;
uniform vec4 col_tear : source_color = vec4(0.784, 0.565, 0.533, 1.0); // moist lid margin #C89088
uniform float coverage : hint_range(0.0, 1.0) = 0.55; // alpha at rest
uniform float roughness_rest : hint_range(0.02, 0.5) = 0.12;
uniform float roughness_tears : hint_range(0.02, 0.5) = 0.05; // asha.md §6.3 grief layer
uniform float spec_aa : hint_range(0.0, 1.0) = 1.0;
group_uniforms;

instance uniform float inst_tears : hint_range(0.0, 1.0) = 0.0;

void fragment() {
	float across = sin(clamp(UV.y, 0.0, 1.0) * HYMN_PI);
	float along = smoothstep(0.0, 0.08, UV.x) * smoothstep(1.0, 0.92, UV.x);
	ALBEDO = col_tear.rgb;
	float r = mix(roughness_rest, roughness_tears, inst_tears);
	ROUGHNESS = mix(r, hymn_char_spec_aa_roughness(NORMAL, r), spec_aa);
	SPECULAR = HYMN_CHAR_CORNEA_F0 / 0.08;
	METALLIC = 0.0;
	ALPHA = clamp(across * along * mix(coverage, 1.0, inst_tears), 0.0, 1.0);
}

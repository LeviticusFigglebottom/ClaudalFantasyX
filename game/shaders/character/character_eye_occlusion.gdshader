// Hymn of the Undertow: eye-occlusion helper (M1-RND-04). A thin shell between the eyelids and the
// eyeball that multiplies the eye by a soft lid shadow, so the eye sits *in* the face instead of
// on it (the biggest single cue against the "stuck-on eye" uncanny read). One variant, all tiers.
// Docs: docs/kb/tech/character_shading.md ("Eyes").
//
// UV contract (authored by Character on the occlusion shell): U runs from the inner canthus (0)
// to the outer canthus (1), V from the upper lid margin (0) to the lower lid margin (1).
shader_type spatial;
render_mode blend_mul, unshaded, depth_draw_never, cull_back, shadows_disabled, fog_disabled;

group_uniforms occlusion;
uniform vec4 col_occlusion : source_color = vec4(0.29, 0.165, 0.133, 1.0); // warm #4A2A22, never grey
uniform float upper_strength : hint_range(0.0, 1.0) = 0.75; // the upper lid and lashes shade most
uniform float upper_width : hint_range(0.01, 0.8) = 0.38;
uniform float lower_strength : hint_range(0.0, 1.0) = 0.35;
uniform float lower_width : hint_range(0.01, 0.8) = 0.18;
uniform float corner_strength : hint_range(0.0, 1.0) = 0.55;
uniform float corner_width : hint_range(0.01, 0.5) = 0.14;
uniform float occlusion_scale : hint_range(0.0, 1.0) = 1.0; // 0 turns the helper off
group_uniforms;

void fragment() {
	float v = UV.y;
	float u = UV.x;
	float upper = upper_strength * (1.0 - smoothstep(0.0, upper_width, v));
	float lower = lower_strength * smoothstep(1.0 - lower_width, 1.0, v);
	float corner = corner_strength * max(1.0 - smoothstep(0.0, corner_width, u), smoothstep(1.0 - corner_width, 1.0, u));
	float occ = clamp(1.0 - (1.0 - upper) * (1.0 - lower) * (1.0 - corner), 0.0, 1.0) * occlusion_scale;
	ALBEDO = mix(vec3(1.0), col_occlusion.rgb, occ);
}

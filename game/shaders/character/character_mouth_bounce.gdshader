// Hymn of the Undertow: hero mouth interior, the unshadowed cavity-bounce pass (M1-RND-24). Single tier.
// An additive next_pass that CharacterShaderTiers.apply_to_tree attaches to every mouth-family material
// (mouth bag, teeth, tongue), with the base material's parameters copied in. It draws only positional
// lights' cavity bounce: shadows_disabled makes their ATTENUATION the distance and cone falloff alone,
// which the base pass cannot separate from the shadow. No ambient, reflections or fog (the base pass
// has them). Docs: docs/kb/tech/character_shading.md ("Mouth interior").
shader_type spatial;
render_mode blend_add, depth_draw_never, cull_back, shadows_disabled, ambient_light_disabled, fog_disabled;
#define HYMN_QUALITY HYMN_QUALITY_HIGH
#define HYMN_MOUTH_BOUNCE_PASS
#include "res://game/shaders/character/character_mouth_body.gdshaderinc"

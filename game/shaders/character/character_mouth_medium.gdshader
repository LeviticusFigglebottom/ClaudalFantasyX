// Hymn of the Undertow: Hero mouth interior (mouth bag, teeth, tongue), MEDIUM tier (Medium preset). M1-RND-21.
// Thin wrapper: the shader lives in the body include. Preset-to-variant mapping:
// game/shaders/character/character_shader_tiers.json. Docs: docs/kb/tech/character_shading.md.
shader_type spatial;
render_mode cull_back;
#define HYMN_QUALITY HYMN_QUALITY_MEDIUM
#include "res://game/shaders/character/character_mouth_body.gdshaderinc"

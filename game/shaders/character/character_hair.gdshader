// Hymn of the Undertow: Hero hair cards, HIGH tier (High and Ultra presets; the default variant). M1-RND-04.
// Thin wrapper: the shader lives in the body include. Preset-to-variant mapping:
// game/shaders/character/character_shader_tiers.json. Docs: docs/kb/tech/character_shading.md.
shader_type spatial;
render_mode cull_disabled;
#define HYMN_QUALITY HYMN_QUALITY_HIGH
#define HYMN_HAIR_ALPHA_MODE 0 // temporal dither, resolved by TAA / FSR2
#include "res://game/shaders/character/character_hair_body.gdshaderinc"

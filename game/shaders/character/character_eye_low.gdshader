// Hymn of the Undertow: Hero eyeball (sclera + iris), LOW tier (Low preset). M1-RND-04.
// Thin wrapper: the shader lives in the body include. Preset-to-variant mapping:
// game/shaders/character/character_shader_tiers.json. Docs: docs/kb/tech/character_shading.md.
shader_type spatial;
render_mode cull_back;
#define HYMN_QUALITY HYMN_QUALITY_LOW
#include "res://game/shaders/character/character_eye_body.gdshaderinc"

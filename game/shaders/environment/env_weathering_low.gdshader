// Hymn of the Undertow: stone and timber weathering, LOW tier (M1-ENV-01, SPEC §8.2 item 7).
// Body and layer docs: env_weathering_body.gdshaderinc. Zone usage: docs/kb/art/environments/haluna_mood_review.md.
shader_type spatial;
render_mode cull_back;
#define HYMN_QUALITY HYMN_QUALITY_LOW
#include "res://game/shaders/environment/env_weathering_body.gdshaderinc"

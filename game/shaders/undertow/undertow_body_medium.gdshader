// Hymn of the Undertow: the Undertow's raymarched body, MEDIUM tier. M1-RND-03.
// Fewer steps, envelope-only light samples, no curl warp. Body: undertow_body.gdshaderinc.
shader_type spatial;
#define HYMN_QUALITY HYMN_QUALITY_MEDIUM
#define UNDERTOW_MAX_STEPS 32
#define UNDERTOW_LIGHT_SAMPLES 1
#define UNDERTOW_LIGHT_NOISE 0
#define UNDERTOW_CURL 0
#define UNDERTOW_OCTAVES 3
#include "res://game/shaders/undertow/undertow_body.gdshaderinc"

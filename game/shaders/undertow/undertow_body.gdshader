// Hymn of the Undertow: the Undertow's raymarched body, HIGH tier (default). M1-RND-03.
// Body: undertow_body.gdshaderinc. Docs: docs/kb/tech/undertow.md.
shader_type spatial;
#define UNDERTOW_MAX_STEPS 48
#define UNDERTOW_LIGHT_SAMPLES 2
#define UNDERTOW_LIGHT_NOISE 1
#define UNDERTOW_CURL 1
#define UNDERTOW_OCTAVES 4
#include "res://game/shaders/undertow/undertow_body.gdshaderinc"

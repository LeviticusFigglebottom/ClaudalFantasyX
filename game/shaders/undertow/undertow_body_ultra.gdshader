// Hymn of the Undertow: the Undertow's raymarched body, ULTRA tier. M1-RND-03.
// More steps, three noisy light samples, five octaves. Body: undertow_body.gdshaderinc.
shader_type spatial;
#define HYMN_QUALITY HYMN_QUALITY_ULTRA
#define UNDERTOW_MAX_STEPS 80
#define UNDERTOW_LIGHT_SAMPLES 3
#define UNDERTOW_LIGHT_NOISE 1
#define UNDERTOW_CURL 1
#define UNDERTOW_OCTAVES 5
#include "res://game/shaders/undertow/undertow_body.gdshaderinc"

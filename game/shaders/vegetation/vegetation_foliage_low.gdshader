// Foliage cards, Low tier: no translucency, no secondary bob or flutter (primary sway only).
shader_type spatial;
render_mode cull_disabled, world_vertex_coords, depth_draw_opaque;

#define HYMN_QUALITY HYMN_QUALITY_LOW
#include "res://game/shaders/vegetation/vegetation_foliage_body.gdshaderinc"

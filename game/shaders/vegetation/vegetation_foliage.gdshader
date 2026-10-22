// Foliage cards: palm fronds, frangipani leaves and flowers, saltgrass, beach vine (M1-ENV-02).
// Default tier (High/Ultra/Medium). The Low preset uses vegetation_foliage_low.gdshader.
shader_type spatial;
render_mode cull_disabled, world_vertex_coords, depth_draw_opaque;

#include "res://game/shaders/vegetation/vegetation_foliage_body.gdshaderinc"

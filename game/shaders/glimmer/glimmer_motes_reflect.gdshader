// Glimmer motes: still-water reflection pass (M1-RND-02). Mirrors each mote about mirror_plane_y
// and draws it dimmer and softer. Depth test is off because the mirrored motes sit below the
// opaque water plane; see docs/kb/tech/glimmer.md "Gotchas" before using it near tall geometry.
shader_type spatial;
render_mode blend_add, unshaded, skip_vertex_transform, depth_draw_never, depth_test_disabled, cull_disabled,
		shadows_disabled, fog_disabled;

#define GLIMMER_MIRROR
#include "res://game/shaders/glimmer/glimmer_motes_draw_body.gdshaderinc"

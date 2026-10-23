// Hymn of the Undertow: depth-only lid over the maelstrom (M1-RND-03). Docs: docs/kb/tech/undertow.md.
// The zone ocean (WaterSurface) is transparent but writes depth at sea level, so it would cover the
// funnel that the storm's opaque sea disc draws BELOW sea level. This invisible disc is drawn in
// the transparent pass just before the water (render_priority below it), a little above the
// highest wave crest, writing depth and no colour: the ocean then fails its depth test over the
// storm's footprint and the funnel shows through. Nothing is rebuilt when the storm moves.
// The raymarched body clips against the OPAQUE depth copy, so the lid never hides the storm.
shader_type spatial;
render_mode blend_mix, unshaded, depth_draw_always, cull_back, shadows_disabled, fog_disabled;

// Height above the storm's sea level (m): the zone's crest height plus the disc's own lift.
uniform float lid_height_m : hint_range(0.0, 50.0) = 3.0;

void vertex() {
	VERTEX.y = lid_height_m;
}

void fragment() {
	ALBEDO = vec3(0.0);
	ALPHA = 0.0;
}

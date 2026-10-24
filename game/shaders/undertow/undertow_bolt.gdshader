// Hymn of the Undertow: one lightning bolt (M2-RND-05). Docs: docs/kb/tech/undertow.md ("Storm events").
// Drawn on an UndertowMeshBuilder.bolt() stroke in storm-local model space. Every segment quad's
// vertices sit on its endpoints; the vertex shader pushes them apart across the view by the bolt's
// width (never thinner than bolt_min_px pixels, so a strike 15 km out still reads). The light is the
// ch20 key colour, at the site's flash level (UndertowBolts sets bolt_level from UndertowState).
shader_type spatial;
render_mode blend_add, unshaded, cull_disabled, depth_draw_never, fog_disabled, shadows_disabled;

group_uniforms bolt;
uniform float bolt_level : hint_range(0.0, 2.0) = 0.0;
uniform float bolt_width_m : hint_range(0.1, 500.0) = 45.0;
uniform float bolt_min_px : hint_range(0.0, 16.0) = 1.5;
uniform float bolt_energy : hint_range(0.0, 64.0) = 6.0;
uniform vec3 col_lightning : source_color = vec3(0.552, 0.672, 1.0);
uniform vec3 col_haze : source_color = vec3(0.35, 0.3, 0.32);
uniform float haze_visibility_m : hint_range(100.0, 200000.0) = 26000.0;
group_uniforms;

varying float v_dist;
varying float v_bright;

void vertex() {
	vec3 world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec3 tangent = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
	vec3 to_cam = CAMERA_POSITION_WORLD - world;
	float dist = length(to_cam);
	vec3 side = normalize(cross(tangent, to_cam));
	// One pixel at this distance: 2 d tan(fov / 2) / viewport height.
	float px = 2.0 * dist / (PROJECTION_MATRIX[1][1] * VIEWPORT_SIZE.y);
	float w = max(bolt_width_m * COLOR.r, bolt_min_px * px);
	world += side * UV.x * 0.5 * w;
	VERTEX = (inverse(MODEL_MATRIX) * vec4(world, 1.0)).xyz;
	v_dist = dist;
	v_bright = COLOR.g * mix(1.0, 0.35, UV.y);
}

void fragment() {
	float x = UV.x;
	float core = exp(-x * x * 9.0);
	float haze = exp(-v_dist / haze_visibility_m);
	// Unshaded and additive: ALBEDO is the light added (EMISSION is ignored when unshaded).
	ALBEDO = col_lightning * bolt_energy * bolt_level * v_bright * core * haze;
}

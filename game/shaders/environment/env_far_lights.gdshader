// Hymn of the Undertow: distant festival lights (M3-ENV-03, pemakar.md §0). Each MultiMesh instance is a
// camera-facing quad with a soft round falloff: the Lanternfall leaf-boats on the far terrace bands, too
// small to model at that range. Additive, unshaded, no depth write; the instance's scale sets its size.
shader_type spatial;
render_mode blend_add, unshaded, cull_disabled, depth_draw_never, fog_disabled;

uniform vec4 col_light : source_color = vec4(1.0, 0.655, 0.341, 1.0); // ch05 lamp key #FFA757
uniform float energy : hint_range(0.0, 20.0) = 3.0;
uniform float core : hint_range(0.0, 1.0) = 0.18; // radius of the hot core (quad half-size = 1)
uniform float fog_dim_m = 900.0; // lights fade with distance (ash haze), half-way at this range

void vertex() {
	// Billboard: keep the instance's scale, face the camera.
	vec3 scale = vec3(length(MODEL_MATRIX[0].xyz), length(MODEL_MATRIX[1].xyz), length(MODEL_MATRIX[2].xyz));
	MODELVIEW_MATRIX = VIEW_MATRIX * mat4(
		INV_VIEW_MATRIX[0] * scale.x, INV_VIEW_MATRIX[1] * scale.y, INV_VIEW_MATRIX[2] * scale.z, MODEL_MATRIX[3]);
}

void fragment() {
	vec2 d = UV * 2.0 - 1.0;
	float r = length(d);
	float glow = exp(-r * r * 6.0) * 0.35 + smoothstep(core * 1.6, core * 0.4, r);
	float dist = length(VERTEX);
	float haze = fog_dim_m / (fog_dim_m + dist);
	ALBEDO = col_light.rgb * energy * glow * haze;
	ALPHA = 1.0;
}

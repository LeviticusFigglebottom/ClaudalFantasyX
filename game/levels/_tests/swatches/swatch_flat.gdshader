// Flat swatch patch for the swatch card (M1-ART-04). Writes a linear-light value straight into the HDR
// buffer, so the only thing between the palette value and the screen is exposure and the tonemapper.
// `lin` is the palette's `linear` triple; `level` is the scene-referred multiplier (0.5 / 1 / 2 ...).
shader_type spatial;
render_mode unshaded, cull_disabled, shadows_disabled, fog_disabled;

uniform vec3 lin = vec3(0.18);
uniform float level = 1.0;

void fragment() {
	ALBEDO = lin * level;
}

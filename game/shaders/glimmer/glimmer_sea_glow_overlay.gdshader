// Night sea-glow overlay (M1-RND-02): a cheap additive pass any zone can put on its sea surface
// until the zone's water shader calls hymn_sea_glow() itself (M1-RND-01 integrates it there).
// Use it as the next_pass of the water material, or on its own plane a few mm above the water.
// Shows zone_energy (else the zone's hymn_zone_sea_glow) clamped to the colour-script band 0.04-0.15;
// off when both are 0 or the zone is hard off (hymn_sea_glow_zone). Not gated by hymn_glimmer.a.
// Docs: docs/kb/tech/glimmer.md. Rule: docs/kb/art/color_script.md, narrative light rule 3.
shader_type spatial;
render_mode blend_add, unshaded, depth_draw_never, cull_back, shadows_disabled, fog_disabled;

#include "res://game/shaders/include/globals.gdshaderinc"
#include "res://game/shaders/include/glimmer.gdshaderinc"

uniform float zone_energy : hint_range(0.0, 0.15) = 0.08;
// Metres of water column under the surface the glow should suggest (0 = surface only).
uniform float column_m : hint_range(0.0, 50.0) = 0.0;
// Pushes the pass towards the camera to avoid z-fighting when drawn as a next_pass (metres).
uniform float depth_bias_m : hint_range(0.0, 0.1) = 0.004;

// Schlick reflectance of water at normal incidence ((1.33 - 1) / (1.33 + 1))^2. Light from below
// the surface reaches the eye through the transmitted part (1 - F), so the glow sinks into the sky
// reflection towards the horizon, as a real lit-from-below sea does.
#define WATER_F0 0.02

varying vec3 v_world;

void vertex() {
	v_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec3 to_cam = normalize(CAMERA_POSITION_WORLD - v_world);
	VERTEX += (inverse(MODEL_MATRIX) * vec4(to_cam * depth_bias_m, 0.0)).xyz;
}

void fragment() {
	float cos_v = clamp(dot(NORMAL, VIEW), 0.0, 1.0);
	float transmission = 1.0 - (WATER_F0 + (1.0 - WATER_F0) * pow(1.0 - cos_v, 5.0));
	ALBEDO = hymn_sea_glow_global(v_world, zone_energy, column_m) * transmission;
}

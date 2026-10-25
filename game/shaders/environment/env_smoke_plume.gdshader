// Hymn of the Undertow: a smoke column (M3-ENV-02, brine_shoals.md §2): the Brine Shoals' burning camp.
// A simple in-repo stand-in for a volumetric column (a request to Rendering is filed): the kit's
// `smoke_plume` mesh is a pair of nested, open, leaning tubes whose UV.y runs 0 at the base to 1 at the top.
//   - soft silhouette: alpha falls with the view angle to the surface (N.V), so a tube reads as a column
//   - billows: world-space value fBm rising with hymn_wind_time (the capture holds that clock, so a frame
//     is reproducible), offset per plume by UV2.y
//   - near the camera the column thins out (near_fade_m), so a camera inside the smoke sees haze, not facets
//   - light: unshaded and self-lit, so the sun side reads at col_lit, the core at col_core, the column
//     glows when the sun is behind it (forward scattering), and the base takes the fire's col_fire
// Alpha-blended, both faces, no depth write.
shader_type spatial;
render_mode blend_mix, cull_disabled, depth_draw_never, unshaded, shadows_disabled;

#include "res://game/shaders/include/common.gdshaderinc"
#include "res://game/shaders/include/globals.gdshaderinc"

group_uniforms smoke;
uniform vec4 col_lit : source_color = vec4(0.722, 0.659, 0.565, 1.0); // fog albedo #B8A890 (colour script ch06)
uniform vec4 col_core : source_color = vec4(0.353, 0.322, 0.290, 1.0); // #5A524A
uniform vec4 col_fire : source_color = vec4(0.878, 0.439, 0.180, 1.0); // ember_orange #E0702E
uniform float light_energy : hint_range(0.0, 8.0) = 2.2; // the column's brightness against the scene's exposure
uniform float density : hint_range(0.0, 1.0) = 0.85;
uniform float edge_softness : hint_range(0.2, 6.0) = 1.6;
uniform float base_fade_m : hint_range(0.0, 0.5) = 0.12; // UV.y over which the base fades in
uniform float top_fade : hint_range(0.0, 1.0) = 0.35; // UV.y span over which the top dissipates
uniform float fire_glow : hint_range(0.0, 4.0) = 0.9;
uniform float forward_scatter : hint_range(0.0, 4.0) = 1.2;
uniform float noise_scale : hint_range(0.1, 8.0) = 2.2; // billows per 10 m
uniform float rise_speed : hint_range(0.0, 1.0) = 0.06; // in noise cells per second
uniform float near_fade_m : hint_range(0.0, 20.0) = 6.0; // the column thins out within this distance of the camera
group_uniforms;

varying vec3 v_world;

void vertex() {
	v_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec3 n_world = normalize((INV_VIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
	vec3 to_cam = normalize(CAMERA_POSITION_WORLD - v_world);
	float facing = abs(dot(n_world, to_cam));
	float t = hymn_wind_time * rise_speed;
	vec3 q = v_world * (noise_scale * 0.1) + vec3(UV2.y * 17.0, -t, UV2.y * 5.0);
	float billow = hymn_fbm3(q, 4, 2.03, 0.5);
	float h = UV.y;
	float shape = smoothstep(0.0, base_fade_m, h) * (1.0 - smoothstep(1.0 - top_fade, 1.0, h));
	float near = smoothstep(near_fade_m * 0.25, near_fade_m, length(CAMERA_POSITION_WORLD - v_world));
	float a = density * pow(facing, edge_softness) * shape * near * smoothstep(0.25, 0.75, billow + 0.15 * (1.0 - h));
	vec3 sun = normalize(hymn_sun_direction);
	float lit = clamp(dot(n_world, sun) * 0.5 + 0.5, 0.0, 1.0) * (0.6 + 0.4 * billow);
	float fwd = pow(clamp(dot(-to_cam, sun), 0.0, 1.0), 6.0) * forward_scatter;
	vec3 col = mix(col_core.rgb, col_lit.rgb, lit) * (1.0 + fwd * (1.0 - a * 0.5));
	col += col_fire.rgb * fire_glow * (1.0 - smoothstep(0.0, 0.12, h));
	ALBEDO = col * light_energy;
	ALPHA = clamp(a, 0.0, 1.0);
}

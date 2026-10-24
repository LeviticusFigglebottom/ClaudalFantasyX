// Hymn of the Undertow: Pemakar's ash-plume (M3-ENV-03, pemakar.md §0 and §2.4). The kit's ash_plume
// mesh is a lofted billowing column; UV.y runs 0 at the caldera vent to 1 at the top. The body is matte
// ash lit by the scene (moon or sky fill); its silhouette softens toward grazing view angles so it never
// reads as a hard-edged solid; the lowest part glows a dull ember from below (the caldera's light), no
// brighter than the night sea-glow, so the lamp pools stay the brightest things in the frame.
shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_back, diffuse_lambert_wrap, specular_disabled;

#include "res://game/shaders/include/common.gdshaderinc"
#include "res://game/shaders/include/globals.gdshaderinc"

group_uniforms body;
uniform vec4 col_body : source_color = vec4(0.243, 0.290, 0.341, 1.0); // storm_slate #3E4A57
uniform vec4 col_body_top : source_color = vec4(0.30, 0.31, 0.33, 1.0); // thinner, paler ash aloft
uniform float body_darken : hint_range(0.0, 1.0) = 0.35; // multiplies the albedo (ash is dark)
uniform float mottle : hint_range(0.0, 1.0) = 0.35;
uniform float mottle_scale_m = 70.0;
uniform float drift_m_s = 1.5; // billows roll upward with hymn_wind_time
group_uniforms;

group_uniforms silhouette;
uniform float opacity : hint_range(0.0, 1.0) = 0.95;
uniform float edge_soft : hint_range(0.01, 1.0) = 0.42; // N.V below this fades out
uniform float top_fade : hint_range(0.0, 1.0) = 0.35; // the last part of the column thins away
group_uniforms;

group_uniforms ember;
uniform vec4 col_ember : source_color = vec4(0.878, 0.439, 0.180, 1.0); // ember_orange #E0702E
uniform float ember_energy : hint_range(0.0, 2.0) = 0.25;
uniform float ember_height : hint_range(0.0, 1.0) = 0.18; // fraction of the column the glow reaches
uniform float ember_underside : hint_range(0.0, 1.0) = 0.6; // extra glow on down-facing billows
group_uniforms;

varying vec3 v_world;

void vertex() {
	v_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec3 q = v_world / mottle_scale_m + vec3(0.0, -hymn_wind_time * drift_m_s / mottle_scale_m, 0.0);
	float n = hymn_fbm3(q, 3, 2.03, 0.5);
	vec3 base = mix(col_body.rgb, col_body_top.rgb, smoothstep(0.2, 0.9, UV.y)) * body_darken;
	ALBEDO = base * (1.0 - mottle + mottle * 2.0 * n);
	ROUGHNESS = 1.0;
	float ndv = abs(dot(normalize(NORMAL), normalize(VIEW)));
	float edge = smoothstep(0.0, edge_soft, ndv);
	float top = 1.0 - smoothstep(1.0 - top_fade, 1.0, UV.y);
	ALPHA = clamp(opacity * edge * top * (0.75 + 0.5 * n), 0.0, 1.0);
	vec3 world_n = normalize((INV_VIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
	float low = 1.0 - smoothstep(0.0, ember_height, UV.y);
	float under = clamp(-world_n.y, 0.0, 1.0) * ember_underside;
	EMISSION = col_ember.rgb * ember_energy * low * (0.55 + 0.9 * n) * (1.0 + under);
}

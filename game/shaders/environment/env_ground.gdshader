// Hymn of the Undertow: zone ground (beach, lanes, village turf, lagoon floor) (M1-ENV-01).
// World-planar (XZ) texturing over a generated terrain mesh. Mask channels come from the terrain
// generator (game/levels/_tests/haluna_mood/haluna_terrain.gd):
//   COLOR.r lane (packed coral-sand paths)   COLOR.g turf (sandy soil, sparse grass, leaf litter)
//   COLOR.b seagrass (lagoon floor patches)   COLOR.a reef rubble (coral boulders and shingle)
// The wet-sand band follows the same live water height as the weathering shader (WeatheringTide).
// One variant serves every tier: six texture fetches, no loops (Low drops the detail sample).
shader_type spatial;
render_mode cull_back;

#include "res://game/shaders/include/common.gdshaderinc"
#include "res://game/shaders/include/globals.gdshaderinc"

group_uniforms sand;
uniform sampler2D tex_sand : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D tex_sand_normal : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform float sand_tile_m = 2.0;
uniform vec4 col_sand_dry : source_color = vec4(0.937, 0.867, 0.706, 1.0); // sand_dry #EFDDB4
uniform vec4 col_sand_wet : source_color = vec4(0.710, 0.616, 0.455, 1.0); // sand_wet #B59D74
uniform vec4 col_seabed : source_color = vec4(0.902, 0.882, 0.839, 1.0); // white coral floor (mortar_white)
uniform float sand_normal_strength : hint_range(0.0, 3.0) = 1.0;
uniform float sand_tint : hint_range(0.0, 1.0) = 0.55; // how far the texture is pulled to col_sand_dry
group_uniforms;

group_uniforms stone;
uniform sampler2D tex_stone : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D tex_stone_normal : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D tex_detail : hint_default_black, filter_linear_mipmap, repeat_enable;
uniform float stone_tile_m = 1.2;
uniform float detail_scale_m = 0.7;
uniform vec4 col_lane : source_color = vec4(0.76, 0.71, 0.62, 1.0);
uniform vec4 col_turf : source_color = vec4(0.55, 0.53, 0.36, 1.0);
uniform vec4 col_turf_grass : source_color = vec4(0.40, 0.47, 0.25, 1.0);
uniform vec4 col_seagrass : source_color = vec4(0.20, 0.30, 0.18, 1.0);
uniform vec4 col_rubble : source_color = vec4(0.725, 0.682, 0.596, 1.0); // coral_stone_weathered
uniform vec4 col_algae : source_color = vec4(0.290, 0.353, 0.180, 1.0); // #4A5A2E
group_uniforms;

group_uniforms tide;
// Tide datum and live water height come from hymn_water_level (y, x), published by the zone sea
// (M1-ENV-05).
// The wet band above the water (swash and capillary rise on a beach), in metres of height.
uniform float wet_band_m : hint_range(0.0, 2.0) = 0.45;
uniform float damp_band_m : hint_range(0.0, 3.0) = 1.1;
uniform float wet_roughness : hint_range(0.0, 1.0) = 0.25;
group_uniforms;

// M2 final pass (env-art): a beach is never one flat tone. Broad value drifts (wind-sorted sand),
// the wrack line of dried weed and shell at high water, and leaf litter on village turf.
group_uniforms breakup;
uniform float sand_macro_variation : hint_range(0.0, 0.4) = 0.12;
uniform float sand_macro_scale_m = 18.0;
uniform float wrack_height_m = 0.9; // above tide_line_y: haluna.md §0 high water
uniform float wrack_width_m : hint_range(0.0, 2.0) = 0.5;
uniform float wrack_cover : hint_range(0.0, 1.0) = 0.55;
uniform vec4 col_wrack : source_color = vec4(0.357, 0.298, 0.235, 1.0); // timber_weathered at ~72% value
uniform float litter_cover : hint_range(0.0, 1.0) = 0.35;
uniform vec4 col_litter : source_color = vec4(0.47, 0.37, 0.24, 1.0); // dry leaf (thatch x timber_weathered)
group_uniforms;

varying vec3 v_world_pos;

void vertex() {
	v_world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

vec3 ground_unpack(vec2 rg) {
	vec2 xy = rg * 2.0 - 1.0;
	return vec3(xy, sqrt(max(0.0, 1.0 - dot(xy, xy))));
}

void fragment() {
	float tide_line_y = hymn_water_level.y;
	float water_height_y = hymn_water_level.x;
	vec3 wp = v_world_pos;
	vec4 m = COLOR;
	vec2 suv = wp.xz / sand_tile_m;
	vec4 sand = texture(tex_sand, suv);
	vec3 sn = texture(tex_sand_normal, suv).rgb;
	vec2 tuv = wp.xz / stone_tile_m;
	vec4 stone = texture(tex_stone, tuv);
	vec3 stn = texture(tex_stone_normal, tuv).rgb;
#if HYMN_QUALITY >= HYMN_QUALITY_MEDIUM
	vec4 det = texture(tex_detail, wp.xz / detail_scale_m);
#else
	vec4 det = vec4(0.5);
#endif
	float big = texture(tex_detail, wp.xz / (detail_scale_m * 40.0)).r;

	// Sand, dry to wet by height above the live water line.
	float above = wp.y - water_height_y;
	float wet = 1.0 - smoothstep(0.0, wet_band_m * (0.7 + 0.6 * big), above);
	float damp = 1.0 - smoothstep(wet_band_m, damp_band_m, above);
	float under = 1.0 - smoothstep(-0.25, 0.0, above);
	vec3 sand_c = mix(sand.rgb, col_sand_dry.rgb * (0.85 + 0.3 * sand.a), sand_tint);
	float macro = texture(tex_detail, wp.xz / sand_macro_scale_m).g * 0.6 + big * 0.4;
	sand_c *= 1.0 + (macro - 0.5) * 2.0 * sand_macro_variation;
	// The wrack line: a ragged band of dried weed and shell grit left by the last high water.
	float wrack_d = abs(wp.y - (tide_line_y + wrack_height_m) + (big - 0.5) * 0.3);
	float wrack = (1.0 - smoothstep(0.0, wrack_width_m, wrack_d)) * smoothstep(0.45, 0.75, det.g * 0.7 + det.b * 0.6);
	sand_c = mix(sand_c, col_wrack.rgb * (0.8 + 0.4 * det.r), wrack * wrack_cover);
	vec3 albedo = mix(sand_c, sand_c * col_sand_wet.rgb / max(col_sand_dry.rgb, vec3(0.05)), max(wet, damp * 0.35));
	albedo = mix(albedo, col_seabed.rgb * (0.85 + 0.2 * sand.a), under);
	float rough = mix(0.92, wet_roughness, wet * (1.0 - under * 0.5));
	vec3 tn = ground_unpack(sn.rg) * vec3(sand_normal_strength, sand_normal_strength, 1.0);

	// Lanes: packed coral gravel and sand, paler and smoother, with stone showing through.
	float lane = clamp(m.r, 0.0, 1.0);
	vec3 lane_c = mix(col_lane.rgb * (0.85 + 0.25 * stone.a), stone.rgb * col_lane.rgb, 0.6);
	albedo = mix(albedo, lane_c, lane);
	tn = mix(tn, ground_unpack(stn.rg) * vec3(0.6, 0.6, 1.0), lane * 0.7);
	rough = mix(rough, 0.85, lane);

	// Turf: sandy soil with sparse grass and litter where the detail noise allows.
	float turf = clamp(m.g, 0.0, 1.0);
	float grass = smoothstep(0.35, 0.75, det.r * 0.7 + big * 0.5) * turf;
	vec3 turf_c = mix(col_turf.rgb * (0.8 + 0.3 * sand.a), col_turf_grass.rgb * (0.7 + 0.5 * det.r), grass);
	float litter = smoothstep(0.55, 0.8, det.b + det.r * 0.3) * litter_cover;
	turf_c = mix(turf_c, col_litter.rgb * (0.8 + 0.4 * sand.a), litter);
	albedo = mix(albedo, turf_c, turf * (1.0 - lane));
	rough = mix(rough, 0.95, turf);

	// Seagrass patches and reef rubble under the lagoon.
	float sg = clamp(m.b, 0.0, 1.0) * smoothstep(0.2, 0.6, det.r * 0.6 + big * 0.6);
	albedo = mix(albedo, col_seagrass.rgb * (0.7 + 0.6 * det.r), sg);
	float rub = clamp(m.a, 0.0, 1.0);
	vec3 rub_c = stone.rgb * col_rubble.rgb / max(vec3(0.6), vec3(0.6));
	float algae = rub * (1.0 - smoothstep(tide_line_y - 0.2, tide_line_y + 0.3, wp.y));
	rub_c = mix(rub_c, col_algae.rgb, algae * smoothstep(0.3, 0.7, det.r));
	albedo = mix(albedo, rub_c, rub);
	tn = mix(tn, ground_unpack(stn.rg) * vec3(1.6, 1.6, 1.0), rub);

	ALBEDO = albedo;
	ROUGHNESS = rough;
	SPECULAR = 0.35 + 0.15 * wet;
	NORMAL_MAP = vec3(tn.xy * 0.5 + 0.5, 1.0);
}

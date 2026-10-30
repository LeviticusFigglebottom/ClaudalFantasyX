// Hymn of the Undertow: stone and timber weathering (M1-ENV-01; SPEC §8.2 item 7; haluna.md §4).
// Included by env_weathering{_low,_medium,,_ultra}.gdshader, which only set HYMN_QUALITY.
//
// One surface shader for every kit material (coral stone, Lit Age coral-concrete, timber, thatch, roof
// tile, lime mortar). It stacks the seven layers of haluna.md §4 in order:
//   1 base (triplanar for stone, mesh UV for boards/thatch/tile)   2 erosion and edge wear (VC.A)
//   3 algae band (height)   4 barnacle crust (height x noise)   5 salt crust (VC.G x spray band)
//   6 moss and lichen (VC.R x up/north-facing x inland height)   7 wetness (VC.B or below the live
//   water height + a capillary band)
// Heights are world Y relative to the tide datum; the wet line follows the live water height. Both come
// from the `hymn_water_level` global (x = water Y now, y = datum), which the zone sea publishes
// (M1-ENV-05; WeatheringTide moves the sea). Below: the old note, with the uniforms now that global.
// Heights are world Y relative to `tide_line_y`; the wet line follows `water_height_y`, which the zone
// writes every time the tide or a flood rig moves (WeatheringTide), so the wet line responds live.
//
// Mesh channels (art README convention 3; kit generators in assets_src/environments/kits/):
//   COLOR.r moss, COLOR.g salt, COLOR.b wet, COLOR.a erosion; UV2.x baked occlusion, UV2.y variation.
// Textures (assets/environments/kits/haluna/textures/, kit_textures.py):
//   tex_albedo  sRGB albedo, A = height        tex_normal  RG = normal XY (+Y up), B = cavity
//   tex_detail  linear: R moss clumps, G salt crystals, B lichen spots, A barnacle cells
//
// Tiers (README "Quality tiers"; costs in docs/kb/art/environments/haluna_mood_review.md):
//   LOW     mesh-UV base (no triplanar), one top-down detail sample, no barnacle relief
//   MEDIUM  triplanar base, one detail sample on the dominant axis, no barnacle relief
//   HIGH    triplanar base and detail, barnacle relief (screen-space bump)
//   ULTRA   HIGH + a macro detail octave (large-scale breakup of moss, salt and algae) and
//           height-sharpened layer edges

#ifndef HYMN_ENV_WEATHERING_BODY_GDSHADERINC
#define HYMN_ENV_WEATHERING_BODY_GDSHADERINC

#include "res://game/shaders/include/common.gdshaderinc"
#include "res://game/shaders/include/globals.gdshaderinc"

// Macro detail octave scale relative to detail_scale_m (Ultra only), and the width of a layer's
// soft edge before height sharpening, in mask units. Tuned on the haluna_mood shots.
#define HYMN_WEATHER_MACRO_SCALE 0.23
#define HYMN_WEATHER_EDGE 0.12

group_uniforms base;
uniform sampler2D tex_albedo : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D tex_normal : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform vec4 col_tint : source_color = vec4(1.0);
// Metres covered by one texture repeat (kit_textures.TILE_M).
uniform vec2 tile_m = vec2(1.2, 1.2);
// Stone: triplanar in world space. Boards, thatch and roof tile: mesh UV (in metres) / tile_m.
uniform bool base_triplanar = true;
uniform float triplanar_sharpness : hint_range(1.0, 16.0) = 4.0;
uniform float normal_strength : hint_range(0.0, 3.0) = 1.0;
uniform float roughness_base : hint_range(0.0, 1.0) = 0.85;
uniform float specular_base : hint_range(0.0, 1.0) = 0.4;
// UV2.y (per block / plank / shell) shifts value and warmth so repeated pieces never match.
uniform float variation_value : hint_range(0.0, 0.5) = 0.12;
uniform float variation_warmth : hint_range(0.0, 0.5) = 0.06;
uniform float ao_strength : hint_range(0.0, 1.0) = 0.8;
uniform float cavity_darken : hint_range(0.0, 1.0) = 0.35;
// Lime wash / mortar / paint over the base: covers the albedo with col_paint (the base relief still
// shows through the normal and a little through value), thinning in cavities and on worn edges.
uniform vec4 col_paint : source_color = vec4(0.902, 0.882, 0.839, 1.0); // mortar_white #E6E1D6
uniform float paint_cover : hint_range(0.0, 1.0) = 0.0;
group_uniforms;

group_uniforms erosion;
// haluna.md §4 layer 2: lighten convex edges by 8 %, open pits.
uniform float erosion_lighten : hint_range(0.0, 0.5) = 0.08;
uniform float erosion_pit_darken : hint_range(0.0, 1.0) = 0.3;
uniform float erosion_roughness : hint_range(0.0, 1.0) = 0.1;
group_uniforms;

group_uniforms tide;
// Tide datum (haluna.md §0) and live surface height: hymn_water_level.y and .x (globals.gdshaderinc).
uniform float capillary_band_m : hint_range(0.0, 2.0) = 0.25;
group_uniforms;

group_uniforms detail;
uniform sampler2D tex_detail : hint_default_black, filter_linear_mipmap, repeat_enable;
uniform float detail_scale_m : hint_range(0.05, 4.0) = 0.5;
group_uniforms;

group_uniforms algae;
uniform bool use_algae = true;
uniform vec4 col_algae : source_color = vec4(0.290, 0.353, 0.180, 1.0); // #4A5A2E
uniform vec2 algae_band_m = vec2(-0.4, 0.1); // relative to tide_line_y
uniform vec2 algae_coverage = vec2(0.4, 0.8);
uniform float algae_roughness : hint_range(0.0, 1.0) = 0.3;
group_uniforms;

group_uniforms barnacle;
uniform bool use_barnacles = true;
uniform vec4 col_barnacle : source_color = vec4(0.902, 0.855, 0.753, 1.0); // bone #E6DAC0
uniform vec2 barnacle_band_m = vec2(-0.6, 0.3);
uniform float barnacle_coverage : hint_range(0.0, 1.0) = 0.55;
uniform float barnacle_bump : hint_range(0.0, 4.0) = 1.2;
group_uniforms;

group_uniforms salt;
uniform bool use_salt = true;
uniform vec4 col_salt : source_color = vec4(0.910, 0.894, 0.847, 1.0); // #E8E4D8
uniform vec2 salt_band_m = vec2(0.1, 2.0);
uniform vec2 salt_coverage = vec2(0.3, 0.6);
uniform float salt_roughness : hint_range(0.0, 1.0) = 0.85;
uniform float salt_cavity_gather : hint_range(0.0, 2.0) = 0.9;
group_uniforms;

group_uniforms moss;
uniform bool use_moss = true;
// palm_green #3E7A3A darkened 30 %.
uniform vec4 col_moss : source_color = vec4(0.208, 0.388, 0.196, 1.0);
uniform vec4 col_lichen : source_color = vec4(0.753, 0.541, 0.227, 1.0); // #C08A3A
uniform float moss_min_height_m = 1.5;
uniform float moss_normal_y : hint_range(0.0, 1.0) = 0.6;
uniform float moss_north_facing : hint_range(0.0, 1.0) = 0.5;
uniform float lichen_coverage : hint_range(0.0, 1.0) = 0.1;
// Fraction of the allowed area (VC.R x facing x inland) that actually carries moss.
uniform float moss_coverage : hint_range(0.0, 1.0) = 0.6;
uniform float moss_roughness : hint_range(0.0, 1.0) = 0.95;
group_uniforms;

group_uniforms wet;
uniform float wet_darken : hint_range(0.0, 1.0) = 0.55; // albedo x 0.55 when soaked
uniform float wet_roughness : hint_range(0.0, 1.0) = 0.12;
uniform float wet_flatten : hint_range(0.0, 1.0) = 0.6; // puddle normal flatten
// The Prologue dressing pass (env-art): 1 reads painted VC.B above the live water as dry grime (rain streaks, an old
// tide mark), darkening toward col_grime without the wet gloss, which mirrored the bright dusk sky and hid the stains
// on Iskarra's towers. 0 (the default) leaves every other material as it was.
uniform float grime_from_wet : hint_range(0.0, 1.0) = 0.0;
uniform vec4 col_grime : source_color = vec4(0.369, 0.353, 0.298, 1.0); // #5E5A4C
group_uniforms;

group_uniforms debug;
// 0 = shaded, 1 = vertex colours (R moss G salt B wet), 2 = layer masks (R salt G algae+moss B wet).
uniform int debug_view : hint_range(0, 2) = 0;
group_uniforms;

varying vec3 v_world_pos;
varying vec3 v_world_normal;

void vertex() {
	v_world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	v_world_normal = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

vec3 hymn_weather_unpack(vec2 rg) {
	vec2 xy = rg * 2.0 - 1.0;
	return vec3(xy, sqrt(max(0.0, 1.0 - dot(xy, xy))));
}

vec3 hymn_weather_tri_weights(vec3 n, float sharpness) {
	vec3 w = pow(abs(n), vec3(sharpness));
	return w / max(w.x + w.y + w.z, HYMN_EPSILON);
}

// Soft band mask between lo and hi with an edge of `soft` metres.
float hymn_weather_band(float y, vec2 band, float soft) {
	return smoothstep(band.x - soft, band.x, y) * (1.0 - smoothstep(band.y, band.y + soft, y));
}

// Coverage threshold: `noise` in [0, 1] covers `coverage` of the area with a soft edge.
float hymn_weather_cover(float noise, float coverage, float edge) {
	return smoothstep(1.0 - coverage - edge, 1.0 - coverage + edge, noise);
}

void fragment() {
	float tide_line_y = hymn_water_level.y;
	float water_height_y = hymn_water_level.x;
	vec3 wp = v_world_pos;
	vec3 wn_geo = normalize((INV_VIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
	vec4 vc = COLOR;
	float ao_baked = UV2.x;
	float variation = UV2.y;

	// ---- 1. Base -----------------------------------------------------------------------------
	vec4 base_a;
	vec3 base_n_tex; // r, g, cavity
	vec3 wn;
#if HYMN_QUALITY >= HYMN_QUALITY_MEDIUM
	if (base_triplanar) {
		vec3 w = hymn_weather_tri_weights(wn_geo, triplanar_sharpness);
		vec2 uv_x = wp.zy / tile_m;
		vec2 uv_y = wp.xz / tile_m;
		vec2 uv_z = wp.xy / tile_m;
		base_a = texture(tex_albedo, uv_x) * w.x + texture(tex_albedo, uv_y) * w.y + texture(tex_albedo, uv_z) * w.z;
		vec3 nt_x = texture(tex_normal, uv_x).rgb;
		vec3 nt_y = texture(tex_normal, uv_y).rgb;
		vec3 nt_z = texture(tex_normal, uv_z).rgb;
		base_n_tex = nt_x * w.x + nt_y * w.y + nt_z * w.z;
		// UDN triplanar normal blend (tangent XY swizzled onto each projection axis).
		vec3 tx = hymn_weather_unpack(nt_x.rg) * vec3(normal_strength, normal_strength, 1.0);
		vec3 ty = hymn_weather_unpack(nt_y.rg) * vec3(normal_strength, normal_strength, 1.0);
		vec3 tz = hymn_weather_unpack(nt_z.rg) * vec3(normal_strength, normal_strength, 1.0);
		vec3 s = sign(wn_geo);
		vec3 dn = vec3(0.0, tx.y, tx.x * s.x) * w.x + vec3(ty.x, 0.0, ty.y * s.y) * w.y
				+ vec3(tz.x * s.z, tz.y, 0.0) * w.z;
		wn = normalize(wn_geo + dn);
	} else
#endif
	{
		vec2 uv = UV / tile_m;
		base_a = texture(tex_albedo, uv);
		base_n_tex = texture(tex_normal, uv).rgb;
		vec3 t = hymn_weather_unpack(base_n_tex.rg);
		t.xy *= normal_strength;
		vec3 nv = normalize(TANGENT * t.x + BINORMAL * t.y + NORMAL * t.z);
		wn = normalize((INV_VIEW_MATRIX * vec4(nv, 0.0)).xyz);
	}
	float height = base_a.a;
	float cavity = base_n_tex.b;
	vec3 albedo = base_a.rgb * col_tint.rgb;
	albedo *= 1.0 + (variation - 0.5) * 2.0 * variation_value;
	albedo *= mix(vec3(1.0), vec3(1.0 + variation_warmth, 1.0, 1.0 - variation_warmth), variation);
	float paint = paint_cover * (1.0 - 0.6 * cavity) * (1.0 - 0.5 * vc.a * (1.0 - height));
	albedo = mix(albedo, col_paint.rgb * (0.9 + 0.1 * height), paint);
	albedo *= 1.0 - cavity_darken * cavity;
	float rough = roughness_base;
	float spec = specular_base;

	// ---- Detail masks (shared by layers 3-6) ---------------------------------------------------
	vec4 det;
#if HYMN_QUALITY >= HYMN_QUALITY_HIGH
	{
		vec3 w = hymn_weather_tri_weights(wn_geo, triplanar_sharpness);
		det = texture(tex_detail, wp.zy / detail_scale_m) * w.x + texture(tex_detail, wp.xz / detail_scale_m) * w.y
				+ texture(tex_detail, wp.xy / detail_scale_m) * w.z;
	}
#elif HYMN_QUALITY >= HYMN_QUALITY_MEDIUM
	{
		vec3 a = abs(wn_geo);
		vec2 duv = a.y > max(a.x, a.z) ? wp.xz : (a.x > a.z ? wp.zy : wp.xy);
		det = texture(tex_detail, duv / detail_scale_m);
	}
#else
	det = texture(tex_detail, wp.xz / detail_scale_m + wp.y * 0.37);
#endif
#if HYMN_QUALITY >= HYMN_QUALITY_ULTRA
	vec4 macro = texture(tex_detail, wp.xz / (detail_scale_m / HYMN_WEATHER_MACRO_SCALE));
	det.rgb = mix(det.rgb, det.rgb * (0.4 + 1.2 * macro.r), 0.6);
	float edge = HYMN_WEATHER_EDGE * 0.5;
#else
	float edge = HYMN_WEATHER_EDGE;
#endif
	float rel = wp.y - tide_line_y;

	// ---- 2. Erosion and edge wear (VC.A) -------------------------------------------------------
	float ero = vc.a;
	albedo *= 1.0 + erosion_lighten * ero * height;
	albedo *= 1.0 - erosion_pit_darken * ero * cavity;
	rough = min(1.0, rough + erosion_roughness * ero);

	// ---- 3. Algae band (height) ----------------------------------------------------------------
	float algae = 0.0;
	if (use_algae) {
		float band = hymn_weather_band(rel, algae_band_m, 0.15);
		float cov = mix(algae_coverage.x, algae_coverage.y, det.r);
		algae = band * hymn_weather_cover(det.r * 0.6 + (1.0 - height) * 0.4, cov, edge);
		albedo = mix(albedo, col_algae.rgb * (0.8 + 0.4 * height), algae);
		rough = mix(rough, algae_roughness, algae);
		spec = mix(spec, 0.5, algae);
	}

	// ---- 4. Barnacle and limpet crust (height x noise) -----------------------------------------
	float barn = 0.0;
	if (use_barnacles) {
		float band = hymn_weather_band(rel, barnacle_band_m, 0.2);
		barn = band * hymn_weather_cover(det.a, barnacle_coverage, edge) * (1.0 - algae * 0.5);
		albedo = mix(albedo, col_barnacle.rgb * (0.7 + 0.3 * det.a), barn * 0.6);
#if HYMN_QUALITY >= HYMN_QUALITY_HIGH
		// Screen-space bump from the barnacle cell height (Mikkelsen 2010, "Bump Mapping
		// Unparametrized Surfaces on the GPU").
		float bh = det.a * barn * barnacle_bump * 0.02;
		vec3 dpdx = dFdx(wp);
		vec3 dpdy = dFdy(wp);
		vec3 r1 = cross(dpdy, wn);
		vec3 r2 = cross(wn, dpdx);
		float detm = dot(dpdx, r1);
		vec3 grad = sign(detm) * (dFdx(bh) * r1 + dFdy(bh) * r2);
		wn = normalize(abs(detm) * wn - grad);
#endif
	}

	// ---- 5. Salt crust (VC.G x spray band, gathered in cavities) --------------------------------
	float salt = 0.0;
	if (use_salt) {
		float band = hymn_weather_band(rel, salt_band_m, 0.3);
		float cov = mix(salt_coverage.x, salt_coverage.y, vc.g);
		float gather = det.g * 0.6 + cavity * salt_cavity_gather * 0.6 + (1.0 - height) * 0.2;
		salt = vc.g * band * hymn_weather_cover(clamp(gather, 0.0, 1.0), cov, edge);
		albedo = mix(albedo, col_salt.rgb, salt);
		rough = mix(rough, salt_roughness, salt);
	}

	// ---- 6. Moss and lichen (VC.R x up- or north-facing x inland height) -----------------------
	if (use_moss) {
		float facing = max(smoothstep(moss_normal_y - 0.15, moss_normal_y + 0.1, wn.y),
				moss_north_facing * smoothstep(0.2, 0.7, -wn.z));
		float inland = smoothstep(moss_min_height_m - 0.3, moss_min_height_m + 0.3, rel);
		float m = vc.r * facing * inland;
		float moss = m * hymn_weather_cover(det.r * 0.7 + cavity * 0.3, clamp(m * moss_coverage, 0.0, 1.0), edge);
		albedo = mix(albedo, col_moss.rgb * (0.75 + 0.5 * det.r), moss);
		rough = mix(rough, moss_roughness, moss);
		// Lichen spots on sun (south-facing, +Z) sides, ~10 % coverage.
		float sun_side = smoothstep(0.0, 0.5, wn.z) * inland * vc.r;
		float lichen = sun_side * hymn_weather_cover(det.b, lichen_coverage, 0.05);
		albedo = mix(albedo, col_lichen.rgb, lichen * 0.8);
		algae = max(algae, moss);
	}

	// ---- 7. Wetness (VC.B, or under the live water height + capillary band) --------------------
	float wobble = (det.r - 0.5) * capillary_band_m * 0.6;
	float tide_wet = 1.0 - smoothstep(water_height_y, water_height_y + capillary_band_m + wobble, wp.y);
	float grime = vc.b * grime_from_wet * (1.0 - tide_wet);
	albedo *= mix(vec3(1.0), col_grime.rgb, grime);
	float wet = clamp(max(vc.b * (1.0 - grime_from_wet), tide_wet), 0.0, 1.0);
	// Porous stone darkens most where it is rough and open (cavities soak first).
	albedo *= mix(1.0, wet_darken * (1.0 - 0.25 * cavity), wet * (1.0 - salt * 0.5));
	rough = mix(rough, wet_roughness, wet * (1.0 - cavity * 0.5));
	spec = mix(spec, 0.5, wet);
	wn = normalize(mix(wn, wn_geo, wet * wet_flatten));

	// ---- Output ------------------------------------------------------------------------------
	float ao = mix(1.0, ao_baked, ao_strength);
	if (debug_view == 1) {
		albedo = vc.rgb;
	} else if (debug_view == 2) {
		albedo = vec3(salt, algae, wet);
	}
	ALBEDO = albedo * mix(1.0, ao, 0.35);
	AO = ao;
	ROUGHNESS = rough;
	SPECULAR = spec;
	NORMAL = normalize((VIEW_MATRIX * vec4(wn, 0.0)).xyz);
}

#endif

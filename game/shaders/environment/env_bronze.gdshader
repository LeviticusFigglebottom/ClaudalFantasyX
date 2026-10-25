// Hymn of the Undertow: weathered Lit Age bronze (M3-ENV-01; tamsule_bell.md §2-3).
// The Tamsule Bell's metal. It reads the kit weathering channels (haluna.md §4) as bronze phenomena:
//   COLOR.g salt   -> verdigris and salt bloom (gathered in cavities, under ledges, on shaded sides)
//   COLOR.a erosion -> worn bright bronze (proud edges, the lip, rope-worn loops): patina rubbed away
//   COLOR.b wet    -> spray streaks (darker, glossier), COLOR.r moss -> grime on undersides
//   UV2.x baked occlusion, UV2.y per-element variation.
// A world-space vertical streak term (the detail map's clump channel stretched along Y) draws verdigris
// runs down the metal: rain and spray carry the copper salts downwards. Detail and pitting come from the shared Haluna kit
// textures (weathering_detail.png: G salt crystals, R clumps; coral_concrete_normal.png: casting pits),
// sampled triplanar in world space, so the kit needs no UVs on the bell.
shader_type spatial;
render_mode cull_back;

#include "res://game/shaders/include/common.gdshaderinc"

group_uniforms base;
uniform vec4 col_bronze : source_color = vec4(0.478, 0.361, 0.220, 1.0); // brass #B08D57 darkened
uniform vec4 col_worn : source_color = vec4(0.690, 0.553, 0.341, 1.0); // brass #B08D57
uniform float metallic_bronze : hint_range(0.0, 1.0) = 0.9;
uniform float roughness_bronze : hint_range(0.0, 1.0) = 0.42;
uniform float roughness_worn : hint_range(0.0, 1.0) = 0.3;
uniform float variation_value : hint_range(0.0, 0.5) = 0.08;
uniform float ao_strength : hint_range(0.0, 1.0) = 0.8;
group_uniforms;

group_uniforms patina;
uniform vec4 col_patina : source_color = vec4(0.373, 0.541, 0.471, 1.0); // bronze_patina #5F8A78
uniform vec4 col_patina_pale : source_color = vec4(0.553, 0.702, 0.635, 1.0); // bloom #8DB3A2
// Coverage of verdigris at VC.G = 0 and 1 (fraction of the area).
uniform vec2 patina_coverage = vec2(0.25, 0.8);
uniform float patina_roughness : hint_range(0.0, 1.0) = 0.85;
// Extra coverage on downward- and north-facing surfaces (out of the sun and the rain-wash).
uniform float patina_shade_bias : hint_range(0.0, 1.0) = 0.25;
// Vertical streaks: period across (m) and along Y (m), and their strength.
uniform vec2 streak_period_m = vec2(0.45, 6.0);
uniform float streak_strength : hint_range(0.0, 1.0) = 0.5;
group_uniforms;

group_uniforms detail;
uniform sampler2D tex_detail : hint_default_black, filter_linear_mipmap, repeat_enable;
uniform sampler2D tex_normal : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform float detail_scale_m : hint_range(0.05, 8.0) = 1.4;
uniform float normal_tile_m : hint_range(0.1, 8.0) = 2.5;
uniform float normal_strength : hint_range(0.0, 3.0) = 0.6;
uniform float triplanar_sharpness : hint_range(1.0, 16.0) = 4.0;
group_uniforms;

group_uniforms wear;
uniform float wear_strength : hint_range(0.0, 1.0) = 0.9;
uniform float wet_darken : hint_range(0.0, 1.0) = 0.6;
uniform float wet_roughness : hint_range(0.0, 1.0) = 0.15;
uniform vec4 col_grime : source_color = vec4(0.153, 0.157, 0.133, 1.0);
group_uniforms;

varying vec3 v_world_pos;
varying vec3 v_world_normal;

void vertex() {
	v_world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	v_world_normal = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

vec3 bronze_unpack(vec2 rg) {
	vec2 xy = rg * 2.0 - 1.0;
	return vec3(xy, sqrt(max(0.0, 1.0 - dot(xy, xy))));
}

vec3 bronze_tri_weights(vec3 n, float sharpness) {
	vec3 w = pow(abs(n), vec3(sharpness));
	return w / max(w.x + w.y + w.z, HYMN_EPSILON);
}

float bronze_cover(float noise, float coverage, float edge) {
	return smoothstep(1.0 - coverage - edge, 1.0 - coverage + edge, noise);
}

void fragment() {
	vec3 wp = v_world_pos;
	vec3 wn_geo = normalize((INV_VIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
	vec4 vc = COLOR;
	float ao_baked = UV2.x;
	float variation = UV2.y;
	vec3 w = bronze_tri_weights(wn_geo, triplanar_sharpness);

	// Casting pits: UDN triplanar normal from the coral-concrete map (B = cavity).
	vec3 nt_x = texture(tex_normal, wp.zy / normal_tile_m).rgb;
	vec3 nt_y = texture(tex_normal, wp.xz / normal_tile_m).rgb;
	vec3 nt_z = texture(tex_normal, wp.xy / normal_tile_m).rgb;
	float cavity = nt_x.b * w.x + nt_y.b * w.y + nt_z.b * w.z;
	vec3 tx = bronze_unpack(nt_x.rg) * vec3(normal_strength, normal_strength, 1.0);
	vec3 ty = bronze_unpack(nt_y.rg) * vec3(normal_strength, normal_strength, 1.0);
	vec3 tz = bronze_unpack(nt_z.rg) * vec3(normal_strength, normal_strength, 1.0);
	vec3 s = sign(wn_geo);
	vec3 dn = vec3(0.0, tx.y, tx.x * s.x) * w.x + vec3(ty.x, 0.0, ty.y * s.y) * w.y + vec3(tz.x * s.z, tz.y, 0.0) * w.z;
	vec3 wn = normalize(wn_geo + dn);

	vec4 det = texture(tex_detail, wp.zy / detail_scale_m) * w.x + texture(tex_detail, wp.xz / detail_scale_m) * w.y
			+ texture(tex_detail, wp.xy / detail_scale_m) * w.z;
	// Streaks: the detail map stretched along Y (horizontal projections only), so runs hang down.
	vec2 sx = vec2(wp.z / streak_period_m.x, wp.y / streak_period_m.y);
	vec2 sz = vec2(wp.x / streak_period_m.x, wp.y / streak_period_m.y);
	float streak = texture(tex_detail, sx).r * w.x + texture(tex_detail, sz).r * w.z + det.r * w.y;

	// Base metal, varied per element.
	vec3 albedo = col_bronze.rgb * (1.0 + (variation - 0.5) * 2.0 * variation_value);
	float metal = metallic_bronze;
	float rough = roughness_bronze;

	// Verdigris (VC.G), more in shade and cavities, broken by crystals and streaks.
	float shade = clamp(max(-wn_geo.y, 0.0) + smoothstep(0.1, 0.8, -wn_geo.z) * 0.6, 0.0, 1.0);
	float cov = mix(patina_coverage.x, patina_coverage.y, vc.g) + patina_shade_bias * shade;
	// The detail map's channels are sparse (R clumps mean ~0.3, G crystals ~0.2, cavity ~0.1), so the
	// gather is a weighted sum scaled to spread over [0, 1]: clumps and streaks set the broad pattern.
	float gather = det.r * 0.9 + det.g * 0.5 + cavity * 1.5 + streak * streak_strength * 0.7 + (1.0 - ao_baked) * 0.4;
	float patina = bronze_cover(clamp(gather, 0.0, 1.0), clamp(cov, 0.0, 1.0), 0.12);
	// Worn bronze (VC.A) rubs the patina away on proud edges.
	float worn = clamp(vc.a * wear_strength * (1.0 - cavity * 0.7), 0.0, 1.0);
	patina *= 1.0 - smoothstep(0.45, 0.85, worn);
	vec3 pcol = mix(col_patina.rgb, col_patina_pale.rgb, clamp(det.g * 0.8 + cavity * 0.4, 0.0, 1.0));
	albedo = mix(albedo, col_worn.rgb, smoothstep(0.45, 0.9, worn) * (1.0 - patina));
	rough = mix(rough, roughness_worn, smoothstep(0.45, 0.9, worn));
	albedo = mix(albedo, pcol, patina);
	metal = mix(metal, 0.0, patina);
	rough = mix(rough, patina_roughness, patina);

	// Grime (VC.R) on undersides, wet spray streaks (VC.B).
	float grime = vc.r * (0.5 + 0.5 * det.r);
	albedo = mix(albedo, col_grime.rgb, grime * 0.7);
	float wet = clamp(vc.b * (0.6 + 0.6 * streak), 0.0, 1.0);
	albedo *= mix(1.0, wet_darken, wet * patina);
	rough = mix(rough, wet_roughness, wet);

	float ao = mix(1.0, ao_baked, ao_strength);
	ALBEDO = albedo * mix(1.0, ao, 0.35);
	AO = ao;
	METALLIC = metal;
	ROUGHNESS = rough;
	NORMAL = normalize((VIEW_MATRIX * vec4(wn, 0.0)).xyz);
}

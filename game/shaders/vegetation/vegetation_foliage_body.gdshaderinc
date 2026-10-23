// Hymn of the Undertow: foliage surface body (M1-ENV-02). Included by vegetation_foliage.gdshader
// (default = High tier) and vegetation_foliage_low.gdshader. Two-sided alpha-scissor cards with
// translucency (custom light(), see below), per-element tint variation, baked crown occlusion and wind.
// Textures (assets/environments/vegetation/, made by assets_src/environments/vegetation/textures.py):
//   tex_albedo        sRGB albedo, A = cut-out mask
//   tex_normal_trans  RG = tangent-space normal XY (Z is rebuilt), B = translucency/thinness mask
// Mesh channels: COLOR = wind weights (vegetation_wind.gdshaderinc); UV2.x = occlusion, UV2.y = tint.
// Alpha: alpha scissor, made temporally smooth by TAA (project default). A coverage boost per mip
// level stops distant cards thinning out (mipmapped alpha loses coverage). Alpha-to-coverage needs
// MSAA, which no preset enables, so it is not used (docs/kb/art/environments/vegetation.md).

#ifndef HYMN_VEGETATION_FOLIAGE_BODY_GDSHADERINC
#define HYMN_VEGETATION_FOLIAGE_BODY_GDSHADERINC

#include "res://game/shaders/vegetation/vegetation_wind.gdshaderinc"

group_uniforms surface;
uniform sampler2D tex_albedo : source_color, filter_linear_mipmap_anisotropic, repeat_disable;
uniform sampler2D tex_normal_trans : hint_default_black, filter_linear_mipmap_anisotropic, repeat_disable;
uniform vec4 col_tint : source_color = vec4(1.0);
// Per-element variation pulls the albedo towards this colour by up to tint_variation (UV2.y).
uniform vec4 col_tint_variation : source_color = vec4(0.86, 0.9, 0.62, 1.0);
uniform float tint_variation : hint_range(0.0, 1.0) = 0.35;
uniform float underside_lighten : hint_range(0.0, 1.0) = 0.25; // undersides read paler and greyer
uniform float alpha_cutoff : hint_range(0.0, 1.0) = 0.5;
uniform float mip_coverage_boost : hint_range(0.0, 1.0) = 0.35;
uniform float normal_strength : hint_range(0.0, 2.0) = 1.0;
uniform float roughness_value : hint_range(0.0, 1.0) = 0.55;
uniform float specular_value : hint_range(0.0, 1.0) = 0.45;
uniform float ao_strength : hint_range(0.0, 1.0) = 0.85;
uniform float ao_in_albedo : hint_range(0.0, 1.0) = 0.5; // occlusion also darkens direct light
group_uniforms;

group_uniforms lighting;
// Soft foliage diffuse: energy-conserving wrap (0 = Lambert). Cards are thin, so light "wraps".
uniform float diffuse_wrap : hint_range(0.0, 1.0) = 0.3;
group_uniforms;

group_uniforms translucency;
// Transmission tint for saturated (green) texels; pale texels (petals) transmit near-white light.
uniform vec4 col_translucency : source_color = vec4(0.78, 0.92, 0.36, 1.0);
uniform float translucency : hint_range(0.0, 4.0) = 1.0;
// Light still reaching a leaf through the leaves above it, where the shadow map says "occluded".
uniform float translucency_shadow_floor : hint_range(0.0, 1.0) = 0.35;
// 1 where the plant's occluder is a solid (an eave, a wall) rather than its own leaves: the floor is
// off there, so a plant under a roof no longer glows (M1-ENV-03). Set per instance by VegetationPlant
// (a ray toward the sun at placement) or by hand.
instance uniform float inst_translucency_shelter : hint_range(0.0, 1.0) = 0.0;
// Exponent of the forward-scattering lobe: the glow when looking towards the sun through leaves.
uniform float translucency_focus : hint_range(1.0, 32.0) = 6.0;
uniform float translucency_forward : hint_range(0.0, 4.0) = 1.4;
group_uniforms;

// GGX specular constants (Walter et al. 2007; Schlick 1994). F0 of a dielectric leaf cuticle
// = 0.08 * specular_value, the same mapping Godot uses for SPECULAR (0.5 -> 4%).
#define HYMN_VEG_F0_SCALE 0.08

void vertex() {
	vec3 origin = MODEL_MATRIX[3].xyz;
	float scale_y = length(MODEL_MATRIX[1].xyz);
	VERTEX = hymn_veg_wind_displace(VERTEX, NORMAL, COLOR, origin, scale_y);
}

float hymn_veg_mip_level(vec2 uv, vec2 size) {
	vec2 dx = dFdx(uv * size);
	vec2 dy = dFdy(uv * size);
	return max(0.0, 0.5 * log2(max(dot(dx, dx), dot(dy, dy))));
}

void fragment() {
	vec4 albedo_a = texture(tex_albedo, UV);
	vec3 nt = texture(tex_normal_trans, UV).rgb;
	vec3 tint = mix(col_tint.rgb, col_tint.rgb * col_tint_variation.rgb, UV2.y * tint_variation);
	vec3 albedo = albedo_a.rgb * tint;
	if (!FRONT_FACING) {
		albedo = mix(albedo, vec3(hymn_luminance(albedo)) * 1.15, underside_lighten);
	}
	float ao = mix(1.0, UV2.x, ao_strength);
	ALBEDO = albedo * mix(1.0, ao, ao_in_albedo);
	AO = ao;
	float mip = hymn_veg_mip_level(UV, vec2(textureSize(tex_albedo, 0)));
	ALPHA = albedo_a.a * (1.0 + mip * mip_coverage_boost);
	ALPHA_SCISSOR_THRESHOLD = alpha_cutoff;
	NORMAL_MAP = vec3(nt.rg, 1.0);
	NORMAL_MAP_DEPTH = normal_strength;
	ROUGHNESS = roughness_value;
	SPECULAR = specular_value;
#if HYMN_QUALITY > HYMN_QUALITY_LOW
	// BACKLIGHT carries the transmission tint x mask into light() (Godot passes it through).
	float hi = max(albedo.r, max(albedo.g, albedo.b));
	float chroma = (hi - min(albedo.r, min(albedo.g, albedo.b))) / max(hi, HYMN_EPSILON);
	BACKLIGHT = mix(vec3(1.0), col_translucency.rgb, chroma) * (translucency * nt.b * mix(1.0, ao, 0.5));
#endif
}

// Custom lighting: wrapped diffuse + GGX specular for the direct lights, plus (above Low) a
// transmission term. Godot's built-in BACKLIGHT is multiplied by the full shadow attenuation, which
// kills the glow of any leaf under another leaf; here a floor lets some light through the canopy.
// Ambient and reflections still come from Godot (they use ALBEDO/ROUGHNESS/SPECULAR/AO).
// NORMAL already faces the viewer on back faces; DIFFUSE_LIGHT is multiplied by ALBEDO afterwards.
void light() {
	float ndl = dot(NORMAL, LIGHT);
	float w = diffuse_wrap;
	float diff = max(0.0, (ndl + w) / ((1.0 + w) * (1.0 + w)));
	DIFFUSE_LIGHT += LIGHT_COLOR * (diff / HYMN_PI) * ATTENUATION;

	vec3 h = normalize(VIEW + LIGHT);
	float cndl = max(ndl, 0.0);
	float ndv = max(dot(NORMAL, VIEW), 1e-4);
	float ndh = clamp(dot(NORMAL, h), 0.0, 1.0);
	float a = max(ROUGHNESS * ROUGHNESS, 1e-3);
	float a2 = a * a;
	float dd = ndh * ndh * (a2 - 1.0) + 1.0;
	float d = a2 / (HYMN_PI * dd * dd);
	float vis = 0.5 / max(cndl * sqrt(ndv * ndv * (1.0 - a2) + a2) + ndv * sqrt(cndl * cndl * (1.0 - a2) + a2), 1e-4);
	float f0 = HYMN_VEG_F0_SCALE * specular_value;
	float f = f0 + (1.0 - f0) * pow(1.0 - clamp(dot(LIGHT, h), 0.0, 1.0), 5.0);
	SPECULAR_LIGHT += LIGHT_COLOR * (d * vis * f * cndl * ATTENUATION * SPECULAR_AMOUNT);

#if HYMN_QUALITY > HYMN_QUALITY_LOW
	float back = max(0.0, -ndl);
	float fwd = pow(clamp(dot(-VIEW, LIGHT), 0.0, 1.0), translucency_focus);
	float through = mix(translucency_shadow_floor * (1.0 - inst_translucency_shelter), 1.0, ATTENUATION);
	DIFFUSE_LIGHT += LIGHT_COLOR * BACKLIGHT * ((back + fwd * translucency_forward) / HYMN_PI) * through;
#endif
}

#endif

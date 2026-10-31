shader_type spatial;
// Battle creatures (M2-CRE-02, docs/kb/art/creatures/pipeline.md "Materials"). The creature GLBs carry their
// colour in vertex data (assets_src/creatures/common/creature_kit.py):
//   COLOR.rgb  albedo (sRGB palette colour)     COLOR.a  wetness (0 dry .. 1 wet)
//   UV         a rest-pose detail coordinate (metres), the domain of the detail noise
//   UV2.x      cavity (0 open .. 1 deep)        UV2.y    emission mask (the spawn_wound weak points)
// One shader for every creature surface; the material sets the surface family (stone, chitin, bronze, lacquer).
render_mode blend_mix, depth_draw_opaque, cull_back, diffuse_burley, specular_schlick_ggx;

uniform vec3 tint : source_color = vec3(1.0);
uniform float roughness_dry : hint_range(0.0, 1.0) = 0.8;
uniform float roughness_wet : hint_range(0.0, 1.0) = 0.25;
uniform float metallic : hint_range(0.0, 1.0) = 0.0;
uniform float specular : hint_range(0.0, 1.0) = 0.5;
// Albedo multiplier at full wetness (the kit's wet rule, haluna.md layer 7: x0.55).
uniform float wet_darken : hint_range(0.0, 1.0) = 0.7;
uniform float clearcoat_wet : hint_range(0.0, 1.0) = 0.5;
uniform float detail_scale = 14.0;
uniform float detail_albedo : hint_range(0.0, 1.0) = 0.12;
uniform float detail_bump : hint_range(0.0, 2.0) = 0.35;
uniform float cavity_albedo : hint_range(0.0, 1.0) = 0.45;
uniform float cavity_ao : hint_range(0.0, 1.0) = 0.7;
uniform vec3 emission_color : source_color = vec3(0.247, 0.878, 0.784);
uniform float emission_energy = 1.6;
// A slow breathing of the wounds (Hz; 0 = steady).
uniform float emission_pulse_hz = 0.0;
uniform float emission_pulse_depth : hint_range(0.0, 1.0) = 0.0;
// A thin back-lit sheen on a translucent edge (fins, frills): 0 = none.
uniform float rim_sheen : hint_range(0.0, 1.0) = 0.0;
// Row 61 (creatures-b): a dark body's rim reads dark on dark, since the sheen is its own albedo. rim_tint mixes
// the sheen toward rim_color (0, the default, leaves every material as it was).
uniform vec3 rim_color : source_color = vec3(1.0);
uniform float rim_tint : hint_range(0.0, 1.0) = 0.0;

float hash2(vec2 p) {
	p = fract(p * vec2(123.34, 456.21));
	p += dot(p, p + 45.32);
	return fract(p.x * p.y);
}

float vnoise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	float a = hash2(i);
	float b = hash2(i + vec2(1.0, 0.0));
	float c = hash2(i + vec2(0.0, 1.0));
	float d = hash2(i + vec2(1.0, 1.0));
	return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

float detail(vec2 p) {
	return vnoise(p) * 0.6 + vnoise(p * 2.07 + 13.1) * 0.3 + vnoise(p * 4.13 + 7.7) * 0.1;
}

vec3 to_linear(vec3 c) {
	return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(vec3(0.04045), c));
}

void fragment() {
	vec2 p = UV * detail_scale;
	float n = detail(p);
	float e = 0.05;
	float nx = detail(p + vec2(e, 0.0)) - n;
	float ny = detail(p + vec2(0.0, e)) - n;
	float wet = clamp(COLOR.a, 0.0, 1.0);
	float cavity = clamp(UV2.x, 0.0, 1.0);
	vec3 base = to_linear(clamp(COLOR.rgb, 0.0, 1.0)) * to_linear(tint);
	base *= 1.0 + detail_albedo * (n - 0.5) * 2.0;
	base *= mix(1.0, 1.0 - cavity_albedo, cavity);
	base *= mix(1.0, wet_darken, wet);
	ALBEDO = base;
	METALLIC = metallic;
	SPECULAR = specular;
	ROUGHNESS = clamp(mix(roughness_dry, roughness_wet, wet) + (n - 0.5) * 0.15, 0.04, 1.0);
	AO = 1.0 - cavity * cavity_ao;
	AO_LIGHT_AFFECT = 0.4;
	CLEARCOAT = wet * clearcoat_wet;
	CLEARCOAT_ROUGHNESS = 0.15;
	float bump = detail_bump * (1.0 - wet * 0.6) / e;
	NORMAL = normalize(NORMAL - (TANGENT * nx + BINORMAL * ny) * bump * 0.02);
	float pulse = 1.0;
	if (emission_pulse_hz > 0.0) {
		pulse = 1.0 - emission_pulse_depth * (0.5 + 0.5 * sin(TIME * 6.2831853 * emission_pulse_hz));
	}
	EMISSION = emission_color * emission_energy * clamp(UV2.y, 0.0, 1.0) * pulse;
	if (rim_sheen > 0.0) {
		float f = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), 3.0);
		EMISSION += mix(base, rim_color, rim_tint) * f * rim_sheen;
	}
}

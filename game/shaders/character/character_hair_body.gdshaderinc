// Hymn of the Undertow: hero hair cards (M1-RND-04, SPEC §8.2 item 5). Body shared by the tier
// wrappers character_hair{,_medium,_low}.gdshader. Docs: docs/kb/tech/character_shading.md.
//
// Shading: Kajiya-Kay with two Scheuermann-shifted highlights along a flow-map tangent (primary:
// cool and narrow; secondary: warm, wider, sparkled per strand), Kajiya diffuse blended with
// wrapped Lambert, a back-lit transmission lobe (a Marschner TT stand-in) and per-strand variation
// from the strand ID and the root-to-tip gradient.
//
// Coverage (HYMN_HAIR_ALPHA_MODE, chosen per tier by the wrapper):
//   0 = temporal dither: opaque pipeline + discard against interleaved gradient noise that steps
//       every frame, decorrelated per card layer. Resolves under TAA / FSR2 (Medium, High, Ultra).
//   1 = Godot hashed alpha (ALPHA_HASH_SCALE): object-space stable hash. Kept for comparison.
//   2 = alpha scissor: hard cut at alpha_cutoff. Low preset, which runs FXAA and has no
//       temporal accumulation to resolve a dither.
// Every mode stays in the opaque pipeline (depth prepass, SSAO, SSR, DOF, shadow casting with the
// same coverage), so there is no sorting. The measured comparison is in the doc.
//
// Maps (asha.md §4.2): tex_hair = R root-to-tip (0 root .. 1 tip), G strand ID (random 0..1),
// B card depth layer (0 innermost .. 1 outermost; dither decorrelation and self-occlusion),
// A alpha. tex_hairflow = RG strand direction in tangent space (0.5 = 0), ignored at
// flow_strength 0 (strands then run along +V). Vertex colours: wind weights (character_wind).

#ifndef HYMN_CHARACTER_HAIR_BODY_GDSHADERINC
#define HYMN_CHARACTER_HAIR_BODY_GDSHADERINC

#ifndef HYMN_HAIR_ALPHA_MODE
#define HYMN_HAIR_ALPHA_MODE 0
#endif
#ifndef HYMN_CHAR_WIND_RESPONSE_DEFAULT
#define HYMN_CHAR_WIND_RESPONSE_DEFAULT 0.0 // scalp cards are bone-bound (asha.md §5)
#endif

#include "res://game/shaders/character/character_brdf.gdshaderinc"
#include "res://game/shaders/character/character_wind.gdshaderinc"

// The dither pattern steps at this rate (frames of TIME). With --fixed-fps 60 it is exactly one
// step per frame; on faster displays a pattern holds for two frames, which TAA still resolves.
#define HYMN_HAIR_DITHER_FPS 60.0
// Golden-ratio offsets decorrelate the dither of overlapping layers (two 50% layers then cover
// 75% instead of sharing one pattern and covering 50%).
#define HYMN_GOLDEN 0.61803399
#define HYMN_SILVER 0.41421356

group_uniforms colour;
uniform vec4 col_root : source_color = vec4(0.125, 0.102, 0.086, 1.0); // hair_black #201A16
uniform vec4 col_tip : source_color = vec4(0.125, 0.102, 0.086, 1.0); // Rhen: hair_copper #A65A2A
uniform float tip_start : hint_range(0.0, 1.0) = 1.0; // root-to-tip value where the tip colour begins
uniform float root_occlusion : hint_range(0.0, 1.0) = 0.5; // AO at the root
uniform float depth_occlusion : hint_range(0.0, 1.0) = 0.45; // AO of the innermost layer
uniform float ao_light_affect : hint_range(0.0, 1.0) = 0.5; // self-shadowing on direct light too
uniform float strand_value_jitter : hint_range(0.0, 0.5) = 0.18;
uniform float strand_hue_jitter : hint_range(0.0, 0.1) = 0.015;
group_uniforms;

group_uniforms maps;
uniform sampler2D tex_hair : hint_default_white, filter_linear_mipmap_anisotropic;
uniform sampler2D tex_hairflow : hint_default_white, filter_linear_mipmap;
uniform float flow_strength : hint_range(0.0, 1.0) = 1.0;
uniform float alpha_boost : hint_range(0.5, 3.0) = 1.15; // offsets coverage loss in alpha mips
uniform float alpha_cutoff : hint_range(0.05, 0.95) = 0.35; // alpha scissor (Low)
uniform bool dither_temporal = true;
group_uniforms;

group_uniforms highlights;
uniform vec4 col_spec_primary : source_color = vec4(0.91, 0.847, 0.784, 1.0); // #E8D8C8
uniform float spec_primary_intensity : hint_range(0.0, 2.0) = 0.35;
uniform float spec_primary_shift : hint_range(-0.5, 0.5) = -0.08;
uniform float spec_primary_exponent : hint_range(4.0, 512.0) = 120.0;
uniform vec4 col_spec_secondary : source_color = vec4(0.541, 0.353, 0.227, 1.0); // #8A5A3A
uniform float spec_secondary_intensity : hint_range(0.0, 2.0) = 0.5; // asha.md §5
uniform float spec_secondary_shift : hint_range(-0.5, 0.5) = 0.12;
uniform float spec_secondary_exponent : hint_range(4.0, 512.0) = 40.0;
uniform float spec_shift_jitter : hint_range(0.0, 0.3) = 0.1; // per strand
uniform float secondary_sparkle : hint_range(0.0, 1.0) = 0.8; // per-strand breakup of lobe 2
uniform float indirect_specular : hint_range(0.0, 1.0) = 0.2; // Godot reflections (keep low)
uniform float indirect_roughness : hint_range(0.0, 1.0) = 0.6;
group_uniforms;

group_uniforms scattering;
uniform float diffuse_wrap : hint_range(0.0, 1.0) = 0.4;
uniform float kajiya_diffuse_mix : hint_range(0.0, 1.0) = 0.5;
uniform vec4 col_transmission : source_color = vec4(0.541, 0.353, 0.227, 1.0); // #8A5A3A, asha.md §5: light through the hair
uniform float transmission_strength : hint_range(0.0, 4.0) = 1.5;
uniform float transmission_power : hint_range(1.0, 32.0) = 6.0;
uniform float transmission_shadow_leak : hint_range(0.0, 1.0) = 0.35; // multiple scattering through shadowed strands
group_uniforms;

varying vec3 v_hair_t;
varying float v_strand;
varying float v_root_tip;

void vertex() {
	VERTEX += hymn_char_wind_offset(VERTEX, NORMAL, COLOR, MODEL_MATRIX);
}

void fragment() {
	vec4 hair = texture(tex_hair, UV);
	float root_tip = hair.r;
	float strand = hair.g;
	float layer = hair.b;

	float a = clamp(hair.a * alpha_boost, 0.0, 1.0);
#if HYMN_HAIR_ALPHA_MODE == 0
	float frame = dither_temporal ? floor(TIME * HYMN_HAIR_DITHER_FPS) : 0.0;
	float threshold = fract(hymn_char_ign(FRAGCOORD.xy, frame) + layer * HYMN_GOLDEN + strand * HYMN_SILVER);
	// a = 1 always passes and a = 0 never does, whatever the threshold.
	if (a < mix(HYMN_EPSILON, 1.0, threshold)) {
		discard;
	}
#elif HYMN_HAIR_ALPHA_MODE == 1
	ALPHA = a;
	ALPHA_HASH_SCALE = 1.0;
#elif HYMN_HAIR_ALPHA_MODE == 2
	ALPHA = a;
	ALPHA_SCISSOR_THRESHOLD = alpha_cutoff;
#else
	ALPHA = a;
#endif

	vec3 col = mix(col_root.rgb, col_tip.rgb, smoothstep(tip_start, 1.0, root_tip));
#if HYMN_QUALITY >= HYMN_QUALITY_MEDIUM
	// Per-strand variation: value and a touch of hue, both from the strand ID.
	float sv = (strand - 0.5) * 2.0;
	col *= 1.0 + sv * strand_value_jitter;
	col = hymn_saturate_color(col, 1.0 + sv * strand_hue_jitter * 10.0);
#endif
	ALBEDO = col;
	AO = mix(root_occlusion, 1.0, smoothstep(0.0, 0.5, root_tip)) * mix(depth_occlusion, 1.0, layer);
	AO_LIGHT_AFFECT = ao_light_affect;
	ROUGHNESS = indirect_roughness;
	SPECULAR = indirect_specular;
	METALLIC = 0.0;

	vec2 flow = mix(vec2(0.0, 1.0), texture(tex_hairflow, UV).rg * 2.0 - 1.0, flow_strength);
	v_hair_t = normalize(TANGENT * flow.x + BINORMAL * flow.y);
	v_strand = strand;
	v_root_tip = root_tip;
}

void light() {
	vec3 t = normalize(v_hair_t);
	float ndl = dot(NORMAL, LIGHT);
	float wrap = hymn_char_wrap(ndl, diffuse_wrap);
	float kd = mix(wrap, hymn_char_kajiya_diffuse(t, LIGHT) * clamp(ndl * 0.5 + 0.5, 0.0, 1.0), kajiya_diffuse_mix);
	DIFFUSE_LIGHT += kd * ATTENUATION * LIGHT_COLOR / PI;

	// Highlights are shadowed by the wrapped term so they die on the dark side of the head.
	float spec_shadow = ATTENUATION * smoothstep(-0.2, 0.4, ndl);
#if HYMN_QUALITY >= HYMN_QUALITY_MEDIUM
	float jitter = (v_strand - 0.5) * 2.0 * spec_shift_jitter;
#else
	float jitter = 0.0;
#endif
	vec3 t1 = hymn_char_shift_tangent(t, NORMAL, spec_primary_shift + jitter);
	vec3 spec = col_spec_primary.rgb
			* (spec_primary_intensity * hymn_char_kajiya_spec(t1, VIEW, LIGHT, spec_primary_exponent));
#if HYMN_QUALITY >= HYMN_QUALITY_MEDIUM
	vec3 t2 = hymn_char_shift_tangent(t, NORMAL, spec_secondary_shift + jitter);
	float sparkle = mix(1.0, smoothstep(0.2, 0.9, fract(v_strand * 7.31 + v_root_tip * 1.7)), secondary_sparkle);
	spec += col_spec_secondary.rgb
			* (spec_secondary_intensity * sparkle * hymn_char_kajiya_spec(t2, VIEW, LIGHT, spec_secondary_exponent));
#endif
	// Intensities are relative to a white Lambert surface facing the light (hence / PI).
	SPECULAR_LIGHT += spec * spec_shadow * LIGHT_COLOR / PI * SPECULAR_AMOUNT;

#if HYMN_QUALITY >= HYMN_QUALITY_HIGH
	// Back-lit transmission (the TT path of Marschner, as a forward-scattering lobe): light behind
	// the hair, seen through it. The shadow map stands in for hair thickness (strands behind the
	// head get nothing), and it is strongest at the silhouette and the tips, where the view crosses
	// the fewest strands.
	float back = pow(clamp(dot(VIEW, -LIGHT), 0.0, 1.0), transmission_power);
	float silhouette = 1.0 - abs(dot(NORMAL, VIEW));
	float thin = mix(0.3, 1.0, v_root_tip) * mix(0.2, 1.0, silhouette * silhouette);
	// Added to SPECULAR_LIGHT because Godot multiplies DIFFUSE_LIGHT by the (near-black) albedo.
	// A little light still reaches strands that the hair itself shadows (multiple scattering).
	float through = mix(ATTENUATION, 1.0, transmission_shadow_leak);
	SPECULAR_LIGHT += col_transmission.rgb * (back * thin * transmission_strength * through) * LIGHT_COLOR / PI;
#endif
}

#endif

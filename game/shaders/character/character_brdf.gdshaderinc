// Hymn of the Undertow: character lighting helpers (M1-RND-04). Stage-agnostic maths used by the
// skin, hair, eye and cloth light() functions. Docs: docs/kb/tech/character_shading.md.
//   #include "res://game/shaders/character/character_brdf.gdshaderinc"
//
// Godot 4.6 light() contract (verified by render probe, see the doc): LIGHT_COLOR already holds
// colour * energy * PI (i.e. the irradiance E), and DIFFUSE_LIGHT is multiplied by ALBEDO after
// the light loop. So Lambert is `ndl * ATTENUATION * LIGHT_COLOR / PI` and a specular BRDF f adds
// `f * ndl * ATTENUATION * LIGHT_COLOR`. The *_lobe helpers below already include the n.l.

#ifndef HYMN_CHARACTER_BRDF_GDSHADERINC
#define HYMN_CHARACTER_BRDF_GDSHADERINC

#include "res://game/shaders/include/common.gdshaderinc"

// Minimum GGX alpha: keeps D finite and the highlight at least ~1 px wide at 1080p for a head
// filling the screen height (measured in the test scene; smaller alphas alias under TAA).
#define HYMN_CHAR_MIN_ALPHA 0.002
// Skin F0 for IOR 1.4: ((1.4 - 1) / (1.4 + 1))^2 = 0.0278 (Donner & Jensen skin data).
#define HYMN_CHAR_SKIN_F0 0.028
// Godot's SPECULAR input maps F0 = 0.08 * SPECULAR, so the skin value for indirect light is:
#define HYMN_CHAR_SKIN_SPECULAR (HYMN_CHAR_SKIN_F0 / 0.08)
// Tear film / cornea F0 for IOR 1.376 (Asha sheet §8.3): ((0.376) / (2.376))^2 = 0.025.
#define HYMN_CHAR_CORNEA_F0 0.025

// ---------------------------------------------------------------------------------------------
// Microfacet terms. `a` is GGX alpha (= perceptual roughness squared).
// ---------------------------------------------------------------------------------------------
float hymn_char_d_ggx(float ndh, float a) {
	float a2 = a * a;
	float d = ndh * ndh * (a2 - 1.0) + 1.0;
	return a2 / (HYMN_PI * d * d);
}

// Height-correlated Smith visibility (Heitz 2014), V = G / (4 n.l n.v).
float hymn_char_v_smith(float ndl, float ndv, float a) {
	float a2 = a * a;
	float gv = ndl * sqrt(ndv * ndv * (1.0 - a2) + a2);
	float gl = ndv * sqrt(ndl * ndl * (1.0 - a2) + a2);
	return 0.5 / max(gv + gl, HYMN_EPSILON);
}

vec3 hymn_char_f_schlick(vec3 f0, float vdh) {
	float f = pow(1.0 - vdh, 5.0);
	return f0 + (vec3(1.0) - f0) * f;
}

float hymn_char_f_schlick1(float f0, float vdh) {
	return f0 + (1.0 - f0) * pow(1.0 - vdh, 5.0);
}

// One isotropic GGX lobe: D * V * F, multiplied by n.l (caller adds LIGHT_COLOR * ATTENUATION).
vec3 hymn_char_ggx_lobe(vec3 n, vec3 v, vec3 l, float roughness, vec3 f0) {
	vec3 h = normalize(v + l);
	float ndl = max(dot(n, l), 0.0);
	float ndv = max(dot(n, v), 1e-4);
	float ndh = max(dot(n, h), 0.0);
	float vdh = max(dot(v, h), 0.0);
	float a = max(roughness * roughness, HYMN_CHAR_MIN_ALPHA);
	return hymn_char_d_ggx(ndh, a) * hymn_char_v_smith(ndl, ndv, a) * hymn_char_f_schlick(f0, vdh) * ndl;
}

// Anisotropic GGX (Burley 2012) with its matching Smith visibility (Heitz 2014). t, b: unit
// tangent/bitangent; at/ab: alphas along them. Returns D * V * F * n.l.
vec3 hymn_char_ggx_aniso_lobe(vec3 n, vec3 t, vec3 b, vec3 v, vec3 l, float at, float ab, vec3 f0) {
	vec3 h = normalize(v + l);
	float ndl = max(dot(n, l), 0.0);
	float ndv = max(dot(n, v), 1e-4);
	float ndh = max(dot(n, h), 0.0);
	float tdh = dot(t, h);
	float bdh = dot(b, h);
	float a2 = at * ab;
	vec3 dv = vec3(ab * tdh, at * bdh, a2 * ndh);
	float w2 = a2 / max(dot(dv, dv), HYMN_EPSILON);
	float d = a2 * w2 * w2 / HYMN_PI;
	float lv = ndl * length(vec3(at * dot(t, v), ab * dot(b, v), ndv));
	float ll = ndv * length(vec3(at * dot(t, l), ab * dot(b, l), ndl));
	float vis = 0.5 / max(lv + ll, HYMN_EPSILON);
	return d * vis * hymn_char_f_schlick(f0, max(dot(v, h), 0.0)) * ndl;
}

// ---------------------------------------------------------------------------------------------
// Charlie sheen (Estevez & Kulla 2017, "Production Friendly Microfacet Sheen BRDF") with the
// Neubelt & Pettineo 2013 visibility, as used by Filament. sheen_roughness in (0, 1].
// ---------------------------------------------------------------------------------------------
float hymn_char_d_charlie(float ndh, float sheen_roughness) {
	float inv_r = 1.0 / max(sheen_roughness * sheen_roughness, 1e-3);
	float sin2h = max(1.0 - ndh * ndh, 0.0078125); // 2^-7 floor avoids pow(0, x) at grazing
	return (2.0 + inv_r) * pow(sin2h, inv_r * 0.5) / HYMN_TAU;
}

float hymn_char_v_neubelt(float ndl, float ndv) {
	return 1.0 / max(4.0 * (ndl + ndv - ndl * ndv), HYMN_EPSILON);
}

vec3 hymn_char_sheen_lobe(vec3 n, vec3 v, vec3 l, vec3 sheen_color, float sheen_roughness) {
	vec3 h = normalize(v + l);
	float ndl = max(dot(n, l), 0.0);
	float ndv = max(dot(n, v), 1e-4);
	float ndh = max(dot(n, h), 0.0);
	return sheen_color * hymn_char_d_charlie(ndh, sheen_roughness) * hymn_char_v_neubelt(ndl, ndv) * ndl;
}

// Albedo scaling so diffuse + sheen stays energy-plausible (Filament's max-channel approximation).
float hymn_char_sheen_albedo_scale(vec3 sheen_color) {
	return 1.0 - 0.157 * max(max(sheen_color.r, sheen_color.g), sheen_color.b);
}

// ---------------------------------------------------------------------------------------------
// Pre-integrated skin diffuse (Penner & Borshukov 2011), analytic fit. Reference and fit:
// assets_src/characters/shader_test/preintegrated_skin_fit.py (d'Eon & Luebke 6-Gaussian profile).
//   D_c(x, u) = s_c (x + sqrt(x^2 + q_c^2)) / (1 + sqrt(1 + q_c^2))
//   q_c = A u + B u^2, s_c = 1 + C u + D u^2, x = N.L, u = scatter_radius / curvature_radius.
// Max abs error vs the integrated LUT over u in [0, 2]: R 0.018, G 0.004, B 0.010.
// ---------------------------------------------------------------------------------------------
#define HYMN_SKIN_PREINT_A vec3(0.2606, 0.0922, 0.0688)
#define HYMN_SKIN_PREINT_B vec3(-0.0592, 0.0054, 0.0028)
#define HYMN_SKIN_PREINT_C vec3(-0.0671, -0.0011, -0.0005)
#define HYMN_SKIN_PREINT_D vec3(0.0064, -0.0135, -0.0072)
#define HYMN_SKIN_PREINT_U_MAX 2.0

// x: one N.L per channel (each channel may use a differently blurred normal).
vec3 hymn_char_preint_skin(vec3 x, float u) {
	u = clamp(u, 0.0, HYMN_SKIN_PREINT_U_MAX);
	vec3 q = HYMN_SKIN_PREINT_A * u + HYMN_SKIN_PREINT_B * u * u;
	vec3 s = vec3(1.0) + HYMN_SKIN_PREINT_C * u + HYMN_SKIN_PREINT_D * u * u;
	return s * (x + sqrt(x * x + q * q)) / (vec3(1.0) + sqrt(vec3(1.0) + q * q));
}

// Wrapped Lambert: (n.l + w) / (1 + w), clamped. Brightens the terminator (not energy-conserving).
float hymn_char_wrap(float ndl, float w) {
	return max((ndl + w) / (1.0 + w), 0.0);
}

// ---------------------------------------------------------------------------------------------
// Hair: Kajiya-Kay (1989) with Scheuermann's (2004) shifted tangents.
// ---------------------------------------------------------------------------------------------
vec3 hymn_char_shift_tangent(vec3 t, vec3 n, float shift) {
	return normalize(t + shift * n);
}

// sin(T, H)^exponent, with a soft directional fade so the lobe dies on the unlit side.
float hymn_char_kajiya_spec(vec3 t, vec3 v, vec3 l, float exponent) {
	vec3 h = normalize(l + v);
	float tdh = dot(t, h);
	float sin_th = sqrt(max(1.0 - tdh * tdh, 0.0));
	float dir_atten = smoothstep(-1.0, 0.0, tdh);
	return dir_atten * pow(sin_th, exponent);
}

// Kajiya-Kay diffuse: sin(T, L), which is how a cylinder (not a card) responds to light.
float hymn_char_kajiya_diffuse(vec3 t, vec3 l) {
	float tdl = dot(t, l);
	return sqrt(max(1.0 - tdl * tdl, 0.0));
}

// ---------------------------------------------------------------------------------------------
// Dithering (fragment stage only).
// ---------------------------------------------------------------------------------------------
// Interleaved gradient noise (Jimenez 2014). Low-discrepancy in screen space, and with the
// per-frame offset its 8-frame sequence integrates under TAA / FSR2 accumulation.
#define HYMN_IGN_MAGIC vec3(0.06711056, 0.00583715, 52.9829189)
#define HYMN_IGN_FRAME_STEP 5.588238
#define HYMN_DITHER_FRAMES 8.0

float hymn_char_ign(vec2 pixel, float frame) {
	pixel += HYMN_IGN_FRAME_STEP * mod(frame, HYMN_DITHER_FRAMES);
	return fract(HYMN_IGN_MAGIC.z * fract(dot(pixel, HYMN_IGN_MAGIC.xy)));
}

// ---------------------------------------------------------------------------------------------
// Specular anti-aliasing (Tokuyoshi & Kaplanyan 2019, "Improved geometric specular AA").
// Widens roughness where the shading normal varies inside the pixel footprint, which is what
// keeps small, bright highlights (the eye's wet spot, gold thread) from crawling under TAA.
// ---------------------------------------------------------------------------------------------
#define HYMN_SPEC_AA_VARIANCE 0.25
#define HYMN_SPEC_AA_THRESHOLD 0.18

float hymn_char_spec_aa_roughness(vec3 n, float roughness) {
	vec3 du = dFdx(n);
	vec3 dv = dFdy(n);
	float variance = HYMN_SPEC_AA_VARIANCE * (dot(du, du) + dot(dv, dv));
	float kernel = min(2.0 * variance, HYMN_SPEC_AA_THRESHOLD);
	float a2 = roughness * roughness * roughness * roughness;
	return sqrt(sqrt(clamp(a2 + kernel, 0.0, 1.0)));
}

// ---------------------------------------------------------------------------------------------
// Normal maps. Tangent-space normals are reconstructed from XY (Godot may import normal maps as
// two-channel RGTC, so B is never trusted). Returns a unit tangent-space vector.
// ---------------------------------------------------------------------------------------------
vec3 hymn_char_unpack_normal(vec2 rg, float strength) {
	vec2 xy = (rg * 2.0 - 1.0) * strength;
	return normalize(vec3(xy, sqrt(max(1.0 - dot(xy, xy), 0.0))));
}

// Reoriented normal mapping (Barré-Brisebois & Hill 2012): detail `d` on base `b`.
vec3 hymn_char_blend_rnm(vec3 b, vec3 d) {
	vec3 t = b + vec3(0.0, 0.0, 1.0);
	vec3 u = d * vec3(-1.0, -1.0, 1.0);
	return normalize(t * dot(t, u) / t.z - u);
}

// Pack a unit tangent-space normal for Godot's NORMAL_MAP input (0..1 encoding, Z rebuilt).
vec3 hymn_char_pack_normal(vec3 n) {
	return n * 0.5 + 0.5;
}

#endif

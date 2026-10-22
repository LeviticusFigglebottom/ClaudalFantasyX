// Hymn of the Undertow: shared shader helpers (colour space, hashing, noise, curl noise).
// Conventions: game/shaders/README.md. Stage-agnostic: no built-ins, so spatial, canvas_item,
// particles, sky and fog shaders can all include it.
//   #include "res://game/shaders/include/common.gdshaderinc"

#ifndef HYMN_COMMON_GDSHADERINC
#define HYMN_COMMON_GDSHADERINC

// ---------------------------------------------------------------------------------------------
// Quality tiers. A variant shader defines HYMN_QUALITY before including this file; the default
// is HIGH. Compare with #if HYMN_QUALITY >= HYMN_QUALITY_HIGH.
// ---------------------------------------------------------------------------------------------
#define HYMN_QUALITY_LOW 0
#define HYMN_QUALITY_MEDIUM 1
#define HYMN_QUALITY_HIGH 2
#define HYMN_QUALITY_ULTRA 3
#ifndef HYMN_QUALITY
#define HYMN_QUALITY HYMN_QUALITY_HIGH
#endif

// Octave cap for every fBm loop (the octave count itself is a uniform/argument).
#if HYMN_QUALITY >= HYMN_QUALITY_HIGH
#define HYMN_FBM_MAX_OCTAVES 8
#else
#define HYMN_FBM_MAX_OCTAVES 4
#endif

#define HYMN_PI 3.14159265358979
#define HYMN_TAU 6.28318530717959
#define HYMN_EPSILON 1e-6

// ---------------------------------------------------------------------------------------------
// Colour space. All lighting math is in linear Rec.709/sRGB primaries.
// ---------------------------------------------------------------------------------------------
#define HYMN_REC709_LUMA vec3(0.2126, 0.7152, 0.0722)

float hymn_luminance(vec3 linear_rgb) {
	return dot(linear_rgb, HYMN_REC709_LUMA);
}

// IEC 61966-2-1 piecewise transfer functions (exact, not the 2.2 gamma approximation).
vec3 hymn_srgb_to_linear(vec3 srgb) {
	vec3 c = max(srgb, vec3(0.0));
	vec3 lo = c / 12.92;
	vec3 hi = pow((c + 0.055) / 1.055, vec3(2.4));
	return mix(lo, hi, step(vec3(0.04045), c));
}

vec3 hymn_linear_to_srgb(vec3 linear_rgb) {
	vec3 c = max(linear_rgb, vec3(0.0));
	vec3 lo = c * 12.92;
	vec3 hi = 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055;
	return mix(lo, hi, step(vec3(0.0031308), c));
}

// Pushes saturation away from (amount > 1) or towards (amount < 1) the pixel's own luminance.
vec3 hymn_saturate_color(vec3 linear_rgb, float amount) {
	return mix(vec3(hymn_luminance(linear_rgb)), linear_rgb, amount);
}

// HSV in [0,1] for all channels (branchless form).
vec3 hymn_rgb_to_hsv(vec3 c) {
	vec4 k = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
	vec4 p = mix(vec4(c.bg, k.wz), vec4(c.gb, k.xy), step(c.b, c.g));
	vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
	float d = q.x - min(q.w, q.y);
	return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + HYMN_EPSILON)), d / (q.x + HYMN_EPSILON), q.x);
}

vec3 hymn_hsv_to_rgb(vec3 hsv) {
	vec3 p = abs(fract(hsv.xxx + vec3(1.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0);
	return hsv.z * mix(vec3(1.0), clamp(p - 1.0, 0.0, 1.0), hsv.y);
}

// Oklab (perceptual; used for grading and gradient interpolation). Input/output are linear sRGB.
float hymn_cbrt(float x) {
	return sign(x) * pow(abs(x), 1.0 / 3.0);
}

vec3 hymn_linear_srgb_to_oklab(vec3 c) {
	float l = 0.4122214708 * c.r + 0.5363325363 * c.g + 0.0514459929 * c.b;
	float m = 0.2119034982 * c.r + 0.6806995451 * c.g + 0.1073969566 * c.b;
	float s = 0.0883024619 * c.r + 0.2817188376 * c.g + 0.6299787005 * c.b;
	l = hymn_cbrt(l);
	m = hymn_cbrt(m);
	s = hymn_cbrt(s);
	return vec3(
		0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
		1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
		0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s);
}

vec3 hymn_oklab_to_linear_srgb(vec3 lab) {
	float l = lab.x + 0.3963377774 * lab.y + 0.2158037573 * lab.z;
	float m = lab.x - 0.1055613458 * lab.y - 0.0638541728 * lab.z;
	float s = lab.x - 0.0894841775 * lab.y - 1.2914855480 * lab.z;
	l = l * l * l;
	m = m * m * m;
	s = s * s * s;
	return vec3(
		4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
		-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
		-0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s);
}

// ---------------------------------------------------------------------------------------------
// Hashing: PCG2D / PCG3D integer hashes (Jarzynski & Olano 2020). Stable across GPUs, no sin().
// *_cell* functions hash integer lattice cells; *_bits* functions hash any float exactly.
// ---------------------------------------------------------------------------------------------
#define HYMN_PCG_MUL 1664525u
#define HYMN_PCG_INC 1013904223u
#define HYMN_UINT_TO_UNIT (1.0 / 4294967295.0)

uvec2 hymn_pcg2d(uvec2 v) {
	v = v * HYMN_PCG_MUL + HYMN_PCG_INC;
	v.x += v.y * HYMN_PCG_MUL;
	v.y += v.x * HYMN_PCG_MUL;
	v = v ^ (v >> 16u);
	v.x += v.y * HYMN_PCG_MUL;
	v.y += v.x * HYMN_PCG_MUL;
	v = v ^ (v >> 16u);
	return v;
}

uvec3 hymn_pcg3d(uvec3 v) {
	v = v * HYMN_PCG_MUL + HYMN_PCG_INC;
	v.x += v.y * v.z;
	v.y += v.z * v.x;
	v.z += v.x * v.y;
	v = v ^ (v >> 16u);
	v.x += v.y * v.z;
	v.y += v.z * v.x;
	v.z += v.x * v.y;
	return v;
}

// Cell hashes: `cell` should hold whole numbers (e.g. floor(p)). Results in [0, 1].
float hymn_hash_cell2(vec2 cell) {
	return float(hymn_pcg2d(uvec2(ivec2(cell))).x) * HYMN_UINT_TO_UNIT;
}

vec2 hymn_hash_cell22(vec2 cell) {
	return vec2(hymn_pcg2d(uvec2(ivec2(cell)))) * HYMN_UINT_TO_UNIT;
}

float hymn_hash_cell3(vec3 cell) {
	return float(hymn_pcg3d(uvec3(ivec3(cell))).x) * HYMN_UINT_TO_UNIT;
}

vec3 hymn_hash_cell33(vec3 cell) {
	return vec3(hymn_pcg3d(uvec3(ivec3(cell)))) * HYMN_UINT_TO_UNIT;
}

// Bit hashes: any float input (e.g. a per-particle seed or a world position). Results in [0, 1].
float hymn_hash12(vec2 p) {
	return float(hymn_pcg2d(floatBitsToUint(p)).x) * HYMN_UINT_TO_UNIT;
}

vec3 hymn_hash33(vec3 p) {
	return vec3(hymn_pcg3d(floatBitsToUint(p))) * HYMN_UINT_TO_UNIT;
}

// ---------------------------------------------------------------------------------------------
// Value noise with quintic interpolation and analytic derivatives. Range [0, 1].
// The *_d variants return vec3(value, d/dx, d/dy) or vec4(value, d/dx, d/dy, d/dz).
// ---------------------------------------------------------------------------------------------
vec3 hymn_value_noise2_d(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
	vec2 du = 30.0 * f * f * (f * (f - 2.0) + 1.0);
	float n00 = hymn_hash_cell2(i);
	float n10 = hymn_hash_cell2(i + vec2(1.0, 0.0));
	float n01 = hymn_hash_cell2(i + vec2(0.0, 1.0));
	float n11 = hymn_hash_cell2(i + vec2(1.0, 1.0));
	float k1 = n10 - n00;
	float k2 = n01 - n00;
	float k3 = n00 - n10 - n01 + n11;
	float value = n00 + k1 * u.x + k2 * u.y + k3 * u.x * u.y;
	return vec3(value, du * vec2(k1 + k3 * u.y, k2 + k3 * u.x));
}

float hymn_value_noise2(vec2 p) {
	return hymn_value_noise2_d(p).x;
}

vec4 hymn_value_noise3_d(vec3 p) {
	vec3 i = floor(p);
	vec3 f = fract(p);
	vec3 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
	vec3 du = 30.0 * f * f * (f * (f - 2.0) + 1.0);
	float n000 = hymn_hash_cell3(i);
	float n100 = hymn_hash_cell3(i + vec3(1.0, 0.0, 0.0));
	float n010 = hymn_hash_cell3(i + vec3(0.0, 1.0, 0.0));
	float n110 = hymn_hash_cell3(i + vec3(1.0, 1.0, 0.0));
	float n001 = hymn_hash_cell3(i + vec3(0.0, 0.0, 1.0));
	float n101 = hymn_hash_cell3(i + vec3(1.0, 0.0, 1.0));
	float n011 = hymn_hash_cell3(i + vec3(0.0, 1.0, 1.0));
	float n111 = hymn_hash_cell3(i + vec3(1.0, 1.0, 1.0));
	float k1 = n100 - n000;
	float k2 = n010 - n000;
	float k3 = n001 - n000;
	float k4 = n000 - n100 - n010 + n110;
	float k5 = n000 - n010 - n001 + n011;
	float k6 = n000 - n100 - n001 + n101;
	float k7 = -n000 + n100 + n010 - n110 + n001 - n101 - n011 + n111;
	float value = n000 + k1 * u.x + k2 * u.y + k3 * u.z + k4 * u.x * u.y + k5 * u.y * u.z + k6 * u.z * u.x
			+ k7 * u.x * u.y * u.z;
	vec3 grad = du * vec3(
			k1 + k4 * u.y + k6 * u.z + k7 * u.y * u.z,
			k2 + k5 * u.z + k4 * u.x + k7 * u.z * u.x,
			k3 + k6 * u.x + k5 * u.y + k7 * u.x * u.y);
	return vec4(value, grad);
}

float hymn_value_noise3(vec3 p) {
	return hymn_value_noise3_d(p).x;
}

// ---------------------------------------------------------------------------------------------
// fBm. Normalised to [0, 1] whatever the octave count. Each octave is rotated (2D) or offset (3D)
// to break lattice alignment. octaves is clamped to HYMN_FBM_MAX_OCTAVES for the active tier.
// Typical arguments: lacunarity 2.0, gain 0.5.
// ---------------------------------------------------------------------------------------------
#define HYMN_FBM_ROT2 mat2(vec2(0.8, 0.6), vec2(-0.6, 0.8))
#define HYMN_FBM_SHIFT3 vec3(17.13, 31.71, 47.37)

float hymn_fbm2(vec2 p, int octaves, float lacunarity, float gain) {
	float sum = 0.0;
	float amp = 1.0;
	float norm = 0.0;
	for (int o = 0; o < HYMN_FBM_MAX_OCTAVES; o++) {
		if (o >= octaves) {
			break;
		}
		sum += amp * hymn_value_noise2(p);
		norm += amp;
		p = HYMN_FBM_ROT2 * p * lacunarity;
		amp *= gain;
	}
	return sum / max(norm, HYMN_EPSILON);
}

float hymn_fbm3(vec3 p, int octaves, float lacunarity, float gain) {
	float sum = 0.0;
	float amp = 1.0;
	float norm = 0.0;
	for (int o = 0; o < HYMN_FBM_MAX_OCTAVES; o++) {
		if (o >= octaves) {
			break;
		}
		sum += amp * hymn_value_noise3(p);
		norm += amp;
		p = p * lacunarity + HYMN_FBM_SHIFT3;
		amp *= gain;
	}
	return sum / max(norm, HYMN_EPSILON);
}

// ---------------------------------------------------------------------------------------------
// Curl noise: divergence-free flow fields for glimmer motes, foam advection and storm wisps.
// 2D: rotate the gradient of one scalar potential. 3D: curl of a vector potential built from three
// decorrelated noise fields (offsets below). Magnitudes are unnormalised (roughly [-2, 2]).
// ---------------------------------------------------------------------------------------------
#define HYMN_CURL_OFFSET_B vec3(31.416, -47.853, 12.793)
#define HYMN_CURL_OFFSET_C vec3(-19.235, 7.719, 63.137)

vec2 hymn_curl_noise2(vec2 p) {
	vec2 g = hymn_value_noise2_d(p).yz;
	return vec2(g.y, -g.x);
}

vec3 hymn_curl_noise3(vec3 p) {
	vec3 ga = hymn_value_noise3_d(p).yzw;
	vec3 gb = hymn_value_noise3_d(p + HYMN_CURL_OFFSET_B).yzw;
	vec3 gc = hymn_value_noise3_d(p + HYMN_CURL_OFFSET_C).yzw;
	// psi = (a, b, c); curl psi = (dc/dy - db/dz, da/dz - dc/dx, db/dx - da/dy)
	return vec3(gc.y - gb.z, ga.z - gc.x, gb.x - ga.y);
}

// Multi-octave curl: each octave is divergence-free, so the weighted sum is too. Not normalised.
// (Octaves are not scaled by frequency, which keeps fine octaves from dominating the flow.)
vec3 hymn_curl_fbm3(vec3 p, int octaves, float lacunarity, float gain) {
	vec3 sum = vec3(0.0);
	float amp = 1.0;
	for (int o = 0; o < HYMN_FBM_MAX_OCTAVES; o++) {
		if (o >= octaves) {
			break;
		}
		sum += amp * hymn_curl_noise3(p);
		p = p * lacunarity + HYMN_FBM_SHIFT3;
		amp *= gain;
	}
	return sum;
}

#endif

// Hymn of the Undertow: the baked noise lattice (M1-RND-10), shared by the raymarched body
// (undertow_body_march.gdshaderinc, spatial and compute) and, since M2-RND-08, the Low-tier shells. One
// trilinear fetch of assets/vfx/undertow/undertow_noise3d.png at a quintic-remapped coordinate replaces the
// eight PCG3D hashes of a hymn_value_noise3. The includer declares `noise_tex` (3D, linear, repeat) and
// `noise_texels` first, and includes this before undertow_common.gdshaderinc, so the striation warp fetches
// the lattice too (UNDERTOW_BAKED_NOISE).

#ifndef HYMN_UNDERTOW_LATTICE_GDSHADERINC
#define HYMN_UNDERTOW_LATTICE_GDSHADERINC

#include "res://game/shaders/include/common.gdshaderinc"

vec4 undertow_lattice(vec3 p) {
	vec3 i = floor(p);
	vec3 f = p - i;
	vec3 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
	return texture(noise_tex, (i + u + 0.5) / noise_texels);
}

float undertow_noise(vec3 p) {
	return undertow_lattice(p).r;
}

// The common include's striation warp fetches this lattice instead of hashing.
#define UNDERTOW_BAKED_NOISE

// hymn_fbm3 (lacunarity 2, gain 0.5) on the baked lattice.
float undertow_fbm(vec3 p, int octaves) {
	float sum = 0.0;
	float amp = 1.0;
	float norm = 0.0;
	for (int o = 0; o < HYMN_FBM_MAX_OCTAVES; o++) {
		if (o >= octaves) {
			break;
		}
		sum += amp * undertow_noise(p);
		norm += amp;
		p = p * 2.0 + HYMN_FBM_SHIFT3;
		amp *= 0.5;
	}
	return sum / max(norm, HYMN_EPSILON);
}

#endif

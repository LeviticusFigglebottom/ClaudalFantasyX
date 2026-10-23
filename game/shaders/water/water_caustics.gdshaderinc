// Hymn of the Undertow: procedural caustic pattern (M1-RND-01). Stage-agnostic.
// Reused by the ocean/river shaders (screen-space projector onto the seabed) and intended for the
// underwater shader (M1 SPEC §8.2 item 2: caustic light on characters).
//
// The pattern is the cell-edge distance (F2 - F1) of an animated Worley field: bright thin lines
// where light focuses, dark cells between. Two layers, each domain-warped by its own field, at
// different scales and drift directions (M1-RND-08): their union keeps the web, their PRODUCT adds
// bright focus knots where the two webs cross (they may exceed 1, like real hot spots). Line width
// and focus vary over metres with low-frequency noise, so the web is neither uniform glass nor tiles.

#ifndef HYMN_WATER_CAUSTICS_GDSHADERINC
#define HYMN_WATER_CAUSTICS_GDSHADERINC

#include "res://game/shaders/include/common.gdshaderinc"

// How far a feature point wanders inside its cell (0.5 would let it touch the border).
#define HYMN_CAUSTIC_JITTER 0.42
// Second layer: scale ratio and drift relative to the first (irrational-ish to avoid beating).
#define HYMN_CAUSTIC_LAYER2_SCALE 1.618
#define HYMN_CAUSTIC_LAYER2_OFFSET vec2(13.7, 7.3)
// Domain-warp amplitude in pattern units (0 = straight polygon edges).
#define HYMN_CAUSTIC_WARP 0.9
// Big sentinel for the nearest-distance search (larger than any squared in-neighbourhood distance).
#define HYMN_CAUSTIC_FAR 8.0
// Layer 2 gets its own warp field (offset into the noise).
#define HYMN_CAUSTIC_WARP2_OFFSET 31.7
// Union weight of the two webs and gain of their product (the focus knots).
#define HYMN_CAUSTIC_UNION 0.6
#define HYMN_CAUSTIC_KNOT 2.0
// Second, finer warp octave: curls the filaments so cells are not straight-edged polygons.
#define HYMN_CAUSTIC_WARP_FINE 0.35
#define HYMN_CAUSTIC_WARP_FINE_SCALE 1.7
// Low-frequency variation (pattern units): focus brightness +-MOD, line width +-WIDTH_VAR.
#define HYMN_CAUSTIC_MOD_SCALE 0.13
#define HYMN_CAUSTIC_MOD_OFFSET vec2(7.1, -3.3)
#define HYMN_CAUSTIC_MOD 0.5
#define HYMN_CAUSTIC_WIDTH_SCALE 0.21
#define HYMN_CAUSTIC_WIDTH_OFFSET vec2(-4.7, 9.9)
#define HYMN_CAUSTIC_WIDTH_VAR 0.4
// Mean of hymn_caustic() as a function of the line width (least-squares fits of a numpy replica of
// this file over 0.065-0.43 pattern units, max error 0.006: tools/gpu_bench/caustic_mean_fit.py).
#define HYMN_CAUSTIC_MEAN2_A -0.0228
#define HYMN_CAUSTIC_MEAN2_B 1.8759
#define HYMN_CAUSTIC_MEAN1_A 0.0105
#define HYMN_CAUSTIC_MEAN1_B 0.8265

// Edge distance of an animated Worley field: 0 on a cell border, about 0.5 at a cell centre.
float hymn_caustic_edge(vec2 p, float t) {
	vec2 cell = floor(p);
	vec2 f = fract(p);
	float f1 = HYMN_CAUSTIC_FAR;
	float f2 = HYMN_CAUSTIC_FAR;
	for (int y = -1; y <= 1; y++) {
		for (int x = -1; x <= 1; x++) {
			vec2 o = vec2(float(x), float(y));
			vec2 h = hymn_hash_cell22(cell + o);
			// Each feature point orbits at its own rate and phase (sin/cos for motion, not hashing).
			float a = HYMN_TAU * h.x + t * (0.6 + 0.8 * h.y);
			vec2 pt = o + 0.5 + HYMN_CAUSTIC_JITTER * vec2(cos(a), sin(a));
			vec2 r = pt - f;
			float d = dot(r, r);
			if (d < f1) {
				f2 = f1;
				f1 = d;
			} else if (d < f2) {
				f2 = d;
			}
		}
	}
	return sqrt(f2) - sqrt(f1);
}

// Domain warp: bends the straight Worley edges into the curved filaments of focused light.
vec2 hymn_caustic_warp(vec2 p, float t, float offset) {
	vec2 coarse = vec2(hymn_value_noise2(p * 0.5 + t * 0.1 + offset), hymn_value_noise2(p * 0.5 - t * 0.1 + 5.2 + offset));
	vec2 q = p * HYMN_CAUSTIC_WARP_FINE_SCALE;
	vec2 fine = vec2(hymn_value_noise2(q + t * 0.17 + offset + 2.3), hymn_value_noise2(q - t * 0.17 + 8.1 + offset));
	return p + HYMN_CAUSTIC_WARP * (coarse - 0.5) + HYMN_CAUSTIC_WARP_FINE * (fine - 0.5);
}

// The union/product combination of two line intensities (shared with the texture pattern).
float hymn_caustic_combine(float l1, float l2) {
	return HYMN_CAUSTIC_UNION * max(l1, l2) + HYMN_CAUSTIC_KNOT * l1 * l2;
}

// Caustic brightness, about [0, 1] with focus knots above 1. p in pattern units (world metres *
// scale), t in seconds * speed. width: line half-width in pattern units (thinner = sharper focus).
// layers: 1 (Low tier: one warped web) or 2.
float hymn_caustic(vec2 p, float t, float width, int layers) {
	float m = hymn_value_noise2(p * HYMN_CAUSTIC_MOD_SCALE + HYMN_CAUSTIC_MOD_OFFSET);
	float w = width
			* (1.0 - HYMN_CAUSTIC_WIDTH_VAR
					+ 2.0 * HYMN_CAUSTIC_WIDTH_VAR
							* hymn_value_noise2(p * HYMN_CAUSTIC_WIDTH_SCALE + HYMN_CAUSTIC_WIDTH_OFFSET));
	float l1 = 1.0 - smoothstep(0.0, w, hymn_caustic_edge(hymn_caustic_warp(p, t, 0.0), t));
	l1 *= l1;
	float c = l1;
	if (layers > 1) {
		vec2 p2 = HYMN_FBM_ROT2 * p * HYMN_CAUSTIC_LAYER2_SCALE + HYMN_CAUSTIC_LAYER2_OFFSET;
		float e2 = hymn_caustic_edge(hymn_caustic_warp(p2, t * 1.3, HYMN_CAUSTIC_WARP2_OFFSET), t * 1.3);
		float l2 = 1.0 - smoothstep(0.0, w * HYMN_CAUSTIC_LAYER2_SCALE, e2);
		c = hymn_caustic_combine(l1, l2 * l2);
	}
	return c * (1.0 - HYMN_CAUSTIC_MOD + 2.0 * HYMN_CAUSTIC_MOD * m);
}

// Spatial and temporal mean of hymn_caustic() at a line width (subtract it so caustics only
// redistribute light: the floor's average brightness does not change with depth).
float hymn_caustic_mean(float width, int layers) {
	return layers > 1 ? HYMN_CAUSTIC_MEAN2_A + HYMN_CAUSTIC_MEAN2_B * width
					  : HYMN_CAUSTIC_MEAN1_A + HYMN_CAUSTIC_MEAN1_B * width;
}

#endif

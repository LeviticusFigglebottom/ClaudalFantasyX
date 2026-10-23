// Hymn of the Undertow: procedural caustic pattern (M1-RND-01). Stage-agnostic.
// Reused by the ocean/river shaders (screen-space projector onto the seabed) and intended for the
// underwater shader (M1 SPEC §8.2 item 2: caustic light on characters).
//
// The pattern is the cell-edge distance (F2 - F1) of an animated Worley field: bright thin lines
// where light focuses, dark cells between. Two layers at different scales and drift directions are
// combined with a soft minimum so the network shimmers and re-forms instead of sliding as one sheet.

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

// Caustic brightness in [0, 1]. p in pattern units (world metres * scale), t in seconds * speed.
// width: line half-width in pattern units (thinner = sharper focus). layers: 1 or 2.
float hymn_caustic(vec2 p, float t, float width, int layers) {
	// Domain warp: bends the straight Worley edges into the curved filaments of focused light.
	p += HYMN_CAUSTIC_WARP * (vec2(hymn_value_noise2(p * 0.5 + t * 0.1), hymn_value_noise2(p * 0.5 - t * 0.1 + 5.2))
			- 0.5);
	float e1 = hymn_caustic_edge(p, t);
	float c = 1.0 - smoothstep(0.0, width, e1);
	if (layers > 1) {
		vec2 p2 = HYMN_FBM_ROT2 * p * HYMN_CAUSTIC_LAYER2_SCALE + HYMN_CAUSTIC_LAYER2_OFFSET;
		float e2 = hymn_caustic_edge(p2, t * 1.3);
		float c2 = 1.0 - smoothstep(0.0, width * HYMN_CAUSTIC_LAYER2_SCALE, e2);
		// Lines brighten where the two networks cross, as real focused light does.
		c = clamp(0.65 * c + 0.65 * c2 + 0.9 * c * c2, 0.0, 1.0);
	}
	return c * c;
}

#endif

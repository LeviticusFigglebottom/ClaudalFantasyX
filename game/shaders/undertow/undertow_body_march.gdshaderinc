// Hymn of the Undertow: the Undertow body's raymarch (M1-RND-03), as a function of one view ray, shared by
// the spatial body (undertow_body.gdshaderinc) and the compute body (undertow_body_compute.glsl, M2-RND-01).
// Docs: docs/kb/tech/undertow.md. The includer declares the uniforms first: the spatial body through
// undertow_body_uniforms.gdshaderinc and globals.gdshaderinc, the compute body in its UBO (with
// UNDERTOW_COMPUTE defined), plus noise_tex either way. The variant defines are listed in
// undertow_body.gdshaderinc.

#ifndef HYMN_UNDERTOW_BODY_MARCH_GDSHADERINC
#define HYMN_UNDERTOW_BODY_MARCH_GDSHADERINC

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

#include "res://game/shaders/undertow/undertow_common.gdshaderinc"

#ifndef UNDERTOW_MAX_STEPS
#define UNDERTOW_MAX_STEPS 48
#endif
#ifndef UNDERTOW_LIGHT_SAMPLES
#define UNDERTOW_LIGHT_SAMPLES 2
#endif
#ifndef UNDERTOW_LIGHT_NOISE
#define UNDERTOW_LIGHT_NOISE 1
#endif
#ifndef UNDERTOW_CURL
#define UNDERTOW_CURL 1
#endif
#ifndef UNDERTOW_OCTAVES
#define UNDERTOW_OCTAVES 4
#endif
#ifndef UNDERTOW_BILLOW_SHADE
#define UNDERTOW_BILLOW_SHADE 1
#endif

// Interleaved gradient noise (Jimenez 2014, "Next Generation Post Processing in Call of Duty"):
// a per-pixel ray offset that hides step banding and that TAA resolves.
#define UNDERTOW_IGN vec3(0.06711056, 0.00583715, 52.9829189)
// Reverse-Z: a depth of 0 is the sky (no opaque surface).
#define UNDERTOW_SKY_DEPTH 1e-7
#define UNDERTOW_FAR_M 1e9
// Stop marching once the ray is this opaque.
#define UNDERTOW_MIN_TRANSMITTANCE 0.015
// Skip shading where the envelope is below this (empty-space skipping).
#define UNDERTOW_MIN_ENVELOPE 0.002
// 1 / (4 pi): Henyey-Greenstein normalisation.
#define UNDERTOW_INV_4PI 0.0795775
// Iteration headroom over UNDERTOW_MAX_STEPS for the skin-refined steps (they spend less budget).
#define UNDERTOW_SKIN_LOOP 2
// Octave count at or below which cloud_noise() skips its detail octave.
#define UNDERTOW_LIGHT_OCTAVES 2
// Finite-difference step of the baked curl, in lattice cells.
#define UNDERTOW_CURL_H 0.125
// Decorrelates the billow field from the cloud and detail fields (arbitrary, fixed).
#define UNDERTOW_BILLOW_OFFSET vec3(-31.7, 8.9, 14.3)
// Mean of |2n - 1| over the quintic value-noise lattice (measured: 0.330 over 4e5 samples).
#define UNDERTOW_BILLOW_MEAN 0.33

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

// hymn_curl_noise3 on the baked lattice: the vector potential is the lattice's RGB (three decorrelated
// fields), its gradients forward differences (four fetches instead of three analytic-gradient lookups).
vec3 undertow_curl(vec3 p) {
	vec3 c = undertow_lattice(p).rgb;
	vec3 gx = (undertow_lattice(p + vec3(UNDERTOW_CURL_H, 0.0, 0.0)).rgb - c) / UNDERTOW_CURL_H;
	vec3 gy = (undertow_lattice(p + vec3(0.0, UNDERTOW_CURL_H, 0.0)).rgb - c) / UNDERTOW_CURL_H;
	vec3 gz = (undertow_lattice(p + vec3(0.0, 0.0, UNDERTOW_CURL_H)).rgb - c) / UNDERTOW_CURL_H;
	// psi = (r, g, b); curl psi = (db/dy - dg/dz, dr/dz - db/dx, dg/dx - dr/dy)
	return vec3(gy.b - gz.g, gz.r - gx.b, gx.g - gy.r);
}

float hg_phase(float cos_t, float g) {
	float g2 = g * g;
	return UNDERTOW_INV_4PI * (1.0 - g2) / pow(max(1.0 + g2 - 2.0 * g * cos_t, HYMN_EPSILON), 1.5);
}

// Ray (storm-local origin ro, unit direction rd) against the bounding cylinder and the
// [0, top] slab. Returns (t_near, t_far); t_near >= t_far means a miss.
vec2 bound_interval(vec3 ro, vec3 rd, float radius, float top) {
	float a = dot(rd.xz, rd.xz);
	float b = dot(ro.xz, rd.xz);
	float c = dot(ro.xz, ro.xz) - radius * radius;
	vec2 tc = vec2(-UNDERTOW_FAR_M, UNDERTOW_FAR_M);
	if (a > HYMN_EPSILON) {
		float disc = b * b - a * c;
		if (disc < 0.0) {
			return vec2(1.0, 0.0);
		}
		float s = sqrt(disc);
		tc = vec2((-b - s) / a, (-b + s) / a);
	} else if (c > 0.0) {
		return vec2(1.0, 0.0);
	}
	vec2 ty = vec2(-UNDERTOW_FAR_M, UNDERTOW_FAR_M);
	if (abs(rd.y) > HYMN_EPSILON) {
		float t0 = -ro.y / rd.y;
		float t1 = (top - ro.y) / rd.y;
		ty = vec2(min(t0, t1), max(t0, t1));
	} else if (ro.y < 0.0 || ro.y > top) {
		return vec2(1.0, 0.0);
	}
	return vec2(max(tc.x, ty.x), min(tc.y, ty.y));
}

// Density in [0, 1] from the envelope eroded by noise: the full envelope keeps everything but the
// noise troughs, a thin envelope only the crests (billows at the wall's surface, wisps outside).
float cloud_density(float env, float n) {
	return clamp((n + erosion_envelope * env - erosion_threshold - coverage_bias) * erosion_contrast, 0.0, 1.0);
}

// Cloud noise in [0, 1] at storm-local p, two-phase advected along the vortex flow. With the curl
// warp on, warp_a / warp_b carry the two phases' warp vectors between calls; they are recomputed only
// when fresh_warp is true (the march decides, see curl_reuse). env is the envelope at p (the billows
// grow on the cloud's eroding fringe); lean gets the billows' drop toward the sun L there (positive =
// the lump faces the sun), 0 elsewhere.
float cloud_noise(vec3 p, int octaves, bool fresh_warp, inout vec3 warp_a, inout vec3 warp_b, float env, vec3 L,
		out float lean) {
	lean = 0.0;
	float ta;
	float tb;
	float wa;
	undertow_phases(ta, tb, wa);
	vec3 pa = undertow_flow_point(p, ta);
	vec3 pb = undertow_flow_point(p, tb);
	if (scud_height_m > 0.0) {
		float squash = mix(scud_stretch, 1.0, smoothstep(scud_height_m * 0.5, scud_height_m, p.y));
		pa.y *= squash;
		pb.y *= squash;
	}
#if UNDERTOW_CURL
	// Turbulence: a divergence-free warp carried with the flow (common.gdshaderinc curl noise).
	if (fresh_warp) {
		warp_a = undertow_curl(pa / curl_scale_m) * curl_warp_m;
		warp_b = undertow_curl(pb / curl_scale_m + HYMN_CURL_OFFSET_B) * curl_warp_m;
	}
	pa += warp_a;
	pb += warp_b;
#endif
	float na = undertow_fbm(pa / noise_scale_m, octaves);
	float nb = undertow_fbm(pb / noise_scale_m, octaves);
	float n = mix(nb, na, wa);
	if (octaves > UNDERTOW_LIGHT_OCTAVES) {
		float da = undertow_noise(pa / detail_scale_m + UNDERTOW_DETAIL_OFFSET);
		float db = undertow_noise(pb / detail_scale_m + UNDERTOW_DETAIL_OFFSET);
		n = mix(n, mix(db, da, wa), detail_weight);
	}
	// The fringe: cloud that is there but not yet solid (density in (0, 1)). The billows reshape its
	// middle, 4 d0 (1 - d0): never the solid core, and never the outermost wisps, which carving would cut
	// loose into floating islands (seen on undertow_horizon_dusk). Nothing to do in empty steps.
	float d0 = billow_weight > 0.0 ? cloud_density(env, n) : 0.0;
	float surface = 4.0 * d0 * (1.0 - d0);
	if (surface > 0.0) {
		float ba = undertow_noise(pa / billow_scale_m + UNDERTOW_BILLOW_OFFSET);
		float bb = undertow_noise(pb / billow_scale_m + UNDERTOW_BILLOW_OFFSET);
		float billow = abs(2.0 * mix(bb, ba, wa) - 1.0);
		// Zero-mean, so the lumps reshape the fringe without thinning the storm's coverage.
		n += billow_weight * surface * (billow - UNDERTOW_BILLOW_MEAN);
#if UNDERTOW_BILLOW_SHADE
		if (billow_shade > 0.0) {
			vec3 step_l = L * billow_shade_step_m;
			float la = undertow_noise((pa + step_l) / billow_scale_m + UNDERTOW_BILLOW_OFFSET);
			float lb = undertow_noise((pb + step_l) / billow_scale_m + UNDERTOW_BILLOW_OFFSET);
			// The lump here minus the lump one step toward the sun (through the same fold).
			lean = (billow - abs(2.0 * mix(lb, la, wa) - 1.0)) * surface;
		}
#endif
	}
	return n;
}

// Coarse two-phase noise for the sun-ward light samples: one octave, no curl warp. Shadows only need
// the billows' large shape, and these samples are the inner loop's inner loop.
float cloud_noise_coarse(vec3 p) {
	float ta;
	float tb;
	float wa;
	undertow_phases(ta, tb, wa);
	float na = undertow_noise(undertow_flow_point(p, ta) / noise_scale_m);
	float nb = undertow_noise(undertow_flow_point(p, tb) / noise_scale_m);
	return mix(nb, na, wa);
}

// Sun-ward optical depth at p (extinction units: transmittance = exp(-it)).
float sun_optical_depth(vec3 p, vec3 L) {
	float od = 0.0;
	for (int k = 1; k <= UNDERTOW_LIGHT_SAMPLES; k++) {
		vec3 q = p + L * (light_step_m * float(k * k));
		float e = undertow_envelope(q);
#if UNDERTOW_LIGHT_NOISE
		float d = e > UNDERTOW_MIN_ENVELOPE ? cloud_density(e, cloud_noise_coarse(q)) : 0.0;
#else
		float d = e * e;
#endif
		od += d * light_step_m * float(2 * k - 1);
	}
	return od * density_per_m * sun_extinction;
}

// The body's march along one view ray (storm-local origin ro, unit direction rd), clipped to the opaque
// surface at distance t_opaque (UNDERTOW_FAR_M: none); frag_coord (pixels) picks the jitter. Returns the
// premultiplied colour (haze applied) and alpha, or alpha < 0 where the ray misses the storm. t_mean gets
// the mean distance of what the ray saw, weighted by opacity (UNDERTOW_FAR_M on a miss).
vec4 undertow_march(vec3 ro, vec3 rd, float t_opaque, vec2 frag_coord, out float t_mean) {
	float top = undertow_height();
	vec2 seg = bound_interval(ro, rd, undertow_bound_r() + bound_margin_m, top);
	float t0 = max(seg.x, 0.0);
	float t1 = min(seg.y, t_opaque);
	if (t1 <= t0) {
		t_mean = UNDERTOW_FAR_M;
		return vec4(-1.0);
	}
	int steps = clamp(march_steps, 1, UNDERTOW_MAX_STEPS);
	float dt = (t1 - t0) / float(steps);
	float ign = fract(UNDERTOW_IGN.z * fract(dot(frag_coord, UNDERTOW_IGN.xy)));
	float offset = mix(0.5, fract(ign + jitter_phase), jitter);
	vec3 L = normalize(hymn_sun_direction + vec3(0.0, HYMN_EPSILON, 0.0));
	float cos_t = dot(rd, L);
	float phase = mix(hg_phase(cos_t, back_scatter), hg_phase(cos_t, forward_scatter), scatter_mix);
	// Per-octave energy x phase (cos_t is per pixel, so the octaves' phases are computed once here).
	vec4 ms_weight = vec4(0.0);
	float ms_a = 1.0;
	float ms_c = 1.0;
	for (int o = 0; o < 4; o++) {
		if (o >= ms_octaves) {
			break;
		}
		ms_weight[o] = ms_a * mix(hg_phase(cos_t, back_scatter * ms_c), hg_phase(cos_t, forward_scatter * ms_c), scatter_mix);
		ms_a *= ms_attenuation;
		ms_c *= ms_eccentricity;
	}
	vec3 sun = col_sun * sun_energy;
	vec3 albedo = col_albedo * albedo_gain;
	float wound_per_m = wound_energy / wound_scale_m;
	vec3 sum = vec3(0.0);
	float T = 1.0;
	float t_weight = 0.0;
	float t_acc = 0.0;
	// Adaptive steps: long strides through empty envelope, short ones inside the cloud (a uniform
	// stride undersamples the billows and leaves streaks along the view rays).
	float t = t0 + offset * dt * dense_step;
	vec3 warp_a = vec3(0.0);
	vec3 warp_b = vec3(0.0);
	// Dense steps since the warp was computed; an empty stride forces a fresh one.
	int warp_age = curl_reuse;
	// Step budget: a skin-refined step spends only its share of a full dense stride, so the refinement
	// never ends a ray before it crosses the wall (it did: see-through holes on undertow_horizon_dusk).
	float budget = 0.0;
	float dense_ds = dense_step * dt;
	for (int i = 0; i < UNDERTOW_MAX_STEPS * UNDERTOW_SKIN_LOOP; i++) {
		if (budget >= float(steps) || T < UNDERTOW_MIN_TRANSMITTANCE || t > t1) {
			break;
		}
		vec3 p = ro + rd * t;
		vec3 parts = undertow_envelope_parts(p);
		float env = max(max(parts.x, parts.y), parts.z);
		float ds = (env < UNDERTOW_MIN_ENVELOPE ? empty_step : dense_step) * dt;
		// Wounds open in the skins of the eyewall only (the canopy and bands carry no rents).
		float skin = env < UNDERTOW_MIN_ENVELOPE ? 0.0 : undertow_wall_skin(p) * parts.x;
		if (skin > 0.0) {
			ds = min(ds, wound_skin_m * skin_step);
		}
		budget += skin > 0.0 ? min(ds / dense_ds, 1.0) : 1.0;
		ds = min(ds, t1 - t + HYMN_EPSILON);
		float t_here = t;
		t += ds;
		if (env < UNDERTOW_MIN_ENVELOPE) {
			warp_age = curl_reuse;
			continue;
		}
		bool fresh_warp = warp_age >= curl_reuse;
		warp_age = fresh_warp ? 1 : warp_age + 1;
		float lean;
		float d = cloud_density(env, cloud_noise(p, UNDERTOW_OCTAVES, fresh_warp, warp_a, warp_b, env, L, lean));
		// Nothing below draws where the cloud is eroded away (a rent only thins it further), so the
		// wound noise is only evaluated where there is cloud (M1-RND-10: same image, fewer hashes).
		if (d <= 0.0) {
			continue;
		}
		float pocket = 0.0;
		float seam = 0.0;
		if (skin > 0.0) {
			seam = undertow_wound(p, pocket) * skin;
			pocket *= skin;
		}
		// A rent: the wall is torn open along the seam, and the light behind it shows.
		d *= 1.0 - clamp(seam, 0.0, 1.0) * rent_depth;
		float h = p.y / top;
		if (d <= 0.0) {
			continue;
		}
		// The rent glows where the wall is: through its depth, strongest at mid density.
		vec3 glow = col_wound * seam * wound_per_m * (0.3 + 2.8 * d * (1.0 - d));
		float sigma = d * density_per_m;
		float ts = exp(-sigma * ds);
		// A lump facing the sun has less of itself between p and the light (lean > 0), one facing away more.
		float tau_sun = max(sun_optical_depth(p, L) - billow_shade * lean, 0.0);
		// Sum of the octaves: transmittance exp(-tau b^i) weighted by energy x phase.
		float sun_ms = 0.0;
		float ms_b = 1.0;
		for (int o = 0; o < 4; o++) {
			if (o >= ms_octaves) {
				break;
			}
			sun_ms += ms_weight[o] * exp(-tau_sun * ms_b);
			ms_b *= ms_extinction;
		}
		vec3 amb = mix(col_ambient_bottom, col_ambient_top, smoothstep(0.0, 1.0, h)) * ambient_energy;
		amb *= exp(-ambient_occlusion * env * d);
		float base = mix(1.0 - base_darkening, 1.0, smoothstep(0.0, 0.45, h));
		float sun_reach = mix(sun_low_floor, 1.0, smoothstep(0.0, sun_clear_height, h));
		vec3 alb = albedo;
		if (water_wall_height_m > 0.0) {
			alb = mix(albedo, col_water_wall, water_wall_mix * (1.0 - smoothstep(0.0, water_wall_height_m, p.y)));
		}
		vec3 lit = alb * (sun * sun_ms * sun_reach * HYMN_TAU * 2.0 + amb) * base;
		// Inner light: lightning in the wall and held light pooled behind the wounds.
		vec3 inner = undertow_lightning(p) + col_held * pocket * pocket_energy * wound_intensity * env;
		vec3 s = lit + inner * (0.35 + 0.65 * d);
		sum += T * (s * (1.0 - ts) + glow * ds);
		t_acc += T * (1.0 - ts) * t_here;
		t_weight += T * (1.0 - ts);
		T *= ts;
	}
	float alpha = 1.0 - T;
	t_mean = t_weight > 0.0 ? t_acc / t_weight : t0;
	float haze = 1.0 - exp(-t_mean / haze_visibility_m);
	return vec4(mix(sum, col_haze * alpha, haze), alpha);
}

#endif

// Hymn of the Undertow: the Undertow's raymarched body (M1-RND-03). Medium, High and Ultra tiers;
// Low draws undertow_shell.gdshader instead. Docs: docs/kb/tech/undertow.md.
//
// Drawn on a proxy cylinder that bounds the storm, BACK faces only (cull_front), so it works with the
// camera outside or inside the storm. The ray is clipped analytically to the bounding cylinder and
// the slab [sea level, top], and against the OPAQUE depth buffer by hand (depth_test_disabled): the
// ocean is a transparent material and is not in that buffer, so the sea-level slab stands in for it.
// Sort it after the water (render_priority, undertow.json "render_priority").
//
// A variant defines before including this file:
//   UNDERTOW_MAX_STEPS      compile-time cap on march_steps
//   UNDERTOW_LIGHT_SAMPLES  sun-ward optical-depth samples per step
//   UNDERTOW_LIGHT_NOISE    1 = those samples include noise, 0 = envelope only
//   UNDERTOW_CURL           1 = curl-noise domain warp (turbulence), 0 = none
//   UNDERTOW_OCTAVES        fBm octaves of the cloud noise

render_mode blend_premul_alpha, unshaded, cull_front, depth_draw_never, depth_test_disabled, fog_disabled,
		shadows_disabled;

#include "res://game/shaders/include/globals.gdshaderinc"

// Baked noise lattice (M1-RND-10): texel (x, y, z) = hymn_pcg3d(x, y, z) in RGB plus a fourth hash in
// A, tileable (assets_src/vfx/undertow/bake_noise3d.py). UndertowStorm binds it from undertow.json
// "noise". One trilinear fetch at a quintic-remapped coordinate is hymn_value_noise3's quintic
// interpolation of the same lattice, at the cost of a texture fetch instead of eight PCG3D hashes.
// The cloud fields use it; the wounds keep hashing (undertow_common.gdshaderinc), so the rents stay
// exactly where they were: their fields span only a few lattice cells, where wrapping shows.
uniform highp sampler3D noise_tex : filter_linear, repeat_enable;
// Lattice cells per texture side (the bake's SIZE; undertow.json "noise.texels").
uniform float noise_texels = 64.0;

vec4 undertow_lattice(vec3 p) {
	vec3 i = floor(p);
	vec3 f = p - i;
	vec3 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
	return texture(noise_tex, (i + u + 0.5) / noise_texels);
}

float undertow_noise(vec3 p) {
	return undertow_lattice(p).r;
}

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
// Octave count at or below which cloud_noise() skips its detail octave.
#define UNDERTOW_LIGHT_OCTAVES 2
// Finite-difference step of the baked curl, in lattice cells.
#define UNDERTOW_CURL_H 0.125

uniform sampler2D depth_tex : hint_depth_texture, filter_nearest, repeat_disable;

group_uniforms march;
uniform int march_steps : hint_range(4, 128) = 44;
uniform float jitter : hint_range(0.0, 1.0) = 1.0;
// Per-frame rotation of the jitter (UndertowState.jitter_phase; 0 = a static pattern). With TAA on,
// the history averages several step phases, so fewer steps band less (M1-RND-10).
uniform float jitter_phase : hint_range(0.0, 1.0) = 0.0;
uniform float bound_margin_m : hint_range(0.0, 5000.0) = 400.0;
// Stride multipliers of the mean step (segment / march_steps) outside and inside the envelope.
uniform float empty_step : hint_range(0.5, 8.0) = 2.5;
uniform float dense_step : hint_range(0.1, 2.0) = 0.55;
// Dense steps that share one curl warp (M1-RND-10, undertow.json quality "curl_reuse"): the warp
// field varies over curl_scale_m (km), the dense steps are hundreds of metres apart. 1 = every step.
uniform int curl_reuse : hint_range(1, 8) = 1;

group_uniforms cloud;
uniform float noise_scale_m : hint_range(10.0, 20000.0) = 2300.0;
uniform float detail_scale_m : hint_range(10.0, 10000.0) = 520.0;
uniform float detail_weight : hint_range(0.0, 1.0) = 0.35;
uniform float coverage_bias : hint_range(-1.0, 1.0) = 0.08;
// Extinction per metre at density 1.
uniform float density_per_m : hint_range(0.00001, 0.05) = 0.0016;
uniform float curl_scale_m : hint_range(10.0, 40000.0) = 4200.0;
uniform float curl_warp_m : hint_range(0.0, 10000.0) = 900.0;
uniform float rent_depth : hint_range(0.0, 1.0) = 0.65;
uniform float erosion_envelope : hint_range(0.0, 2.0) = 0.6;
uniform float erosion_threshold : hint_range(0.0, 2.0) = 0.9;
uniform float erosion_contrast : hint_range(0.1, 20.0) = 4.0;

group_uniforms lighting;
// Sun (or moon) radiance: the zone's key light colour x energy (UndertowStorm copies it).
uniform vec3 col_sun : source_color = vec3(0.888, 0.381, 0.069);
uniform float sun_energy : hint_range(0.0, 16.0) = 1.0;
uniform vec3 col_ambient_top : source_color = vec3(0.159, 0.209, 0.271);
uniform vec3 col_ambient_bottom : source_color = vec3(0.004, 0.069, 0.091);
uniform float ambient_energy : hint_range(0.0, 8.0) = 1.0;
// Cloud single-scattering albedo (cool white) x gain. The mass reads as storm_slate through its own
// shadowing, not through a dark albedo: lit tops stay able to catch the dusk gold.
uniform vec3 col_albedo : source_color = vec3(0.48, 0.55, 0.63);
uniform float albedo_gain : hint_range(0.0, 4.0) = 1.0;
uniform float sun_extinction : hint_range(0.0, 4.0) = 0.85;
uniform float ambient_occlusion : hint_range(0.0, 8.0) = 1.4;
uniform float forward_scatter : hint_range(0.0, 0.95) = 0.55;
uniform float back_scatter : hint_range(-0.95, 0.0) = -0.25;
uniform float scatter_mix : hint_range(0.0, 1.0) = 0.7;
uniform float light_step_m : hint_range(10.0, 5000.0) = 650.0;
uniform float base_darkening : hint_range(0.0, 1.0) = 0.75;
// Direct light reaching the storm's lower body (a low sun has crossed the outer bands first):
// full above sun_clear_height, sun_low_floor of it at sea level.
uniform float sun_clear_height : hint_range(0.0, 1.0) = 0.8;
uniform float sun_low_floor : hint_range(0.0, 1.0) = 0.12;
// Aerial perspective toward the zone's fog colour (the storm is kilometres away).
uniform vec3 col_haze : source_color = vec3(0.35, 0.3, 0.32);
uniform float haze_visibility_m : hint_range(100.0, 200000.0) = 26000.0;

group_uniforms glow;
uniform float wound_energy : hint_range(0.0, 64.0) = 5.0;
uniform float pocket_energy : hint_range(0.0, 16.0) = 0.9;
group_uniforms;

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

// Cloud noise in [0, 1] at storm-local p, two-phase advected along the vortex flow. With the curl
// warp on, warp_a / warp_b carry the two phases' warp vectors between calls; they are recomputed only
// when fresh_warp is true (the march decides, see curl_reuse).
float cloud_noise(vec3 p, int octaves, bool fresh_warp, inout vec3 warp_a, inout vec3 warp_b) {
	float ta;
	float tb;
	float wa;
	undertow_phases(ta, tb, wa);
	vec3 pa = undertow_flow_point(p, ta);
	vec3 pb = undertow_flow_point(p, tb);
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

// Density in [0, 1] from the envelope eroded by noise: the full envelope keeps everything but the
// noise troughs, a thin envelope only the crests (billows at the wall's surface, wisps outside).
float cloud_density(float env, float n) {
	return clamp((n + erosion_envelope * env - erosion_threshold - coverage_bias) * erosion_contrast, 0.0, 1.0);
}

float sun_transmittance(vec3 p, vec3 L) {
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
	return exp(-od * density_per_m * sun_extinction);
}

void fragment() {
	vec3 world = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec3 ro = undertow_local(CAMERA_POSITION_WORLD);
	vec3 rd = normalize(world - CAMERA_POSITION_WORLD);
	float top = undertow_height();
	vec2 seg = bound_interval(ro, rd, undertow_bound_r() + bound_margin_m, top);
	float depth = texture(depth_tex, SCREEN_UV).r;
	float t_opaque = UNDERTOW_FAR_M;
	if (depth > UNDERTOW_SKY_DEPTH) {
		vec4 v = INV_PROJECTION_MATRIX * vec4(SCREEN_UV * 2.0 - 1.0, depth, 1.0);
		t_opaque = length(v.xyz / v.w);
	}
	float t0 = max(seg.x, 0.0);
	float t1 = min(seg.y, t_opaque);
	if (t1 <= t0) {
		discard;
	}
	int steps = clamp(march_steps, 1, UNDERTOW_MAX_STEPS);
	float dt = (t1 - t0) / float(steps);
	float ign = fract(UNDERTOW_IGN.z * fract(dot(FRAGCOORD.xy, UNDERTOW_IGN.xy)));
	float offset = mix(0.5, fract(ign + jitter_phase), jitter);
	vec3 L = normalize(hymn_sun_direction + vec3(0.0, HYMN_EPSILON, 0.0));
	float cos_t = dot(rd, L);
	float phase = mix(hg_phase(cos_t, back_scatter), hg_phase(cos_t, forward_scatter), scatter_mix);
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
	for (int i = 0; i < UNDERTOW_MAX_STEPS; i++) {
		if (i >= steps || T < UNDERTOW_MIN_TRANSMITTANCE || t > t1) {
			break;
		}
		vec3 p = ro + rd * t;
		vec3 parts = undertow_envelope_parts(p);
		float env = max(max(parts.x, parts.y), parts.z);
		float ds = (env < UNDERTOW_MIN_ENVELOPE ? empty_step : dense_step) * dt;
		ds = min(ds, t1 - t + HYMN_EPSILON);
		float t_here = t;
		t += ds;
		if (env < UNDERTOW_MIN_ENVELOPE) {
			warp_age = curl_reuse;
			continue;
		}
		bool fresh_warp = warp_age >= curl_reuse;
		warp_age = fresh_warp ? 1 : warp_age + 1;
		float d = cloud_density(env, cloud_noise(p, UNDERTOW_OCTAVES, fresh_warp, warp_a, warp_b));
		// Nothing below draws where the cloud is eroded away (a rent only thins it further), so the
		// wound noise is only evaluated where there is cloud (M1-RND-10: same image, fewer hashes).
		if (d <= 0.0) {
			continue;
		}
		// Wounds open in the skins of the eyewall only (the canopy and bands carry no rents).
		float pocket = 0.0;
		float seam = 0.0;
		float skin = undertow_wall_skin(p) * parts.x;
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
		float t_sun = sun_transmittance(p, L);
		vec3 amb = mix(col_ambient_bottom, col_ambient_top, smoothstep(0.0, 1.0, h)) * ambient_energy;
		amb *= exp(-ambient_occlusion * env * d);
		float base = mix(1.0 - base_darkening, 1.0, smoothstep(0.0, 0.45, h));
		float sun_reach = mix(sun_low_floor, 1.0, smoothstep(0.0, sun_clear_height, h));
		vec3 lit = albedo * (sun * t_sun * sun_reach * phase * HYMN_TAU * 2.0 + amb) * base;
		// Inner light: lightning in the wall and held light pooled behind the wounds.
		vec3 inner = undertow_lightning(p) + col_held * pocket * pocket_energy * wound_intensity * env;
		vec3 s = lit + inner * (0.35 + 0.65 * d);
		sum += T * (s * (1.0 - ts) + glow * ds);
		t_acc += T * (1.0 - ts) * t_here;
		t_weight += T * (1.0 - ts);
		T *= ts;
	}
	float alpha = 1.0 - T;
	float t_mean = t_weight > 0.0 ? t_acc / t_weight : t0;
	float haze = 1.0 - exp(-t_mean / haze_visibility_m);
	ALBEDO = mix(sum, col_haze * alpha, haze);
	ALPHA = alpha;
}

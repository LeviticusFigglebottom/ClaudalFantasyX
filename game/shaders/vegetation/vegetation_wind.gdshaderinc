// Hymn of the Undertow: vegetation wind (M1-ENV-02). Vertex-stage only; needs render_mode
// world_vertex_coords so VERTEX and NORMAL arrive in world space (MultiMesh instances included).
// Conventions: docs/kb/art/environments/vegetation.md ("Wind conventions").
//   COLOR.r primary sway weight (0 root .. 1 most bent)     -> whole-plant bend downwind + sway
//   COLOR.g secondary bend weight (0 frond/blade base .. 1 tip) -> per-element bob     (not on Low)
//   COLOR.b element phase 0..1                                -> desynchronises elements
//   COLOR.a flutter weight (0 rib .. 1 leaflet edge)          -> fast flutter along the normal (not on Low)
// Driven by the globals hymn_wind (xyz = direction * m/s, w = gust 0..1) and hymn_wind_time (s).
// Per-instance phase: hash of the instance origin, plus the optional inst_wind_phase override.
//   #include "res://game/shaders/vegetation/vegetation_wind.gdshaderinc"

#ifndef HYMN_VEGETATION_WIND_GDSHADERINC
#define HYMN_VEGETATION_WIND_GDSHADERINC

#include "res://game/shaders/include/common.gdshaderinc"
#include "res://game/shaders/include/globals.gdshaderinc"

// Wind speed (m/s) at which wind_response is reached: the Haluna trade wind (brief §1.1).
#define HYMN_VEG_REFERENCE_WIND_MS 6.0
// Gust field: world-space wavelength (m) of the travelling gust noise.
#define HYMN_VEG_GUST_WAVELENGTH_M 18.0
// Ratio between the two sway sines (irrational-ish so the sum never visibly repeats).
#define HYMN_VEG_SWAY_RATIO 2.31
#define HYMN_VEG_CROSS_RATIO 1.73
#define HYMN_VEG_FLUTTER_SPATIAL vec3(2.7, 1.3, 3.1)

group_uniforms wind;
uniform float wind_response : hint_range(0.0, 2.0) = 0.5; // brief: saltgrass 0.9, palm ~0.5, frangipani ~0.3
uniform float plant_height_m : hint_range(0.1, 30.0) = 10.0; // authored height at scale 1
uniform float sway_lean : hint_range(0.0, 0.2) = 0.03; // static downwind lean, fraction of height
uniform float sway_amplitude : hint_range(0.0, 0.2) = 0.02; // oscillation, fraction of height
uniform float sway_frequency_hz : hint_range(0.01, 3.0) = 0.22;
uniform float secondary_amplitude_m : hint_range(0.0, 1.0) = 0.15;
uniform float secondary_frequency_hz : hint_range(0.05, 5.0) = 0.7;
uniform float flutter_amplitude_m : hint_range(0.0, 0.2) = 0.02;
uniform float flutter_frequency_hz : hint_range(0.1, 12.0) = 3.5;
uniform float gust_contrast : hint_range(0.0, 2.0) = 1.2;
group_uniforms;

instance uniform float inst_wind_phase = 0.0;

struct HymnVegWind {
	vec3 dir; // unit downwind direction (horizontal)
	float strength; // 0 = calm; 1 = reference wind at wind_response 1
	float gust; // 0.4..1.6 multiplier from the travelling gust field
	float phase; // per-instance phase in [0, 1)
};

HymnVegWind hymn_veg_wind_at(vec3 origin) {
	HymnVegWind w;
	vec3 wv = vec3(hymn_wind.x, 0.0, hymn_wind.z);
	float speed = length(wv);
	w.dir = speed > HYMN_EPSILON ? wv / speed : vec3(1.0, 0.0, 0.0);
	w.strength = speed / HYMN_VEG_REFERENCE_WIND_MS * wind_response;
	vec2 gp = (origin.xz - w.dir.xz * hymn_wind_time * speed) / HYMN_VEG_GUST_WAVELENGTH_M;
	float g = hymn_fbm2(gp, 2, 2.0, 0.5);
	w.gust = mix(1.0, max(0.0, 1.0 + (g - 0.5) * 2.0 * gust_contrast), clamp(hymn_wind.w, 0.0, 1.0));
	w.phase = fract(hymn_hash12(origin.xz) + inst_wind_phase);
	return w;
}

// Returns the displaced world-space vertex. `origin` is the plant root (MODEL_MATRIX[3].xyz) and
// `scale_y` the instance's vertical scale (length(MODEL_MATRIX[1].xyz)).
vec3 hymn_veg_wind_displace(vec3 world, vec3 world_normal, vec4 weights, vec3 origin, float scale_y) {
	HymnVegWind w = hymn_veg_wind_at(origin);
	float t = hymn_wind_time;
	float k = w.strength * w.gust;
	float height = plant_height_m * scale_y;
	float ph = w.phase * HYMN_TAU;
	float osc = 0.6 * sin(t * sway_frequency_hz * HYMN_TAU + ph)
			+ 0.4 * sin(t * sway_frequency_hz * HYMN_VEG_SWAY_RATIO * HYMN_TAU + ph * 3.0);
	float cross_osc = sin(t * sway_frequency_hz * HYMN_VEG_CROSS_RATIO * HYMN_TAU + ph * 5.0);
	vec3 cross_dir = vec3(-w.dir.z, 0.0, w.dir.x);
	// Primary: the whole plant leans downwind and sways about its root, keeping its length.
	vec3 rel = world - origin;
	vec3 disp = (w.dir * (sway_lean + sway_amplitude * osc) + cross_dir * (0.3 * sway_amplitude * cross_osc))
			* (weights.r * k * height);
	vec3 bent = rel + disp;
	float len_rel = length(rel);
	bent = len_rel > HYMN_EPSILON ? normalize(bent) * len_rel : bent;
#if HYMN_QUALITY > HYMN_QUALITY_LOW
	// Secondary: each frond/branch/blade bobs on its own phase (mostly vertical, a little downwind).
	float eph = (weights.b + w.phase) * HYMN_TAU;
	float bob = sin(t * secondary_frequency_hz * HYMN_TAU + eph) * 0.7
			+ sin(t * secondary_frequency_hz * 1.9 * HYMN_TAU + eph * 2.0) * 0.3;
	bent += normalize(vec3(0.0, 1.0, 0.0) + w.dir * 0.6) * (weights.g * secondary_amplitude_m * k * bob);
	// Flutter: leaflet edges ripple along their normal; a spatial term makes it travel.
	float fl = sin(t * flutter_frequency_hz * HYMN_TAU + eph * 3.0 + dot(world, HYMN_VEG_FLUTTER_SPATIAL));
	bent += world_normal * (weights.a * flutter_amplitude_m * k * fl);
#endif
	return origin + bent;
}

#endif

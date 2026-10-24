// Hymn of the Undertow: the Undertow storm, shared storm-space maths (M1-RND-03, SPEC §8.2 item 9).
// Docs: docs/kb/tech/undertow.md. Tunables: game/data/vfx/undertow.json (UndertowStorm pushes them).
// Every storm shader (raymarched body, Low-tier shells, spray, sea funnel) includes this file, so the
// body, its shells and the sea agree on the shape, the rotation, the wounds and the lightning.
//
// Storm-local space: origin = the eye at sea level (storm_center), +Y up, metres. Nothing reads TIME:
// storm_time_s is the storm's own clock (UndertowStorm.time_s), so cutscenes can pause and scrub it.
// Light meaning (docs/kb/art/color_script.md rule 1): the wounds are spawn_wound rents; the light
// pooled inside them and the motes they shed are glimmer_held, and both sink (drift DOWN the wall).

#ifndef HYMN_UNDERTOW_COMMON_GDSHADERINC
#define HYMN_UNDERTOW_COMMON_GDSHADERINC

#include "res://game/shaders/include/glimmer.gdshaderinc"

// Lightning sites pushed by UndertowStorm (= undertow.json lightning.sites, tested).
#define UNDERTOW_MAX_FLASHES 4
// Palette (docs/kb/art/palette.json), linear sRGB: spawn_wound #3FE0C8.
#define UNDERTOW_SPAWN_WOUND vec3(0.0497, 0.7454, 0.5776)
// Decorrelating offsets for the noise fields below (arbitrary, fixed: they only pick other noise).
#define UNDERTOW_WOUND_OFFSET vec3(13.7, -41.3, 27.1)
#define UNDERTOW_PRESENCE_OFFSET vec3(-71.9, 5.3, 33.8)
#define UNDERTOW_DETAIL_OFFSET vec3(5.17, 19.3, -8.71)
#define UNDERTOW_STRIATION_OFFSET vec3(-23.3, 11.9, 47.6)
// Second wound octave: frequency ratio and weight (a lacunarity just off 2 hides the lattice).
#define UNDERTOW_WOUND_LACUNARITY 2.03
#define UNDERTOW_WOUND_DETAIL 0.35
// Fraction of the presence noise used to fade a wound in (soft edge of a rent region).
#define UNDERTOW_PRESENCE_SOFT 0.18
// Radii are clamped to this fraction of the eye radius before 1/r maths (the axis is singular).
#define UNDERTOW_AXIS_GUARD 0.25

// The uniforms (undertow_common_uniforms.gdshaderinc); the compute body declares them in its UBO.
#ifndef UNDERTOW_COMPUTE
#include "res://game/shaders/undertow/undertow_common_uniforms.gdshaderinc"
#endif

vec3 undertow_local(vec3 world_pos) {
	return world_pos - storm_center;
}

vec2 undertow_rotate(vec2 v, float angle) {
	float c = cos(angle);
	float s = sin(angle);
	return vec2(c * v.x - s * v.y, s * v.x + c * v.y);
}

// Height scale: a sleeping storm is lower (calm_shrink at intensity 0).
float undertow_height() {
	return height_m * mix(calm_shrink, 1.0, storm_intensity);
}

// Angular speed (rad/s) at radius r: differential rotation, fastest at the eyewall.
float undertow_omega(float r) {
	return rotation_rad_s * pow(eye_radius_m / max(r, eye_radius_m * UNDERTOW_AXIS_GUARD), rotation_falloff);
}

// Eye radius and outer wall radius at normalised height h in [0, 1].
float undertow_eye_r(float h) {
	return eye_radius_m * (1.0 + (eye_flare - 1.0) * pow(clamp(h, 0.0, 1.0), eye_flare_power));
}

float undertow_wall_r(float h) {
	return undertow_eye_r(h) + wall_thickness_m * (1.0 - wall_taper * clamp(h, 0.0, 1.0));
}

// Radius of the bounding cylinder every storm part fits in (the raymarch proxy uses it too).
float undertow_bound_r() {
	return max(max(canopy_radius_m, band_radius_m), undertow_wall_r(1.0) + wall_softness_m);
}

// Log-spiral phase of the inflow bands at a storm-local point (bands spiral IN toward the eye).
float undertow_spiral_phase(vec2 xz) {
	float r = max(length(xz), eye_radius_m * UNDERTOW_AXIS_GUARD);
	return atan(xz.y, xz.x) + band_twist * log(r / eye_radius_m);
}

// Helical striation in [0, 1] at p: bands that wind up the wall and turn with the eyewall (rigidly,
// so they never wind up). Phase = height / spacing + starts * angle / tau, bent by the warp field.
float undertow_striation(vec3 p) {
	float spin = -rotation_rad_s * storm_time_s;
	float a = atan(p.z, p.x) + spin;
	float phase = p.y / striation_spacing_m + striation_starts * a / HYMN_TAU;
	float depth = 1.0;
	if (striation_warp > 0.0 || striation_vary > 0.0) {
		// Sampled in the frame that turns with the eyewall, so the bends ride the helix.
		vec2 xz = undertow_rotate(p.xz, spin);
		vec3 q = vec3(xz.x, p.y, xz.y) / striation_warp_scale_m + UNDERTOW_STRIATION_OFFSET;
#ifdef UNDERTOW_BAKED_NOISE
		// The body's baked lattice: two decorrelated channels for one fetch.
		vec2 n = undertow_lattice(q).rg;
#else
		vec2 n = vec2(hymn_value_noise3(q), hymn_value_noise3(q + UNDERTOW_PRESENCE_OFFSET));
#endif
		phase += striation_warp * (2.0 * n.x - 1.0);
		depth = 1.0 - striation_vary * n.y;
	}
	return mix(1.0, pow(0.5 + 0.5 * cos(HYMN_TAU * phase), striation_sharpness), depth);
}

// Analytic coverage envelope parts in [0, 1] (no noise): x = the eyewall, y = the anvil canopy,
// z = the spiral rain bands. Cheap; the raymarch uses them for empty-space skipping and the wound
// mask, the shells for placement.
vec3 undertow_envelope_parts(vec3 p) {
	float H = undertow_height();
	float h = p.y / H;
	if (h <= 0.0 || h >= 1.0) {
		return vec3(0.0);
	}
	float r = length(p.xz);
	float ri = undertow_eye_r(h);
	float ro = undertow_wall_r(h);
	float wall = smoothstep(ri - wall_softness_m * 0.25, ri + wall_softness_m, r)
			* (1.0 - smoothstep(ro - wall_softness_m, ro + wall_softness_m, r));
	wall *= 1.0 - smoothstep(1.0 - top_softness, 1.0, h);
	if (wall > 0.0) {
		wall *= mix(1.0, undertow_striation(p), striation_strength);
	}
	if (skirt_height_m > 0.0) {
		float sh = clamp(p.y / skirt_height_m, 0.0, 1.0);
		float reach = ro + skirt_reach_m * (1.0 - sh) * (1.0 - sh);
		float skirt = (1.0 - smoothstep(0.55, 1.0, sh))
				* smoothstep(ri - wall_softness_m * 0.25, ri + wall_softness_m, r)
				* (1.0 - smoothstep(reach - wall_softness_m, reach + wall_softness_m, r));
		wall = max(wall, skirt * skirt_density);
	}
	float ch = canopy_height_m * H / height_m;
	float canopy = (1.0 - smoothstep(0.0, canopy_thickness_m * 0.5, abs(p.y - ch)))
			* (1.0 - smoothstep(canopy_radius_m - canopy_softness_m, canopy_radius_m, r))
			* smoothstep(ri, ri + wall_softness_m, r);
	float arm = pow(0.5 + 0.5 * cos(band_arms * undertow_spiral_phase(p.xz)), band_sharpness);
	if (band_join_m > 0.0) {
		arm = mix(1.0, arm, smoothstep(ro, ro + band_join_m, r));
	}
	float band = arm * band_density * (1.0 - smoothstep(0.0, band_height_m, p.y))
			* smoothstep(ro - wall_softness_m, ro + wall_softness_m, r)
			* (1.0 - smoothstep(band_radius_m * 0.55, band_radius_m, r));
	return vec3(wall, canopy, band) * smoothstep(0.0, 0.2, storm_intensity + 0.05);
}

float undertow_envelope(vec3 p) {
	vec3 e = undertow_envelope_parts(p);
	return max(max(e.x, e.y), e.z);
}

// Height window the rents open in (h = fraction of the storm's height).
float undertow_wound_band(float h) {
	return smoothstep(wound_height_min, wound_height_min + 0.1, h)
			* (1.0 - smoothstep(wound_height_max - 0.1, wound_height_max, h));
}

// 1 within wound_skin_m of the eyewall's two faces (the eye face and the outer face), else 0:
// where the rents open. Keeps the cylinder-mapped wound pattern off the wall's interior.
float undertow_wall_skin(vec3 p) {
	float h = clamp(p.y / undertow_height(), 0.0, 1.0);
	float r = length(p.xz);
	float d_in = abs(r - undertow_eye_r(h) - wall_softness_m * 0.5);
	float d_out = abs(r - undertow_wall_r(h) + wall_softness_m * 0.5);
	return (1.0 - smoothstep(0.5 * wound_skin_m, wound_skin_m, min(d_in, d_out))) * undertow_wound_band(h);
}

// Two-phase clocks for advection: sample at ta and tb, blend a with weight wa. Each phase resets
// while its weight is 0, so the differential rotation never winds the pattern up.
void undertow_phases(out float ta, out float tb, out float wa) {
	float fa = fract(storm_time_s / flow_cycle_s);
	float fb = fract(storm_time_s / flow_cycle_s + 0.5);
	ta = fa * flow_cycle_s;
	tb = fb * flow_cycle_s;
	wa = 1.0 - abs(2.0 * fa - 1.0);
}

// Where the fluid at p was `t` seconds ago (rotated back by omega(r) t, rising with the updraft).
vec3 undertow_flow_point(vec3 p, float t) {
	float r = length(p.xz);
	vec2 xz = undertow_rotate(p.xz, -undertow_omega(r) * t);
	return vec3(xz.x, p.y - updraft_m_s * t, xz.y);
}

// Glimmer wounds: thin seams (rents) on the wall where held light bleeds out, in regions picked by a
// low-frequency presence field. They ride the eyewall rotation and slide DOWN (held light sinks).
// Returns the seam strength in [0, 1]; `pocket` gets the presence (held light pooled behind it).
float undertow_wound(vec3 p, out float pocket) {
	float t = storm_time_s;
	// Sampled on a fixed-radius cylinder (angle around the storm, height), so a seam is constant
	// through the wall's depth: a slit through the wall, not a 3D sparkle a raymarch would alias.
	float a = atan(p.z, p.x) - rotation_rad_s * t;
	float y = p.y + wound_sink_m_s * t;
	// Mapped at mid-wall so seams keep their proportions on both faces.
	float map_r = eye_radius_m + 0.5 * wall_thickness_m;
	vec3 q = vec3(cos(a) * map_r, y, sin(a) * map_r) / wound_scale_m;
	float n = hymn_value_noise3(q + UNDERTOW_WOUND_OFFSET) * (1.0 - UNDERTOW_WOUND_DETAIL)
			+ hymn_value_noise3(q * UNDERTOW_WOUND_LACUNARITY) * UNDERTOW_WOUND_DETAIL;
	float ridge = 1.0 - abs(2.0 * n - 1.0);
	float seam = smoothstep(1.0 - wound_width, 1.0, ridge);
	vec3 qp = vec3(cos(a) * map_r, y, sin(a) * map_r) / wound_presence_scale_m;
	float pres = hymn_value_noise3(qp + UNDERTOW_PRESENCE_OFFSET);
	pocket = smoothstep(1.0 - wound_coverage, 1.0 - wound_coverage + UNDERTOW_PRESENCE_SOFT, pres);
	return seam * pocket * wound_intensity;
}

// Lightning-like inner glow at p (linear radiance, before density weighting).
vec3 undertow_lightning(vec3 p) {
	float g = 0.0;
	float inv_r2 = 1.0 / (lightning_radius_m * lightning_radius_m);
	for (int i = 0; i < UNDERTOW_MAX_FLASHES; i++) {
		vec4 s = lightning_sites[i];
		if (s.w > 0.0) {
			vec3 d = p - s.xyz;
			g += s.w * exp(-dot(d, d) * inv_r2);
		}
	}
	return col_lightning * lightning_energy * g;
}

#endif

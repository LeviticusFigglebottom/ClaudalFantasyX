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

group_uniforms storm;
uniform vec3 storm_center = vec3(0.0);
// The storm clock (s). Driven by UndertowStorm, never by TIME.
uniform float storm_time_s = 0.0;
// 0 = asleep (the Calm), 1 = fully risen. Scales coverage and height.
uniform float storm_intensity : hint_range(0.0, 1.0) = 1.0;
// Angular speed at the eyewall (rad/s); it falls off outward as (eye / r)^rotation_falloff.
uniform float rotation_rad_s : hint_range(0.0, 0.2) = 0.012;
uniform float rotation_falloff : hint_range(0.0, 2.0) = 0.85;
// Two-phase advection period (s): differential rotation would wind the noise up without bound.
uniform float flow_cycle_s : hint_range(10.0, 7200.0) = 900.0;
uniform float updraft_m_s : hint_range(0.0, 60.0) = 9.0;

group_uniforms shape;
uniform float eye_radius_m : hint_range(50.0, 20000.0) = 1300.0;
// The eye widens upward like a stadium: radius at the top = eye_radius_m * eye_flare.
uniform float eye_flare : hint_range(1.0, 5.0) = 2.1;
uniform float eye_flare_power : hint_range(0.5, 4.0) = 1.6;
uniform float wall_thickness_m : hint_range(100.0, 20000.0) = 2700.0;
uniform float wall_taper : hint_range(0.0, 0.9) = 0.3;
uniform float wall_softness_m : hint_range(1.0, 5000.0) = 700.0;
uniform float height_m : hint_range(500.0, 30000.0) = 11500.0;
uniform float top_softness : hint_range(0.01, 0.5) = 0.12;
uniform float canopy_height_m : hint_range(0.0, 30000.0) = 8600.0;
uniform float canopy_thickness_m : hint_range(10.0, 10000.0) = 2600.0;
uniform float canopy_radius_m : hint_range(100.0, 40000.0) = 8800.0;
uniform float canopy_softness_m : hint_range(1.0, 10000.0) = 2400.0;
uniform float band_radius_m : hint_range(100.0, 40000.0) = 10500.0;
uniform float band_height_m : hint_range(10.0, 10000.0) = 3200.0;
uniform float band_arms : hint_range(0.0, 8.0) = 3.0;
// Log-spiral pitch of the rain bands: phase = theta + band_twist * ln(r / eye).
uniform float band_twist : hint_range(0.0, 8.0) = 2.6;
uniform float band_sharpness : hint_range(0.5, 8.0) = 2.2;
uniform float band_density : hint_range(0.0, 1.0) = 0.55;
// Fraction of its height a sleeping (intensity 0) storm keeps.
uniform float calm_shrink : hint_range(0.0, 1.0) = 0.55;
// The wall's foot (M2-RND-01): a skirt of lifted water and spray that flares out from the wall's base
// by skirt_reach_m at sea level and closes at skirt_height_m, so the wall stands in the sea instead
// of on a flat horizon. 0 = no skirt.
uniform float skirt_height_m : hint_range(0.0, 8000.0) = 0.0;
uniform float skirt_reach_m : hint_range(0.0, 20000.0) = 0.0;
// Envelope of the skirt (below 1 the cloud noise tears it into rags of spray and scud).
uniform float skirt_density : hint_range(0.0, 1.0) = 1.0;
// The rain bands are continuous (their troughs filled) within band_join_m of the wall, so the flank
// masses grow out of the wall instead of standing beside it. 0 = the plain spiral.
uniform float band_join_m : hint_range(0.0, 20000.0) = 0.0;
// Helical striations wound around the wall (the rotating "plates" that make a vortex read from the
// side): vertical spacing, number of helix starts, depth of the modulation and its sharpness.
uniform float striation_spacing_m : hint_range(10.0, 10000.0) = 1500.0;
uniform float striation_starts : hint_range(0.0, 8.0) = 2.0;
uniform float striation_strength : hint_range(0.0, 1.0) = 0.55;
uniform float striation_sharpness : hint_range(0.5, 8.0) = 1.6;
// Irregular striations (M2-RND-01): one low-frequency noise sample in the rotating frame bends the
// helix by up to striation_warp turns of phase and flattens it by up to striation_vary, so the plates
// read as torn fluid instead of a machined thread. Scale of that field in metres. 0, 0 = the pure helix.
uniform float striation_warp : hint_range(0.0, 2.0) = 0.0;
uniform float striation_vary : hint_range(0.0, 1.0) = 0.0;
uniform float striation_warp_scale_m : hint_range(100.0, 40000.0) = 5000.0;

group_uniforms wounds;
uniform float wound_intensity : hint_range(0.0, 4.0) = 1.0;
uniform float wound_scale_m : hint_range(10.0, 10000.0) = 1100.0;
uniform float wound_width : hint_range(0.005, 0.5) = 0.075;
uniform float wound_coverage : hint_range(0.0, 1.0) = 0.42;
// Depth of the skin on each wall face that the rents open in (m).
uniform float wound_skin_m : hint_range(10.0, 10000.0) = 900.0;
// Height window (fraction of the storm's height) the rents open in.
uniform float wound_height_min : hint_range(0.0, 1.0) = 0.15;
uniform float wound_height_max : hint_range(0.0, 1.0) = 0.85;
uniform float wound_presence_scale_m : hint_range(10.0, 40000.0) = 4200.0;
// Held light sinks: the seam pattern slides DOWN the wall at this speed.
uniform float wound_sink_m_s : hint_range(0.0, 100.0) = 5.0;
uniform vec3 col_wound : source_color = vec3(0.0497, 0.7454, 0.5776);
uniform vec3 col_held : source_color = vec3(0.2122, 0.5647, 0.6939);

group_uniforms lightning;
// xyz = storm-local position (already rotated with the wall), w = flash level (0 = dark).
uniform vec4 lightning_sites[UNDERTOW_MAX_FLASHES];
uniform float lightning_radius_m : hint_range(10.0, 20000.0) = 2100.0;
uniform vec3 col_lightning : source_color = vec3(0.552, 0.672, 1.0);
uniform float lightning_energy : hint_range(0.0, 64.0) = 2.6;
group_uniforms;

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

// Hymn of the Undertow: the maelstrom, the sea pulled down into the Undertow's eye (M1-RND-03).
// Docs: docs/kb/tech/undertow.md. Drawn on a polar disc (UndertowMeshBuilder.sea_disc) centred on
// the eye, in storm-local model space (the MeshInstance3D sits at storm_center, unrotated).
// The zone's WaterSurface is carved under it (UndertowStorm), and its look parameters (deep colour,
// foam colour, sea-glow energy) are copied in, so the funnel's rim dissolves into the zone's ocean.
//
// The profile is mirrored in GDScript by UndertowState.sea_height() (tested): keep them together.
shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_back, diffuse_burley, specular_schlick_ggx;

#include "res://game/shaders/include/globals.gdshaderinc"
#include "res://game/shaders/undertow/undertow_common.gdshaderinc"

// Water's F0 = 0.02, as Godot's SPECULAR (F0 = 0.08 * SPECULAR); same value as the water shader.
#define UNDERTOW_WATER_SPECULAR 0.25
// Finite-difference step for the vertex normal, as a fraction of the local ring spacing (m).
#define UNDERTOW_SEA_NORMAL_STEP_M 6.0
#define UNDERTOW_SWELL_OFFSET vec3(3.1, 0.0, -7.7)
#define UNDERTOW_FOAM_OFFSET vec3(-11.3, 4.9, 2.6)
// Foam ring sharpness exponent (narrow bright crests between wide gaps).
#define UNDERTOW_RING_POWER 6.0
// Anti-aliasing of the spiral patterns (row 17, the eye's rings): toward the axis the log-spiral winds
// without limit, so a pattern whose noise coordinate changes by more than this per pixel fades to its mean.
#define UNDERTOW_SEA_AA_START 0.35
#define UNDERTOW_SEA_AA_END 1.2
// Mean of the throat streak mask (smoothstep(0.45, 0.9) of value noise): what an unresolvable streak averages to.
#define UNDERTOW_THROAT_STREAK_MEAN 0.2
// Throat streaks: cycles around the axis, and the sink scale (fraction of the throat radius per noise cell).
// Long along the sink and narrow around: streaks running down into the throat, never rings from above.
#define UNDERTOW_THROAT_STREAK_AROUND 14.0
#define UNDERTOW_THROAT_STREAK_SINK 2.0

group_uniforms sea_shape;
uniform float funnel_depth_m : hint_range(0.0, 2000.0) = 260.0;
uniform float throat_radius_m : hint_range(10.0, 10000.0) = 520.0;
uniform float funnel_radius_m : hint_range(10.0, 20000.0) = 2700.0;
uniform float lip_height_m : hint_range(0.0, 200.0) = 30.0;
uniform float lip_radius_m : hint_range(0.0, 30000.0) = 3300.0;
uniform float lip_width_m : hint_range(1.0, 10000.0) = 1300.0;
uniform float swell_height_m : hint_range(0.0, 100.0) = 14.0;
uniform float swell_scale_m : hint_range(1.0, 5000.0) = 420.0;
uniform float sea_radius_m : hint_range(100.0, 60000.0) = 14000.0;
uniform float fade_start_m : hint_range(100.0, 60000.0) = 11500.0;
// Lifted above the zone ocean's rest level so the disc wins the depth test where they overlap.
uniform float sea_lift_m : hint_range(0.0, 10.0) = 1.0;

group_uniforms sea_look;
uniform vec3 col_sea_deep : source_color = vec3(0.0018, 0.0103, 0.0242);
uniform vec3 col_foam : source_color = vec3(0.855, 0.922, 0.905);
uniform float sea_darkening : hint_range(0.0, 1.0) = 0.55;
// Share of the sky reflection the storm blots out (half at the rim, all of it under the storm).
uniform float sea_reflection_dim : hint_range(0.0, 1.0) = 0.0;
uniform float sea_roughness : hint_range(0.0, 1.0) = 0.16;
uniform float foam_scale_m : hint_range(1.0, 5000.0) = 160.0;
// Streak elongation along the inflow spiral (1 = round blobs).
uniform float foam_streak : hint_range(1.0, 40.0) = 9.0;
uniform float foam_amount : hint_range(0.0, 1.0) = 0.62;
// Log-spiral pitch of the surface streamlines: angle + foam_pitch * ln(r). Large = nearly circular
// (a maelstrom's water mostly circles; it creeps inward).
uniform float foam_pitch : hint_range(0.0, 12.0) = 3.5;
uniform int foam_octaves : hint_range(1, 8) = 4;
uniform float foam_ring_spacing_m : hint_range(10.0, 5000.0) = 380.0;
uniform float foam_ring_radius_m : hint_range(10.0, 40000.0) = 5200.0;
uniform float inflow_m_s : hint_range(0.0, 60.0) = 6.0;
uniform float throat_glow_energy : hint_range(0.0, 32.0) = 2.2;
// How far the throat streaks have sunk (m): UndertowState integrates sea.glow_sink_m_s over the storm
// clock, piecewise, so the Letting (unbinding, M2-RND-05) can reverse it. Negative = risen.
uniform float glow_drift_m = 0.0;
// Night sea-glow (colour script rule 3), copied from the zone's WaterSurface.sea_glow_energy.
uniform float sea_glow_energy : hint_range(0.0, 0.15) = 0.0;
group_uniforms;

varying vec3 v_local;
varying float v_slope;

// Rest profile (no swell): the funnel (a 1 / (1 + (r / throat)^2) vortex, faded out by the funnel
// radius) plus the surge lip heaped against the wall. Mirrors UndertowState.sea_height().
float sea_profile(float r) {
	float k = r / throat_radius_m;
	float funnel = -funnel_depth_m / (1.0 + k * k) * (1.0 - smoothstep(0.35 * funnel_radius_m, funnel_radius_m, r));
	float x = (r - lip_radius_m) / lip_width_m;
	float lip = lip_height_m * exp(-x * x);
	return (funnel + lip) * storm_intensity;
}

// Storm swell: rotating with the vortex, strongest under the wall, gone at the rim.
float sea_swell(vec2 xz) {
	float r = length(xz);
	vec2 q = undertow_rotate(xz, -undertow_omega(r) * storm_time_s * 0.5);
	float n = hymn_value_noise3(vec3(q.x, storm_time_s * 0.4, q.y) / swell_scale_m + UNDERTOW_SWELL_OFFSET);
	float under_wall = 1.0 - smoothstep(lip_radius_m, fade_start_m, r);
	return (2.0 * n - 1.0) * swell_height_m * under_wall * storm_intensity;
}

float sea_height(vec2 xz) {
	return sea_profile(length(xz)) + sea_swell(xz) + sea_lift_m;
}

void vertex() {
	vec2 xz = VERTEX.xz;
	float y = sea_height(xz);
	float e = UNDERTOW_SEA_NORMAL_STEP_M + length(xz) * 0.004;
	float hx = sea_height(xz + vec2(e, 0.0));
	float hz = sea_height(xz + vec2(0.0, e));
	vec3 n = normalize(vec3(y - hx, e, y - hz));
	VERTEX.y = y;
	NORMAL = n;
	v_local = VERTEX;
	v_slope = 1.0 - n.y;
}

// Foam: streaks stretched along the inflow spiral. Coordinates are steady in spiral space (angle
// around the spiral, radius drifting inward at inflow_m_s), so the pattern never winds up.
float sea_foam(vec3 p, out vec3 q) {
	float r = max(length(p.xz), throat_radius_m * UNDERTOW_AXIS_GUARD);
	float c = atan(p.z, p.x) + foam_pitch * log(r / eye_radius_m) - rotation_rad_s * storm_time_s;
	// A fixed circle in noise space: streaks are foam_scale_m wide at the lip and converge inward.
	float around = lip_radius_m / foam_scale_m;
	float a = (r + inflow_m_s * storm_time_s) / (foam_scale_m * foam_streak);
	q = vec3(cos(c) * around, a, sin(c) * around);
	return hymn_fbm3(q + UNDERTOW_FOAM_OFFSET, foam_octaves, 2.0, 0.5);
}

void fragment() {
	vec3 p = v_local;
	float r = length(p.xz);
	// The normal per pixel, as the vertex stage derives it: interpolated across the funnel's coarse rings it
	// lit each ring as a facet, concentric specular bands in the eye (row 17).
	float e = UNDERTOW_SEA_NORMAL_STEP_M + r * 0.004;
	float h0 = sea_height(p.xz);
	vec3 n_local = normalize(vec3(h0 - sea_height(p.xz + vec2(e, 0.0)), e, h0 - sea_height(p.xz + vec2(0.0, e))));
	NORMAL = normalize((VIEW_MATRIX * MODEL_MATRIX * vec4(n_local, 0.0)).xyz);
	// Rim: dissolve into the zone ocean with a stable dither (opaque pass, no sorting problems).
	float keep = 1.0 - smoothstep(fade_start_m, sea_radius_m, r);
	if (hymn_hash12(floor(FRAGCOORD.xy)) > keep) {
		discard;
	}
	float under_storm = 1.0 - smoothstep(lip_radius_m, foam_ring_radius_m * 1.6, r);
	vec3 foam_q;
	float f = sea_foam(p, foam_q);
	// Where the spiral winds faster than a pixel can show (near the axis), the streaks average out.
	f = mix(f, 0.5, smoothstep(UNDERTOW_SEA_AA_START, UNDERTOW_SEA_AA_END, length(fwidth(foam_q))));
	// Foam rings: surge crests circling the funnel, drawn inward over time.
	float ring_phase = (r + inflow_m_s * storm_time_s) / foam_ring_spacing_m;
	float rings = pow(0.5 + 0.5 * cos(HYMN_TAU * ring_phase), UNDERTOW_RING_POWER);
	rings *= smoothstep(throat_radius_m, lip_radius_m, r) * (1.0 - smoothstep(foam_ring_radius_m * 0.7, foam_ring_radius_m, r));
	float cover = foam_amount * storm_intensity * (0.35 + 0.65 * under_storm + 0.6 * v_slope);
	float foam = smoothstep(1.0 - cover, 1.3 - cover, f + rings * 0.2);
	foam = clamp(foam, 0.0, 1.0);
	vec3 deep = col_sea_deep * (1.0 - sea_darkening * under_storm);
	ALBEDO = mix(deep, col_foam * (0.55 + 0.45 * (1.0 - v_slope)), foam);
	ROUGHNESS = mix(sea_roughness, 0.8, foam);
	// Near the wall the sky the sea would reflect is the storm itself (M2-RND-01).
	SPECULAR = UNDERTOW_WATER_SPECULAR * (1.0 - sea_reflection_dim * mix(0.5, 1.0, under_storm));
	METALLIC = 0.0;
	// Held light sinking into the throat: cyan streaks spiralling down (never rising).
	float throat = 1.0 - smoothstep(throat_radius_m * 0.3, funnel_radius_m * 0.75, r);
	// The spiral stops winding inside half the throat: from above, a spiral wound to the axis reads as rings (row 17).
	float c = atan(p.z, p.x) + foam_pitch * log(max(r, throat_radius_m * 0.5) / eye_radius_m);
	float sink = (r + glow_drift_m) / (throat_radius_m * UNDERTOW_THROAT_STREAK_SINK);
	vec3 streak_q = vec3(cos(c) * UNDERTOW_THROAT_STREAK_AROUND, sink, sin(c) * UNDERTOW_THROAT_STREAK_AROUND);
	float streak = hymn_value_noise3(streak_q);
	float streak_aa = smoothstep(UNDERTOW_SEA_AA_START, UNDERTOW_SEA_AA_END, length(fwidth(streak_q)));
	float pocket;
	float lip;
	float halo;
	float seam = undertow_wound(vec3(p.x, max(p.y, 0.0), p.z), pocket, lip, halo);
	vec3 glow = col_held * throat_glow_energy * wound_intensity * throat * mix(smoothstep(0.45, 0.9, streak), UNDERTOW_THROAT_STREAK_MEAN, streak_aa);
	glow += col_wound * seam * throat;
	// The storm's lightning lights the sea under it; foam catches it most.
	vec3 flash = undertow_lightning(vec3(p.x, 0.0, p.z)) * (0.04 + 0.5 * foam);
	vec3 world = p + storm_center;
	EMISSION = glow + flash + hymn_sea_glow_global(world, sea_glow_energy, 0.0);
}

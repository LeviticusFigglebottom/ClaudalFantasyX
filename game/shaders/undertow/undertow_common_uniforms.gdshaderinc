// Hymn of the Undertow: the storm-wide uniforms of undertow_common.gdshaderinc (M1-RND-03), split out
// (M2-RND-01) so the compute body (undertow_body_compute.glsl) can declare the same names in its UBO
// instead. tools/gen_undertow_compute.py reads this file; regenerate after editing it.

#ifndef HYMN_UNDERTOW_COMMON_UNIFORMS_GDSHADERINC
#define HYMN_UNDERTOW_COMMON_UNIFORMS_GDSHADERINC

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
// Held light sinks: how far the seam pattern has slid DOWN the wall (m). UndertowState integrates
// wounds.sink_m_s over the storm clock, piecewise, so the Letting (unbinding, M2-RND-05) can reverse it
// without the pattern jumping. Negative = risen.
uniform float wound_drift_m = 0.0;
// Torn rents (M2-RND-05): around each seam's open core, a dark lip of torn cloud rent_lip_width seam
// widths wide (its lit colour darkened by rent_lip_dark), and a wider halo (rent_halo_width) where the
// light pouring out of the rent scatters in the cloud beside it (rent_halo_energy x the seam glow).
uniform float rent_lip_width : hint_range(1.0, 8.0) = 2.5;
uniform float rent_lip_dark : hint_range(0.0, 1.0) = 0.6;
uniform float rent_halo_width : hint_range(1.0, 16.0) = 6.0;
uniform float rent_halo_energy : hint_range(0.0, 4.0) = 0.35;
uniform vec3 col_wound : source_color = vec3(0.0497, 0.7454, 0.5776);
uniform vec3 col_held : source_color = vec3(0.2122, 0.5647, 0.6939);

group_uniforms lightning;
// xyz = storm-local position (already rotated with the wall), w = flash level (0 = dark).
uniform vec4 lightning_sites[UNDERTOW_MAX_FLASHES];
uniform float lightning_radius_m : hint_range(10.0, 20000.0) = 2100.0;
uniform vec3 col_lightning : source_color = vec3(0.552, 0.672, 1.0);
uniform float lightning_energy : hint_range(0.0, 64.0) = 2.6;
group_uniforms;

#endif

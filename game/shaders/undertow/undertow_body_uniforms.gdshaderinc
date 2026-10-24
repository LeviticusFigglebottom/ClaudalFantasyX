// Hymn of the Undertow: the raymarched body's uniforms (M1-RND-03), split out (M2-RND-01) so the compute
// body (undertow_body_compute.glsl) can declare the same names in its UBO instead.
// tools/gen_undertow_compute.py reads this file; regenerate after editing it.

#ifndef HYMN_UNDERTOW_BODY_UNIFORMS_GDSHADERINC
#define HYMN_UNDERTOW_BODY_UNIFORMS_GDSHADERINC

// Lattice cells per texture side (the bake's SIZE; undertow.json "noise.texels").
uniform float noise_texels = 64.0;

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
// Longest dense step inside the wall skin the rents glow in, as a fraction of wound_skin_m (M2-RND-01).
// A skin a few hundred-metre steps deep holds 1-3 steps by the jitter's whim, and that variance is the
// rents' stipple, which TAA averages but FSR2 keeps. 1 = no refinement.
uniform float skin_step : hint_range(0.05, 1.0) = 1.0;

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
// Scud (M2-RND-01): below scud_height_m the noise is squashed vertically by scud_stretch, so the
// skirt and the low wall tear into ragged horizontal rags between the sea and the cloud base.
uniform float scud_height_m : hint_range(0.0, 8000.0) = 0.0;
uniform float scud_stretch : hint_range(1.0, 8.0) = 1.0;
// Billows (M2-RND-01): on the cloud's eroding fringe (density between 0 and 1, the surface a view sees) a
// noise field of billow_scale_m (between the cloud and detail scales, so the lumps read kilometres away) is
// folded into billow noise |2n - 1|, rounded lumps between creases, and added (zero-mean) x billow_weight.
// Its sun-ward difference over billow_shade_step_m shades each lump like a surface (billow_shade = the
// optical depth removed per unit of difference). billow_weight 0 = the M1 look.
uniform float billow_weight : hint_range(0.0, 1.0) = 0.0;
uniform float billow_scale_m : hint_range(10.0, 10000.0) = 1000.0;
uniform float billow_shade : hint_range(0.0, 8.0) = 0.0;
uniform float billow_shade_step_m : hint_range(1.0, 2000.0) = 150.0;

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
// Multiple scattering (M2-RND-01; Wrenninge et al. 2013, "Oz: The Great and Volumetric"): the sun term
// is a sum of ms_octaves octaves, octave i with energy ms_attenuation^i, extinction ms_extinction^i and
// phase eccentricity ms_eccentricity^i. Deeper light survives (lit interiors, soft silver edges, no flat
// slab of single-scattered tone). 1 octave = single scattering (the M1 look).
uniform int ms_octaves : hint_range(1, 4) = 1;
uniform float ms_attenuation : hint_range(0.0, 1.0) = 0.5;
uniform float ms_extinction : hint_range(0.0, 1.0) = 0.4;
uniform float ms_eccentricity : hint_range(0.0, 1.0) = 0.6;
// Direct light reaching the storm's lower body (a low sun has crossed the outer bands first):
// full above sun_clear_height, sun_low_floor of it at sea level.
uniform float sun_clear_height : hint_range(0.0, 1.0) = 0.8;
uniform float sun_low_floor : hint_range(0.0, 1.0) = 0.12;
// Aerial perspective toward the zone's fog colour (the storm is kilometres away).
uniform vec3 col_haze : source_color = vec3(0.35, 0.3, 0.32);
uniform float haze_visibility_m : hint_range(100.0, 200000.0) = 26000.0;
// Water lifted into the wall's foot (M2-RND-01): below water_wall_height_m the albedo turns toward
// col_water_wall (the sea's own dark slate-teal), so the base reads as a wall of dark water rather
// than more cloud. 0 = off.
uniform vec3 col_water_wall : source_color = vec3(0.03, 0.06, 0.07);
uniform float water_wall_height_m : hint_range(0.0, 8000.0) = 0.0;
uniform float water_wall_mix : hint_range(0.0, 1.0) = 0.0;

group_uniforms glow;
uniform float wound_energy : hint_range(0.0, 64.0) = 5.0;
uniform float pocket_energy : hint_range(0.0, 16.0) = 0.9;
group_uniforms;

#endif

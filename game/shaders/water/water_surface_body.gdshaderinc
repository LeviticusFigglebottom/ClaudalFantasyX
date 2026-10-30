// Hymn of the Undertow: ocean / shallows / river water surface (M1-RND-01, SPEC §8.2 item 1).
// Body include: the wrappers water_ocean*.gdshader and water_river*.gdshader set the tier and the
// flowmap switch, then include this file. Docs: docs/kb/tech/water.md.
//
//   #define HYMN_QUALITY HYMN_QUALITY_LOW   (optional; default HIGH)
//   #define HYMN_WATER_FLOWMAP              (optional; river variant, flow from tex_flow)
//   #include "res://game/shaders/water/water_surface_body.gdshaderinc"
//
// Shading model, in order:
//   geometry   Gerstner sum (water_waves.gdshaderinc), world space, driven by hymn_wind_time
//   normal     Gerstner normal (per vertex, or per pixel at High+) + wind-driven detail ripples
//   body       refraction of the opaque scene (screen texture, distorted), with the seabed lit by
//              projected caustics, then Beer-Lambert absorption over view path + sun path, plus
//              in-scattered colour (col_scatter_shallow -> col_deep with depth) lit per light
//   reflection engine sky/probe reflection (SPECULAR, Fresnel by the engine) where screen-space
//              reflection misses; a short SSR march against the depth buffer where it hits
//   foam       shoreline (depth difference) + crest (Jacobian < threshold), advected by curl noise
//              (ocean) or the flowmap (river), lit as a diffuse surface
//   SSS        sun through thin crests (light())
//   glow       night sea-glow via hymn_sea_glow() (glimmer.gdshaderinc; never cut on any tier)
//              + glimmer focus response
//
// The material is drawn in the transparent pass (it reads the screen texture) and covers the scene
// behind it fully: refraction, not alpha, is what makes it see-through.

#ifndef HYMN_WATER_SURFACE_BODY_GDSHADERINC
#define HYMN_WATER_SURFACE_BODY_GDSHADERINC

render_mode blend_mix, depth_draw_always, cull_back, world_vertex_coords;

#include "res://game/shaders/include/common.gdshaderinc"
#include "res://game/shaders/include/globals.gdshaderinc"
#include "res://game/shaders/include/glimmer.gdshaderinc"
#include "res://game/shaders/water/water_waves.gdshaderinc"
#include "res://game/shaders/water/water_caustics.gdshaderinc"

// ---------------------------------------------------------------------------------------------
// Tier table (compile time). Costs per term are measured in docs/kb/tech/water.md.
// ---------------------------------------------------------------------------------------------
#if HYMN_QUALITY >= HYMN_QUALITY_ULTRA
#define WATER_PIXEL_WAVES 1
#define WATER_DETAIL_LAYERS 3
#define WATER_SSR_STEPS 32
#define WATER_SSR_REFINE 6
#define WATER_CAUSTIC_LAYERS 2
#define WATER_CHROMATIC 1
#define WATER_CURL_FOAM 1
#elif HYMN_QUALITY >= HYMN_QUALITY_HIGH
#define WATER_PIXEL_WAVES 1
#define WATER_DETAIL_LAYERS 3
#define WATER_SSR_STEPS 20
#define WATER_SSR_REFINE 4
#define WATER_CAUSTIC_LAYERS 2
#define WATER_CHROMATIC 0
#define WATER_CURL_FOAM 1
#elif HYMN_QUALITY >= HYMN_QUALITY_MEDIUM
#define WATER_PIXEL_WAVES 0
#define WATER_DETAIL_LAYERS 2
#define WATER_SSR_STEPS 12
#define WATER_SSR_REFINE 0
#define WATER_CAUSTIC_LAYERS 1
#define WATER_CHROMATIC 0
#define WATER_CURL_FOAM 1
#else
#define WATER_PIXEL_WAVES 0
#define WATER_DETAIL_LAYERS 1
#define WATER_SSR_STEPS 0
#define WATER_SSR_REFINE 0
#define WATER_CAUSTIC_LAYERS 1
#define WATER_CHROMATIC 0
#define WATER_CURL_FOAM 0
#endif

// Water's index of refraction and its Fresnel reflectance at normal incidence ((n-1)/(n+1))^2.
#define WATER_IOR 1.333
#define WATER_F0 0.0204
// Godot maps SPECULAR s to dielectric F0 = 0.16 s^2, so s = sqrt(0.0204 / 0.16) gives water's F0.
#define WATER_SPECULAR 0.357
// Reverse-Z depth at or below this is "no geometry" (sky).
#define WATER_SKY_DEPTH 1e-6
// SSR: reflected rays must rise at least this much (world Y of the unit ray) to be marched; the
// depth-test thickness grows with distance along the ray; hits more than WATER_SSR_BELOW_M under
// the surface are seabed seen through the water, not reflections.
#define WATER_SSR_MIN_RISE 0.01
// Ripple layers: per-layer amplitude gain and frequency step (not exactly 2, to avoid alignment).
#define WATER_DETAIL_GAIN 0.5
#define WATER_DETAIL_LACUNARITY 2.03
// Foam pattern fBm, the drift of the curl field itself, and how much of the wind pushes foam.
#define WATER_FOAM_OCTAVES 3
#define WATER_FOAM_LACUNARITY 2.0
#define WATER_FOAM_GAIN 0.55
#define WATER_FOAM_FIELD_DRIFT 0.01
#define WATER_FOAM_WIND_SHARE 0.5
// Foam keeps this share far away, fading over detail_fade_m x WATER_FOAM_FADE_SCALE.
#define WATER_FOAM_FAR_KEEP 0.5
#define WATER_FOAM_FADE_SCALE 4.0
// Caustic projection along a low sun is clamped at this elevation (sine) so it cannot smear.
#define WATER_CAUSTIC_MIN_SUN_Y 0.2
// Highest coverage the shoreline foam core reaches (1 would be a solid painted line).
#define WATER_SHORE_CORE_MAX 0.8
#define WATER_SSR_THICKNESS_GROWTH 0.05
#define WATER_SSR_BELOW_M 0.05
// Phase offset of the second flow layer in two-phase advection (half a cycle).
#define WATER_FLOW_HALF 0.5

uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap, repeat_disable;
uniform sampler2D depth_tex : hint_depth_texture, filter_nearest, repeat_disable;

// Runtime feature toggles: uniform across a draw, so the branches are coherent and nearly free.
// The tier caps the cost; these let a zone (or the cost benchmark) switch a term off.
group_uniforms features;
uniform bool use_refraction = true;
uniform bool use_caustics = true;
uniform bool use_ssr = true;
uniform bool use_foam = true;
uniform bool use_sss = true;
uniform bool use_detail_normals = true;

group_uniforms waves;
uniform float time_scale : hint_range(0.0, 4.0) = 1.0;
uniform float lod_fade_wavelengths : hint_range(0.0, 200.0) = 60.0;

group_uniforms colour;
// Scattered colour seen through deep water (color script "deep color"); linear via source_color.
uniform vec3 col_deep : source_color = vec3(0.082, 0.412, 0.627);
// Scattered colour over shallow floors (art ramp: lagoon teal at 1-4 m); it hands over to
// col_deep as the vertical depth grows to scatter_depth_m (reef blue by ~15 m).
uniform vec3 col_scatter_shallow : source_color = vec3(0.122, 0.639, 0.651);
uniform float scatter_depth_m : hint_range(0.1, 100.0) = 12.0;
// Per-channel extinction, m^-1 (color script "Water absorption"): transmittance = exp(-sigma d).
uniform vec3 absorption_per_m = vec3(0.45, 0.065, 0.045);
// Multiplies absorption_per_m: one knob for murk without retyping the colour-script triple.
uniform float absorption_scale : hint_range(0.0, 8.0) = 1.0;
// Light also travels down to the seabed before it comes back up (vertical depth x this).
uniform float sun_path_factor : hint_range(0.0, 2.0) = 1.0;
// Single-scattering albedo of the water column: the in-scattered colour is output as diffuse
// ALBEDO, so the engine lights it with the zone's real sun, moon, lamps, ambient and shadows.
uniform float scatter_energy : hint_range(0.0, 1.0) = 0.25;
// Fraction of scatter that ignores the sun angle (wave faces turned away still glow a little).
uniform float scatter_wrap : hint_range(0.0, 1.0) = 0.5;
// Path length used where the depth buffer shows sky (open sea with no seabed in view), metres.
uniform float max_path_m : hint_range(1.0, 1000.0) = 200.0;

group_uniforms refraction;
uniform float refraction_strength : hint_range(0.0, 0.2) = 0.04;
// Depth over which the distortion ramps in (no distortion at the waterline itself), metres.
uniform float refraction_depth_m : hint_range(0.01, 10.0) = 1.5;
// Ultra only: extra offset for R and B relative to G (dispersion).
uniform float refraction_dispersion : hint_range(0.0, 0.5) = 0.12;

group_uniforms reflection;
uniform float roughness_near : hint_range(0.0, 1.0) = 0.03;
uniform float roughness_far : hint_range(0.0, 1.0) = 0.12;
// Distance at which roughness reaches roughness_far (stands in for sub-pixel wave slopes), metres.
uniform float roughness_far_m : hint_range(1.0, 5000.0) = 600.0;
uniform float ssr_max_distance_m : hint_range(1.0, 500.0) = 60.0;
uniform float ssr_thickness_m : hint_range(0.01, 10.0) = 0.8;
// Step distribution: t_i = max_distance * (i / steps)^ssr_step_exponent (denser near the surface).
uniform float ssr_step_exponent : hint_range(1.0, 3.0) = 1.8;
// Screen-edge fade width for SSR hits, in UV units.
uniform float ssr_edge_fade : hint_range(0.0, 0.5) = 0.08;
uniform float glint_strength : hint_range(0.0, 4.0) = 1.0;
// The sun is a disc, not a point: clamp the roughness the sun glint sees so it never aliases.
uniform float glint_min_roughness : hint_range(0.01, 0.5) = 0.06;

group_uniforms detail;
uniform float detail_scale_per_m : hint_range(0.01, 10.0) = 0.55;
uniform float detail_strength : hint_range(0.0, 2.0) = 0.22;
uniform float detail_speed_m_s : hint_range(0.0, 4.0) = 0.35;
// Detail normals fade out with distance (they alias into glitter otherwise), metres.
uniform float detail_fade_m : hint_range(1.0, 2000.0) = 120.0;
// Fallback travel direction (world XZ) of ripples when hymn_wind is calm.
uniform vec2 calm_direction = vec2(0.6, -0.8);
// Wind speed (m/s) at which ripples reach wind_chop x their calm strength.
uniform float wind_reference_m_s : hint_range(0.1, 40.0) = 8.0;
uniform float wind_chop : hint_range(1.0, 4.0) = 1.6;

group_uniforms foam;
uniform vec3 col_foam : source_color = vec3(0.855, 0.922, 0.906);
// Vertical water depth (not distance!) of the solid foam line at the shore and of the lacy wash
// zone beyond it. On a 1:30 beach, 0.1 m of depth is already 3 m of beach.
uniform float foam_shore_width_m : hint_range(0.0, 2.0) = 0.03;
uniform float foam_wash_depth_m : hint_range(0.0, 4.0) = 0.3;
// Wash bands rolling in toward the shore (spacing in metres of depth).
uniform float foam_band_spacing_m : hint_range(0.01, 4.0) = 0.07;
uniform float foam_band_speed : hint_range(0.0, 4.0) = 0.6;
uniform float foam_band_strength : hint_range(0.0, 1.0) = 0.45;
// Horizontal Jacobian below this makes crest foam; softness widens the ramp.
uniform float foam_crest_threshold : hint_range(0.0, 1.5) = 0.8;
uniform float foam_crest_softness : hint_range(0.01, 1.0) = 0.25;
uniform float foam_scale_per_m : hint_range(0.05, 20.0) = 1.6;
uniform float foam_softness : hint_range(0.01, 1.0) = 0.12;
// Curl-noise advection of the foam pattern (ocean) and its cycle length.
uniform float foam_flow_scale_per_m : hint_range(0.001, 2.0) = 0.07;
uniform float foam_flow_speed_m_s : hint_range(0.0, 4.0) = 0.25;
uniform float flow_cycle_s : hint_range(0.5, 20.0) = 4.0;
uniform float foam_roughness : hint_range(0.0, 1.0) = 0.75;

// Mean coverage of the streak profile below (line smoothstep(0.6, 0.88) x flecks) over value noise:
// what unresolved streaks average to (measured: 0.114 over 5e5 samples).
#define WATER_STREAK_MEAN 0.11
// Patch size of the streak gate, in streak lengths.
#define WATER_STREAK_PATCH 0.6
// Meander (M2-RND-01): the lines wander across by up to this many streak widths, over a field this
// many streak lengths wide, so they read as windrows on a moving sea instead of ruled rails.
#define WATER_STREAK_MEANDER 3.0
#define WATER_STREAK_MEANDER_SCALE 0.4
// Flecks: along its length a line breaks into foam flecks this many per streak length, keeping
// WATER_STREAK_FLECK_FLOOR of its coverage between them.
#define WATER_STREAK_FLECKS 10.0
#define WATER_STREAK_FLECK_FLOOR 0.3

group_uniforms storm;
// The sea answering the Undertow (M2-RND-01). UndertowStorm sets these on its zone water: within
// storm_reach_m of the storm's centre the sea darkens toward it (body, in-scatter and the reflected
// sky, which the storm itself blots out), turns choppier and rougher, and carries wind streaks drawn
// in toward the storm. storm_reach_m 0 (the default, no storm) changes nothing.
uniform vec2 storm_center_xz = vec2(0.0);
uniform float storm_reach_m : hint_range(0.0, 200000.0) = 0.0;
uniform float storm_darken : hint_range(0.0, 1.0) = 0.0;
// How much of the reflected sky the storm blots out near it (it fills that sky).
uniform float storm_reflection_dim : hint_range(0.0, 1.0) = 0.0;
uniform float storm_chop : hint_range(0.0, 8.0) = 0.0;
uniform float storm_roughness : hint_range(0.0, 1.0) = 0.0;
uniform float storm_streak_amount : hint_range(0.0, 1.0) = 0.0;
uniform float storm_streak_length_m : hint_range(1.0, 5000.0) = 240.0;
uniform float storm_streak_width_m : hint_range(0.1, 500.0) = 9.0;
uniform float storm_streak_fade_m : hint_range(10.0, 50000.0) = 2500.0;
uniform float storm_streak_drift : hint_range(0.0, 4.0) = 0.05;
// The storm in the reflection (M2-RND-05; UndertowEvents pushes these). The engine's sky reflection
// never sees the storm, so the sea reflects it here:
// - storm_body_tex (the half-res body's premultiplied frame, ready before the water draws): the
//   reflected ray's point at the storm's distance is projected to the screen and the storm's own
//   pixel there is the reflection (its wounds and lightning included).
// - Off screen, or without that texture (Low's shells, Ultra's full-resolution body), an impostor: a
//   vertical cylinder from the sea to storm_reflect_height_m whose radius widens from
//   storm_reflect_wall_m.x to .y (the wall), and the canopy's ring (radius, height above the sea,
//   thickness), coloured low at the sea to high at the top, plus glow, hazed by distance.
// Where the storm is reflected, the engine's sky reflection gives way to it. storm_reflect 0 = off.
uniform float storm_reflect : hint_range(0.0, 1.0) = 0.0;
uniform sampler2D storm_body_tex : filter_linear, repeat_disable;
uniform bool storm_body_ready = false;
uniform vec3 storm_reflect_center = vec3(0.0);
uniform vec2 storm_reflect_wall_m = vec2(4000.0, 4000.0);
uniform float storm_reflect_height_m = 11500.0;
uniform vec3 storm_reflect_canopy = vec3(0.0);
uniform float storm_reflect_soft_m = 600.0;
uniform vec3 storm_reflect_low : source_color = vec3(0.0);
uniform vec3 storm_reflect_high : source_color = vec3(0.0);
uniform vec3 storm_reflect_glow : source_color = vec3(0.0);
uniform vec3 storm_reflect_haze : source_color = vec3(0.35, 0.3, 0.32);
uniform float storm_reflect_visibility_m = 26000.0;

group_uniforms caustics;
uniform float caustic_strength : hint_range(0.0, 8.0) = 1.6;
uniform float caustic_scale_per_m : hint_range(0.05, 10.0) = 0.9;
uniform float caustic_speed : hint_range(0.0, 4.0) = 0.7;
// Line half-width in pattern units at shallow depth; grows with depth (light defocuses), faster
// the deeper it gets: width + blur * depth * (1 + depth / falloff).
uniform float caustic_width : hint_range(0.005, 0.5) = 0.06;
uniform float caustic_blur_per_m : hint_range(0.0, 0.2) = 0.02;
// Depth band (art: sharp and bright in 0.3-4 m): ramp in over fade_in, decay with falloff.
uniform float caustic_fade_in_m : hint_range(0.01, 2.0) = 0.25;
uniform float caustic_falloff_m : hint_range(0.1, 40.0) = 6.0;
// Ultra: per-channel scale spread (rainbow fringes on the lines).
uniform float caustic_chroma : hint_range(0.0, 0.1) = 0.025;
// Contrast also fades with view distance (far caustics average out; no tiling across the lagoon).
uniform float caustic_view_fade_m : hint_range(1.0, 500.0) = 30.0;
// 0 = procedural web (water_caustics.gdshaderinc); 1 = an authored tiling pattern in caustic_tex
// (R = brightness; e.g. light through Ilun's nets), drawn as two drifting layers combined like the
// procedural ones.
uniform int caustic_pattern : hint_enum("Procedural", "Texture") = 0;
uniform sampler2D caustic_tex : hint_default_black, filter_linear_mipmap, repeat_enable;
// Mean of caustic_tex's two-layer pattern (the procedural mean is fitted in the include). It is
// subtracted so the floor's average brightness is unchanged and only the contrast is added.
uniform float caustic_mean : hint_range(0.0, 2.0) = 0.18;

group_uniforms subsurface;
uniform vec3 col_sss : source_color = vec3(0.247, 0.816, 0.788);
uniform float sss_strength : hint_range(0.0, 8.0) = 1.4;
uniform float sss_power : hint_range(1.0, 16.0) = 4.0;
uniform float sss_distortion : hint_range(0.0, 1.0) = 0.35;
// Crest thickness term: crest = smoothstep(lo, hi, height / water_amplitude_sum).
uniform float sss_crest_lo : hint_range(-1.0, 1.0) = 0.0;
uniform float sss_crest_hi : hint_range(-1.0, 1.0) = 0.35;
// The crest term fades with the steepness of the view ray (M1-RND-18): full at |view.y| below lo
// (grazing low cameras), gone above hi. A high camera (40 m up, 39 deg down) otherwise lit every
// crest of the swell into pale-teal sheets over deep water. sin(6 deg) and sin(16 deg).
uniform float sss_view_fade_lo : hint_range(0.0, 1.0) = 0.10;
uniform float sss_view_fade_hi : hint_range(0.0, 1.0) = 0.28;
// ...and only for a camera this high above the shaded water (metres, from lo to hi): a 5.5 m camera
// sees its near water steeply too, and keeps its crests (the low shots stay as approved).
uniform float sss_view_height_lo_m : hint_range(0.0, 500.0) = 10.0;
uniform float sss_view_height_hi_m : hint_range(0.0, 500.0) = 25.0;
// The lift the crest SSS used to give deep water seen from above, given back evenly: the deep end of
// the in-scatter (col_deep) grows by this share over the same view-steepness ramp, never as crest
// patches, and the shallow bands keep their colour. 0 = off.
uniform float scatter_view_lift : hint_range(0.0, 4.0) = 1.5;
// sss_strength at which scatter_view_lift was tuned (the default): weaker SSS gets less lift.
#define SSS_LIFT_TUNED_STRENGTH 1.4

group_uniforms sea_glow;
// Color script rule 3: this surface's own sea-glow energy (0.04-0.15 at night; 0 = use the zone's
// hymn_zone_sea_glow). Colour, noise and the column build-up come from glimmer.gdshaderinc. Not gated
// by hymn_glimmer.a; a zone hard off (ending_dock) wins over this value. Never cut by a tier.
uniform float sea_glow_energy : hint_range(0.0, 0.15) = 0.0;
// How strongly the water brightens under hymn_glimmer_focus (motes gathering).
uniform float glimmer_response : hint_range(0.0, 4.0) = 0.6;

#ifdef HYMN_WATER_FLOWMAP
group_uniforms flow;
// RG = flow direction in UV space, 0.5 = still (data texture: never source_color).
uniform sampler2D tex_flow : hint_default_black, filter_linear, repeat_enable;
uniform float flow_speed_m_s : hint_range(0.0, 8.0) = 1.2;
#endif
group_uniforms;

varying vec2 v_rest_xz;
varying float v_jacobian;
varying float v_height;
// Fragment -> light.
varying float v_crest;
varying float v_foam;

float water_time() {
	return hymn_wind_time * time_scale;
}

// Coverage of the storm impostor along the world ray o + t d (M2-RND-05): how much of the storm the
// reflected ray meets (0..1, soft at the silhouette), the hit's height fraction and distance.
float water_storm_hit(vec3 o, vec3 d, out float h, out float dist) {
	vec3 q = o - storm_reflect_center;
	vec2 dxz = d.xz;
	float dd = max(dot(dxz, dxz), 1e-6);
	float tc = -dot(q.xz, dxz) / dd;
	h = 0.0;
	dist = 0.0;
	if (tc <= 0.0) {
		return 0.0;
	}
	float miss = length(q.xz + dxz * tc);
	float cover = 0.0;
	// The wall: the ray's height where it passes closest (rays rise from the sea, so this is low).
	float y = q.y + d.y * tc;
	float hw = clamp(y / storm_reflect_height_m, 0.0, 1.0);
	float r = mix(storm_reflect_wall_m.x, storm_reflect_wall_m.y, hw);
	float in_wall = 1.0 - smoothstep(r - storm_reflect_soft_m, r + storm_reflect_soft_m, miss);
	float tall = 1.0 - smoothstep(storm_reflect_height_m * 0.9, storm_reflect_height_m, y);
	cover = in_wall * tall * step(0.0, y);
	h = hw;
	dist = tc * sqrt(dd);
	// The canopy ring: where the ray crosses the canopy's height, inside its radius.
	if (storm_reflect_canopy.x > 0.0 && d.y > 1e-4) {
		float tk = (storm_reflect_canopy.y - q.y) / d.y;
		if (tk > 0.0) {
			float rk = length(q.xz + dxz * tk);
			float ck = (1.0 - smoothstep(storm_reflect_canopy.x - storm_reflect_soft_m * 4.0, storm_reflect_canopy.x, rk));
			if (ck > cover) {
				cover = ck;
				h = 1.0;
				dist = tk * length(d);
			}
		}
	}
	return cover;
}

void vertex() {
	vec3 rest = VERTEX;
	float dist = length(rest.xz - CAMERA_POSITION_WORLD.xz);
	vec3 disp;
	vec3 n;
	float jac;
	hymn_water_gerstner(rest.xz, water_time(), dist, lod_fade_wavelengths, disp, n, jac);
	VERTEX = rest + disp;
	NORMAL = n;
	v_rest_xz = rest.xz;
	v_jacobian = jac;
	v_height = disp.y;
}

// View-space position of the opaque scene at uv (reverse-Z depth buffer).
vec3 scene_view_pos(vec2 uv, mat4 inv_proj) {
	float d = texture(depth_tex, uv).r;
	vec4 v = inv_proj * vec4(uv * 2.0 - 1.0, max(d, WATER_SKY_DEPTH), 1.0);
	return v.xyz / v.w;
}

// Ring ripples (M4-A2P-047, Ch14's first ripple in four hundred years): up to WATER_RIPPLE_MAX sources set by a
// RippleField (game/world/water/ripple_field.gd), each (x, z, start s, height m). A source sends one ring outward at
// ripple_speed_m_s: a short wave packet ripple_width_m wide, fading over ripple_decay_s and with distance. Its own
// clock (ripple_now_s), so a still mirror (time_scale 0) still carries them. ripple_count 0 costs nothing.
#define WATER_RIPPLE_MAX 16
uniform vec4 ripple_sources[WATER_RIPPLE_MAX];
uniform int ripple_count = 0;
uniform float ripple_now_s = 0.0;
uniform float ripple_speed_m_s : hint_range(0.05, 10.0) = 1.4;
uniform float ripple_wavelength_m : hint_range(0.05, 5.0) = 0.7;
uniform float ripple_width_m : hint_range(0.05, 10.0) = 1.1;
uniform float ripple_decay_s : hint_range(0.1, 60.0) = 6.0;

// The rings' slope (d height / dx, d height / dz) at world `p`.
vec2 ring_slope(vec2 p) {
	vec2 s = vec2(0.0);
	float k = 6.2831853 / ripple_wavelength_m;
	for (int i = 0; i < min(ripple_count, WATER_RIPPLE_MAX); i++) {
		vec4 r = ripple_sources[i];
		float age = ripple_now_s - r.z;
		if (r.w <= 0.0 || age < 0.0) {
			continue;
		}
		vec2 d = p - r.xy;
		float dist = length(d);
		float x = dist - ripple_speed_m_s * age;
		float env = exp(-x * x / (ripple_width_m * ripple_width_m)) * exp(-age / ripple_decay_s) / sqrt(1.0 + dist);
		s += d / max(dist, HYMN_EPSILON) * (r.w * env * k * cos(k * x));
	}
	return s;
}

// Wind-driven ripple slope (d height / dx, d height / dz) from layered derivative noise.
vec2 detail_slope(vec2 p, vec2 dir, float t) {
	vec2 slope = vec2(0.0);
	float amp = 1.0;
	float freq = 1.0;
	mat2 rot = HYMN_FBM_ROT2;
	vec2 d = dir;
	for (int i = 0; i < WATER_DETAIL_LAYERS; i++) {
		vec2 q = p * detail_scale_per_m * freq - d * t * detail_speed_m_s * detail_scale_per_m * freq;
		vec3 nd = hymn_value_noise2_d(q);
		slope += nd.yz * amp * freq * detail_scale_per_m;
		amp *= WATER_DETAIL_GAIN;
		freq *= WATER_DETAIL_LACUNARITY;
		d = rot * d;
	}
	return slope;
}

#if WATER_SSR_STEPS > 0
// Screen-space reflection: marches view-space ray `r` from `vtx` against the depth buffer. Returns the
// hit weight (0 = miss; screen-edge and distance fades folded in), the reflected colour in `col` and
// the hit's world position in `hit_world`. `water_y` is the water's world height (only geometry above
// the water is reflected).
float water_ssr_march(vec3 vtx, vec3 r, float water_y, mat4 proj, mat4 inv_proj, mat4 inv_view, out vec3 col,
		out vec3 hit_world) {
	col = vec3(0.0);
	hit_world = vec3(0.0);
	float prev_t = 0.0;
	for (int i = 1; i <= WATER_SSR_STEPS; i++) {
		float ti = ssr_max_distance_m * pow(float(i) / float(WATER_SSR_STEPS), ssr_step_exponent);
		vec3 p = vtx + r * ti;
		vec4 clip = proj * vec4(p, 1.0);
		if (clip.w <= 0.0) {
			return 0.0;
		}
		vec2 uv = clip.xy / clip.w * 0.5 + 0.5;
		if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
			return 0.0;
		}
		float sz = scene_view_pos(uv, inv_proj).z;
		if (p.z < sz) {
			float lo = prev_t;
			float hi = ti;
#if WATER_SSR_REFINE > 0
			for (int j = 0; j < WATER_SSR_REFINE; j++) {
				float mid = 0.5 * (lo + hi);
				vec3 pm = vtx + r * mid;
				vec4 cm = proj * vec4(pm, 1.0);
				vec2 um = cm.xy / cm.w * 0.5 + 0.5;
				if (pm.z < scene_view_pos(um, inv_proj).z) {
					hi = mid;
				} else {
					lo = mid;
				}
			}
#endif
			vec3 ph = vtx + r * hi;
			vec4 ch = proj * vec4(ph, 1.0);
			vec2 uh = ch.xy / ch.w * 0.5 + 0.5;
			float gap = scene_view_pos(uh, inv_proj).z - ph.z;
			hit_world = (inv_view * vec4(ph, 1.0)).xyz;
			// Only geometry above the water can be reflected by it.
			if (gap < ssr_thickness_m + hi * WATER_SSR_THICKNESS_GROWTH && hit_world.y > water_y - WATER_SSR_BELOW_M) {
				vec2 edge = smoothstep(vec2(0.0), vec2(ssr_edge_fade), uh)
						* smoothstep(vec2(0.0), vec2(ssr_edge_fade), 1.0 - uh);
				col = textureLod(screen_tex, uh, 0.0).rgb;
				return edge.x * edge.y * (1.0 - hi / ssr_max_distance_m);
			}
			return 0.0;
		}
		prev_t = ti;
	}
	return 0.0;
}

// Still actors (M3-RND-03, hymn_still_actor_*): vertical capsules, treated as cylinders. True when world
// ray (o, d) passes through one of them.
bool water_still_cylinder(vec3 o, vec3 d, vec4 c, float h) {
	if (c.w <= 0.0) {
		return false;
	}
	vec2 oc = o.xz - c.xz;
	float a = dot(d.xz, d.xz);
	float b = dot(oc, d.xz);
	float k = dot(oc, oc) - c.w * c.w;
	float disc = b * b - a * k;
	if (a < HYMN_EPSILON || disc < 0.0) {
		return false;
	}
	float sq = sqrt(disc);
	float t0 = max((-b - sq) / a, 0.0);
	float t1 = (-b + sq) / a;
	if (t1 < 0.0) {
		return false;
	}
	// The ray's height over [t0, t1] must overlap the capsule's [base, base + h].
	float y0 = o.y + d.y * t0;
	float y1 = o.y + d.y * t1;
	return max(y0, y1) >= c.y && min(y0, y1) <= c.y + h;
}

bool water_still_ray(vec3 o, vec3 d) {
	return water_still_cylinder(o, d, hymn_still_actor_0, hymn_still_actor_heights.x)
			|| water_still_cylinder(o, d, hymn_still_actor_1, hymn_still_actor_heights.y);
}

bool water_still_inside(vec3 p, vec4 c, float h) {
	return c.w > 0.0 && distance(p.xz, c.xz) <= c.w && p.y >= c.y && p.y <= c.y + h;
}

bool water_still_point(vec3 p) {
	return water_still_inside(p, hymn_still_actor_0, hymn_still_actor_heights.x)
			|| water_still_inside(p, hymn_still_actor_1, hymn_still_actor_heights.y);
}
#endif

float foam_pattern(vec2 p) {
	return hymn_fbm2(p * foam_scale_per_m, WATER_FOAM_OCTAVES, WATER_FOAM_LACUNARITY, WATER_FOAM_GAIN);
}

// Two-phase advection of the foam pattern along `flow` (m/s): no stretching, no visible reset.
float advected_foam(vec2 p, vec2 flow, float t) {
	float ph0 = fract(t / flow_cycle_s);
	float ph1 = fract(t / flow_cycle_s + WATER_FLOW_HALF);
	float a = foam_pattern(p - flow * ph0 * flow_cycle_s);
	float b = foam_pattern(p - flow * ph1 * flow_cycle_s + vec2(WATER_FLOW_HALF));
	float w = abs(1.0 - 2.0 * ph0);
	return mix(b, a, w);
}

// The authored-texture pattern: two layers of caustic_tex drifting apart, combined like the web.
float caustic_tex_pattern(vec2 q, float ts) {
	float l1 = texture(caustic_tex, q + vec2(0.11, 0.07) * ts).r;
	float l2 = texture(caustic_tex, HYMN_FBM_ROT2 * q * HYMN_CAUSTIC_LAYER2_SCALE - vec2(0.05, 0.13) * ts).r;
	return hymn_caustic_combine(l1, l2);
}

vec3 caustic_light(vec2 p, float depth, float view_dist, float t) {
	float width = caustic_width + caustic_blur_per_m * depth * (1.0 + depth / caustic_falloff_m);
	vec2 q = p * caustic_scale_per_m;
	float ts = t * caustic_speed;
	float band = smoothstep(0.0, caustic_fade_in_m, depth) * exp(-depth / caustic_falloff_m)
			* exp(-view_dist / caustic_view_fade_m);
	if (caustic_pattern == 1) {
		return vec3(caustic_tex_pattern(q, ts) - caustic_mean) * band;
	}
	float mean = hymn_caustic_mean(width, WATER_CAUSTIC_LAYERS);
#if WATER_CHROMATIC
	vec3 c = vec3(
			hymn_caustic(q * (1.0 - caustic_chroma), ts, width, WATER_CAUSTIC_LAYERS),
			hymn_caustic(q, ts, width, WATER_CAUSTIC_LAYERS),
			hymn_caustic(q * (1.0 + caustic_chroma), ts, width, WATER_CAUSTIC_LAYERS));
#else
	vec3 c = vec3(hymn_caustic(q, ts, width, WATER_CAUSTIC_LAYERS));
#endif
	// Caustics redistribute light, they do not add it: modulate around the pattern's mean.
	return (c - mean) * band;
}

void fragment() {
	float t = water_time();
	vec3 world = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float view_dist = length(VERTEX);

	// --- Normal --------------------------------------------------------------------------------
	vec3 n_geo;
	float jac;
#if WATER_PIXEL_WAVES
	vec3 disp_px;
	hymn_water_gerstner(v_rest_xz, t, view_dist, lod_fade_wavelengths, disp_px, n_geo, jac);
#else
	n_geo = normalize((INV_VIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
	jac = v_jacobian;
#endif
	vec2 wind_xz = hymn_wind.xz;
	float wind_speed = length(wind_xz);
	vec2 wind_dir = wind_speed > HYMN_EPSILON ? wind_xz / wind_speed : normalize(calm_direction);
	float chop = mix(1.0, wind_chop, clamp(wind_speed / wind_reference_m_s, 0.0, 1.0));
	// Storm response weight (1 at the storm, 0 at storm_reach_m) and the inflow direction toward it.
	float storm_k = 0.0;
	vec2 to_storm = vec2(0.0, 1.0);
	if (storm_reach_m > 0.0) {
		vec2 dv = storm_center_xz - world.xz;
		float d_storm = length(dv);
		storm_k = 1.0 - smoothstep(0.0, storm_reach_m, d_storm);
		to_storm = dv / max(d_storm, HYMN_EPSILON);
		chop *= 1.0 + storm_chop * storm_k;
	}
	vec3 n_world = n_geo;
	if (use_detail_normals) {
		vec2 slope;
#ifdef HYMN_WATER_FLOWMAP
		vec2 flow_uv = texture(tex_flow, UV).rg * 2.0 - 1.0;
		float ph0 = fract(t / flow_cycle_s);
		float ph1 = fract(t / flow_cycle_s + WATER_FLOW_HALF);
		vec2 flow_m = flow_uv * flow_speed_m_s;
		vec2 s0 = detail_slope(world.xz - flow_m * ph0 * flow_cycle_s, wind_dir, t);
		vec2 s1 = detail_slope(world.xz - flow_m * ph1 * flow_cycle_s + vec2(WATER_FLOW_HALF), wind_dir, t);
		slope = mix(s1, s0, abs(1.0 - 2.0 * ph0));
#else
		slope = detail_slope(world.xz, wind_dir, t);
#endif
		float fade = exp(-view_dist / detail_fade_m);
		n_world = normalize(n_geo + vec3(-slope.x, 0.0, -slope.y) * detail_strength * chop * fade);
	}
	if (ripple_count > 0) {
		vec2 rs = ring_slope(world.xz);
		n_world = normalize(n_world + vec3(-rs.x, 0.0, -rs.y));
	}
	vec3 n_view = normalize((VIEW_MATRIX * vec4(n_world, 0.0)).xyz);
	float ndv = clamp(dot(n_view, VIEW), 0.0, 1.0);

	// --- Depth: vertical depth for foam, view path for absorption ------------------------------
	vec3 scene0 = scene_view_pos(SCREEN_UV, INV_PROJECTION_MATRIX);
	vec3 scene0_world = (INV_VIEW_MATRIX * vec4(scene0, 1.0)).xyz;
	float vdepth0 = max(world.y - scene0_world.y, 0.0);

	// --- Refraction -----------------------------------------------------------------------------
	vec2 uv_r = SCREEN_UV;
	if (use_refraction) {
		float ramp = clamp(vdepth0 / refraction_depth_m, 0.0, 1.0);
		vec2 offs = n_view.xy * refraction_strength * ramp;
		vec2 cand = clamp(SCREEN_UV - offs, vec2(0.0), vec2(1.0));
		// Reject samples of geometry in front of the water (it would leak into the refraction).
		if (scene_view_pos(cand, INV_PROJECTION_MATRIX).z < VERTEX.z) {
			uv_r = cand;
		}
	}
	vec3 scene = scene_view_pos(uv_r, INV_PROJECTION_MATRIX);
	vec3 scene_world = (INV_VIEW_MATRIX * vec4(scene, 1.0)).xyz;
	bool sky_behind = texture(depth_tex, uv_r).r <= WATER_SKY_DEPTH;
	float vdepth = sky_behind ? max_path_m : max(world.y - scene_world.y, 0.0);
	// Underwater path of the view ray. The screen-space ray is unbent, but real light refracts
	// toward the normal (Snell, IOR 1.333), so at grazing angles the true path to the floor is
	// much shorter than the unbent one: use vertical depth / cos(refracted angle), capped by the
	// unbent length. This also keys colour to vertical depth, as the art ramp is written.
	float sin_t = sqrt(max(1.0 - ndv * ndv, 0.0)) / WATER_IOR;
	float cos_t = sqrt(max(1.0 - sin_t * sin_t, 0.0));
	float path = sky_behind ? max_path_m : min(max(length(scene) - view_dist, 0.0), vdepth / cos_t);

	vec3 refr;
#if WATER_CHROMATIC
	if (use_refraction) {
		vec2 d_uv = (uv_r - SCREEN_UV) * refraction_dispersion;
		refr = vec3(
				textureLod(screen_tex, uv_r - d_uv, 0.0).r,
				textureLod(screen_tex, uv_r, 0.0).g,
				textureLod(screen_tex, uv_r + d_uv, 0.0).b);
	} else {
		refr = textureLod(screen_tex, uv_r, 0.0).rgb;
	}
#else
	refr = textureLod(screen_tex, uv_r, 0.0).rgb;
#endif

	// --- Caustics: projected along the sun onto whatever the refraction sees -----------------
	vec3 sun = normalize(hymn_sun_direction);
	if (use_caustics && !sky_behind && sun.y > 0.0) {
		vec2 entry = scene_world.xz + sun.xz * (vdepth / max(sun.y, WATER_CAUSTIC_MIN_SUN_Y));
		vec3 c = caustic_light(entry, vdepth, view_dist, t);
		// Multiplicative on the lit seabed: shadowed seabed stays dark, as real caustics do.
		refr *= max(vec3(1.0) + caustic_strength * c * sun.y, vec3(0.0));
	}

	// --- Absorption and scattering (Beer-Lambert per channel) ---------------------------------
	vec3 sigma = absorption_per_m * absorption_scale;
	vec3 trans = exp(-sigma * (path + vdepth * sun_path_factor));
	vec3 inscatter = 1.0 - exp(-sigma * path);
	vec3 body = refr * trans;

	// --- Foam -----------------------------------------------------------------------------------
	float foam = 0.0;
	if (use_foam) {
		float shore = 1.0 - smoothstep(0.0, foam_shore_width_m, vdepth0);
		float bands = 0.5 + 0.5 * sin(HYMN_TAU * (vdepth0 / foam_band_spacing_m + t * foam_band_speed));
		float wash = 1.0 - smoothstep(0.0, foam_wash_depth_m, vdepth0);
		// Capping the core below 1 keeps holes in the foam even at the waterline (lace, not paint).
		float shore_cov = max(shore * WATER_SHORE_CORE_MAX, wash * bands * foam_band_strength);
		float crest_cov = 1.0 - smoothstep(foam_crest_threshold - foam_crest_softness, foam_crest_threshold, jac);
		float cover = clamp(max(shore_cov, crest_cov * chop), 0.0, 1.0);
#ifdef HYMN_WATER_FLOWMAP
		vec2 flow = (texture(tex_flow, UV).rg * 2.0 - 1.0) * flow_speed_m_s;
		float pattern = advected_foam(world.xz, flow, t);
#elif WATER_CURL_FOAM
		vec2 flow = hymn_curl_noise2(world.xz * foam_flow_scale_per_m + vec2(t * WATER_FOAM_FIELD_DRIFT)) * foam_flow_speed_m_s;
		flow += wind_dir * foam_flow_speed_m_s * WATER_FOAM_WIND_SHARE;
		float pattern = advected_foam(world.xz, flow, t);
#else
		float pattern = foam_pattern(world.xz - wind_dir * t * foam_flow_speed_m_s);
#endif
		foam = smoothstep(1.0 - cover, 1.0 - cover + foam_softness, pattern) * cover;
		// Far foam thins to half (it is sub-pixel lace there) instead of vanishing.
		foam *= mix(WATER_FOAM_FAR_KEEP, 1.0, exp(-view_dist / (detail_fade_m * WATER_FOAM_FADE_SCALE)));
	}

	// Wind streaks toward the storm: foam lines stretched along the inflow (every tier).
	if (storm_k > 0.0 && storm_streak_amount > 0.0) {
		vec2 across = vec2(-to_storm.y, to_storm.x);
		vec2 q = vec2(dot(world.xz, to_storm) / storm_streak_length_m, dot(world.xz, across) / storm_streak_width_m);
		q.y += WATER_STREAK_MEANDER
				* (2.0 * hymn_value_noise2(world.xz / (storm_streak_length_m * WATER_STREAK_MEANDER_SCALE)) - 1.0);
		vec2 qd = q + vec2(t * storm_streak_drift, 0.0);
		float sn = hymn_value_noise2(qd);
		// Past a few pixels per streak the lines alias: fade them to their mean coverage instead.
		float resolved = 1.0 - smoothstep(0.2, 0.6, fwidth(q.y));
		// Broken lines, not rails: a coarser patch field gates them along their length.
		float patch = hymn_value_noise2(world.xz / (storm_streak_length_m * WATER_STREAK_PATCH));
		float fleck = hymn_value_noise2(vec2(qd.x * WATER_STREAK_FLECKS, qd.y) + vec2(0.0, WATER_STREAK_FLECKS));
		float line = smoothstep(0.6, 0.88, sn) * mix(WATER_STREAK_FLECK_FLOOR, 1.0, smoothstep(0.3, 0.7, fleck));
		float cov = mix(WATER_STREAK_MEAN, line, resolved) * smoothstep(0.45, 0.75, patch);
		float streak = cov * storm_k * storm_streak_amount * exp(-view_dist / storm_streak_fade_m);
		foam = max(foam, streak);
	}

	// --- Screen-space reflection --------------------------------------------------------------
	float fresnel = WATER_F0 + (1.0 - WATER_F0) * pow(1.0 - ndv, 5.0);
	float ssr_hit = 0.0;
	vec3 ssr_col = vec3(0.0);
#if WATER_SSR_STEPS > 0
	if (use_ssr) {
		// A still actor's reflection never ripples (M3-RND-03): where the flat mirror ray meets a still
		// actor's capsule and the flat march lands on him, his reflection is the flat one.
		bool still = false;
		if (hymn_still_actor_0.w > 0.0 || hymn_still_actor_1.w > 0.0) {
			vec3 r_flat = reflect(-VIEW, normalize((VIEW_MATRIX * vec4(0.0, 1.0, 0.0, 0.0)).xyz));
			vec3 rw_flat = (INV_VIEW_MATRIX * vec4(r_flat, 0.0)).xyz;
			if (water_still_ray(world, rw_flat)) {
				vec3 col_flat;
				vec3 hit_flat;
				float h_flat = water_ssr_march(VERTEX, r_flat, world.y, PROJECTION_MATRIX, INV_PROJECTION_MATRIX,
						INV_VIEW_MATRIX, col_flat, hit_flat);
				if (h_flat > 0.0 && water_still_point(hit_flat)) {
					ssr_hit = h_flat;
					ssr_col = col_flat;
					still = true;
				}
			}
		}
		if (!still) {
			vec3 r = reflect(-VIEW, n_view);
			// Ripple normals can bend a reflected ray under the surface; it would "hit" the seabed.
			float r_rise = (INV_VIEW_MATRIX * vec4(r, 0.0)).y;
			if (r_rise > WATER_SSR_MIN_RISE) {
				vec3 hit_world;
				ssr_hit = water_ssr_march(VERTEX, r, world.y, PROJECTION_MATRIX, INV_PROJECTION_MATRIX, INV_VIEW_MATRIX,
						ssr_col, hit_world);
			}
		}
	}
#endif

	// --- Night sea-glow and glimmer response (every tier) --------------------------------------
	// Shared glimmer-stream term (glimmer.gdshaderinc): the zone or material energy (hymn_sea_glow_zone,
	// a zone hard off wins), clamped to the rule-3 band, column = the underwater view path. Seen
	// through the surface: x (1 - Fresnel).
	float glow_energy = hymn_sea_glow_energy(hymn_sea_glow_zone(sea_glow_energy));
	vec3 glow = hymn_sea_glow(world, t, glow_energy, path) * (1.0 - fresnel);
	if (hymn_glimmer_focus.w > 0.0) {
		float f = 1.0 - smoothstep(0.0, hymn_glimmer_focus.w, distance(world, hymn_glimmer_focus.xyz));
		glow += hymn_glimmer.rgb * hymn_glimmer.a * glimmer_response * f * f;
	}

	// --- Outputs --------------------------------------------------------------------------------
	float water = 1.0 - foam;
	float view_steep = abs((INV_VIEW_MATRIX * vec4(VIEW, 0.0)).y);
	float view_high = smoothstep(sss_view_height_lo_m, max(sss_view_height_hi_m, sss_view_height_lo_m + HYMN_EPSILON),
			view_dist * view_steep);
	float view_keep = 1.0 - smoothstep(sss_view_fade_lo, max(sss_view_fade_hi, sss_view_fade_lo + HYMN_EPSILON), view_steep)
			* view_high;
	// The lift stands in for the crest SSS a high camera loses, so it scales with that SSS: none on a
	// material with SSS off (the storm sea, M1-RND-18 S1), full at the sss_strength it was tuned at.
	float lift_gate = use_sss ? clamp(sss_strength / SSS_LIFT_TUNED_STRENGTH, 0.0, 1.0) : 0.0;
	vec3 deep_lit = col_deep * (1.0 + scatter_view_lift * lift_gate * (1.0 - view_keep));
	vec3 col_scatter = mix(col_scatter_shallow, deep_lit, smoothstep(0.0, scatter_depth_m, vdepth));
	v_foam = foam;
	v_crest = use_sss ? smoothstep(sss_crest_lo, sss_crest_hi, v_height / max(water_amplitude_sum, HYMN_EPSILON))
			* water * view_keep : 0.0;
	float rough = mix(roughness_near, roughness_far, clamp(view_dist / roughness_far_m, 0.0, 1.0));
	rough = min(rough + storm_roughness * storm_k, 1.0);
	float storm_dim = 1.0 - storm_darken * storm_k;
	body *= storm_dim;
	col_scatter *= storm_dim;

	// Foam is a lit diffuse surface; so is the in-scattering column under the surface.
	ALBEDO = col_foam * foam + col_scatter * inscatter * scatter_energy * water * (1.0 - fresnel);
	ROUGHNESS = mix(rough, foam_roughness, foam);
	METALLIC = 0.0;
	// The storm in the reflection (M2-RND-05): where the reflected ray meets the storm impostor, the
	// sky it would reflect is the storm.
	float storm_cover = 0.0;
	vec3 storm_ref = vec3(0.0);
	if (storm_reflect > 0.0) {
		vec3 rw = normalize((INV_VIEW_MATRIX * vec4(reflect(-VIEW, n_view), 0.0)).xyz);
		rw.y = max(rw.y, 1e-3);
		float sh;
		float sd;
		float cover = water_storm_hit(world, rw, sh, sd);
		vec3 sc = mix(storm_reflect_low, storm_reflect_high, smoothstep(0.0, 1.0, sh)) + storm_reflect_glow;
		storm_ref = mix(sc, storm_reflect_haze, 1.0 - exp(-sd / storm_reflect_visibility_m));
		if (storm_body_ready) {
			// The storm's own pixel where the reflected ray reaches the storm's distance.
			float s_far = sd > 0.0 ? sd : length(storm_reflect_center.xz - world.xz);
			vec4 qc = PROJECTION_MATRIX * (VIEW_MATRIX * vec4(world + rw * s_far, 1.0));
			vec2 quv = qc.xy / max(qc.w, HYMN_EPSILON) * 0.5 + 0.5;
			if (qc.w > 0.0 && quv.x >= 0.0 && quv.x <= 1.0 && quv.y >= 0.0 && quv.y <= 1.0) {
				vec4 b = textureLod(storm_body_tex, quv, 0.0);
				cover = b.a;
				storm_ref = b.rgb / max(b.a, 1e-3);
			}
		}
		storm_cover = cover * storm_reflect * (1.0 - ssr_hit);
	}
	// Engine reflection (sky, probes) only where SSR found nothing.
	SPECULAR = WATER_SPECULAR * water * (1.0 - ssr_hit) * storm_dim * (1.0 - storm_reflection_dim * storm_k)
			* (1.0 - storm_cover);
	NORMAL = n_view;
	EMISSION = body * water * (1.0 - fresnel * ssr_hit)
			+ ssr_col * fresnel * ssr_hit * water + glow * water + storm_ref * fresnel * storm_cover * water;
}

void light() {
	vec3 lc = LIGHT_COLOR * ATTENUATION;
	float ndl = dot(NORMAL, LIGHT);
	float ndl_c = max(ndl, 0.0);
	// Foam and column in-scatter (the engine multiplies DIFFUSE_LIGHT by ALBEDO). The column is
	// lit through the surface, so wave faces turned from the light still glow a little (wrap).
	DIFFUSE_LIGHT += lc * mix(ndl_c, 1.0, scatter_wrap * (1.0 - v_foam)) / HYMN_PI;
	// Sun through thin crests: strongest looking toward the light, through the wave. The soft wrap
	// term is view-dependent too (toward_light): light through a crest only reaches an eye on the far
	// side. Without it, a sun behind the camera painted saturated bands along every swell crest, and a
	// high noon camera saw pale crest patches (M1-RND-08).
	vec3 h_sss = normalize(LIGHT + NORMAL * sss_distortion);
	float back = pow(clamp(dot(VIEW, -h_sss), 0.0, 1.0), sss_power);
	float wrap = 0.5 + 0.5 * ndl;
	float toward_light = clamp(0.5 - 0.5 * dot(VIEW, LIGHT), 0.0, 1.0);
	SPECULAR_LIGHT += col_sss * lc * v_crest * sss_strength * (back + 0.25 * wrap * toward_light) / HYMN_PI;
	// Sun glint: GGX with Schlick Fresnel and Smith-Schlick visibility. The half vector is guarded
	// (LIGHT = -VIEW has none) and vdh clamped: at the anti-solar pixel VIEW = LIGHT = hv, rounding
	// can push dot(VIEW, hv) past 1, and pow() of the negative 1 - vdh is NaN on some drivers; one
	// NaN pixel blooms into a white disc through glow (M1-RND-08).
	vec3 hv = LIGHT + VIEW;
	hv *= inversesqrt(max(dot(hv, hv), HYMN_EPSILON));
	float ndh = max(dot(NORMAL, hv), 0.0);
	float ndv = max(dot(NORMAL, VIEW), HYMN_EPSILON);
	float vdh = clamp(dot(VIEW, hv), 0.0, 1.0);
	float a = max(ROUGHNESS, glint_min_roughness);
	a *= a;
	float a2 = a * a;
	float dd = ndh * ndh * (a2 - 1.0) + 1.0;
	float d_ggx = a2 / (HYMN_PI * dd * dd);
	float k = a * 0.5;
	float vis = 0.25 / ((ndl_c * (1.0 - k) + k) * (ndv * (1.0 - k) + k));
	float f = WATER_F0 + (1.0 - WATER_F0) * pow(1.0 - vdh, 5.0);
	SPECULAR_LIGHT += lc * ndl_c * d_ggx * vis * f * glint_strength * (1.0 - v_foam);
}

#endif

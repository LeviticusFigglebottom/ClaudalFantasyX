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

	// --- Screen-space reflection --------------------------------------------------------------
	float fresnel = WATER_F0 + (1.0 - WATER_F0) * pow(1.0 - ndv, 5.0);
	float ssr_hit = 0.0;
	vec3 ssr_col = vec3(0.0);
#if WATER_SSR_STEPS > 0
	vec3 r = reflect(-VIEW, n_view);
	// Ripple normals can bend a reflected ray under the surface; it would "hit" the seabed.
	float r_rise = (INV_VIEW_MATRIX * vec4(r, 0.0)).y;
	if (use_ssr && r_rise > WATER_SSR_MIN_RISE) {
		float prev_t = 0.0;
		for (int i = 1; i <= WATER_SSR_STEPS; i++) {
			float ti = ssr_max_distance_m * pow(float(i) / float(WATER_SSR_STEPS), ssr_step_exponent);
			vec3 p = VERTEX + r * ti;
			vec4 clip = PROJECTION_MATRIX * vec4(p, 1.0);
			if (clip.w <= 0.0) {
				break;
			}
			vec2 uv = clip.xy / clip.w * 0.5 + 0.5;
			if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
				break;
			}
			float sz = scene_view_pos(uv, INV_PROJECTION_MATRIX).z;
			if (p.z < sz) {
				float lo = prev_t;
				float hi = ti;
#if WATER_SSR_REFINE > 0
				for (int j = 0; j < WATER_SSR_REFINE; j++) {
					float mid = 0.5 * (lo + hi);
					vec3 pm = VERTEX + r * mid;
					vec4 cm = PROJECTION_MATRIX * vec4(pm, 1.0);
					vec2 um = cm.xy / cm.w * 0.5 + 0.5;
					if (pm.z < scene_view_pos(um, INV_PROJECTION_MATRIX).z) {
						hi = mid;
					} else {
						lo = mid;
					}
				}
#endif
				vec3 ph = VERTEX + r * hi;
				vec4 ch = PROJECTION_MATRIX * vec4(ph, 1.0);
				vec2 uh = ch.xy / ch.w * 0.5 + 0.5;
				float gap = scene_view_pos(uh, INV_PROJECTION_MATRIX).z - ph.z;
				float hit_y = (INV_VIEW_MATRIX * vec4(ph, 1.0)).y;
				// Only geometry above the water can be reflected by it.
				if (gap < ssr_thickness_m + hi * WATER_SSR_THICKNESS_GROWTH && hit_y > world.y - WATER_SSR_BELOW_M) {
					vec2 edge = smoothstep(vec2(0.0), vec2(ssr_edge_fade), uh)
							* smoothstep(vec2(0.0), vec2(ssr_edge_fade), 1.0 - uh);
					ssr_hit = edge.x * edge.y * (1.0 - hi / ssr_max_distance_m);
					ssr_col = textureLod(screen_tex, uh, 0.0).rgb;
				}
				break;
			}
			prev_t = ti;
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

	// Foam is a lit diffuse surface; so is the in-scattering column under the surface.
	ALBEDO = col_foam * foam + col_scatter * inscatter * scatter_energy * water * (1.0 - fresnel);
	ROUGHNESS = mix(rough, foam_roughness, foam);
	METALLIC = 0.0;
	// Engine reflection (sky, probes) only where SSR found nothing.
	SPECULAR = WATER_SPECULAR * water * (1.0 - ssr_hit);
	NORMAL = n_view;
	EMISSION = body * water * (1.0 - fresnel * ssr_hit)
			+ ssr_col * fresnel * ssr_hit * water + glow * water;
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

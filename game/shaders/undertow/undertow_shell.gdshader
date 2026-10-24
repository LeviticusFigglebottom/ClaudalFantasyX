// Hymn of the Undertow: the Low-tier body (M1-RND-03). Stacked lathe shells instead of a raymarch.
// Docs: docs/kb/tech/undertow.md. Each shell is a unit open cylinder (radius 1, height 1, centred)
// that the vertex shader maps onto the SAME envelope the raymarched body uses (undertow_common):
//   shell_kind 0: a wall shell at shell_fraction across the eyewall (0 = the eye face, 1 = outside)
//   shell_kind 1: the anvil canopy (the cylinder's height becomes the radius, eye to canopy edge)
// The cloud noise, wounds and lightning are evaluated on the shell surface, so Low keeps the
// silhouette, the vortex banding, the glimmer wounds and the inner glows; it loses depth (parallax
// between three surfaces instead of a volume) and soft self-shadowing.
shader_type spatial;
render_mode blend_mix, unshaded, cull_disabled, depth_draw_opaque, fog_disabled, shadows_disabled;

#define HYMN_QUALITY HYMN_QUALITY_LOW
#include "res://game/shaders/include/globals.gdshaderinc"
#include "res://game/shaders/undertow/undertow_common.gdshaderinc"

#define UNDERTOW_UNIT_HALF 0.5
#define UNDERTOW_SHELL_OCTAVES 3
// Canopy dome: the anvil's underside rises this fraction of its thickness toward the eye.
#define UNDERTOW_CANOPY_DOME 0.35
#define UNDERTOW_BULGE_OFFSET vec3(7.3, 0.0, -2.9)
// A shell is one surface, not a column of medium: its seam glow is scaled down to match the
// raymarch's per-metre wound emission integrated through a wall skin.
#define UNDERTOW_SHELL_WOUND_GAIN 0.08

group_uniforms shell;
uniform int shell_kind : hint_range(0, 1) = 0;
uniform float shell_fraction : hint_range(0.0, 1.0) = 0.45;
uniform float alpha_cut : hint_range(0.0, 1.0) = 0.42;
uniform float noise_scale_m : hint_range(10.0, 20000.0) = 2300.0;
uniform float coverage_bias : hint_range(-1.0, 1.0) = 0.08;
uniform vec3 col_sun : source_color = vec3(0.888, 0.381, 0.069);
uniform float sun_energy : hint_range(0.0, 16.0) = 1.0;
uniform vec3 col_ambient_top : source_color = vec3(0.159, 0.209, 0.271);
uniform vec3 col_ambient_bottom : source_color = vec3(0.004, 0.069, 0.091);
uniform float ambient_energy : hint_range(0.0, 8.0) = 1.0;
uniform vec3 col_albedo : source_color = vec3(0.48, 0.55, 0.63);
uniform float albedo_gain : hint_range(0.0, 4.0) = 1.0;
uniform float base_darkening : hint_range(0.0, 1.0) = 0.75;
uniform float sun_clear_height : hint_range(0.0, 1.0) = 0.8;
uniform float sun_low_floor : hint_range(0.0, 1.0) = 0.12;
uniform vec3 col_haze : source_color = vec3(0.35, 0.3, 0.32);
uniform float haze_visibility_m : hint_range(100.0, 200000.0) = 26000.0;
uniform float wound_energy : hint_range(0.0, 64.0) = 5.0;
uniform float pocket_energy : hint_range(0.0, 16.0) = 0.9;
group_uniforms;

varying vec3 v_local;
varying vec3 v_normal;

void vertex() {
	float u = VERTEX.y + UNDERTOW_UNIT_HALF;
	vec2 dir = normalize(VERTEX.xz);
	float H = undertow_height();
	float bulge = hymn_value_noise3(vec3(dir.x * 3.0, u * 4.0, dir.y * 3.0) + UNDERTOW_BULGE_OFFSET) - 0.5;
	vec3 p;
	vec3 n;
	if (shell_kind == 0) {
		float r = mix(undertow_eye_r(u), undertow_wall_r(u), shell_fraction) + bulge * wall_softness_m;
		p = vec3(dir.x * r, u * H, dir.y * r);
		n = vec3(dir.x, 0.0, dir.y) * (shell_fraction < 0.5 ? -1.0 : 1.0);
	} else {
		float ch = canopy_height_m * H / height_m;
		float r0 = undertow_eye_r(ch / H);
		float r = mix(r0, canopy_radius_m, u);
		float y = ch - canopy_thickness_m * UNDERTOW_CANOPY_DOME * u * u + bulge * canopy_thickness_m * 0.3;
		p = vec3(dir.x * r, y, dir.y * r);
		n = vec3(0.0, -1.0, 0.0);
	}
	VERTEX = p;
	NORMAL = n;
	v_local = p;
	v_normal = n;
}

void fragment() {
	vec3 p = v_local;
	float ta;
	float tb;
	float wa;
	undertow_phases(ta, tb, wa);
	float na = hymn_fbm3(undertow_flow_point(p, ta) / noise_scale_m, UNDERTOW_SHELL_OCTAVES, 2.0, 0.5);
	float nb = hymn_fbm3(undertow_flow_point(p, tb) / noise_scale_m, UNDERTOW_SHELL_OCTAVES, 2.0, 0.5);
	float n = mix(nb, na, wa);
	float env = max(undertow_envelope(p), shell_kind == 1 ? 0.6 : 0.0);
	float d = clamp((n + env - 1.0 - coverage_bias) * 2.0 * (1.0 + env), 0.0, 1.0);
	float pocket;
	float lip;
	float halo;
	float H = undertow_height();
	float h = p.y / H;
	float on_wall = (shell_kind == 0 ? 1.0 : 0.0) * undertow_wound_band(h);
	float seam = undertow_wound(p, pocket, lip, halo) * on_wall;
	pocket *= on_wall;
	lip *= on_wall;
	halo *= on_wall;
	vec3 L = normalize(hymn_sun_direction + vec3(0.0, HYMN_EPSILON, 0.0));
	float wrap = clamp(dot(normalize(v_normal), L) * 0.5 + 0.5, 0.0, 1.0);
	// Same direct-light reach as the raymarch (a low sun only lights the upper storm), and a cheap
	// self-shadow from the noise: billow crests catch the light, troughs and thick cores do not.
	float self_shadow = mix(sun_low_floor, 1.0, smoothstep(0.0, sun_clear_height, h)) * mix(0.25, 1.1, n);
	vec3 amb = mix(col_ambient_bottom, col_ambient_top, smoothstep(0.0, 1.0, h)) * ambient_energy;
	float base = mix(1.0 - base_darkening, 1.0, smoothstep(0.0, 0.45, h));
	vec3 lit = col_albedo * albedo_gain * (col_sun * sun_energy * wrap * self_shadow + amb * (1.0 - 0.5 * d)) * base;
	lit *= 1.0 - rent_lip_dark * lip;
	vec3 inner = undertow_lightning(p) * 0.6 + col_held * pocket * pocket_energy * wound_intensity * 0.5;
	inner *= 1.0 - rent_lip_dark * lip;
	vec3 glow = col_wound * (seam + halo * rent_halo_energy * d) * wound_energy * UNDERTOW_SHELL_WOUND_GAIN;
	vec3 col = lit + inner + glow;
	float dist = length(p + storm_center - CAMERA_POSITION_WORLD);
	float haze = 1.0 - exp(-dist / haze_visibility_m);
	ALBEDO = mix(col, col_haze, haze);
	ALPHA = clamp(d * 2.0 + seam, 0.0, 1.0) * step(alpha_cut * 0.5, d + seam);
	// Hashed alpha: soft, order-independent edges in the opaque pass (TAA smooths the dither).
	ALPHA_HASH_SCALE = 1.0;
}

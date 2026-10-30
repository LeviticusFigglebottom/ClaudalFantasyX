// Hymn of the Undertow: a burning's flame tongues, licking and flickering (M3-RND-1315). Docs: docs/kb/tech/fire.md.
// On the sculpted tongues of the Brine Shoals kit's camp fires (b_fire.py, their bs_fire_outer / bs_fire_core slots),
// in object space (origin at the fire bed's centre on the ground, +Y up):
// - the tongues sway downwind-ish and stretch as a lick runs up them, more toward the tip (nothing moves at the bed);
// - rising noise tears the upper half of each tongue into licks (discard), so the tips break and re-form;
// - the colour runs from the slot's base to its tip colour and flickers with slow noise per fire.
// - the tongue is translucent: dense at its heart and foot, thinning toward its silhouette and its torn tips (opaque,
//   the camp's fires read as cut card against the noon flats; M3-ENV-1326), and broken into licks so that at arm's
//   length no smooth cone shows (the 10-29 audit).
// All on the held weather clock (hymn_wind_time), never TIME, so a capture is deterministic. Unshaded: the flame is
// its own light (the zone's fire lights do the lighting). Never glimmer colours (references.md §1.4 rule 10).
shader_type spatial;
render_mode unshaded, cull_disabled, shadows_disabled, fog_disabled, depth_draw_never;

#include "res://game/shaders/include/globals.gdshaderinc"
#include "res://game/shaders/include/common.gdshaderinc"

uniform vec3 base_color : source_color = vec3(0.949, 0.651, 0.29);
uniform vec3 tip_color : source_color = vec3(0.878, 0.439, 0.18);
// An emission over the albedo (0 for the camp: added to the unshaded colour it clipped the ch06 grade to flat red).
uniform float emission = 0.0;
// The foot burns brighter than the tip.
uniform float foot_gain = 1.15;
uniform float tip_gain = 0.72;
// Volume: a tongue's heart (facing the camera) is brighter than its silhouette, which runs to the tip colour (up close
// a flat colour read as a paper cutout).
uniform float heart_gain = 1.2;
uniform float rim_power = 0.7;
// The tallest tongue (the large fire's); the sway and the tearing scale with height over it.
uniform float height_m = 2.6;
uniform float sway_m = 0.22;
uniform float stretch = 0.1;
uniform float speed = 1.0;
uniform float flicker = 0.22;
// How much of a tongue's upper half the rising noise tears away (0: none).
uniform float tear = 0.55;
uniform float tear_scale_per_m = 2.6;
uniform float rise_m_s = 1.6;
// Opacity: a tongue's heart (facing the camera) at its foot, its silhouette, and how much the tips thin it.
uniform float heart_alpha : hint_range(0.0, 1.0) = 0.78;
uniform float rim_alpha : hint_range(0.0, 1.0) = 0.0;
uniform float tip_thin : hint_range(0.0, 1.0) = 0.75;
// The rising noise also thins the body into licks (0: an even sheet).
uniform float lick_breakup : hint_range(0.0, 1.0) = 0.85;
// The heart runs toward this hot colour where it faces the camera, low in the tongue.
uniform vec3 hot_color : source_color = vec3(1.0, 0.86, 0.55);

varying float v_h;
varying vec3 v_obj;
varying float v_phase;

void vertex() {
	float h = clamp(VERTEX.y / height_m, 0.0, 1.0);
	float t = hymn_wind_time * speed;
	// Each placed fire its own phase (its world position).
	float ph = dot(MODEL_MATRIX[3].xyz, vec3(0.37, 0.11, 0.61));
	float k = h * h;
	VERTEX.x += sway_m * k * (sin(t * 2.3 + ph + VERTEX.z * 1.7) + 0.5 * sin(t * 5.3 + ph * 1.3 + VERTEX.y * 2.0));
	VERTEX.z += sway_m * k * 0.7 * cos(t * 1.9 + ph * 0.7 + VERTEX.x * 1.3);
	VERTEX.y *= 1.0 + stretch * h * sin(t * 6.7 + ph + VERTEX.x * 3.1 + VERTEX.z * 2.3);
	v_h = h;
	v_obj = VERTEX;
	v_phase = ph;
}

void fragment() {
	float t = hymn_wind_time * speed;
	vec3 q = vec3(v_obj.x, v_obj.y - t * rise_m_s, v_obj.z) * tear_scale_per_m;
	float n = hymn_value_noise3(q) * 0.65 + hymn_value_noise3(q * 2.1 + vec3(5.3)) * 0.35;
	if (n < tear * smoothstep(0.35, 1.0, v_h)) {
		discard;
	}
	float f = hymn_value_noise3(vec3(t * 4.0, v_phase, v_phase * 0.5)) * 2.0 - 1.0;
	float facing = pow(clamp(abs(dot(NORMAL, VIEW)), 0.0, 1.0), rim_power);
	vec3 body = mix(base_color, tip_color, smoothstep(0.25, 1.0, v_h));
	body = mix(body, hot_color, facing * facing * (1.0 - smoothstep(0.0, 0.6, v_h)));
	vec3 c = mix(tip_color * 0.8, body * heart_gain, facing) * (1.0 + flicker * f) * (0.85 + 0.3 * n)
			* mix(foot_gain, tip_gain, v_h);
	ALBEDO = c;
	EMISSION = c * emission;
	float licks = mix(1.0, smoothstep(0.25, 0.75, n + 0.35 * (1.0 - v_h)), lick_breakup);
	ALPHA = mix(rim_alpha, heart_alpha, facing) * (1.0 - tip_thin * smoothstep(0.3, 1.0, v_h)) * licks;
}

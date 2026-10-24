// Hymn of the Undertow: curtains of held light streaming off the storm's wounds (M2-RND-05).
// Docs: docs/kb/tech/undertow.md ("Storm events"). Drawn on UndertowMeshBuilder.streamers() curtains in
// storm-local model space (the MeshInstance3D sits at storm_center). The ribbons ride the eyewall's
// rotation; along each one a pattern of motes slides with the wounds' drift (down while held,
// colour script rule 1; up after the Letting, when UndertowState lerps col_held to glimmer_lift).
// Additive light, drawn after the body (render_priority), near half only: the far half is behind
// the wall, which the body would otherwise not cover.
shader_type spatial;
render_mode blend_add, unshaded, cull_disabled, depth_draw_never, fog_disabled, shadows_disabled;

#include "res://game/shaders/include/globals.gdshaderinc"
#include "res://game/shaders/undertow/undertow_common.gdshaderinc"

#define UNDERTOW_STREAMER_OFFSET vec3(-17.3, 29.1, 7.7)
// Share of the light in a thin continuous veil under the motes.
#define UNDERTOW_STREAMER_VEIL 0.25
// |cos| of the view angle below which a curtain (seen edge-on) has faded out.
#define UNDERTOW_STREAMER_EDGE_ON 0.25

group_uniforms streamers;
uniform float streamer_energy : hint_range(0.0, 32.0) = 1.4;
// Size of one clump of motes along the ribbon (m), and how much of the ribbon they cover.
uniform float streamer_mote_scale_m : hint_range(1.0, 5000.0) = 140.0;
uniform float streamer_mote_cover : hint_range(0.0, 1.0) = 0.35;
uniform vec3 col_haze : source_color = vec3(0.35, 0.3, 0.32);
uniform float haze_visibility_m : hint_range(100.0, 200000.0) = 26000.0;
group_uniforms;

varying vec3 v_local;

void vertex() {
	// The wounds turn with the wall (undertow_wound: atan - rotation x t), so the ribbons do too.
	VERTEX.xz = undertow_rotate(VERTEX.xz, rotation_rad_s * storm_time_s);
	NORMAL.xz = undertow_rotate(NORMAL.xz, rotation_rad_s * storm_time_s);
	v_local = VERTEX;
}

void fragment() {
	vec3 cam = CAMERA_POSITION_WORLD - storm_center;
	if (dot(v_local.xz, cam.xz) < 0.0) {
		discard;
	}
	float s = UV.y;
	float across = 1.0 - abs(2.0 * UV.x - 1.0);
	// Arc length (UV2.y, m) minus the drift: held light slides down the curtain (toward s = 1).
	float along = (UV2.y - wound_drift_m) / streamer_mote_scale_m;
	vec3 q = vec3(UV.x * 4.0 + UV2.x * 37.0, along, UV2.x * 11.0);
	float n = hymn_value_noise3(q + UNDERTOW_STREAMER_OFFSET);
	float motes = smoothstep(1.0 - streamer_mote_cover, 1.0, n);
	float fade = smoothstep(0.0, 0.08, s) * pow(1.0 - s, 1.5) * across * across;
	float dist = length(v_local - cam);
	float haze = exp(-dist / haze_visibility_m);
	// A curtain seen edge-on (at the storm's silhouette) is a hard line: fade it with how squarely it
	// faces the camera.
	float facing = smoothstep(UNDERTOW_STREAMER_EDGE_ON, 1.0, abs(dot(NORMAL, VIEW)));
	float k = (motes + UNDERTOW_STREAMER_VEIL) * fade * facing * streamer_energy * wound_intensity * storm_intensity * haze;
	// Unshaded and additive: ALBEDO is the light added (EMISSION is ignored when unshaded).
	ALBEDO = col_held * k;
}

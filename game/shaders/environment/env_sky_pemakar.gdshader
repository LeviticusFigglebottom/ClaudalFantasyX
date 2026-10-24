// Hymn of the Undertow: Pemakar's dusk and festival-night sky (M3-ENV-03; color script ch05, pemakar.md
// §0). A zenith-to-horizon gradient, an afterglow lobe on the horizon toward the set sun (dusk: the last
// ember in the west behind the plume; night: off), faint stars that come out as the glow goes, and a
// warm ash-haze band low on the horizon from the town's own lights.
shader_type sky;

#include "res://game/shaders/include/common.gdshaderinc"

group_uniforms sky;
uniform vec4 col_zenith : source_color = vec4(0.063, 0.102, 0.2, 1.0); // #101A33 (ch05)
uniform vec4 col_horizon : source_color = vec4(0.227, 0.165, 0.227, 1.0); // #3A2A3A (ch05)
uniform vec4 col_ground : source_color = vec4(0.02, 0.039, 0.078, 1.0); // night_sky #050A14 lifted
uniform float sky_energy : hint_range(0.0, 4.0) = 1.0;
uniform float horizon_curve : hint_range(0.01, 1.0) = 0.25;
group_uniforms;

group_uniforms afterglow;
uniform vec4 col_glow : source_color = vec4(0.878, 0.439, 0.180, 1.0); // ember_orange #E0702E
uniform float glow_energy : hint_range(0.0, 4.0) = 0.0;
uniform float glow_azimuth_deg = 285.0; // compass bearing of the set sun (0 north, 90 east)
uniform float glow_width_deg : hint_range(5.0, 180.0) = 55.0;
uniform float glow_height : hint_range(0.01, 1.0) = 0.18; // how high the lobe climbs (sin elevation)
group_uniforms;

group_uniforms haze;
uniform vec4 col_haze : source_color = vec4(0.353, 0.227, 0.180, 1.0); // fog albedo #5A3A2E (ch05)
uniform float haze_energy : hint_range(0.0, 2.0) = 0.0;
uniform float haze_height : hint_range(0.01, 0.5) = 0.06;
group_uniforms;

group_uniforms stars;
uniform float star_grid : hint_range(16.0, 512.0) = 200.0;
uniform float star_density : hint_range(0.0, 1.0) = 0.08;
uniform float star_energy : hint_range(0.0, 20.0) = 1.2;
group_uniforms;

void sky() {
	vec3 d = normalize(EYEDIR);
	float up = d.y;
	float t = pow(clamp(up, 0.0, 1.0), horizon_curve);
	vec3 col = mix(col_horizon.rgb, col_zenith.rgb, t);
	if (up < 0.0) {
		col = mix(col_horizon.rgb, col_ground.rgb, smoothstep(0.0, 0.08, -up));
	}
	// Bearing of this view direction: north is -Z, east +X.
	float bearing = degrees(atan(d.x, -d.z));
	float dang = abs(mod(bearing - glow_azimuth_deg + 540.0, 360.0) - 180.0);
	float lobe = exp(-pow(dang / glow_width_deg, 2.0)) * exp(-max(up, 0.0) / glow_height);
	col += col_glow.rgb * glow_energy * lobe * step(-0.02, up);
	col += col_haze.rgb * haze_energy * exp(-abs(up) / haze_height);
	if (up > 0.02) {
		vec2 uv = vec2(atan(d.x, d.z), acos(clamp(d.y, -1.0, 1.0))) * star_grid / 3.14159;
		vec2 cell = floor(uv);
		float h = hymn_hash12(cell);
		vec2 off = vec2(hymn_hash12(cell + 7.3), hymn_hash12(cell + 3.1));
		float dd = length(fract(uv) - off);
		float star = step(1.0 - star_density, h) * smoothstep(0.12, 0.0, dd);
		float fade = smoothstep(0.02, 0.3, up) * (1.0 - clamp(glow_energy * lobe * 4.0, 0.0, 1.0));
		col += vec3(0.86, 0.9, 1.0) * star * star_energy * fade;
	}
	COLOR = col * sky_energy;
}

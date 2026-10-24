// Hymn of the Undertow: zone night sky (M2-ENV-02; color script `ch02_night`, haluna.md H10).
// A gradient sky from the night zenith to a lighter horizon band, a field of fixed stars, and the
// moon's disc and halo on the first directional light (the Moon, `#9DB4D9`). Deterministic: no TIME,
// the stars come from a hashed cell grid on the view sphere. The stars and the moon disc are drawn in
// the visible pass only: the radiance cubemap (sky fill, water reflections) sees the gradient alone,
// so the validated night fill (ambient energy, the `night_sea` reflection) is not lifted by them.

shader_type sky;

#include "res://game/shaders/include/common.gdshaderinc"

group_uniforms sky;
uniform vec4 col_zenith : source_color = vec4(0.043, 0.086, 0.188, 1.0); // night zenith (water_night)
uniform vec4 col_horizon : source_color = vec4(0.118, 0.180, 0.306, 1.0); // night horizon band
uniform vec4 col_ground : source_color = vec4(0.024, 0.102, 0.169, 1.0); // night deep #061A2B
uniform float sky_energy : hint_range(0.0, 4.0) = 1.0;
uniform float horizon_curve : hint_range(0.01, 1.0) = 0.2;
group_uniforms;

group_uniforms stars;
// Cells per unit of the view direction: larger is a finer grid (more, smaller candidates).
uniform float star_grid : hint_range(16.0, 512.0) = 180.0;
// Share of cells that hold a star.
uniform float star_density : hint_range(0.0, 1.0) = 0.12;
// Star radius in grid cells (a cell is about 1 / star_grid rad).
uniform float star_size : hint_range(0.01, 0.5) = 0.12;
uniform float star_energy : hint_range(0.0, 20.0) = 2.5;
// Stars fade out below this elevation (sin of the angle above the horizon): the haze band.
uniform float star_horizon_fade : hint_range(0.0, 0.5) = 0.18;
uniform vec4 col_star : source_color = vec4(0.86, 0.90, 1.0, 1.0);
group_uniforms;

group_uniforms moon;
uniform vec4 col_moon : source_color = vec4(0.616, 0.706, 0.851, 1.0); // moon #9DB4D9
uniform float moon_disc_deg : hint_range(0.1, 5.0) = 1.1;
uniform float moon_disc_energy : hint_range(0.0, 40.0) = 6.0;
uniform float moon_halo : hint_range(0.0, 2.0) = 0.25;
uniform float moon_halo_deg : hint_range(1.0, 40.0) = 12.0;
// M3-ENV-04B: the lit share of the disc (1 = full, as before; 0.5 = a half moon, `ch09`). The terminator is a
// straight chord across the disc, perpendicular to `moon_lit_angle_deg` (the lit side's direction on the
// disc, clockwise from the disc's up); the unlit part keeps `moon_earthshine` of the disc's light.
uniform float moon_lit_fraction : hint_range(0.0, 1.0) = 1.0;
uniform float moon_lit_angle_deg : hint_range(-180.0, 180.0) = 0.0;
uniform float moon_earthshine : hint_range(0.0, 0.2) = 0.03;
group_uniforms;

vec3 gradient(vec3 dir) {
	float up = dir.y;
	if (up < 0.0) {
		return mix(col_horizon.rgb, col_ground.rgb, clamp(-up * 4.0, 0.0, 1.0));
	}
	float t = pow(clamp(up, 0.0, 1.0), horizon_curve);
	return mix(col_horizon.rgb, col_zenith.rgb, t);
}

// One star per occupied grid cell, at a hashed point inside it, projected onto the sphere.
float stars(vec3 dir) {
	vec3 p = dir * star_grid;
	vec3 cell = floor(p);
	vec3 h = hymn_hash_cell33(cell);
	if (h.x > star_density) {
		return 0.0;
	}
	vec3 centre = normalize(cell + hymn_hash_cell33(cell + vec3(17.0, 31.0, 7.0)));
	float d = length(dir - centre) * star_grid;
	float core = 1.0 - smoothstep(0.0, star_size, d);
	// A few bright stars, many faint ones.
	float mag = mix(0.15, 1.0, pow(h.y, 6.0));
	return core * mag;
}

void sky() {
	vec3 dir = normalize(EYEDIR);
	vec3 col = gradient(dir) * sky_energy;
	if (!AT_CUBEMAP_PASS) {
		float fade = smoothstep(0.0, star_horizon_fade, dir.y);
		col += col_star.rgb * stars(dir) * star_energy * fade;
		if (LIGHT0_ENABLED) {
			float cos_a = dot(dir, LIGHT0_DIRECTION);
			float disc = smoothstep(cos(radians(moon_disc_deg)), cos(radians(moon_disc_deg * 0.85)), cos_a);
			if (moon_lit_fraction < 1.0) {
				vec3 right = normalize(cross(LIGHT0_DIRECTION, vec3(0.0, 1.0, 0.0)));
				vec3 up_d = cross(right, LIGHT0_DIRECTION);
				float a = radians(moon_lit_angle_deg);
				vec2 q = vec2(dot(dir, right), dot(dir, up_d)) / sin(radians(moon_disc_deg));
				float along = dot(q, vec2(sin(a), cos(a)));
				float edge = 1.0 - 2.0 * moon_lit_fraction;
				disc *= mix(moon_earthshine, 1.0, smoothstep(edge - 0.06, edge + 0.06, along));
			}
			float halo = pow(max(cos_a, 0.0), 90.0 / moon_halo_deg) * moon_halo;
			col += col_moon.rgb * (disc * moon_disc_energy + halo);
		}
	}
	COLOR = col;
}

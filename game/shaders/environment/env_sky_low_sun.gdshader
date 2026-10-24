// Hymn of the Undertow: low-sun sky for dawn and sunset frames (M2-ENV-11, the battle arenas).
// The noon cumulus sky (env_sky_cumulus) is symmetric around the zenith; a sun a few degrees up is not.
// This sky warms the horizon towards the sun's azimuth and cools it away from it, adds a broad forward
// glow and the disc, and lays thin cloud bands on a plane (one fbm, no march) lit from below on the sun
// side. Colours are inputs from the colour script (sub-frames ch02 dawn, ch03_boss); the LUT does the
// grade after the tonemapper. Cheap enough for every tier and the radiance cubemap.
shader_type sky;

group_uniforms sky;
uniform vec4 col_zenith : source_color = vec4(0.306, 0.498, 0.722, 1.0); // ch02 zenith #4E7FB8
uniform vec4 col_horizon_sun : source_color = vec4(0.965, 0.788, 0.627, 1.0); // ch02 horizon #F6C9A0
uniform vec4 col_horizon_away : source_color = vec4(0.70, 0.75, 0.83, 1.0); // away from the sun
uniform vec4 col_ground : source_color = vec4(0.30, 0.40, 0.48, 1.0); // below the horizon (reflections)
uniform float sky_energy : hint_range(0.0, 4.0) = 1.0;
uniform float background_energy : hint_range(0.0, 4.0) = 1.0;
uniform float horizon_curve : hint_range(0.01, 1.0) = 0.2;
// How far round the horizon the sun-side warmth reaches (exponent on the azimuth term; higher = tighter).
uniform float azimuth_power : hint_range(0.2, 8.0) = 1.5;
// A low warm band hugging the horizon on the sun side (the last of the light under the haze).
uniform vec4 col_band : source_color = vec4(1.0, 0.85, 0.66, 1.0);
uniform float band_energy : hint_range(0.0, 4.0) = 0.6;
uniform float band_height : hint_range(0.005, 0.3) = 0.06;
// A third stop between the horizon and the zenith, strongest towards the sun, so a warm horizon does not
// mix with the blue overhead through grey-magenta (the colour script's magenta-free sunsets). 0 = off.
uniform vec4 col_mid : source_color = vec4(0.7, 0.55, 0.38, 1.0);
uniform float mid_strength : hint_range(0.0, 1.0) = 0.0;
uniform float mid_height : hint_range(0.01, 0.6) = 0.12;
uniform float mid_width : hint_range(0.01, 0.6) = 0.12;
group_uniforms;

group_uniforms sun;
uniform vec4 col_glow : source_color = vec4(1.0, 0.85, 0.66, 1.0);
uniform float glow_energy : hint_range(0.0, 8.0) = 1.2;
uniform float glow_power : hint_range(1.0, 64.0) = 6.0;
uniform float halo_energy : hint_range(0.0, 16.0) = 2.0;
uniform float halo_power : hint_range(8.0, 2048.0) = 160.0;
uniform float sun_disc_deg : hint_range(0.1, 5.0) = 0.55;
uniform float sun_disc_energy : hint_range(0.0, 100.0) = 16.0;
group_uniforms;

group_uniforms clouds;
uniform vec4 col_cloud_lit : source_color = vec4(1.0, 0.82, 0.65, 1.0);
uniform vec4 col_cloud_shadow : source_color = vec4(0.55, 0.59, 0.72, 1.0);
uniform float cloud_coverage : hint_range(0.0, 1.0) = 0.42;
uniform float cloud_softness : hint_range(0.01, 0.5) = 0.18;
uniform float cloud_opacity : hint_range(0.0, 1.0) = 0.85;
uniform float cloud_height_m = 2400.0;
uniform float cloud_scale_m = 7000.0;
// Stretch of the bands (x across, y along the wind): > 1 makes long streaks.
uniform vec2 cloud_stretch = vec2(1.0, 3.5);
uniform float cloud_wind_deg = 250.0; // the azimuth the bands run along
uniform vec2 cloud_offset_m = vec2(0.0, 0.0);
uniform float cloud_sun_energy : hint_range(0.0, 8.0) = 2.2; // undersides lit by the low sun
uniform float cloud_ambient_energy : hint_range(0.0, 4.0) = 0.9;
uniform float cloud_horizon_fade : hint_range(0.0, 0.3) = 0.05;
group_uniforms;

float hash12(vec2 p) {
	vec3 p3 = fract(vec3(p.xyx) * 0.1031);
	p3 += dot(p3, p3.yzx + 33.33);
	return fract((p3.x + p3.y) * p3.z);
}

float vnoise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	float a = hash12(i);
	float b = hash12(i + vec2(1.0, 0.0));
	float c = hash12(i + vec2(0.0, 1.0));
	float d = hash12(i + vec2(1.0, 1.0));
	return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}

float fbm(vec2 p) {
	float v = 0.0;
	float a = 0.5;
	for (int k = 0; k < 5; k++) {
		v += a * vnoise(p);
		p = p * 2.03 + vec2(17.3, 9.1);
		a *= 0.5;
	}
	return v / 0.96875;
}

vec3 gradient(vec3 dir, vec3 sun_dir) {
	float h = clamp(dir.y, 0.0, 1.0);
	float g = pow(max(1.0 - h, 0.0), 1.0 / max(horizon_curve, 0.01) * 0.25);
	vec2 d2 = normalize(dir.xz + vec2(1e-5));
	vec2 s2 = normalize(sun_dir.xz + vec2(1e-5));
	float toward = pow(clamp(dot(d2, s2) * 0.5 + 0.5, 0.0, 1.0), azimuth_power);
	vec3 horizon = mix(col_horizon_away.rgb, col_horizon_sun.rgb, toward);
	vec3 c = mix(col_zenith.rgb, horizon, g);
	float mid = mid_strength * exp(-pow((h - mid_height) / mid_width, 2.0)) * (0.35 + 0.65 * toward);
	c = mix(c, col_mid.rgb, mid);
	c += col_band.rgb * band_energy * toward * exp(-h / band_height);
	if (dir.y < 0.0) {
		c = mix(horizon, col_ground.rgb, smoothstep(0.0, 0.25, -dir.y));
	}
	return c * sky_energy;
}

vec4 cloud_layer(vec3 dir, vec3 sun_dir) {
	if (dir.y <= 0.004) {
		return vec4(0.0);
	}
	vec2 p = dir.xz / dir.y * cloud_height_m + cloud_offset_m;
	float a = radians(cloud_wind_deg);
	// Rotate into the wind frame: x across the bands, y along them (azimuth from north = -Z).
	vec2 along = vec2(sin(a), -cos(a));
	vec2 across = vec2(-along.y, along.x);
	vec2 q = vec2(dot(p, across), dot(p, along)) / (cloud_scale_m * cloud_stretch);
	float n = fbm(q);
	float cover = smoothstep(1.0 - cloud_coverage - cloud_softness, 1.0 - cloud_coverage + cloud_softness, n);
	float far = smoothstep(0.004, 0.004 + cloud_horizon_fade, dir.y);
	float alpha = cover * cloud_opacity * far;
	vec2 d2 = normalize(dir.xz + vec2(1e-5));
	vec2 s2 = normalize(sun_dir.xz + vec2(1e-5));
	float toward = clamp(dot(d2, s2) * 0.5 + 0.5, 0.0, 1.0);
	// Thick cores are darker (their undersides face away from the low sun); thin edges catch it.
	float lit = toward * toward * (1.0 - 0.55 * smoothstep(0.55, 0.95, n)) * (0.6 + 0.4 * (1.0 - dir.y));
	vec3 col = col_cloud_shadow.rgb * cloud_ambient_energy + col_cloud_lit.rgb * cloud_sun_energy * lit;
	return vec4(col * alpha, alpha);
}

void sky() {
	vec3 sun_dir = LIGHT0_ENABLED ? LIGHT0_DIRECTION : vec3(0.0, 1.0, 0.0);
	vec3 dir = EYEDIR;
	vec3 c = gradient(dir, sun_dir);
	float mu = max(dot(dir, sun_dir), 0.0);
	float e = LIGHT0_ENABLED ? 1.0 : 0.0;
	c += col_glow.rgb * (glow_energy * pow(mu, glow_power) + halo_energy * pow(mu, halo_power)) * e;
	if (!AT_CUBEMAP_PASS && LIGHT0_ENABLED) {
		float disc = smoothstep(cos(radians(sun_disc_deg)), cos(radians(sun_disc_deg * 0.8)), mu);
		c += LIGHT0_COLOR * sun_disc_energy * disc;
	}
	vec4 cl = cloud_layer(dir, sun_dir);
	COLOR = (c * (1.0 - cl.a) + cl.rgb) * (AT_CUBEMAP_PASS ? 1.0 : background_energy);
}

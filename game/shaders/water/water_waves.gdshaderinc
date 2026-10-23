// Hymn of the Undertow: Gerstner wave sum (M1-RND-01). Stage-agnostic (no built-ins), so the
// spatial water shader and the canvas_item parity probe share exactly this code.
// The GDScript mirror is game/world/water/gerstner_waves.gd. Change both together; the parity
// probe (game/levels/_tests/water/wave_parity_probe.tscn) and tests/unit/test_water_waves.gd
// fail if they drift apart.
//
// Packed per-wave constants (computed on the CPU by GerstnerWaves.pack(), never by hand):
//   water_wave_a[i] = (dir.x, dir.z, k, omega)     dir: unit travel direction in world XZ
//   water_wave_b[i] = (amplitude_m, horiz_m, phase_rad, 0)
// with k = TAU / wavelength, omega = sqrt(g k) (deep-water dispersion), horiz = steepness / (k N).
//
// Displacement of the rest point p0 (world XZ) at time t:
//   theta_i = k_i dot(dir_i, p0) - omega_i t + phase_i
//   x/z    += -horiz_i dir_i sin(theta_i)      (particles bunch toward the crest)
//   y      +=  amplitude_i cos(theta_i)

#ifndef HYMN_WATER_WAVES_GDSHADERINC
#define HYMN_WATER_WAVES_GDSHADERINC

#include "res://game/shaders/include/common.gdshaderinc"

// Array size of the wave uniforms. Mirrors GerstnerWaves.MAX_WAVES.
#define HYMN_WATER_MAX_WAVES 8

uniform vec4 water_wave_a[HYMN_WATER_MAX_WAVES];
uniform vec4 water_wave_b[HYMN_WATER_MAX_WAVES];
uniform int water_wave_count = 0;
// Sum of amplitudes (m): normalises crest height for subsurface glow. Written by WaterSurface.
uniform float water_amplitude_sum = 1.0;

// Displacement plus analytic tangent frame and the horizontal Jacobian (< 1 = compressed water,
// which is where crests fold and foam forms). lod_fade_wavelengths > 0 fades each wave out once
// view_dist exceeds that many of its own wavelengths (visual LOD only; 0 disables it).
void hymn_water_gerstner(
		vec2 p0,
		float t,
		float view_dist,
		float lod_fade_wavelengths,
		out vec3 disp,
		out vec3 normal,
		out float jacobian) {
	disp = vec3(0.0);
	float jxx = 1.0;
	float jzz = 1.0;
	float jxz = 0.0;
	float dhx = 0.0;
	float dhz = 0.0;
	for (int i = 0; i < HYMN_WATER_MAX_WAVES; i++) {
		if (i >= water_wave_count) {
			break;
		}
		vec4 a = water_wave_a[i];
		vec4 b = water_wave_b[i];
		float fade = 1.0;
		if (lod_fade_wavelengths > 0.0) {
			float wavelength = HYMN_TAU / a.z;
			float fade_start = wavelength * lod_fade_wavelengths;
			// Fade over one further fade_start: a smooth, scale-relative ramp.
			fade = clamp(2.0 - view_dist / fade_start, 0.0, 1.0);
		}
		float amp = b.x * fade;
		float horiz = b.y * fade;
		float theta = a.z * dot(a.xy, p0) - a.w * t + b.z;
		float s = sin(theta);
		float c = cos(theta);
		disp.xz += -horiz * a.xy * s;
		disp.y += amp * c;
		float wa = horiz * a.z * c;
		jxx -= wa * a.x * a.x;
		jzz -= wa * a.y * a.y;
		jxz -= wa * a.x * a.y;
		float wh = amp * a.z * s;
		dhx -= wh * a.x;
		dhz -= wh * a.y;
	}
	// Tangents d(P)/dx0 = (jxx, dhx, jxz) and d(P)/dz0 = (jxz, dhz, jzz); normal = cross(tz, tx).
	vec3 tx = vec3(jxx, dhx, jxz);
	vec3 tz = vec3(jxz, dhz, jzz);
	normal = normalize(cross(tz, tx));
	jacobian = jxx * jzz - jxz * jxz;
}

#endif

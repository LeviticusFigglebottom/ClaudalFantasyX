// Hymn of the Undertow: glimmer helpers shared with other shader domains (M1-RND-02).
// Docs: docs/kb/tech/glimmer.md. Meaning rules: docs/kb/art/color_script.md, narrative light rule 3.
// Includes common.gdshaderinc itself. For hymn_sea_glow_global(), include globals.gdshaderinc FIRST:
//   #include "res://game/shaders/include/globals.gdshaderinc"   // optional, enables *_global helpers
//   #include "res://game/shaders/include/glimmer.gdshaderinc"
// Stage-agnostic except where noted: no built-ins are used.

#ifndef HYMN_GLIMMER_GDSHADERINC
#define HYMN_GLIMMER_GDSHADERINC

#include "res://game/shaders/include/common.gdshaderinc"

// ---------------------------------------------------------------------------------------------
// Palette (docs/kb/art/palette.json), linear sRGB. Motes take their colours from
// game/data/vfx/glimmer.json at runtime; these constants are for shaders that have no JSON path
// (water, storm, emissive props) and must match palette.json.
// ---------------------------------------------------------------------------------------------
#define HYMN_GLIMMER_LIFT vec3(1.0, 0.8148, 0.4793)       // glimmer_lift   #FFE9B8 (released)
#define HYMN_GLIMMER_LIFT_HI vec3(0.9047, 0.9387, 1.0)    // glimmer_lift_hi #F4F8FF
#define HYMN_GLIMMER_HELD vec3(0.2122, 0.5647, 0.6939)    // glimmer_held   #7FC6D9 (held)
#define HYMN_GLIMMER_BOUND vec3(0.0782, 0.4508, 0.4342)   // glimmer_bound  #4FB3B0 (machines)
#define HYMN_SEA_GLOW_COLOR vec3(0.0116, 0.147, 0.1878)   // sea_glow       #1C6B78

// ---------------------------------------------------------------------------------------------
// Night sea-glow (colour script rule 3): faint emission of a thousand years of anchored dead.
// Energy 0.04-0.15 while on, modulated by slow noise with a period of 8-20 s and +-25% amplitude.
// It is EXACTLY 0 only in ending_dock. Never drop it below the floor for performance.
// ---------------------------------------------------------------------------------------------
#define HYMN_SEA_GLOW_ENERGY_MIN 0.04        // rule 3 floor
#define HYMN_SEA_GLOW_ENERGY_MAX 0.15        // rule 3 ceiling
#define HYMN_SEA_GLOW_MOD_AMPLITUDE 0.25     // rule 3: +-25%
#define HYMN_SEA_GLOW_PERIOD_S 13.0          // rule 3: 8-20 s; noise correlation time
#define HYMN_SEA_GLOW_PATCH_M 7.0            // horizontal size of a brighter or dimmer patch
#define HYMN_SEA_GLOW_DETAIL_SCALE 3.1       // second octave, finer patches
#define HYMN_SEA_GLOW_DETAIL_WEIGHT 0.35
#define HYMN_SEA_GLOW_DETAIL_OFFSET vec3(41.7, -13.3, 7.9)
#define HYMN_SEA_GLOW_COLUMN_PER_M 0.45      // in-water column build-up (1 - exp(-k * metres))
#define HYMN_SEA_GLOW_COLUMN_GAIN 1.0        // a deep column at most doubles the surface glow

// Zone energy gated by the scene glimmer intensity (hymn_glimmer.a): any intensity > 0 turns the
// glow on at the zone's colour-script energy, clamped to the rule-3 band; intensity 0 turns it off
// (ending_dock). Separate from mote brightness on purpose: the rule-3 band does not scale with it.
float hymn_sea_glow_energy(float zone_energy, float glimmer_intensity) {
	if (glimmer_intensity <= 0.0 || zone_energy <= 0.0) {
		return 0.0;
	}
	return clamp(zone_energy, HYMN_SEA_GLOW_ENERGY_MIN, HYMN_SEA_GLOW_ENERGY_MAX);
}

// Slow modulation in [1 - amplitude, 1 + amplitude] for a world position and a clock in seconds.
float hymn_sea_glow_modulation(vec3 world_pos, float time_s) {
	vec3 p = vec3(world_pos.xz / HYMN_SEA_GLOW_PATCH_M, time_s / HYMN_SEA_GLOW_PERIOD_S);
	float n = hymn_value_noise3(p) * (1.0 - HYMN_SEA_GLOW_DETAIL_WEIGHT)
			+ hymn_value_noise3(p * HYMN_SEA_GLOW_DETAIL_SCALE + HYMN_SEA_GLOW_DETAIL_OFFSET)
					* HYMN_SEA_GLOW_DETAIL_WEIGHT;
	return 1.0 + HYMN_SEA_GLOW_MOD_AMPLITUDE * (2.0 * n - 1.0);
}

// Linear-light emission to ADD to a water surface (EMISSION) or water-column colour.
//   world_pos : world-space point on the surface (only .xz and the clock drive the noise)
//   time_s    : a pausable clock in seconds (hymn_wind_time, or a cinematic uniform), not raw TIME
//   energy    : already-gated energy, normally hymn_sea_glow_energy(zone_energy, hymn_glimmer.a)
//   column_m  : metres of water the view ray travels below the surface (0 = surface only); a
//               deeper column glows up to (1 + HYMN_SEA_GLOW_COLUMN_GAIN) times brighter
// Cost: two 3D value-noise lookups (16 PCG3D hashes) and an exp. Returns vec3(0) when energy <= 0.
vec3 hymn_sea_glow(vec3 world_pos, float time_s, float energy, float column_m) {
	if (energy <= 0.0) {
		return vec3(0.0);
	}
	float column = 1.0 + HYMN_SEA_GLOW_COLUMN_GAIN * (1.0 - exp(-HYMN_SEA_GLOW_COLUMN_PER_M * max(column_m, 0.0)));
	return HYMN_SEA_GLOW_COLOR * energy * hymn_sea_glow_modulation(world_pos, time_s) * column;
}

#ifdef HYMN_GLOBALS_GDSHADERINC
// Convenience form reading the project globals: gate = hymn_glimmer.a, clock = hymn_wind_time.
vec3 hymn_sea_glow_global(vec3 world_pos, float zone_energy, float column_m) {
	float energy = hymn_sea_glow_energy(zone_energy, hymn_glimmer.a);
	return hymn_sea_glow(world_pos, hymn_wind_time, energy, column_m);
}
#endif

#endif

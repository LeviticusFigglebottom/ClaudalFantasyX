// Hymn of the Undertow: project-wide global shader uniforms (README.md, "Global uniforms").
// REQUIRES matching [shader_globals] entries in project.godot. On a GPU renderer a shader that
// declares an unregistered global uniform fails to compile, so do not include this file until
// those entries exist (the headless dummy renderer does not check, so CI cannot catch it).
//   #include "res://game/shaders/include/globals.gdshaderinc"

#ifndef HYMN_GLOBALS_GDSHADERINC
#define HYMN_GLOBALS_GDSHADERINC

// Wind: xyz = world-space direction * speed (m/s), w = gust strength in [0, 1].
global uniform vec4 hymn_wind;
// Seconds of wind animation; advanced by the weather system (not TIME, so cutscenes can pause it).
global uniform float hymn_wind_time;
// Time of day in hours [0, 24). Story scenes lock it (SPEC §8.1).
global uniform float hymn_time_of_day;
// Normalised world-space direction towards the sun (or moon at night).
global uniform vec3 hymn_sun_direction;
// Glimmer: rgb = linear tint, a = intensity multiplier for the whole scene.
global uniform vec4 hymn_glimmer;
// Glimmer focus: xyz = world position the motes gather around, w = radius in metres (0 = none).
global uniform vec4 hymn_glimmer_focus;
// Zone night sea-glow energy (colour script rule 3; 0 = off, e.g. ending_dock). Independent of the
// mote energy hymn_glimmer.a. Written by GlimmerField.set_scene_sea_glow() (M1-RND-08).
global uniform float hymn_zone_sea_glow;
// Zone water level: x = current world Y of the sea's rest plane (tide and floods included), y = the
// tide-line datum (world Y) stone weathering keys its wet band to. Written each frame by the zone's
// WaterSurface (publishes_water_level, M1-RND-08).
global uniform vec2 hymn_water_level;

#endif

// Hymn of the Undertow: underwater god rays (M2-RND-02). Docs: docs/kb/tech/underwater.md.
// The fog material of UnderwaterRig's FogVolume. Its density is a 2D noise sampled on the plane
// perpendicular to the sun, so it is constant along the light's direction, and Godot's volumetric fog,
// lit by the sun, draws it as shafts. They fade with depth below the surface and drift slowly
// (hymn_wind_time, the pausable weather clock). Only where volumetric fog is on (High, Ultra).
shader_type fog;

#include "res://game/shaders/include/globals.gdshaderinc"
#include "res://game/shaders/include/common.gdshaderinc"

#define UNDERWATER_SHAFT_AXIS_GUARD 1e-3

uniform float density = 0.045;
uniform float shaft_scale_m = 2.2;
uniform float shaft_contrast = 2.2;
uniform float drift_m_s = 0.25;
uniform float depth_falloff_m = 14.0;
uniform float water_rest_y = 0.0;
uniform vec3 col_scatter : source_color = vec3(0.05, 0.63, 0.58);

void fog() {
	vec3 p = WORLD_POSITION;
	float below = water_rest_y - p.y;
	vec3 L = normalize(hymn_sun_direction + vec3(0.0, UNDERWATER_SHAFT_AXIS_GUARD, 0.0));
	// Two axes across the light: the shaft pattern lives on them, constant along L.
	vec3 ax = normalize(cross(L, abs(L.z) < 0.9 ? vec3(0.0, 0.0, 1.0) : vec3(1.0, 0.0, 0.0)));
	vec3 ay = cross(L, ax);
	vec2 uv = vec2(dot(p, ax), dot(p, ay)) / shaft_scale_m + vec2(drift_m_s * hymn_wind_time / shaft_scale_m, 0.0);
	float shaft = pow(hymn_value_noise2(uv), shaft_contrast);
	DENSITY = below > 0.0 ? density * shaft * exp(-below / depth_falloff_m) : 0.0;
	ALBEDO = col_scatter;
}

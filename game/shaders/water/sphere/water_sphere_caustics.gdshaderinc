// Hymn of the Undertow: caustic light on what's inside the Reefball's water (M3-RND-04). Docs: docs/kb/tech/water_sphere.md.
// For the sphere's MULTIPLY pass: the opaque point behind each pixel (from the depth buffer), if it's inside the ball,
// is lit by the shared caustic web (water_caustics.gdshaderinc) projected along the sun: the pattern lies on the plane
// across the sun's direction, so it falls on players and the floor alike, and slides over a moving body. Its normal
// (from the depth's screen derivatives) faces it to the sun: a face turned away gets none. The web only
// redistributes light around its mean, fading with the water above the point along the sun, with view distance, and
// at the wall. The multiply can't tell sun from shadow: a point in a shadow still gets the web (faint: it scales
// what's there).

#include "res://game/shaders/water/water_caustics.gdshaderinc"

#define SPHERE_CAUSTIC_LAYERS 2

uniform bool use_caustics = true;
// Toward the sun (WaterSphereRig, from the scene's first visible DirectionalLight3D).
uniform vec3 sun_dir = vec3(0.0, 1.0, 0.0);
uniform float caustic_strength = 1.2;
uniform float caustic_scale_per_m = 0.9;
uniform float caustic_speed = 0.7;
uniform float caustic_width = 0.06;
uniform float caustic_blur_per_m = 0.01;
uniform float caustic_fade_in_m = 0.25;
uniform float caustic_falloff_m = 12.0;
uniform float caustic_view_fade_m = 40.0;
// The web fades out over this distance inside the wall (no hard line where a body crosses it).
uniform float caustic_wall_soft_m = 0.3;

// The factor the multiply pass applies to the opaque point behind this pixel (1 = no caustic).
float sphere_caustic(vec2 screen_uv, float depth, mat4 inv_proj, mat4 inv_view) {
	if (!use_caustics || depth <= SPHERE_SKY_DEPTH) {
		return 1.0;
	}
	vec4 v = inv_proj * vec4(screen_uv * 2.0 - 1.0, depth, 1.0);
	vec3 view_p = v.xyz / v.w;
	vec3 p = (inv_view * vec4(view_p, 1.0)).xyz;
	float inside = sphere_radius_m - length(p - sphere_center);
	// The surface's normal from the depth's derivatives (both computed before any branch on the pixel).
	vec3 n = normalize(cross(dFdx(p), dFdy(p)));
	vec3 to_cam = (inv_view * vec4(0.0, 0.0, 0.0, 1.0)).xyz - p;
	n = dot(n, to_cam) < 0.0 ? -n : n;
	if (inside <= 0.0) {
		return 1.0;
	}
	vec3 s = normalize(sun_dir);
	// Water above the point along the sun: to the ball's wall.
	float d = sphere_hit(p, s).y;
	vec3 u = normalize(cross(s, abs(s.y) < 0.99 ? vec3(0.0, 1.0, 0.0) : vec3(1.0, 0.0, 0.0)));
	vec3 w = cross(s, u);
	vec2 q = vec2(dot(p, u), dot(p, w)) * caustic_scale_per_m;
	float width = caustic_width + caustic_blur_per_m * d * (1.0 + d / caustic_falloff_m);
	float c = hymn_caustic(q, hymn_wind_time * caustic_speed, width, SPHERE_CAUSTIC_LAYERS)
			- hymn_caustic_mean(width, SPHERE_CAUSTIC_LAYERS);
	float band = smoothstep(0.0, caustic_fade_in_m, d) * exp(-d / caustic_falloff_m)
			* exp(-length(view_p) / caustic_view_fade_m) * smoothstep(0.0, caustic_wall_soft_m, inside);
	float facing = clamp(dot(n, s), 0.0, 1.0);
	return max(1.0 + caustic_strength * light_level * facing * band * c, 0.0);
}

// Hymn of the Undertow: the Reefball water sphere's surface (M3-RND-01). Docs: docs/kb/tech/water_sphere.md.
// On WaterSphereRig's sphere mesh, both faces:
// - From outside (front faces): the ball refracts what's behind and inside it (the screen, offset by the surface
//   normal) and reflects the sky (Godot's specular, ROUGHNESS low: a Fresnel rim and the sun's glint).
// - From inside (back faces): inside the Snell window (asin(1/ior) from the inward normal) the stadium shows through,
//   refracted; outside it, total internal reflection: the water's own deep colour.
// A slow swell displaces the surface along its normal and stays spherical. The full-screen passes then absorb and
// in-scatter along each ray's water, as for everything inside the ball.
shader_type spatial;
render_mode blend_mix, cull_disabled, depth_draw_never, shadows_disabled;

#include "res://game/shaders/water/sphere/water_sphere.gdshaderinc"

uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap, repeat_disable;
uniform sampler2D depth_tex : hint_depth_texture, filter_nearest, repeat_disable;
uniform float ior = 1.333;
// Screen-space refraction offset per unit of the view-space normal's xy, at a metre from the camera (scaled by 1/z).
uniform float refraction_strength = 0.6;
// Low tier: no screen sample; the ball is a tinted Fresnel shell.
uniform bool use_refraction = true;
uniform vec3 col_tir : source_color = vec3(0.004, 0.068, 0.091);
uniform float tir_gain = 2.2;
uniform float window_soft_deg = 5.0;
uniform float tir_alpha = 0.9;
uniform float roughness = 0.04;
uniform float swell_m = 0.12;
uniform float swell_scale_m = 6.0;
uniform float swell_speed = 0.35;

varying vec3 v_world;

// The screen behind this surface fragment, offset by `off` for refraction. Where the offset sample lands on
// something nearer than the surface (a player in front of the wall), the offset would drag that object's pixels
// into the water as a ghost copy, so the sample falls back to the unrefracted pixel.
vec3 refracted(vec2 uv, vec2 off, float frag_z, mat4 inv_proj) {
	vec2 uv2 = clamp(uv + off, vec2(0.0), vec2(1.0));
	float d = texture(depth_tex, uv2).r;
	vec4 v = inv_proj * vec4(uv2 * 2.0 - 1.0, d, 1.0);
	float z = v.z / v.w;
	return textureLod(screen_tex, z > frag_z ? uv : uv2, 0.0).rgb;
}

// The swell's phase is on the unit ball's direction (a flattened drop's too: mesh and normal stay unit-ball based).
float swell(vec3 dir, float t) {
	float k = sphere_radius_m / swell_scale_m;
	return sin(dot(dir, vec3(0.8, 0.3, 0.5)) * k + t) * 0.5 + sin(dot(dir, vec3(-0.4, 0.7, 0.6)) * k * 1.7 - 1.3 * t)
			* 0.3 + sin(dot(dir, vec3(0.2, -0.9, 0.4)) * k * 2.9 + 0.7 * t) * 0.2;
}

void vertex() {
	vec3 dir = normalize(VERTEX);
	VERTEX += dir * swell_m * swell(dir, hymn_wind_time * swell_speed);
	v_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec3 n_out = sphere_normal(v_world);
	// The swell's slope perturbs the normal a little (finite differences of the same function on the sphere).
	vec3 t1 = normalize(cross(n_out, abs(n_out.y) < 0.99 ? vec3(0.0, 1.0, 0.0) : vec3(1.0, 0.0, 0.0)));
	vec3 t2 = cross(n_out, t1);
	float e = 0.02;
	float tm = hymn_wind_time * swell_speed;
	float h0 = swell(n_out, tm);
	float slope = swell_m / max(sphere_radius_m, 1.0);
	vec3 n_w = normalize(
		n_out - (t1 * (swell(normalize(n_out + t1 * e), tm) - h0) + t2 * (swell(normalize(n_out + t2 * e), tm) - h0))
				* slope / e
	);
	vec3 view_w = normalize(CAMERA_POSITION_WORLD - v_world);
	if (FRONT_FACING) {
		NORMAL = normalize((VIEW_MATRIX * vec4(n_w, 0.0)).xyz);
		vec3 behind = col_scatter * 0.25;
		if (use_refraction) {
			// At grazing angles (the ball's silhouette) the offset would sweep across the screen in bands: it fades
			// out toward the rim, where the Fresnel reflection takes over anyway.
			float facing = clamp(dot(n_w, view_w) * 2.0, 0.0, 1.0);
			vec2 off = NORMAL.xy * refraction_strength * facing / max(-VERTEX.z, 1.0);
			behind = refracted(SCREEN_UV, -off, VERTEX.z, INV_PROJECTION_MATRIX);
		}
		// The surface adds no diffuse of its own: what's behind comes through, the sky reflects (Godot's specular).
		ALBEDO = vec3(0.0);
		EMISSION = behind;
		ROUGHNESS = roughness;
		SPECULAR = 0.5;
		METALLIC = 0.0;
		ALPHA = 1.0;
	} else {
		// From outside, the far wall's back faces must not draw: one mesh, no depth write, so wherever their
		// triangles came later they painted the dark TIR over the near face (wedges along the rings).
		if (sphere_inside_m(CAMERA_POSITION_WORLD) < 0.0) {
			discard;
		}
		vec3 n_in = -n_w;
		NORMAL = normalize((VIEW_MATRIX * vec4(n_in, 0.0)).xyz);
		// The ray from the camera to this point leaves the water only within the critical angle of the outward normal.
		vec3 rd = -view_w;
		float cos_t = dot(rd, n_w);
		float crit = asin(1.0 / ior);
		float soft = radians(window_soft_deg);
		float inside = smoothstep(cos(crit + soft), cos(max(crit - soft, 0.0)), cos_t);
		vec3 through = col_scatter * 0.5;
		if (use_refraction) {
			vec2 off = NORMAL.xy * refraction_strength / max(-VERTEX.z, 1.0);
			through = refracted(SCREEN_UV, off, VERTEX.z, INV_PROJECTION_MATRIX);
		}
		ALBEDO = vec3(0.0);
		EMISSION = mix(col_tir * tir_gain * light_level, through, inside);
		ROUGHNESS = 1.0;
		SPECULAR = 0.0;
		METALLIC = 0.0;
		ALPHA = mix(tir_alpha, 1.0, inside);
	}
}

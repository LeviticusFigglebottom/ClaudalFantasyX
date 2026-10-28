// Hymn of the Undertow: a volumetric smoke column (M3-RND-21). Docs: docs/kb/tech/smoke.md. Driven by SmokeColumn.
// Drawn on the back faces of a box that bounds the column (so a camera inside it still sees smoke), with no depth test:
// each pixel marches its view ray through the box, in the node's own space, up to the opaque scene (the depth buffer),
// and composites the smoke's density front to back.
// - The column (the kit plume's frame): it rises along +Y to height_m, its spine bending downwind toward +X by lean_m
//   (the node is yawed downwind), widening from base_radius_m to top_radius_m and thinning as it rises.
// - Billows: value fBm rising at rise_m_s on the held weather clock (hymn_wind_time, never TIME), offset per column.
// - Light: unshaded. The side and the tops toward the sun read col_lit, the shaded core col_core; the column glows
//   when the sun is behind it (forward scatter); the base takes the fire (col_fire). Never glimmer colours, never
//   rising gold motes (references.md §1.4 rule 10).
shader_type spatial;
render_mode blend_mix, unshaded, cull_front, depth_test_disabled, depth_draw_never, shadows_disabled;

#include "res://game/shaders/include/common.gdshaderinc"
#include "res://game/shaders/include/globals.gdshaderinc"

uniform sampler2D depth_tex : hint_depth_texture, filter_nearest, repeat_disable;
// The box mesh's centre in the column's frame (the mesh is a child at that offset; the march is in the column's frame).
uniform vec3 box_offset = vec3(5.0, 7.0, 0.0);
uniform vec3 box_min = vec3(-6.0, 0.0, -6.0);
uniform vec3 box_max = vec3(16.0, 14.0, 6.0);
uniform float height_m = 14.0;
uniform float lean_m = 9.0;
uniform float base_radius_m = 0.45;
uniform float top_radius_m = 4.0;
uniform float density = 0.6;
uniform float top_thin = 0.65;
uniform float base_fade = 0.06;
uniform float top_fade = 0.35;
uniform float edge_noise = 0.9;
uniform float noise_scale_per_m = 0.32;
uniform float rise_m_s = 0.5;
uniform float seed = 0.0;
uniform vec3 col_lit : source_color = vec3(0.769, 0.737, 0.682);
uniform vec3 col_core : source_color = vec3(0.235, 0.235, 0.227);
uniform vec3 col_fire : source_color = vec3(0.878, 0.439, 0.18);
uniform float light_energy = 1.6;
uniform float fire_glow = 0.6;
uniform float fire_band = 0.12;
uniform float forward_scatter = 0.6;
uniform int steps = 24;

varying vec3 v_obj;

void vertex() {
	v_obj = VERTEX + box_offset;
}

vec3 spine(float h) {
	return vec3(lean_m * pow(h, 1.5) + 0.4 * sin(h * 5.0), 0.0, 0.8 * sin(h * 3.0 + 1.0));
}

float radius_at(float h) {
	return base_radius_m + (top_radius_m - base_radius_m) * pow(h, 0.9);
}

// The smoke's density at an object-space point (0 outside the column).
float smoke_density(vec3 p, float t) {
	float h = p.y / height_m;
	if (h <= 0.0 || h >= 1.0) {
		return 0.0;
	}
	vec3 c = spine(h);
	float d = length(p.xz - c.xz) / radius_at(h);
	if (d > 1.0 + edge_noise * 0.5) {
		return 0.0;
	}
	vec3 q = p * noise_scale_per_m + vec3(seed * 17.0, -t * rise_m_s * noise_scale_per_m, seed * 5.0);
	float n = hymn_fbm3(q, 3, 2.03, 0.5);
	float shape = 1.0 - smoothstep(0.25, 1.0, d + (n - 0.5) * edge_noise);
	float fade = smoothstep(0.0, base_fade, h) * (1.0 - smoothstep(1.0 - top_fade, 1.0, h));
	return density * shape * fade * mix(1.0, 1.0 - top_thin, h) * (0.55 + 0.9 * n);
}

void fragment() {
	mat4 inv_model = inverse(MODEL_MATRIX);
	vec3 ro = (inv_model * vec4(CAMERA_POSITION_WORLD, 1.0)).xyz + box_offset;
	vec3 rd = normalize(v_obj - ro);
	// The box's slabs: entry and exit along the ray (object units).
	vec3 inv = 1.0 / rd;
	vec3 ta = (box_min - ro) * inv;
	vec3 tb = (box_max - ro) * inv;
	vec3 t_lo = min(ta, tb);
	vec3 t_hi = max(ta, tb);
	float t0 = max(max(max(t_lo.x, t_lo.y), t_lo.z), 0.0);
	float t1 = min(min(t_hi.x, t_hi.y), t_hi.z);
	// The opaque scene behind the pixel ends the march.
	float depth = texture(depth_tex, SCREEN_UV).r;
	if (depth > 1e-7) {
		vec4 v = INV_PROJECTION_MATRIX * vec4(SCREEN_UV * 2.0 - 1.0, depth, 1.0);
		vec3 p_world = (INV_VIEW_MATRIX * vec4(v.xyz / v.w, 1.0)).xyz;
		t1 = min(t1, dot((inv_model * vec4(p_world, 1.0)).xyz + box_offset - ro, rd));
	}
	if (t1 <= t0) {
		discard;
	}
	vec3 sun = normalize((inv_model * vec4(normalize(hymn_sun_direction), 0.0)).xyz);
	float fwd = pow(clamp(dot(rd, sun), 0.0, 1.0), 6.0) * forward_scatter;
	float t = hymn_wind_time;
	float dt = (t1 - t0) / float(steps);
	// A fixed per-pixel offset into the first step, interleaved gradient noise (no banding, an even fine dither rather
	// than white grain; the same every frame).
	float ign = fract(52.9829189 * fract(dot(FRAGCOORD.xy, vec2(0.06711056, 0.00583715))));
	float s = t0 + dt * ign;
	float trans = 1.0;
	vec3 col = vec3(0.0);
	for (int i = 0; i < steps; i++) {
		vec3 p = ro + rd * s;
		float dens = smoke_density(p, t);
		if (dens > 0.0) {
			float h = p.y / height_m;
			vec3 c = spine(h);
			vec3 out_dir = normalize(vec3(p.x - c.x, radius_at(h) * 0.6, p.z - c.z));
			float lit = clamp(dot(out_dir, sun) * 0.5 + 0.5, 0.0, 1.0);
			vec3 light = mix(col_core, col_lit, lit) * (1.0 + fwd);
			light += col_fire * fire_glow * (1.0 - smoothstep(0.0, fire_band, h));
			float a = 1.0 - exp(-dens * dt);
			col += trans * a * light;
			trans *= 1.0 - a;
			if (trans < 0.02) {
				break;
			}
		}
		s += dt;
	}
	float alpha = 1.0 - trans;
	if (alpha < 0.004) {
		discard;
	}
	ALBEDO = col / alpha * light_energy;
	ALPHA = alpha;
}

// Glimmer motes: draw-pass body (M1-RND-02). Included by glimmer_motes_draw.gdshader and
// glimmer_motes_reflect.gdshader (define GLIMMER_MIRROR first). Uses the per-particle layout
// documented in glimmer_motes_process.gdshader. The mesh is a 1x1 QuadMesh.
//
// Each mote is a soft additive billboard: a hot gaussian core and a round inverse-square halo at
// the head, and a short soft tail (a fading gaussian streak along the screen-space velocity).
// Soft-particle depth fade hides the hard line where a quad meets opaque geometry (the sea
// surface, a figure). Output is HDR (the core reaches several times 1.0) so Environment glow blooms it;
// nothing here clamps.

#ifndef GLIMMER_MOTES_DRAW_BODY_GDSHADERINC
#define GLIMMER_MOTES_DRAW_BODY_GDSHADERINC

#include "res://game/shaders/include/common.gdshaderinc"

// The core gaussian reaches exp(-CORE_K) = 2% at one core radius.
#define CORE_K 4.0
// Halo fades to zero over the outer part of the quad so the square edge never shows.
#define HALO_EDGE_START 0.55
// A trailing mote spreads its light along the streak: alpha / (1 + this * trail length).
#define TRAIL_ENERGY_SPREAD 0.5
// Oklab b above which a mote counts as warm (gold) for the halo chroma gain.
#define HALO_WARM_B 0.02
// Schlick reflectance of water at normal incidence ((1.33 - 1) / (1.33 + 1))^2.
#define WATER_F0 0.02

group_uniforms look;
uniform float halo_scale : hint_range(1.0, 20.0) = 7.0;   // quad half-size in core radii
uniform float core_gain : hint_range(0.0, 10.0) = 1.0;
uniform float halo_gain : hint_range(0.0, 2.0) = 0.2;
uniform float halo_falloff : hint_range(0.01, 4.0) = 0.35; // inverse-square halo: 1 / (1 + k r^2), r in core radii
// Oklab chroma gain of the halo for warm (released, gold) motes: same hue as the core, richer, so a
// pale gold core blown towards white by bloom still reads gold at dusk (M1-RND-08). 1 = off.
uniform float halo_chroma_gain : hint_range(1.0, 3.0) = 1.0;
uniform float streak_gain : hint_range(0.0, 2.0) = 0.35;  // brightness of the tail streak
uniform float streak_width : hint_range(0.1, 4.0) = 1.5;  // tail half-width, in core radii
uniform float trail_time_s : hint_range(0.0, 4.0) = 0.35; // trail length = screen speed * this
uniform float trail_max_ratio : hint_range(0.0, 10.0) = 1.2; // cap, in halo radii
uniform float trail_scale : hint_range(0.0, 1.0) = 1.0;   // quality tier (0 = round billboards)
// Motes fade out as they approach the lens: invisible nearer than start, full beyond end.
uniform float near_fade_start_m : hint_range(0.0, 10.0) = 0.6;
uniform float near_fade_end_m : hint_range(0.0, 20.0) = 2.0;
// Soft particles: fade over this distance in front of opaque geometry.
uniform float soft_depth_m : hint_range(0.01, 5.0) = 0.35;
uniform sampler2D depth_texture : hint_depth_texture, filter_nearest;
#ifdef GLIMMER_MIRROR
group_uniforms reflection;
uniform float mirror_plane_y = 0.0;
uniform float reflection_gain : hint_range(0.0, 4.0) = 1.0;      // multiplies the Fresnel reflectance
uniform float reflection_softness : hint_range(1.0, 4.0) = 1.6;  // larger, softer reflected halo
#endif

varying vec3 v_color;
varying float v_alpha;
varying vec2 v_local;   // x across, y along velocity; units of halo radius, head at origin
varying float v_trail;  // trail length in halo radii
varying vec3 v_halo_color;

void vertex() {
	vec3 center_w = MODEL_MATRIX[3].xyz;
	vec3 vel_w = INSTANCE_CUSTOM.xyz;
	float core_r = length(MODEL_MATRIX[0].xyz);
	float gain = 1.0;
	float soft = 1.0;
#ifdef GLIMMER_MIRROR
	float above = center_w.y - mirror_plane_y;
	center_w.y = mirror_plane_y - above;
	vel_w.y = -vel_w.y;
	// Reflectance for the ray from the camera to the mirrored mote, where it crosses the plane.
	vec3 ray = normalize(center_w - CAMERA_POSITION_WORLD);
	float cos_i = clamp(abs(ray.y), 0.0, 1.0);
	float fresnel = WATER_F0 + (1.0 - WATER_F0) * pow(1.0 - cos_i, 5.0);
	gain = reflection_gain * fresnel * step(0.0, above);
	soft = reflection_softness;
#endif
	vec3 center = (VIEW_MATRIX * vec4(center_w, 1.0)).xyz;
	vec2 vs = (VIEW_MATRIX * vec4(vel_w, 0.0)).xy;
	float speed = length(vs);
	vec2 axis = speed > HYMN_EPSILON ? vs / speed : vec2(0.0, 1.0);
	vec2 side = vec2(-axis.y, axis.x);
	float halo_r = core_r * halo_scale * soft;
	float trail = min(speed * trail_time_s * trail_scale / max(halo_r, HYMN_EPSILON), trail_max_ratio);
	vec2 q = VERTEX.xy * 2.0;  // QuadMesh corners -> [-1, 1]
	float along = mix(-(1.0 + trail), 1.0, q.y * 0.5 + 0.5);
	VERTEX = center + vec3((side * q.x + axis * along) * halo_r, 0.0);
	NORMAL = vec3(0.0, 0.0, 1.0);
	v_local = vec2(q.x, along);
	v_trail = trail;
	v_color = COLOR.rgb;
	vec3 lab = hymn_linear_srgb_to_oklab(max(COLOR.rgb, vec3(0.0)));
	float warm = smoothstep(0.0, HALO_WARM_B, lab.z);
	lab.yz *= mix(1.0, halo_chroma_gain, warm);
	v_halo_color = max(hymn_oklab_to_linear_srgb(lab), vec3(0.0));
	// Spread the same light over a longer streak instead of adding energy with speed.
	float near = smoothstep(near_fade_start_m, max(near_fade_end_m, near_fade_start_m + HYMN_EPSILON), -center.z);
	v_alpha = COLOR.a * gain * near / (1.0 + TRAIL_ENERGY_SPREAD * trail) / (soft * soft);
	// Invisible motes (at the lens, absorbed under water, unborn) collapse to zero area: no overdraw.
	if (v_alpha <= HYMN_EPSILON) {
		VERTEX = center;
	}
}

// View-space z of the opaque scene at this pixel (Vulkan / Forward+: depth is already in [0, 1]).
float scene_view_z(vec2 screen_uv, mat4 inv_projection) {
	float depth = texture(depth_texture, screen_uv).x;
	vec4 view = inv_projection * vec4(screen_uv * 2.0 - 1.0, depth, 1.0);
	return view.z / view.w;
}

void fragment() {
	vec2 p = v_local;
	// Head: hot core plus a round halo (round on purpose: a halo smeared along the tail shows a
	// hard edge through the core where the smear starts).
	float r_head = length(p);                                         // halo radii from the head
	float rc = r_head * halo_scale;                                   // core radii from the head
	float core = exp(-CORE_K * rc * rc);
	float halo = 1.0 / (1.0 + halo_falloff * rc * rc) * (1.0 - smoothstep(HALO_EDGE_START, 1.0, r_head));
	// Tail: a gaussian streak behind the head that thins and fades towards its end.
	float tail_t = v_trail > HYMN_EPSILON ? clamp(-p.y / v_trail, 0.0, 1.0) : 1.0;
	float fade = (1.0 - tail_t) * (1.0 - tail_t) * step(p.y, 0.0);
	float width = streak_width * (1.0 - 0.5 * tail_t);
	float across = p.x * halo_scale / width;
	float streak = exp(-CORE_K * across * across) * fade;
	float light = core * core_gain + halo * halo_gain + streak * streak_gain;
	// Soft particles.
	float scene_z = scene_view_z(SCREEN_UV, INV_PROJECTION_MATRIX);
#ifdef GLIMMER_MIRROR
	// The mirrored mote lies below the water plane: compare the opaque scene with the point where
	// this view ray meets the plane, so a figure standing in front of the water hides the reflection.
	vec3 world = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float cam_h = CAMERA_POSITION_WORLD.y - mirror_plane_y;
	float drop = CAMERA_POSITION_WORLD.y - world.y;
	float t = drop > HYMN_EPSILON ? clamp(cam_h / drop, 0.0, 1.0) : 0.0;
	float plane_z = VERTEX.z * t;
	float soft = clamp(1.0 + (plane_z - scene_z) / soft_depth_m, 0.0, 1.0) * step(0.0, cam_h);
#else
	float soft = clamp((VERTEX.z - scene_z) / soft_depth_m, 0.0, 1.0);
#endif
	ALBEDO = v_color * (core * core_gain + streak * streak_gain) + v_halo_color * (halo * halo_gain);
	ALPHA = clamp(v_alpha * soft, 0.0, 1.0);
}

#endif

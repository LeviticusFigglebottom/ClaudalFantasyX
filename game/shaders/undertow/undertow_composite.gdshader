// Hymn of the Undertow: composite of the half-resolution storm body (M2-RND-01, experimental).
// Docs: docs/kb/tech/undertow.md. Drawn on the body's own proxy cylinder in the game view, it lays the
// body, rendered premultiplied into a smaller SubViewport (UndertowHalfRes), over the frame at
// SCREEN_UV. A world-space mesh (not a screen quad) gives TAA/FSR2 the storm's real camera motion
// vectors, so the history reprojects as it did for the full-resolution body. Occlusion: the
// SubViewport sees no opaque geometry, so a pixel whose opaque depth is nearer than where the view
// ray enters the storm's wall cylinder (radius occluder_radius_m, slab [0, top_m], storm-local) drops
// the storm. Geometry inside that cylinder (rare) is not occluded.
// Compute mode (use_front, M2-RND-01): body_tex comes from UndertowBodyEffect, which marched against
// this frame's opaque depth, and front_tex holds the mean distance of what each ray saw. A pixel whose
// own opaque surface is nearer than that drops the storm: exact occlusion, inside the volume too, and
// sharp at the full resolution (the march clipped at the farthest surface of the pixel's footprint).
shader_type spatial;
render_mode blend_premul_alpha, unshaded, cull_front, depth_draw_never, depth_test_disabled, fog_disabled,
		shadows_disabled;

uniform sampler2D body_tex : filter_linear, repeat_disable; // linear HDR (the SubViewport uses use_hdr_2d)
uniform sampler2D depth_tex : hint_depth_texture, filter_nearest, repeat_disable;
uniform vec3 storm_center = vec3(0.0);
uniform float occluder_radius_m = 10000.0;
uniform float top_m = 12000.0;
// Compute mode: the effect's front-distance texture (r = metres from the camera), and the switch.
uniform sampler2D front_tex : filter_nearest, repeat_disable;
uniform bool use_front = false;

#define COMPOSITE_FAR_M 1e9
// Reverse-Z: a depth of 0 is the sky (no opaque surface).
#define COMPOSITE_SKY_DEPTH 1e-7

// Distance along the ray (origin ro, unit rd, storm-local) to where it enters the capped wall
// cylinder (radius occluder_radius_m, slab [0, top_m]): 0 from inside, COMPOSITE_FAR_M on a miss.
float entry_t(vec3 ro, vec3 rd) {
	float a = dot(rd.xz, rd.xz);
	float b = dot(ro.xz, rd.xz);
	float c = dot(ro.xz, ro.xz) - occluder_radius_m * occluder_radius_m;
	vec2 tc = vec2(-COMPOSITE_FAR_M, COMPOSITE_FAR_M);
	if (a > 1e-8) {
		float disc = b * b - a * c;
		if (disc < 0.0) {
			return COMPOSITE_FAR_M;
		}
		float s = sqrt(disc);
		tc = vec2((-b - s) / a, (-b + s) / a);
	} else if (c > 0.0) {
		return COMPOSITE_FAR_M;
	}
	vec2 ty = vec2(-COMPOSITE_FAR_M, COMPOSITE_FAR_M);
	if (abs(rd.y) > 1e-8) {
		float t0 = -ro.y / rd.y;
		float t1 = (top_m - ro.y) / rd.y;
		ty = vec2(min(t0, t1), max(t0, t1));
	} else if (ro.y < 0.0 || ro.y > top_m) {
		return COMPOSITE_FAR_M;
	}
	float t_in = max(tc.x, ty.x);
	float t_out = min(tc.y, ty.y);
	if (t_out < max(t_in, 0.0)) {
		return COMPOSITE_FAR_M;
	}
	return max(t_in, 0.0);
}

void fragment() {
	// Four bilinear taps half a texel apart (a 3 x 3 tent over the half-res frame). At half resolution
	// each march-jitter sample covers a 2 x 2 block, which narrows the TAA neighbourhood clamp so the
	// history cannot average the jitter out; the tent removes the stipple first.
	vec2 o = 0.5 / vec2(textureSize(body_tex, 0));
	vec4 body = 0.25 * (texture(body_tex, SCREEN_UV + vec2(-o.x, -o.y)) + texture(body_tex, SCREEN_UV + vec2(o.x, -o.y))
			+ texture(body_tex, SCREEN_UV + vec2(-o.x, o.y)) + texture(body_tex, SCREEN_UV + vec2(o.x, o.y)));
	float depth = texture(depth_tex, SCREEN_UV).r;
	if (depth > COMPOSITE_SKY_DEPTH && body.a > 0.0) {
		vec4 v = INV_PROJECTION_MATRIX * vec4(SCREEN_UV * 2.0 - 1.0, depth, 1.0);
		float t_opaque = length(v.xyz / v.w);
		if (use_front) {
			if (t_opaque < texture(front_tex, SCREEN_UV).r) {
				discard;
			}
		} else {
			vec3 ro = CAMERA_POSITION_WORLD - storm_center;
			vec3 world = (INV_VIEW_MATRIX * vec4(v.xyz / v.w, 1.0)).xyz;
			vec3 rd = normalize(world - CAMERA_POSITION_WORLD);
			if (t_opaque < entry_t(ro, rd)) {
				discard;
			}
		}
	}
	ALBEDO = body.rgb;
	ALPHA = body.a;
}

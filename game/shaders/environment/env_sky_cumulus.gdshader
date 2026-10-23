// Hymn of the Undertow: zone sky with sculpted cumulus (M1-ENV-01 mood test; SPEC §8.1 "painted
// procedural cloud layers. Clouds are a signature element: big, sculpted cumulus"; references §1.6).
// A REQUEST TO RENDERING: this is the Environment stream's mood-test sky, not the signature sky R&D.
// It exists so the Haluna shots have an enormous sky to compose against; fold it into the sky work.
//
// Model: a gradient sky (zenith / horizon colours from the colour script) plus a cumulus slab between
// cloud_base_m and cloud_top_m. Cloud columns come from 2D coverage noise (how much cloud stands on
// a patch of sky) that also sets each column's height, so cells grow rounded domes; 3D fbm erodes
// the tops into billows and the bases stay flat. A march (cloud_steps) integrates density; lighting
// is a two-sample sun march (Beer octaves + powder) plus a height ramp from `col_cloud_shadow`
// (blue-lilac undersides, never grey) to `col_cloud_lit`. Sunlight that has crossed cloud is tinted
// towards `col_cloud_shadow` too (multiple scattering picks up the sky's blue), so the shaded side
// never falls to neutral grey. The clouds render in the half-resolution sky pass and are composited
// in the full pass. The sun disc is drawn only in the full pass, not in the radiance cubemap, so it
// never doubles the water shader's own glint (water.md "Gotchas").
//
// Banding and grain (review-sweep-F B1): the march uses a fixed half-step offset, not per-pixel
// white-noise jitter (the half-res pass turned that into 2x2 stipple, and captures run without TAA),
// density edges are soft enough to span several steps, and the erosion octaves are coarser than the
// step and fade out with distance (cloud_detail_fade_m) so they cannot alias into vertical streaks
// along near-horizontal rays.
//
// `background_energy` scales only what the camera sees (the full-res pass), not the radiance cubemap,
// so the visible sky can sit in its colour-script column without changing the sky fill or the water's
// validated sky reflection. Deterministic: no TIME; `cloud_offset_m` drifts the field.
//
// Cost (M1-RND-12; docs/kb/qa/gpu/2026-10-23-rnd-12-sky.md). Both noises read baked lattices instead
// of hashing. The height field (every march step, the empty ones too) reads `cloud_lattice2`
// (assets_src/vfx/sky/bake_cloud_lattice2.py): the same PCG2D hash per signed cell, four corners per
// textureGather, interpolated in ALU, so the cloud layout is the approved one. The erosion fbm reads
// the PCG3D lattice `cloud_lattice` (the Undertow's assets/vfx/undertow/undertow_noise3d.png) with one
// trilinear fetch per octave; it wraps every 64 cells, so the billows differ from the hashed ones. The quality uniforms (cloud_steps, cloud_erosion_octaves,
// cloud_light_detail, cloud_cubemap_steps) are set per graphics preset by GraphicsSettings
// (graphics_presets.json "sky_detail"); the defaults here are Ultra, which the capture rig renders.
// The radiance cubemap runs its own, cheaper march: it is filtered for fill and reflections, and the
// zone's Sky uses PROCESS_MODE_INCREMENTAL, so a moving sun or drifting offset re-renders it
// time-sliced over frames instead of all six faces in one frame.
shader_type sky;
render_mode use_half_res_pass;

#include "res://game/shaders/include/common.gdshaderinc"

group_uniforms sky;
uniform vec4 col_zenith : source_color = vec4(0.180, 0.498, 0.839, 1.0); // sky_zenith_noon #2E7FD6
uniform vec4 col_horizon : source_color = vec4(0.663, 0.863, 0.949, 1.0); // sky_horizon_noon #A9DCF2
uniform vec4 col_ground : source_color = vec4(0.42, 0.62, 0.70, 1.0); // below the horizon (reflections)
uniform float sky_energy : hint_range(0.0, 4.0) = 1.0;
uniform float horizon_curve : hint_range(0.01, 1.0) = 0.18;
uniform float sun_disc_deg : hint_range(0.1, 5.0) = 0.6;
uniform float sun_glow : hint_range(0.0, 4.0) = 0.6;
uniform float sun_disc_energy : hint_range(0.0, 100.0) = 30.0;
// Visible sky only (full-res pass); the radiance cubemap (fill, reflections) uses sky_energy alone.
uniform float background_energy : hint_range(0.0, 4.0) = 1.0;
group_uniforms;

group_uniforms clouds;
uniform vec4 col_cloud_lit : source_color = vec4(1.0, 0.973, 0.933, 1.0); // cumulus_lit #FFF8EE
uniform vec4 col_cloud_shadow : source_color = vec4(0.561, 0.655, 0.769, 1.0); // cumulus_shadow #8FA7C4
uniform float cloud_base_m = 900.0;
uniform float cloud_top_m = 3200.0;
uniform float cloud_scale_m = 1700.0; // size of a cumulus cell
uniform float cloud_coverage : hint_range(0.0, 1.0) = 0.48; // towards the horizon
uniform float cloud_coverage_overhead : hint_range(0.0, 1.0) = 0.12;
uniform float cloud_clear_radius_m = 2200.0;
uniform float cloud_density : hint_range(0.0, 0.05) = 0.006;
uniform float cloud_erosion : hint_range(0.0, 1.0) = 0.9;
uniform float cloud_erosion_scale_m = 520.0; // billow size; keep it well above the march step
// Erosion fades out between half this distance and this distance (it would alias against the step).
uniform float cloud_detail_fade_m = 26000.0;
// Dome profile: the dome top is field^power x fraction of the slab (smaller power = flatter tops).
uniform float cloud_dome_power : hint_range(0.1, 1.0) = 0.7;
uniform float cloud_tower_fraction : hint_range(0.1, 1.0) = 0.85;
// Density ramp per slab fraction: 10 = 0 to 1 across a tenth of the slab (about 230 m).
uniform float cloud_edge_sharpness : hint_range(1.0, 60.0) = 10.0;
uniform float cloud_light_absorption : hint_range(0.0, 4.0) = 1.0;
uniform float cloud_sun_energy : hint_range(0.0, 12.0) = 6.0;
uniform float cloud_ambient_energy : hint_range(0.0, 8.0) = 3.4;
uniform float cloud_max_distance_m = 60000.0;
uniform vec2 cloud_offset_m = vec2(900.0, -1400.0);
uniform int cloud_steps : hint_range(4, 96) = 64;
// Quality (per preset, graphics_presets.json "sky_detail"): erosion octaves; how much of the erosion
// the two sun samples see (shadows hardly need billows); coarse steps of the radiance-cubemap march.
uniform int cloud_erosion_octaves : hint_range(1, 4) = 4;
uniform float cloud_light_detail : hint_range(0.0, 1.0) = 1.0;
uniform int cloud_cubemap_steps : hint_range(4, 96) = 24;
// The baked PCG3D lattice and its size in cells (assets_src/vfx/undertow/bake_noise3d.py SIZE).
uniform highp sampler3D cloud_lattice : filter_linear, repeat_enable;
uniform float cloud_lattice_cells = 64.0;
// The baked signed PCG2D lattice and its size in cells (bake_cloud_lattice2.py SIZE).
uniform sampler2D cloud_lattice2 : filter_nearest, repeat_enable;
uniform float cloud_lattice2_cells = 512.0;
// Longest march through the slab, in slab thicknesses (grazing rays are capped here).
uniform float cloud_march_slabs : hint_range(1.0, 6.0) = 2.5;
// Fine-step divisor inside cloud, and how many empty fine steps end a refinement.
uniform float cloud_refine : hint_range(1.0, 16.0) = 4.0;
uniform int cloud_refine_exit : hint_range(1, 32) = 6;
// Horizon haze: clouds fade into the horizon colour with distance (aerial perspective).
uniform float haze_distance_m = 38000.0;
// The deck fades out over this last fraction of cloud_max_distance_m (no cut at the far edge).
uniform float cloud_far_fade : hint_range(0.01, 1.0) = 0.25;
group_uniforms;

// Iteration budget of the adaptive march, in coarse steps: the coarse steps themselves plus this
// share of the fine steps (64 steps at refine 4: 192 iterations, as before M1-RND-12).
#define CLOUD_FINE_BUDGET 0.5
// Erosion octaves the radiance-cubemap march samples at most.
#define CLOUD_CUBEMAP_OCTAVES 2

// hymn_value_noise2 of the baked lattice: textureGather at the shared corner of texels i and i + 1
// returns (i0 j1, i1 j1, i1 j0, i0 j0); quintic interpolation in ALU, as hymn_value_noise2_d.
float cloud_noise2(vec2 p) {
	vec2 i = floor(p);
	vec2 f = p - i;
	vec2 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
	vec4 g = textureGather(cloud_lattice2, (i + 1.0) / cloud_lattice2_cells, 0);
	return mix(mix(g.w, g.z, u.x), mix(g.x, g.y, u.x), u.y);
}

// hymn_fbm2 (rotated octaves) over the baked lattice.
float cloud_fbm2(vec2 p, int octaves, float lacunarity) {
	float sum = 0.0;
	float amp = 1.0;
	float norm = 0.0;
	for (int o = 0; o < octaves; o++) {
		sum += amp * cloud_noise2(p);
		norm += amp;
		p = HYMN_FBM_ROT2 * p * lacunarity;
		amp *= 0.5;
	}
	return sum / max(norm, HYMN_EPSILON);
}

// hymn_value_noise3 of the baked lattice: one trilinear fetch at a quintic-remapped coordinate.
float cloud_noise3(vec3 p) {
	vec3 i = floor(p);
	vec3 f = p - i;
	vec3 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
	return texture(cloud_lattice, (i + u + 0.5) / cloud_lattice_cells).r;
}

// hymn_fbm3 (lacunarity 2, gain 0.5, the same octave shift) over the baked lattice.
float cloud_fbm3(vec3 p, int octaves) {
	float sum = 0.0;
	float amp = 1.0;
	float norm = 0.0;
	for (int o = 0; o < octaves; o++) {
		sum += amp * cloud_noise3(p);
		norm += amp;
		p = p * 2.0 + HYMN_FBM_SHIFT3;
		amp *= 0.5;
	}
	return sum / max(norm, HYMN_EPSILON);
}

// 0 where no cloud stands, up to 1 under the tallest tower (2D coverage as a height field).
float cloud_height_field(vec2 xz) {
	vec2 p = (xz + cloud_offset_m) / cloud_scale_m;
	// Three octaves only: the dome walls extrude this field vertically, so any finer 2D detail would
	// draw vertical streaks up the cloud faces. The 3D erosion supplies the fine shape instead.
	float c = cloud_fbm2(p, 3, 2.03);
	// Fair-weather noon: the sky overhead stays mostly clear while cumulus banks up towards the
	// horizon (coverage rises with distance from the viewer, who sits at the origin of EYEDIR).
	float far = smoothstep(cloud_clear_radius_m, cloud_clear_radius_m * 4.0, length(xz));
	float thr = 1.0 - mix(cloud_coverage_overhead, cloud_coverage, far);
	return clamp((c - thr) / max(1.0 - thr, 0.01), 0.0, 1.0);
}

// Cumulus as domes over the height field: a point is inside where its height fraction is under
// field^dome_power; 3D fbm (weighted by `detail`, 0..1; `octaves` deep) erodes the surface into
// billows; flat bases.
float cloud_density_at(vec3 p, float detail, int octaves) {
	float hf = cloud_height_field(p.xz);
	if (hf <= 0.0) {
		return 0.0;
	}
	float h = (p.y - cloud_base_m) / (cloud_top_m - cloud_base_m);
	float surf = pow(hf, cloud_dome_power) * cloud_tower_fraction - h;
	float reach = cloud_erosion * (0.35 + h) * 0.5;
	if (surf < -reach) {
		return 0.0;
	}
	float ero = 0.0;
	if (detail > 0.01) {
		ero = (cloud_fbm3(p / cloud_erosion_scale_m, octaves) - 0.5) * detail;
	}
	float d = (surf + ero * cloud_erosion * (0.35 + h)) * cloud_edge_sharpness;
	d *= smoothstep(0.0, 0.04, h);
	return clamp(d, 0.0, 1.0);
}

// Premultiplied: rgb is the light the clouds add, a their coverage (both already faded by haze).
vec4 clouds(vec3 dir, vec3 sun_dir, int steps, int octaves) {
	if (dir.y < 0.01) {
		return vec4(0.0);
	}
	float slab = cloud_top_m - cloud_base_m;
	float t0 = cloud_base_m / dir.y;
	float t1 = cloud_top_m / dir.y;
	if (t0 > cloud_max_distance_m) {
		return vec4(0.0);
	}
	t1 = min(t1, t0 + slab * cloud_march_slabs);
	// Adaptive march: coarse steps through empty sky; at the first density, step back and refine
	// to 1/cloud_refine of the step, so no single step adds a large slice of opacity (that is what
	// draws contour rings); after cloud_refine_exit empty fine steps, go coarse again.
	float dt_coarse = (t1 - t0) / float(steps);
	float dt_fine = dt_coarse / cloud_refine;
	float detail = 1.0 - smoothstep(cloud_detail_fade_m * 0.5, cloud_detail_fade_m, t0);
	float light_detail = detail * cloud_light_detail;
	float trans = 1.0;
	vec3 light = vec3(0.0);
	float mu = dot(dir, sun_dir);
	float phase = 0.8 + 0.9 * pow(max(mu, 0.0), 6.0); // forward-scatter silver lining
	float dl = slab * 0.18;
	float t = t0 + 0.5 * dt_coarse;
	bool fine = false;
	int empty_run = 0;
	float d_prev = 0.0;
	int iterations = steps + int(float(steps) * cloud_refine * CLOUD_FINE_BUDGET);
	for (int i = 0; i < iterations; i++) {
		if (t > t1) {
			break;
		}
		// Iteration budget (review-sweep-H R3): once even coarse steps would no longer reach t1 with
		// the iterations left, march the rest at the step that does, instead of cutting far cloud off.
		float reach_dt = (t1 - t) / float(iterations - i);
		bool tight = reach_dt >= dt_coarse;
		vec3 p = dir * t;
		float d = cloud_density_at(p, detail, octaves);
		if (!fine || tight) {
			if (d <= 0.0) {
				t += max(dt_coarse, reach_dt);
				continue;
			}
			if (!tight) {
				fine = true;
				empty_run = 0;
				d_prev = 0.0;
				t = max(t0, t - dt_coarse + 0.5 * dt_fine);
				continue;
			}
		}
		float dt = tight ? reach_dt : dt_fine;
		if (d > 0.0) {
			empty_run = 0;
			float sigma = d * cloud_density;
			// Two-sample light march towards the sun.
			float od = cloud_density_at(p + sun_dir * dl, light_detail, octaves)
					+ cloud_density_at(p + sun_dir * dl * 2.5, light_detail, octaves);
			// Multiple scattering, approximated by three Beer octaves (each a = 0.5, b = 0.4):
			// without it the interiors go black, and real cumulus never does.
			float tau = od * cloud_density * dl * cloud_light_absorption;
			float sun_t = (exp(-tau) + 0.6 * exp(-tau * 0.3) + 0.45 * exp(-tau * 0.08)) / 2.05;
			float powder = 1.0 - exp(-sigma * dt_coarse * 2.0);
			float hfrac = clamp((p.y - cloud_base_m) / slab, 0.0, 1.0);
			vec3 amb = mix(col_cloud_shadow.rgb, col_cloud_lit.rgb, smoothstep(0.1, 0.9, hfrac)) * cloud_ambient_energy;
			// Light that crossed cloud is bluer: multiple scattering mixes in the sky's colour.
			vec3 sun_col = mix(col_cloud_shadow.rgb, col_cloud_lit.rgb, sun_t);
			vec3 sun_c = sun_col * cloud_sun_energy * sun_t * mix(1.0, powder, 0.5) * phase;
			vec3 c = amb * (0.45 + 0.55 * hfrac) + sun_c;
			// Trapezoid rule over the step: the opacity a step adds varies smoothly with where the
			// samples fall against the cloud surface, so lower step counts do not draw contours.
			float a = 1.0 - exp(-0.5 * (d + d_prev) * cloud_density * dt);
			light += trans * a * c;
			trans *= 1.0 - a;
			if (trans < 0.02) {
				break;
			}
		} else {
			empty_run += 1;
			if (empty_run >= cloud_refine_exit) {
				fine = false;
			}
		}
		d_prev = d;
		t += dt;
	}
	float haze = 1.0 - exp(-t0 / haze_distance_m);
	float far = 1.0 - smoothstep(cloud_max_distance_m * (1.0 - cloud_far_fade), cloud_max_distance_m, t0);
	float fade = (1.0 - haze * 0.5) * far;
	return vec4(light * fade, (1.0 - trans) * fade);
}

vec3 sky_gradient(vec3 dir) {
	float h = clamp(dir.y, 0.0, 1.0);
	float g = pow(1.0 - h, 1.0 / max(horizon_curve, 0.01) * 0.25);
	vec3 c = mix(col_zenith.rgb, col_horizon.rgb, g);
	if (dir.y < 0.0) {
		c = mix(col_horizon.rgb, col_ground.rgb, smoothstep(0.0, 0.3, -dir.y));
	}
	return c * sky_energy;
}

void sky() {
	vec3 sun_dir = LIGHT0_ENABLED ? LIGHT0_DIRECTION : vec3(0.0, 1.0, 0.0);
	vec3 dir = EYEDIR;
	if (AT_HALF_RES_PASS) {
		vec4 cl = clouds(dir, sun_dir, cloud_steps, cloud_erosion_octaves);
		COLOR = cl.rgb;
		ALPHA = cl.a;
	} else {
		vec3 c = sky_gradient(dir);
		float mu = dot(dir, sun_dir);
		c += col_horizon.rgb * sun_glow * pow(max(mu, 0.0), 24.0) * (LIGHT0_ENABLED ? LIGHT0_ENERGY * 0.25 : 0.0);
		if (!AT_CUBEMAP_PASS && LIGHT0_ENABLED) {
			float disc = smoothstep(cos(radians(sun_disc_deg)), cos(radians(sun_disc_deg * 0.8)), mu);
			c += LIGHT0_COLOR * sun_disc_energy * disc;
		}
		vec4 cl = AT_CUBEMAP_PASS
				? clouds(dir, sun_dir, cloud_cubemap_steps, min(cloud_erosion_octaves, CLOUD_CUBEMAP_OCTAVES))
				: HALF_RES_COLOR;
		// Over-compositing of premultiplied cloud light (review-sweep-H R4: mix() multiplied it by
		// alpha a second time, darkening thin edges and hazed far cloud quadratically).
		COLOR = (c * (1.0 - cl.a) + cl.rgb * (LIGHT0_ENABLED ? 1.0 : 0.3)) * (AT_CUBEMAP_PASS ? 1.0 : background_energy);
	}
}

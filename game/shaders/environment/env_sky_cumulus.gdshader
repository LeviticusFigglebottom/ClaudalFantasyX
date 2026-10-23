// Hymn of the Undertow: zone sky with sculpted cumulus (M1-ENV-01 mood test; SPEC §8.1 "painted
// procedural cloud layers. Clouds are a signature element: big, sculpted cumulus"; references §1.6).
// A REQUEST TO RENDERING: this is the Environment stream's mood-test sky, not the signature sky R&D.
// It exists so the Haluna shots have an enormous sky to compose against; fold it into the sky work.
//
// Model: a gradient sky (zenith / horizon colours from the colour script) plus a cumulus slab between
// cloud_base_m and cloud_top_m. Cloud columns come from 2D coverage noise (how much cloud stands on
// a patch of sky) that also sets each column's height, so cells grow rounded towers; 3D fbm erodes
// the tops into cauliflower and the bases stay flat. A short march (cloud_steps) integrates density;
// lighting is a two-sample sun march (Beer + powder) plus a height ramp from `col_cloud_shadow`
// (blue-lilac undersides, never grey) to `col_cloud_lit`. The clouds render in the half-resolution
// sky pass and are composited in the full pass. The sun disc is drawn only in the full pass, not in
// the radiance cubemap, so it never doubles the water shader's own glint (water.md "Gotchas").
// Deterministic: no TIME; `cloud_offset_m` drifts the field when a zone animates it.
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
group_uniforms;

group_uniforms clouds;
uniform vec4 col_cloud_lit : source_color = vec4(1.0, 0.973, 0.933, 1.0); // cumulus_lit #FFF8EE
uniform vec4 col_cloud_shadow : source_color = vec4(0.561, 0.655, 0.769, 1.0); // cumulus_shadow #8FA7C4
uniform float cloud_base_m = 900.0;
uniform float cloud_top_m = 3200.0;
uniform float cloud_scale_m = 1700.0; // size of a cumulus cell
uniform float cloud_coverage : hint_range(0.0, 1.0) = 0.4; // towards the horizon
uniform float cloud_coverage_overhead : hint_range(0.0, 1.0) = 0.18;
uniform float cloud_clear_radius_m = 2500.0;
uniform float cloud_density : hint_range(0.0, 0.05) = 0.006;
uniform float cloud_erosion : hint_range(0.0, 1.0) = 0.6;
uniform float cloud_edge_sharpness : hint_range(1.0, 40.0) = 8.0;
uniform float cloud_light_absorption : hint_range(0.0, 4.0) = 0.6;
uniform float cloud_sun_energy : hint_range(0.0, 8.0) = 3.0;
uniform float cloud_ambient_energy : hint_range(0.0, 4.0) = 2.0;
uniform float cloud_max_distance_m = 60000.0;
uniform vec2 cloud_offset_m = vec2(0.0, 0.0);
uniform int cloud_steps : hint_range(4, 64) = 48;
// Horizon haze: clouds fade into the horizon colour with distance (aerial perspective).
uniform float haze_distance_m = 38000.0;
group_uniforms;

// 0 where no cloud stands, up to 1 under the tallest tower (2D coverage as a height field).
float cloud_height_field(vec2 xz) {
	vec2 p = (xz + cloud_offset_m) / cloud_scale_m;
	float c = hymn_fbm2(p, 5, 2.03, 0.5);
	// Fair-weather noon: the sky overhead stays mostly clear while cumulus banks up towards the
	// horizon (coverage rises with distance from the viewer, who sits at the origin of EYEDIR).
	float far = smoothstep(cloud_clear_radius_m, cloud_clear_radius_m * 4.0, length(xz));
	float thr = 1.0 - mix(cloud_coverage_overhead, cloud_coverage, far);
	return clamp((c - thr) / max(1.0 - thr, 0.01), 0.0, 1.0);
}

// Cumulus as domes over the height field: a point is inside where its height fraction is under
// sqrt(field) (sqrt broadens the domes); 3D fbm erodes the surface into cauliflower; flat bases.
float cloud_density_at(vec3 p) {
	float hf = cloud_height_field(p.xz);
	if (hf <= 0.0) {
		return 0.0;
	}
	float h = (p.y - cloud_base_m) / (cloud_top_m - cloud_base_m);
	float surf = sqrt(hf) - h;
	float ero = hymn_fbm3(p / (cloud_scale_m * 0.12), 4, 2.1, 0.55) - 0.5;
	float d = surf * cloud_edge_sharpness + ero * cloud_erosion * (0.6 + h) * cloud_edge_sharpness * 0.25;
	d *= smoothstep(0.0, 0.03, h);
	return clamp(d, 0.0, 1.0);
}

vec4 clouds(vec3 dir, vec3 sun_dir) {
	if (dir.y < 0.01) {
		return vec4(0.0);
	}
	float t0 = cloud_base_m / dir.y;
	float t1 = cloud_top_m / dir.y;
	if (t0 > cloud_max_distance_m) {
		return vec4(0.0);
	}
	t1 = min(t1, t0 + (cloud_top_m - cloud_base_m) * 3.0);
	float dt = (t1 - t0) / float(cloud_steps);
	// Per-direction jitter of the sample positions: with 40 steps the residual grain is far less
	// objectionable than the stair-stepping a fixed offset gives (captures run without TAA).
	float jitter = 0.5 + 0.6 * (hymn_hash12(dir.xz * 8192.0 + dir.y * 17.0) - 0.5);
	float trans = 1.0;
	vec3 light = vec3(0.0);
	float mu = dot(dir, sun_dir);
	float phase = 0.6 + 0.9 * pow(max(mu, 0.0), 6.0); // forward-scatter silver lining
	for (int i = 0; i < cloud_steps; i++) {
		float t = t0 + (float(i) + jitter) * dt;
		vec3 p = dir * t;
		float d = cloud_density_at(p);
		if (d > 0.0) {
			float sigma = d * cloud_density;
			// Two-sample light march towards the sun.
			float dl = (cloud_top_m - cloud_base_m) * 0.18;
			float od = cloud_density_at(p + sun_dir * dl) + cloud_density_at(p + sun_dir * dl * 2.5);
			// Multiple scattering, approximated by three Beer octaves (each a = 0.5, b = 0.4):
			// without it the interiors go black, and real cumulus never does.
			float tau = od * cloud_density * dl * cloud_light_absorption;
			float sun_t = (exp(-tau) + 0.5 * exp(-tau * 0.4) + 0.25 * exp(-tau * 0.16)) / 1.75;
			float powder = 1.0 - exp(-sigma * dt * 2.0);
			float hfrac = clamp((p.y - cloud_base_m) / (cloud_top_m - cloud_base_m), 0.0, 1.0);
			vec3 amb = mix(col_cloud_shadow.rgb, col_cloud_lit.rgb, smoothstep(0.0, 0.8, hfrac)) * cloud_ambient_energy;
			vec3 sun_c = col_cloud_lit.rgb * cloud_sun_energy * sun_t * mix(1.0, powder, 0.5) * phase;
			vec3 c = amb * (0.55 + 0.45 * hfrac) + sun_c;
			float a = 1.0 - exp(-sigma * dt);
			light += trans * a * c;
			trans *= 1.0 - a;
			if (trans < 0.02) {
				break;
			}
		}
	}
	float haze = 1.0 - exp(-t0 / haze_distance_m);
	return vec4(light, (1.0 - trans) * (1.0 - haze * 0.85));
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
		vec4 cl = clouds(dir, sun_dir);
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
		vec4 cl = AT_CUBEMAP_PASS ? clouds(dir, sun_dir) : vec4(HALF_RES_COLOR.rgb, HALF_RES_COLOR.a);
		COLOR = mix(c, cl.rgb * (LIGHT0_ENABLED ? 1.0 : 0.3), cl.a);
	}
}

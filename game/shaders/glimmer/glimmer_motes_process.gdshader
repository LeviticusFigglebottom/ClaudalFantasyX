// Glimmer motes: particle process shader (M1-RND-02). Driven by GlimmerField
// (game/vfx/glimmer/glimmer_field.gd); every uniform below is pushed from game/data/vfx/glimmer.json.
// Docs: docs/kb/tech/glimmer.md. Meaning rules: docs/kb/art/color_script.md, narrative light rules 1-2.
//
// Per-particle layout (read by glimmer_motes_draw*.gdshader):
//   TRANSFORM  basis = uniform scale of the core radius (m), origin = world position
//   COLOR      rgb = linear colour * energy (HDR), a = life/absorption envelope
//   CUSTOM     xyz = world velocity (m/s, for the stretched trail), w = unused
//   USERDATA1  four uniform randoms fixed at spawn (motion)
//   USERDATA3  four more (x = brightness)
//   USERDATA2  x = age (s), y = spiral phase (rad), z = spiral sense (+-1), w = core radius (m)
shader_type particles;
render_mode disable_force;

#include "res://game/shaders/include/globals.gdshaderinc"
#include "res://game/shaders/include/glimmer.gdshaderinc"

// Must equal attractor.max in glimmer.json (a test checks it).
#define HYMN_GLIMMER_MAX_ATTRACTORS 8
// Must equal GlimmerField.MAX_SPAWN_POINTS (a test checks it).
#define HYMN_GLIMMER_MAX_SPAWN_POINTS 16
#define EMISSION_BOX 0
#define EMISSION_DISC 1
#define SALT_A 0x9E3779B9u
#define SALT_B 0x85EBCA6Bu
#define SALT_C 0xC2B2AE35u

group_uniforms state;
// Transition endpoints from GlimmerState.shader_state(). blend: 0 held, 1 released.
// machine: 1 = bound (still, teal). Outside a release from == to and progress == 1.
uniform float blend_from : hint_range(0.0, 1.0) = 0.0;
uniform float blend_to : hint_range(0.0, 1.0) = 0.0;
uniform float machine_from : hint_range(0.0, 1.0) = 0.0;
uniform float machine_to : hint_range(0.0, 1.0) = 0.0;
uniform float transition_progress : hint_range(0.0, 1.0) = 1.0;
// The release travels outward from release_origin as a wave: a mote's own lerp starts after
// wave_fraction * rank of the field-wide duration (rank: distance / wave radius, plus jitter).
uniform vec3 release_origin = vec3(0.0);
uniform float release_wave_radius_m : hint_range(0.01, 100.0) = 4.0;
uniform float release_wave_fraction : hint_range(0.0, 0.9) = 0.4;
uniform float release_wave_jitter : hint_range(0.0, 1.0) = 0.3;
uniform float flow_time_s = 0.0;                             // GlimmerField clock (pausable)

group_uniforms colours;
uniform vec3 col_released : source_color = vec3(1.0, 0.914, 0.722);
uniform vec3 col_released_hi : source_color = vec3(0.957, 0.973, 1.0);
uniform vec3 col_held : source_color = vec3(0.498, 0.776, 0.851);
uniform vec3 col_machine : source_color = vec3(0.31, 0.702, 0.69);
uniform float energy_released : hint_range(0.0, 10.0) = 3.0;
uniform float energy_held : hint_range(0.0, 10.0) = 1.5;
uniform float energy_machine : hint_range(0.0, 10.0) = 1.2;
uniform float released_hi_shift : hint_range(0.0, 1.0) = 0.55;
uniform bool follow_scene_intensity = true;  // energy = hymn_glimmer.a instead of energy_<mode>
uniform float intensity : hint_range(0.0, 10.0) = 1.0;
uniform float brightness_min : hint_range(0.0, 1.0) = 0.3;  // dimmest mote relative to the brightest
uniform float brightness_power : hint_range(0.1, 8.0) = 1.5;

group_uniforms emission;
uniform int emission_shape : hint_range(0, 1) = 0;
uniform vec3 emission_extents_m = vec3(3.0, 1.0, 3.0);  // box half-extents; disc: x = outer radius, y = half height
uniform float emission_inner_radius_m : hint_range(0.0, 50.0) = 0.0;
// Vertical density gradient: > 1 packs motes toward the bottom of the volume (near the water and
// the figure), < 1 toward the top. 1 = uniform (M1-RND-08).
uniform float emission_height_bias : hint_range(0.1, 8.0) = 1.0;
// Disc emission: > 1 clusters motes toward the centre (the figure), sparse at the rim. 1 = uniform.
uniform float emission_center_bias : hint_range(0.1, 8.0) = 1.0;
// Authored spawn points (local to the field): mote i starts at spawn_points[i % count]. 0 = random.
uniform int spawn_point_count : hint_range(0, 16) = 0;
uniform vec3 spawn_points[HYMN_GLIMMER_MAX_SPAWN_POINTS];
// Field -> world (identity unless the field is in local space). The motion rules live in world
// space (water height, sea direction, attractors), particles in local space follow their host.
uniform mat4 field_to_world = mat4(1.0);
uniform mat3 world_to_field_basis = mat3(1.0);
uniform float size_min_m : hint_range(0.001, 1.0) = 0.012;
uniform float size_max_m : hint_range(0.001, 1.0) = 0.045;
uniform float size_power : hint_range(0.5, 8.0) = 3.0;

group_uniforms motion;
uniform vec3 sea_direction = vec3(0.0, 0.0, 1.0);
uniform float water_height_m = 0.0;
uniform float rise_min_mps : hint_range(0.0, 2.0) = 0.15;
uniform float rise_max_mps : hint_range(0.0, 2.0) = 0.4;
uniform float spiral_radius_min_m : hint_range(0.0, 3.0) = 0.2;
uniform float spiral_radius_max_m : hint_range(0.0, 3.0) = 0.6;
uniform float spiral_rate_rad_s : hint_range(0.0, 6.0) = 0.7;
uniform float released_curl_scale : hint_range(0.0, 4.0) = 0.6;
uniform float drift_min_mps : hint_range(0.0, 2.0) = 0.05;
uniform float drift_max_mps : hint_range(0.0, 2.0) = 0.2;
uniform float down_bias_min_deg : hint_range(0.0, 90.0) = 15.0;
uniform float down_bias_max_deg : hint_range(0.0, 90.0) = 30.0;
uniform float heading_spread_deg : hint_range(0.0, 180.0) = 35.0;
uniform float held_curl_scale : hint_range(0.0, 4.0) = 1.0;
uniform float curl_frequency : hint_range(0.01, 4.0) = 0.35;
uniform float curl_strength_mps : hint_range(0.0, 2.0) = 0.09;
uniform float curl_evolve : hint_range(0.0, 1.0) = 0.04;
uniform int curl_octaves : hint_range(1, 4) = 2;
uniform float response_rate : hint_range(0.05, 20.0) = 1.4;
uniform float underwater_drag : hint_range(0.0, 20.0) = 3.0;
uniform float underwater_absorb_per_m : hint_range(0.0, 20.0) = 2.2;

group_uniforms life;
uniform float breath_rate_hz : hint_range(0.0, 2.0) = 0.18;
uniform float breath_depth : hint_range(0.0, 1.0) = 0.22;
uniform float fade_in_fraction : hint_range(0.001, 1.0) = 0.12;
uniform float fade_out_fraction : hint_range(0.001, 1.0) = 0.3;
// Persistent fields (GlimmerField.respawn = false): fade in over persist_fade_in_s, never fade out.
uniform bool persistent = false;
uniform float persist_fade_in_s : hint_range(0.01, 30.0) = 1.5;

group_uniforms attractors;
uniform int attractor_count : hint_range(0, 8) = 0;
uniform vec4 attractor_pos_radius[HYMN_GLIMMER_MAX_ATTRACTORS];  // xyz world pos, w orbit radius (m)
uniform vec4 attractor_params[HYMN_GLIMMER_MAX_ATTRACTORS];      // strength, swirl, half height (m), influence (m)
uniform float attractor_pull_mps : hint_range(0.0, 4.0) = 0.5;
uniform float attractor_swirl_mps : hint_range(0.0, 4.0) = 0.45;
uniform float attractor_keep_drift : hint_range(0.0, 1.0) = 0.55;
uniform float attractor_influence_scale : hint_range(1.0, 10.0) = 3.0;
uniform bool follow_global_focus = true;  // hymn_glimmer_focus as an extra attractor
uniform float focus_strength : hint_range(0.0, 4.0) = 0.8;
uniform float focus_half_height_m : hint_range(0.0, 4.0) = 0.8;

vec4 rand4(uint seed_value, uint number, uint salt) {
	uvec3 h = hymn_pcg3d(uvec3(seed_value, number, salt));
	uvec3 h2 = hymn_pcg3d(h ^ uvec3(salt));
	return vec4(vec3(h), float(h2.x)) * HYMN_UINT_TO_UNIT;
}

// Orbit velocity around one vertical-segment attractor. Returns xyz = velocity, w = weight [0, 1].
vec4 orbit(vec3 pos, vec4 pos_radius, vec4 params, float sense) {
	float radius = max(pos_radius.w, HYMN_EPSILON);
	vec3 axis_point = vec3(pos_radius.x, clamp(pos.y, pos_radius.y - params.z, pos_radius.y + params.z), pos_radius.z);
	vec3 d = pos - axis_point;
	float dist = length(d);
	float influence = max(params.w, radius * 1.01);
	float weight = (1.0 - smoothstep(radius, influence, dist)) * clamp(params.x, 0.0, 1.0);
	if (weight <= 0.0) {
		return vec4(0.0);
	}
	vec3 n = d / max(dist, HYMN_EPSILON);
	// Spring towards the orbit shell: push out inside, pull in outside.
	vec3 radial = -n * clamp((dist - radius) / radius, -1.0, 1.0) * attractor_pull_mps * params.x;
	vec3 flat_n = vec3(n.x, 0.0, n.z);
	float flat_len = length(flat_n);
	vec3 tangent = flat_len > HYMN_EPSILON ? cross(vec3(0.0, 1.0, 0.0), flat_n / flat_len) : vec3(0.0);
	vec3 swirl = tangent * attractor_swirl_mps * params.y * params.x * sense;
	return vec4(radial + swirl, weight);
}

vec3 oklab_mix(vec3 a, vec3 b, float t) {
	return max(hymn_oklab_to_linear_srgb(mix(hymn_linear_srgb_to_oklab(a), hymn_linear_srgb_to_oklab(b), t)), vec3(0.0));
}

void start() {
	vec4 r0 = rand4(RANDOM_SEED, NUMBER, SALT_A);
	vec4 r1 = rand4(RANDOM_SEED, NUMBER, SALT_B);
	USERDATA1 = r1;
	USERDATA3 = rand4(RANDOM_SEED, NUMBER, SALT_C);
	float core = mix(size_min_m, size_max_m, pow(r0.w, size_power));
	USERDATA2 = vec4(0.0, r1.w * HYMN_TAU, r0.w > 0.2 ? 1.0 : -1.0, core);
	if (RESTART_POSITION) {
		vec3 local;
		if (emission_shape == EMISSION_DISC) {
			float outer = emission_extents_m.x;
			float inner = min(emission_inner_radius_m, outer);
			float rad = sqrt(mix(inner * inner, outer * outer, pow(r0.y, emission_center_bias)));
			float ang = r0.x * HYMN_TAU;
			local = vec3(cos(ang) * rad, (r0.z * 2.0 - 1.0) * emission_extents_m.y, sin(ang) * rad);
		} else {
			local = (r0.xyz * 2.0 - 1.0) * emission_extents_m;
		}
		local.y = (pow(r0.z, emission_height_bias) * 2.0 - 1.0) * emission_extents_m.y;
		if (spawn_point_count > 0) {
			local = spawn_points[int(NUMBER) % min(spawn_point_count, HYMN_GLIMMER_MAX_SPAWN_POINTS)];
		}
		vec3 world = (EMISSION_TRANSFORM * vec4(local, 1.0)).xyz;
		TRANSFORM = mat4(vec4(core, 0.0, 0.0, 0.0), vec4(0.0, core, 0.0, 0.0), vec4(0.0, 0.0, core, 0.0), vec4(world, 1.0));
	}
	if (RESTART_VELOCITY) {
		VELOCITY = vec3(0.0);
	}
	if (RESTART_CUSTOM) {
		CUSTOM = vec4(0.0);
	}
	if (RESTART_COLOR) {
		COLOR = vec4(0.0);
	}
}

void process() {
	vec4 r = USERDATA1;
	float age = USERDATA2.x + DELTA;
	USERDATA2.x = age;
	float life_t = clamp(age / max(LIFETIME, HYMN_EPSILON), 0.0, 1.0);
	vec3 pos = (field_to_world * vec4(TRANSFORM[3].xyz, 1.0)).xyz;
	float rank = clamp(length(pos - release_origin) / release_wave_radius_m, 0.0, 1.0);
	rank = mix(rank, r.z, release_wave_jitter);
	float local = smoothstep(0.0, 1.0,
			clamp((transition_progress - release_wave_fraction * rank) / (1.0 - release_wave_fraction), 0.0, 1.0));
	float blend = mix(blend_from, blend_to, local);
	float still = mix(machine_from, machine_to, local);

	// Coherent drift: one shared divergence-free field, so neighbours move together like a current.
	vec3 q = pos * curl_frequency + vec3(0.0, flow_time_s * curl_evolve, 0.0);
	vec3 curl = hymn_curl_fbm3(q, curl_octaves, 2.0, 0.5) * curl_strength_mps;

	// Held: sideways and down, towards the sea.
	vec3 sea = vec3(sea_direction.x, 0.0, sea_direction.z);
	sea = length(sea) > HYMN_EPSILON ? normalize(sea) : vec3(0.0, 0.0, 1.0);
	float heading = radians((r.x * 2.0 - 1.0) * heading_spread_deg);
	vec3 lateral = vec3(sea.x * cos(heading) - sea.z * sin(heading), 0.0, sea.x * sin(heading) + sea.z * cos(heading));
	float bias = radians(mix(down_bias_min_deg, down_bias_max_deg, r.y));
	vec3 v_held = mix(drift_min_mps, drift_max_mps, r.z) * (cos(bias) * lateral - vec3(0.0, sin(bias), 0.0));

	// Released: a slow vertical spiral upwards.
	float spiral_r = mix(spiral_radius_min_m, spiral_radius_max_m, r.w);
	float omega = spiral_rate_rad_s * USERDATA2.z;
	float ang = USERDATA2.y + age * omega;
	vec3 v_released = vec3(0.0, mix(rise_min_mps, rise_max_mps, r.x), 0.0)
			+ spiral_r * omega * vec3(-sin(ang), 0.0, cos(ang));

	vec3 target = mix(v_held, v_released, blend) + curl * mix(held_curl_scale, released_curl_scale, blend);

	// Gathering around the living: per-emitter attractors plus the scene focus.
	vec3 pull = vec3(0.0);
	float weight = 0.0;
	for (int i = 0; i < HYMN_GLIMMER_MAX_ATTRACTORS; i++) {
		if (i >= attractor_count) {
			break;
		}
		vec4 o = orbit(pos, attractor_pos_radius[i], attractor_params[i], USERDATA2.z);
		pull += o.xyz * o.w;
		weight = max(weight, o.w);
	}
	if (follow_global_focus && hymn_glimmer_focus.w > 0.0) {
		vec4 params = vec4(focus_strength, 1.0, focus_half_height_m, hymn_glimmer_focus.w * attractor_influence_scale);
		vec4 o = orbit(pos, hymn_glimmer_focus, params, USERDATA2.z);
		pull += o.xyz * o.w;
		weight = max(weight, o.w);
	}
	target = mix(target, pull + target * attractor_keep_drift, weight);

	// Bound glimmer never moves.
	target *= 1.0 - still;

	float depth = max(water_height_m - pos.y, 0.0);
	float response = response_rate + underwater_drag * step(HYMN_EPSILON, depth);
	if (depth > 0.0) {
		target *= 1.0 / (1.0 + underwater_drag);
	}
	VELOCITY = mix(VELOCITY, world_to_field_basis * target, 1.0 - exp(-DELTA * response));
	CUSTOM = vec4(VELOCITY, 0.0);

	// Colour: hue lerp in Oklab (held -> released), whitening towards lift_hi as a released mote
	// climbs out of its life into the sky; bound teal overrides both.
	vec3 col = oklab_mix(col_held, col_released, blend);
	col = oklab_mix(col, col_released_hi, blend * released_hi_shift * smoothstep(0.35, 1.0, life_t));
	col = mix(col, col_machine, still);
	// The zone's colour-script energy (hymn_glimmer.a) replaces the per-mode defaults when followed.
	float energy = follow_scene_intensity ? hymn_glimmer.a : mix(mix(energy_held, energy_released, blend), energy_machine, still);
	energy *= intensity * mix(brightness_min, 1.0, pow(USERDATA3.x, brightness_power));
	float breath = 1.0 + breath_depth * (1.0 - still) * sin(HYMN_TAU * breath_rate_hz * age + USERDATA2.y);
	float envelope = persistent ? smoothstep(0.0, persist_fade_in_s, age)
								: smoothstep(0.0, fade_in_fraction, life_t) * (1.0 - smoothstep(1.0 - fade_out_fraction, 1.0, life_t));
	float absorb = exp(-underwater_absorb_per_m * depth);
	COLOR = vec4(col * energy * breath, envelope * absorb);

	float core = USERDATA2.w;
	TRANSFORM[0].xyz = vec3(core, 0.0, 0.0);
	TRANSFORM[1].xyz = vec3(0.0, core, 0.0);
	TRANSFORM[2].xyz = vec3(0.0, 0.0, core);
}

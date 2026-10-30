shader_type spatial;
// Ambient wildlife (M3-CRE-611, docs/kb/art/wildlife.md). One surface for the gulls, crabs, fish and insects, drawn through
// MultiMesh. The meshes carry the creature kit's vertex data (assets_src/wildlife/common/wildlife_kit.py):
//   COLOR.rgb  albedo (sRGB palette colour)     COLOR.a  wetness (0 dry .. 1 wet)
//   UV         a rest-pose detail coordinate (metres)
//   UV2.x      cavity (0 open .. 1 deep)        UV2.y    the motion mask (below)
// Wildlife never emits, except the firefly's lantern (mode 6, glow_energy > 0): an animal's light, never glimmer.
// The motion comes from the CPU through INSTANCE_CUSTOM, so it is deterministic (no TIME):
//   r phase (radians, wrapped)  g amplitude (0 .. 1)  b mode  a mode parameter
// Modes: 0 still; 1 flap (UV2.y = wing span 0 .. 1; a = the wings' dihedral, radians); 2 head turn (UV2.y = 1 on
// the head; a = yaw, radians; g = a nod); 3 legs (|UV2.y| = hip 0 .. tip 1, its sign the gait group); 4 swim (no
// mask: the body bends by its distance behind the snout); 5 wing flutter (M3-CRE-616: |UV2.y| = wing span root 0 ..
// tip 1, its sign the side; the wings beat about the body's long axis; a = the wings' rest angle, radians); 6 the
// firefly (M4-A2P-056): mode 5's flutter at a rest angle of 0, a = the lantern's blink (0 dark .. 1 lit).
render_mode blend_mix, depth_draw_opaque, cull_disabled, diffuse_burley, specular_schlick_ggx;

uniform float roughness_dry : hint_range(0.0, 1.0) = 0.8;
uniform float roughness_wet : hint_range(0.0, 1.0) = 0.25;
uniform float metallic : hint_range(0.0, 1.0) = 0.0;
uniform float specular : hint_range(0.0, 1.0) = 0.5;
uniform float wet_darken : hint_range(0.0, 1.0) = 0.7;
uniform float clearcoat_wet : hint_range(0.0, 1.0) = 0.3;
uniform float detail_scale = 40.0;
uniform float detail_albedo : hint_range(0.0, 1.0) = 0.06;
uniform float cavity_albedo : hint_range(0.0, 1.0) = 0.4;
uniform float cavity_ao : hint_range(0.0, 1.0) = 0.6;
// A thin back-lit sheen on an edge (a fish's silver flank): 0 = none.
uniform float rim_sheen : hint_range(0.0, 1.0) = 0.0;
// Flap (mode 1): the shoulder, the stroke (radians at amplitude 1), how far the stroke lags toward the tip
// (radians over the span) and the body's bob against it (metres at amplitude 1).
uniform vec3 wing_pivot = vec3(0.045, 0.018, 0.0);
uniform float flap_angle = 0.75;
uniform float flap_lag = 0.9;
uniform float flap_bob = 0.02;
// Head turn (mode 2): the neck pivot and the nod (radians at amplitude 1).
uniform vec3 head_pivot = vec3(0.0, 0.17, 0.1);
uniform float nod_angle = 0.35;
// Legs (mode 3): stride and lift at the tip (metres at amplitude 1).
uniform float leg_stride = 0.012;
uniform float leg_lift = 0.008;
// Swim (mode 4): the snout's z, the body length, the sweep at the tail (metres at amplitude 1) and the wave
// number of the body wave (radians per metre).
uniform float swim_head_z = 0.075;
uniform float swim_length = 0.14;
uniform float swim_sweep = 0.018;
uniform float swim_wave = 32.0;
// Flutter (mode 5): the wing root (x = its distance from the body's axis), the beat (radians at amplitude 1), the z
// behind which the hind pair lies and the hind pair's lag (radians), and the body's bob (metres at amplitude 1).
uniform vec3 flutter_pivot = vec3(0.0012, 0.0015, 0.0);
uniform float flutter_angle = 0.5;
uniform float flutter_split_z = -1.0;
uniform float flutter_hind_lag = 0.0;
uniform float flutter_bob = 0.001;
// Glow (mode 6): the lantern (the mesh behind glow_tail_z, model space) lit glow_color at glow_energy x the blink.
uniform vec4 glow_color : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform float glow_energy = 0.0;
uniform float glow_tail_z = 0.0;
// The lit lantern swells about glow_centre (model space), so a 1 cm insect's light still reads as a point at any
// distance (a bloom stand-in that needs no post effect): at full blink its radius grows from glow_radius to about
// glow_angle (radians) of the view at the lantern's distance, so near it stays small and far it holds a few pixels.
uniform vec3 glow_centre = vec3(0.0);
uniform float glow_radius = 0.0017;
uniform float glow_angle = 0.0;

varying float glow;

vec2 rot2(vec2 p, float a) {
	float c = cos(a);
	float s = sin(a);
	return vec2(p.x * c - p.y * s, p.x * s + p.y * c);
}

void vertex() {
	float phase = INSTANCE_CUSTOM.r;
	float amp = INSTANCE_CUSTOM.g;
	int mode = int(INSTANCE_CUSTOM.b + 0.5);
	float aux = INSTANCE_CUSTOM.a;
	float m = UV2.y;
	glow = 0.0;
	if (mode == 6) {
		glow = aux * smoothstep(glow_tail_z + 0.0006, glow_tail_z - 0.0006, VERTEX.z);
		float dist = length((MODELVIEW_MATRIX * vec4(glow_centre, 1.0)).xyz);
		float swell = max(dist * glow_angle / glow_radius - 1.0, 0.0);
		VERTEX = glow_centre + (VERTEX - glow_centre) * (1.0 + swell * glow);
		mode = 5;
		aux = 0.0;
	}
	if (mode == 1) {
		if (m > 0.0) {
			float side = VERTEX.x < 0.0 ? -1.0 : 1.0;
			float a = amp * flap_angle * sin(phase - m * flap_lag) + aux * (0.4 + 0.6 * m);
			vec2 p = rot2(vec2(abs(VERTEX.x) - wing_pivot.x, VERTEX.y - wing_pivot.y), a);
			VERTEX.x = side * (p.x + wing_pivot.x);
			VERTEX.y = p.y + wing_pivot.y;
			vec2 n = rot2(vec2(NORMAL.x * side, NORMAL.y), a);
			NORMAL.x = n.x * side;
			NORMAL.y = n.y;
		}
		VERTEX.y -= amp * flap_bob * sin(phase);
	} else if (mode == 2) {
		if (m > 0.0) {
			vec3 p = VERTEX - head_pivot;
			p.yz = rot2(p.yz, -amp * nod_angle * m * max(sin(phase), 0.0));
			p.xz = rot2(p.xz, -aux * m);
			VERTEX = head_pivot + p;
			NORMAL.yz = rot2(NORMAL.yz, -amp * nod_angle * m * max(sin(phase), 0.0));
			NORMAL.xz = rot2(NORMAL.xz, -aux * m);
		}
	} else if (mode == 3) {
		float w = abs(m);
		if (w > 0.0) {
			float g = phase + (m < 0.0 ? 3.14159265 : 0.0);
			VERTEX.x += amp * leg_stride * w * sin(g) * (VERTEX.x < 0.0 ? -1.0 : 1.0);
			VERTEX.y += amp * leg_lift * w * max(cos(g), 0.0);
		}
	} else if (mode == 4) {
		float d = swim_head_z - VERTEX.z;
		float t = clamp(d / swim_length, 0.0, 1.0);
		float k = 0.12 + t * t;
		VERTEX.x += amp * swim_sweep * k * sin(phase - d * swim_wave);
		NORMAL.x -= amp * swim_sweep * k * swim_wave * cos(phase - d * swim_wave) * NORMAL.z;
		NORMAL = normalize(NORMAL);
	} else if (mode == 5) {
		float w = abs(m);
		if (w > 0.0) {
			float side = m < 0.0 ? -1.0 : 1.0;
			float lag = VERTEX.z < flutter_split_z ? flutter_hind_lag : 0.0;
			// the beat flexes a little toward the tip
			float a = (amp * flutter_angle * sin(phase - lag) + aux) * (0.85 + 0.15 * w);
			vec2 p = rot2(vec2(side * VERTEX.x - flutter_pivot.x, VERTEX.y - flutter_pivot.y), a);
			VERTEX.x = side * (p.x + flutter_pivot.x);
			VERTEX.y = p.y + flutter_pivot.y;
			vec2 n = rot2(vec2(NORMAL.x * side, NORMAL.y), a);
			NORMAL.x = n.x * side;
			NORMAL.y = n.y;
		}
		VERTEX.y -= amp * flutter_bob * sin(phase);
	}
}

float hash2(vec2 p) {
	p = fract(p * vec2(123.34, 456.21));
	p += dot(p, p + 45.32);
	return fract(p.x * p.y);
}

float vnoise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	float a = hash2(i);
	float b = hash2(i + vec2(1.0, 0.0));
	float c = hash2(i + vec2(0.0, 1.0));
	float d = hash2(i + vec2(1.0, 1.0));
	return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

vec3 to_linear(vec3 c) {
	return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(vec3(0.04045), c));
}

void fragment() {
	float n = vnoise(UV * detail_scale);
	float wet = clamp(COLOR.a, 0.0, 1.0);
	float cavity = clamp(UV2.x, 0.0, 1.0);
	vec3 base = to_linear(clamp(COLOR.rgb, 0.0, 1.0));
	base *= 1.0 + detail_albedo * (n - 0.5) * 2.0;
	base *= mix(1.0, 1.0 - cavity_albedo, cavity);
	base *= mix(1.0, wet_darken, wet);
	ALBEDO = base;
	METALLIC = metallic;
	SPECULAR = specular;
	ROUGHNESS = clamp(mix(roughness_dry, roughness_wet, wet) + (n - 0.5) * 0.1, 0.04, 1.0);
	AO = 1.0 - cavity * cavity_ao;
	AO_LIGHT_AFFECT = 0.4;
	CLEARCOAT = wet * clearcoat_wet;
	CLEARCOAT_ROUGHNESS = 0.15;
	if (rim_sheen > 0.0) {
		float f = pow(1.0 - clamp(abs(dot(NORMAL, VIEW)), 0.0, 1.0), 3.0);
		EMISSION = base * f * rim_sheen;
	}
	if (glow_energy > 0.0) {
		EMISSION += glow_color.rgb * glow_energy * glow;
	}
}

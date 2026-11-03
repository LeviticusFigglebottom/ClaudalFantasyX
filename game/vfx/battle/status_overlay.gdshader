// The on-body status look (FAST-TRACK 11-03; docs/kb/tech/battle_status_looks.md): a material_overlay on every
// surface of a fighter while a status with an "overlay" row (status_looks.json) holds. Unshaded, so it reads in a
// dark arena as in noon sun. The pattern gives each status its own motion as well as its colour (colour-blind safe):
//   0 rim        a steady edge glow
//   1 pulse      the whole body breathes in the colour
//   2 bands_up   bands climb the body (a tide rising: Haste quick, Doom slow)
//   3 bands_down bands sink down the body (a veil falling: Darkness, Slow)
//   4 flicker    the colour flickers in patches (Confuse)
//   5 hatch      diagonal hatching (Zombie)
//   6 frost      a still, even glaze with a hard rim, no motion at all (Stop)
shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_never, cull_back, depth_test_default, shadows_disabled, fog_disabled;

uniform vec4 tint : source_color = vec4(1.0);
uniform float strength : hint_range(0.0, 1.0) = 0.5;
uniform int pattern = 0;
uniform float speed = 1.0;
// Band and hatch spacing, in metres of world height.
uniform float band_m = 0.35;
uniform float rim_power = 2.5;

varying vec3 world_pos;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	float rim = pow(1.0 - clamp(dot(normalize(NORMAL), normalize(VIEW)), 0.0, 1.0), rim_power);
	float t = TIME * speed;
	float a = rim;
	if (pattern == 1) {
		a = mix(0.35, 1.0, 0.5 + 0.5 * sin(t * 6.2832)) * (0.45 + 0.55 * rim);
	} else if (pattern == 2) {
		float b = fract(world_pos.y / band_m - t);
		a = max(rim * 0.6, smoothstep(0.55, 0.85, b) * (1.0 - smoothstep(0.85, 1.0, b)) * 1.4);
	} else if (pattern == 3) {
		float b = fract(world_pos.y / band_m + t);
		a = max(rim * 0.6, smoothstep(0.0, 0.25, b) * (1.0 - smoothstep(0.25, 0.6, b)) * 1.2);
	} else if (pattern == 4) {
		vec2 cell = floor(world_pos.xy / (band_m * 0.5) + vec2(floor(t * 4.0)));
		a = max(rim, step(0.62, hash(cell)) * 0.9);
	} else if (pattern == 5) {
		float h = fract((world_pos.y + world_pos.x + world_pos.z) / (band_m * 0.5) - t * 0.25);
		a = max(rim * 0.7, step(0.7, h) * 0.85);
	} else if (pattern == 6) {
		a = 0.55 + 0.45 * smoothstep(0.3, 0.6, rim);
	}
	ALBEDO = tint.rgb;
	ALPHA = clamp(a * strength, 0.0, 1.0);
}

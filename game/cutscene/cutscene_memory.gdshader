shader_type canvas_item;
// M5-A3P-1600: CutsceneMemory's layer (game/cutscene/cutscene_memory.gd). The frame under it loses its colour, washes
// toward the look's colour, and goes soft and pale toward the edges. Every value is set from sequencer.json's memory
// looks; `amount` eases the whole look in and out. The luma weights are Rec. 709's.

uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;
uniform float amount = 0.0;
uniform float desaturate = 0.0;
uniform float wash = 0.0;
uniform vec4 wash_color : source_color = vec4(1.0);
// Distance from the centre in screen heights (0 at the centre, 1 at the top and bottom edges' middle).
uniform float edge_inner = 1.0;
uniform float edge_outer = 2.0;
uniform float edge_wash = 0.0;
uniform float edge_blur_lod = 0.0;

void fragment() {
	vec2 from_centre = SCREEN_UV - vec2(0.5);
	from_centre.x *= SCREEN_PIXEL_SIZE.y / SCREEN_PIXEL_SIZE.x;
	float edge = smoothstep(edge_inner, edge_outer, length(from_centre) * 2.0) * amount;
	vec3 sharp = textureLod(screen_tex, SCREEN_UV, 0.0).rgb;
	vec3 soft = textureLod(screen_tex, SCREEN_UV, edge_blur_lod).rgb;
	vec3 col = mix(sharp, soft, edge);
	float luma = dot(col, vec3(0.2126, 0.7152, 0.0722));
	col = mix(col, vec3(luma), desaturate * amount);
	col = mix(col, wash_color.rgb, clamp(wash * amount + edge_wash * edge, 0.0, 1.0));
	COLOR = vec4(col, 1.0);
}

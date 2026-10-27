shader_type canvas_item;
// A flat silhouette of whatever the item draws (M2-UI-26): every drawn pixel takes `tint`, keeping
// its coverage, so a never-Read foe's live portrait in the bestiary shows its shape and nothing more.

uniform vec4 tint : source_color = vec4(0.024, 0.063, 0.118, 0.9);

void fragment() {
	COLOR = vec4(tint.rgb, texture(TEXTURE, UV).a * tint.a);
}

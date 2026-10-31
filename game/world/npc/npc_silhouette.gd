class_name NpcSilhouette
extends RefCounted
## A villager body drawn as one glowing silhouette (M3-HER-1142; docs/kb/tech/field_npc.md "Silhouette"): every
## surface of the actor wears npc_silhouette.gdshader in one colour, over its own maps, and casts no shadow. The
## Corrow storm figure (act1_ch08 W22) is an Oruvel diver's crowd body worn this way: a man's shape, no face.

const SHADER := preload("res://game/world/npc/npc_silhouette.gdshader")
const PARAM_GLOW := &"glow"
## Drawn after the other transparent surfaces at priority 0 (the storm sea, a blend_mix surface that writes depth):
## seen from high on the wall the sea sorted after the figure and painted over it. It still depth-tests against the
## sea, so what stands under the waves stays under them.
const RENDER_PRIORITY := 1

## The maps a silhouette surface copies from the material it wore:
## [its parameter, the source parameters tried in order].
const MAPS := [
	[&"tex_albedo", [&"tex_albedo", &"tex_hair"]],
	[&"tex_normal", [&"tex_normal"]],
	[&"tex_orm", [&"tex_orm"]],
]


## Puts the silhouette in `glow` on every mesh under `actor` (each surface its own material, carrying the maps the
## surface wore, so the shape keeps its folds and seams under the glow); returns how many surfaces it changed. The
## materials belong to the meshes and their FieldNpc (no shared cache), so they free with the actor (the PC's pass 3:
## a cached material outlived the figure and freeing it logged "material is null").
static func apply(actor: Node, glow: Color) -> int:
	if actor == null:
		return 0
	var changed := 0
	for node: Node in actor.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		for i in mi.mesh.get_surface_count():
			mi.set_surface_override_material(i, material_for(glow, mi.get_active_material(i)))
			changed += 1
	return changed


## A silhouette material in `glow`, with the maps `worn` carries (none: plain glow).
static func material_for(glow: Color, worn: Material = null) -> ShaderMaterial:
	var mat := ShaderMaterial.new()
	mat.shader = SHADER
	mat.render_priority = RENDER_PRIORITY
	mat.set_shader_parameter(PARAM_GLOW, glow)
	var src := worn as ShaderMaterial
	if src != null:
		for m: Array in MAPS:
			for from: StringName in m[1]:
				var tex: Variant = src.get_shader_parameter(from)
				if tex is Texture2D:
					mat.set_shader_parameter(m[0], tex)
					break
	return mat


## Every surface override material under `actor` (its tints and its silhouette), for its FieldNpc to hold until the
## meshes are gone (PC row 85).
static func overrides_of(actor: Node) -> Array[Material]:
	var out: Array[Material] = []
	if actor == null:
		return out
	for node: Node in actor.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		for i in mi.mesh.get_surface_count():
			var m := mi.get_surface_override_material(i)
			if m != null:
				out.append(m)
	return out

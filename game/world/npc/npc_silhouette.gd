class_name NpcSilhouette
extends RefCounted
## A villager body drawn as one glowing silhouette (M3-HER-1142; docs/kb/tech/field_npc.md "Silhouette"): every
## surface of the actor wears npc_silhouette.gdshader in one colour and casts no shadow. The Corrow storm figure
## (act1_ch08 W22) is an Oruvel diver's crowd body worn this way: a man's shape, no face. Materials are shared per
## colour.

const SHADER := preload("res://game/world/npc/npc_silhouette.gdshader")
const PARAM_GLOW := &"glow"
## Drawn after the other transparent surfaces at priority 0 (the storm sea, a blend_mix surface that writes depth):
## seen from high on the wall the sea sorted after the figure and painted over it. It still depth-tests against the
## sea, so what stands under the waves stays under them.
const RENDER_PRIORITY := 1

static var _cache: Dictionary = {}


## Puts the silhouette in `glow` on every mesh under `actor`; returns how many meshes it changed.
static func apply(actor: Node, glow: Color) -> int:
	if actor == null:
		return 0
	var mat := material_for(glow)
	var changed := 0
	for node: Node in actor.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		mi.material_override = mat
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		changed += 1
	return changed


## The shared silhouette material for one colour.
static func material_for(glow: Color) -> ShaderMaterial:
	var key := glow.to_html(false)
	if not _cache.has(key):
		var mat := ShaderMaterial.new()
		mat.shader = SHADER
		mat.render_priority = RENDER_PRIORITY
		mat.set_shader_parameter(PARAM_GLOW, glow)
		_cache[key] = mat
	return _cache[key] as ShaderMaterial

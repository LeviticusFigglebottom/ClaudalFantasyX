class_name CharacterShaderTiers
extends RefCounted
## Maps a graphics preset to the character shader tier and swaps hero materials to the matching
## compile-time variant (M1-RND-04). Shaders cannot read the preset at runtime, so each tier is a
## separate shader (game/shaders/README.md, "Quality tiers"); every variant of a family declares
## the same uniforms, so swapping `ShaderMaterial.shader` keeps all authored parameters.
##
## Usage, after GraphicsSettings applies a preset (and when a character is spawned):
##   CharacterShaderTiers.apply_to_tree(character_root, CharacterShaderTiers.tier_for_preset(gs.preset_id))
##
## Data: game/shaders/character/character_shader_tiers.json. Docs: docs/kb/tech/character_shading.md.

const DATA_PATH := "res://game/shaders/character/character_shader_tiers.json"
const KEY_PRESET_TIERS := "preset_tiers"
const KEY_DEFAULT_TIER := "default_tier"
const KEY_FAMILIES := "families"
const KEY_SINGLE_TIER := "single_tier"

static var _data: Dictionary = {}


## The parsed tier table (cached after the first call).
static func data() -> Dictionary:
	if _data.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if typeof(parsed) != TYPE_DICTIONARY:
			push_error("CharacterShaderTiers: cannot read %s" % DATA_PATH)
			return {}
		_data = parsed as Dictionary
	return _data


static func families() -> PackedStringArray:
	return PackedStringArray((data().get(KEY_FAMILIES, {}) as Dictionary).keys())


static func tiers() -> PackedStringArray:
	var out := PackedStringArray()
	for fam: String in families():
		for tier: String in (data()[KEY_FAMILIES][fam] as Dictionary).keys():
			if not out.has(tier):
				out.append(tier)
	return out


## Character tier for a GraphicsSettings preset id; unknown ids get the default tier.
static func tier_for_preset(preset_id: String) -> String:
	var table := data().get(KEY_PRESET_TIERS, {}) as Dictionary
	return str(table.get(preset_id, data().get(KEY_DEFAULT_TIER, "")))


## Shader path of `family` at `tier` ("" when either is unknown).
static func shader_path(family: String, tier: String) -> String:
	var fam := (data().get(KEY_FAMILIES, {}) as Dictionary).get(family, {}) as Dictionary
	return str(fam.get(tier, ""))


## Family whose variants include `shader` ("" for single-tier or foreign shaders).
static func family_of(shader: Shader) -> String:
	if shader == null:
		return ""
	var fams := data().get(KEY_FAMILIES, {}) as Dictionary
	for fam: String in fams:
		if (fams[fam] as Dictionary).values().has(shader.resource_path):
			return fam
	return ""


## Swaps one material to `tier`. Returns true when the shader changed.
static func apply_tier(material: Material, tier: String) -> bool:
	var sm := material as ShaderMaterial
	if sm == null:
		return false
	var fam := family_of(sm.shader)
	if fam.is_empty():
		return false
	var path := shader_path(fam, tier)
	if path.is_empty() or path == sm.shader.resource_path:
		return false
	sm.shader = load(path) as Shader
	return true


## Swaps every character material under `root` (material overrides and surface overrides) to
## `tier`. Each material is visited once. Returns the number of materials changed.
static func apply_to_tree(root: Node, tier: String) -> int:
	var seen := {}
	var changed := 0
	var stack: Array[Node] = [root]
	while not stack.is_empty():
		var node: Node = stack.pop_back()
		stack.append_array(node.get_children())
		for mat in _materials_of(node):
			if seen.has(mat):
				continue
			seen[mat] = true
			if apply_tier(mat, tier):
				changed += 1
	return changed


static func _materials_of(node: Node) -> Array[Material]:
	var out: Array[Material] = []
	var gi := node as GeometryInstance3D
	if gi == null:
		return out
	if gi.material_override != null:
		out.append(gi.material_override)
	var mi := node as MeshInstance3D
	if mi != null and mi.mesh != null:
		for i in mi.mesh.get_surface_count():
			var m := mi.get_surface_override_material(i)
			if m == null:
				m = mi.mesh.surface_get_material(i)
			if m != null:
				out.append(m)
	return out

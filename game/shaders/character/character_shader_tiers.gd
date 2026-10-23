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
## Meta on a material copy apply_to_tree made: [root instance id, the copy's own instance id].
const OWNER_META := &"hymn_tier_owner"

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


## Shader path `material` should switch to for `tier`, or "" when it is not a tiered character
## material, the tier is unknown, or it is already at that tier.
static func target_shader_path(material: Material, tier: String) -> String:
	var sm := material as ShaderMaterial
	if sm == null:
		return ""
	var fam := family_of(sm.shader)
	if fam.is_empty():
		return ""
	var path := shader_path(fam, tier)
	if path.is_empty() or path == sm.shader.resource_path:
		return ""
	return path


## Swaps one material to `tier` **in place**. Returns true when the shader changed. The caller must
## own `material`: every instance sharing it changes too. Trees go through apply_to_tree.
static func apply_tier(material: Material, tier: String) -> bool:
	var path := target_shader_path(material, tier)
	if path.is_empty():
		return false
	(material as ShaderMaterial).shader = load(path) as Shader
	return true


## Swaps every character material under `root` (material overrides, surface overrides and the
## mesh's own surface materials) to `tier`, copy-on-swap (M1-RND-19): a material that needs a new
## shader and is not a copy this function made for this same `root` is duplicated first, and the
## copy goes into the slot (a mesh surface material lands in the surface override slot). Shared
## `.tres` resources, import-time overrides and meshes are never mutated, so instances that share
## a material can sit at different tiers. Slots under `root` that shared one source share one copy,
## and calling again on the same root swaps its own copies in place instead of copying again.
## Each source material is visited once. Returns the number of source materials changed.
static func apply_to_tree(root: Node, tier: String) -> int:
	var done := {}
	var changed := 0
	var root_id := root.get_instance_id()
	var stack: Array[Node] = [root]
	while not stack.is_empty():
		var node: Node = stack.pop_back()
		stack.append_array(node.get_children())
		var gi := node as GeometryInstance3D
		if gi == null:
			continue
		var over := gi.material_override
		if over != null:
			changed += _visit(over, tier, root_id, done)
			if done[over] != over:
				gi.material_override = done[over] as Material
		var mi := node as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		for i in mi.mesh.get_surface_count():
			var src := mi.get_surface_override_material(i)
			if src == null:
				src = mi.mesh.surface_get_material(i)
			if src == null:
				continue
			changed += _visit(src, tier, root_id, done)
			if done[src] != src:
				mi.set_surface_override_material(i, done[src] as Material)
	return changed


## True when `material` is a copy apply_to_tree made for the tree rooted at `root_id`. The meta
## also names the copy itself, so a duplicate of an owned copy (meta and all) is not owned.
static func owns(material: Material, root_id: int) -> bool:
	var tag: Variant = material.get_meta(OWNER_META, PackedInt64Array())
	return tag is PackedInt64Array and tag == PackedInt64Array([root_id, material.get_instance_id()])


## Records in `done` the material that replaces `source` in its slots; returns 1 when it swapped.
static func _visit(source: Material, tier: String, root_id: int, done: Dictionary) -> int:
	if done.has(source):
		return 0
	done[source] = source
	if target_shader_path(source, tier).is_empty():
		return 0
	var target := source
	if not owns(source, root_id):
		target = source.duplicate() as Material
		target.set_meta(OWNER_META, PackedInt64Array([root_id, target.get_instance_id()]))
	apply_tier(target, tier)
	done[source] = target
	return 1

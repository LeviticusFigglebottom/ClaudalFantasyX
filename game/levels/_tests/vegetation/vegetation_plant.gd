class_name VegetationPlant
extends Node3D
## Dresses an instanced procedural-vegetation .glb (M1-ENV-02): swaps the glTF placeholder
## materials for the vegetation shader materials (matched by material name) and turns the authored
## `<name>-lodN` meshes into visibility-range LODs. Attach it to the root of an instanced .glb.
## Until the M1-ART-02 post-import script exists this does the job at runtime; the same mapping
## can move into `game/core/import/vegetation_post_import.gd` unchanged.

const LOD_SUFFIX := "-lod"

## glTF material name -> material to use (e.g. &"palm_frond" -> palm_frond.tres).
@export var materials: Dictionary[StringName, Material] = {}
## visibility_range_end (m) of LOD0, LOD1, LOD2...; the last LOD ends at the last value.
@export var lod_end_m: PackedFloat32Array = PackedFloat32Array([45.0, 120.0, 400.0])
## Hysteresis around each switch distance (m), so LODs do not flicker at the boundary.
@export var lod_margin_m: float = 2.0
## Show only this LOD (for screenshots and debugging); -1 = distance-based.
@export var force_lod: int = -1
## Cast shadows from LODs above this index only as a cheap fallback (-1 = every LOD casts).
@export var shadow_lod_max: int = -1
## Small foliage (vines, grass tufts): tagged small_foliage, so vegetation_detail Low may drop its
## shadows (M1-ENV-05). Trees and palms keep theirs.
@export var small_foliage: bool = false


func _ready() -> void:
	apply()


func apply() -> void:
	for node: Node in find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		_apply_materials(mi)
		_apply_lod(mi, lod_index(mi.name))
		_tag(mi)


## vegetation_detail groups (graphics_presets.json vegetation_groups): a mesh with an authored
## visibility range scales it; small foliage may lose its shadows on Low.
func _tag(mi: MeshInstance3D) -> void:
	if mi.visible and mi.visibility_range_end > 0.0:
		mi.add_to_group(GraphicsSettings.vegetation_group(GraphicsSettings.VEG_GROUP_LOD))
	if small_foliage:
		mi.add_to_group(GraphicsSettings.vegetation_group(GraphicsSettings.VEG_GROUP_SMALL_SHADOWS))


static func lod_index(node_name: String) -> int:
	var at := node_name.rfind(LOD_SUFFIX)
	if at < 0:
		return 0
	var digits := node_name.substr(at + LOD_SUFFIX.length())
	return int(digits) if digits.is_valid_int() else 0


func _apply_materials(mi: MeshInstance3D) -> void:
	if mi.mesh == null:
		return
	for i in mi.mesh.get_surface_count():
		var src := mi.mesh.surface_get_material(i)
		if src == null:
			continue
		var key := StringName(src.resource_name)
		if materials.has(key):
			mi.set_surface_override_material(i, materials[key])
		else:
			push_warning("VegetationPlant %s: no material for '%s'" % [name, key])


func _apply_lod(mi: MeshInstance3D, lod: int) -> void:
	if force_lod >= 0:
		mi.visible = lod == force_lod
		mi.visibility_range_begin = 0.0
		mi.visibility_range_end = 0.0
		return
	mi.visible = lod < lod_end_m.size()
	if not mi.visible:
		return
	mi.visibility_range_begin = 0.0 if lod == 0 else lod_end_m[lod - 1]
	mi.visibility_range_end = lod_end_m[lod]
	mi.visibility_range_begin_margin = lod_margin_m if lod > 0 else 0.0
	mi.visibility_range_end_margin = lod_margin_m
	mi.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED
	if shadow_lod_max >= 0 and lod > shadow_lod_max:
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF

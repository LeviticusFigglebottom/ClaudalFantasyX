class_name VegetationPlant
extends Node3D
## Dresses an instanced procedural-vegetation .glb (M1-ENV-02): swaps the glTF placeholder
## materials for the vegetation shader materials (matched by material name) and turns the authored
## `<name>-lodN` meshes into visibility-range LODs. Attach it to the root of an instanced .glb.
## Until the M1-ART-02 post-import script exists this does the job at runtime; the same mapping
## can move into `game/core/import/vegetation_post_import.gd` unchanged.

## Shelter modes of the `shelter` export.
enum Shelter { AUTO, OPEN, SHELTERED }

const LOD_SUFFIX := "-lod"
const SHELTER_PARAM := &"inst_translucency_shelter"
## The shelter probe starts at this fraction of the plant's height (its crown: a palm's trunk passes
## under a neighbour's eave while its crown stands in the sun), and runs this far toward the sun (m).
const SHELTER_PROBE_CROWN := 0.8
const SHELTER_PROBE_LENGTH_M := 40.0

## glTF material name -> material to use (e.g. &"palm_frond" -> palm_frond.tres).
@export var materials: Dictionary[StringName, Material] = {}
## visibility_range_end (m) of LOD0, LOD1, LOD2...; the last LOD ends at the last value.
@export var lod_end_m: PackedFloat32Array = PackedFloat32Array([45.0, 120.0, 400.0])
## Hysteresis around each switch distance (m), so LODs do not flicker at the boundary.
@export var lod_margin_m: float = 2.0
## Fade-out width (m) of the last LOD at its final distance (M1-ENV-03), so a palm does not pop off
## against the sky. Only the last cut fades: Godot's visibility-range fade alpha-blends the instance
## (not a dither), which turned trunks into translucent ghosts at the LOD0 -> 1 switch
## (review-sweep-N). LOD switches stay hard, with lod_margin_m hysteresis. 0 = no fade.
@export var lod_fade_m: float = 6.0
## Show only this LOD (for screenshots and debugging); -1 = distance-based.
@export var force_lod: int = -1
## Cast shadows from LODs above this index only as a cheap fallback (-1 = every LOD casts).
@export var shadow_lod_max: int = -1
## Small foliage (vines, grass tufts): tagged small_foliage, so vegetation_detail Low may drop its
## shadows (M1-ENV-05). Trees and palms keep theirs.
@export var small_foliage: bool = false
## Shelter from solid occluders (M1-ENV-03): SHELTERED turns the leaves' through-shadow translucency
## floor off, so a plant under an eave does not glow. AUTO casts one ray from the plant's crown toward
## the sun (the hymn_sun_direction global, via ShaderGlobals) once placed: a hit on `shelter_mask` means
## sheltered. OPEN keeps the floor.
@export var shelter: Shelter = Shelter.AUTO
## Physics layers the shelter probe tests (the world's solids: buildings, cliffs).
@export_flags_3d_physics var shelter_mask: int = 1


func _ready() -> void:
	apply()
	match shelter:
		Shelter.AUTO:
			if is_inside_tree():
				# The physics space is only queryable once the scene's bodies have been placed.
				await get_tree().physics_frame
				set_shelter(1.0 if is_sheltered() else 0.0)
		Shelter.OPEN:
			set_shelter(0.0)
		Shelter.SHELTERED:
			set_shelter(1.0)


## Writes the shelter weight to every mesh of the plant.
func set_shelter(value: float) -> void:
	for node: Node in find_children("*", "MeshInstance3D", true, false):
		(node as MeshInstance3D).set_instance_shader_parameter(SHELTER_PARAM, value)


## True when a solid lies between the crown and the sun (plants carry no collision, so any hit is a
## building, a cliff or a canopy of stone).
func is_sheltered() -> bool:
	if get_world_3d() == null:
		return false
	var from := global_position + Vector3.UP * crown_height() * SHELTER_PROBE_CROWN
	var query := PhysicsRayQueryParameters3D.create(from, from + sun_direction() * SHELTER_PROBE_LENGTH_M, shelter_mask)
	return not get_world_3d().direct_space_state.intersect_ray(query).is_empty()


## Height of the plant's tallest mesh above its origin (world metres), from the meshes' AABBs.
func crown_height() -> float:
	var top := 0.0
	for node: Node in find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh != null:
			var box := mi.global_transform * mi.get_aabb()
			top = maxf(top, box.end.y - global_position.y)
	return top


## Unit vector toward the sun: the hymn_sun_direction global as last written (ShaderGlobals), else up.
func sun_direction() -> Vector3:
	var sun: Variant = ShaderGlobals.get_value(&"hymn_sun_direction")
	if sun is Vector3 and (sun as Vector3).length_squared() > 0.0:
		return (sun as Vector3).normalized()
	return Vector3.UP


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
	var last := lod == lod_end_m.size() - 1
	var fade_out := last and lod_fade_m > 0.0
	mi.visibility_range_begin = 0.0 if lod == 0 else lod_end_m[lod - 1]
	mi.visibility_range_end = lod_end_m[lod]
	# Fading uses the margins as fade spans (no hysteresis), so the faded LOD's switch-in stays hard.
	mi.visibility_range_begin_margin = 0.0 if lod == 0 or fade_out else lod_margin_m
	mi.visibility_range_end_margin = lod_fade_m if fade_out else lod_margin_m
	mi.visibility_range_fade_mode = (
		GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF if fade_out else GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED
	)
	if shadow_lod_max >= 0 and lod > shadow_lod_max:
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF

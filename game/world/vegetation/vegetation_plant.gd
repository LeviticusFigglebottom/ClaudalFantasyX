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
const SUN_GLOBAL := &"hymn_sun_direction"
## The shelter probe starts at this fraction of the plant's height (its crown: a palm's trunk passes
## under a neighbour's eave while its crown stands in the sun), and runs this far toward the sun (m).
const SHELTER_PROBE_CROWN := 0.8
const SHELTER_PROBE_LENGTH_M := 40.0
## AUTO shelter re-probes when the hymn_sun_direction global turns by more than this (deg), so a sun
## written every frame (a time-of-day sweep) costs a ray per plant only every so often.
const SHELTER_REPROBE_DEG := 0.5

## glTF material name -> material to use (e.g. &"palm_frond" -> palm_frond.tres).
@export var materials: Dictionary[StringName, Material] = {}
## Switch distance (m) from LOD0 to LOD1, LOD1 to LOD2...; the last LOD ends at the last value.
## Each LOD is the visibility-range child of the next one (lod_range), so exactly one draws.
@export var lod_end_m: PackedFloat32Array = PackedFloat32Array([45.0, 120.0, 400.0])
## Hysteresis around each switch distance (m), so LODs do not flicker at the boundary. At the switch
## into a faded last LOD it is the half-width of a crossfade instead (Godot fades over both margins).
@export var lod_margin_m: float = 2.0
## Fade-out half-width (m) of the last LOD at its final distance (M1-ENV-03), so a palm does not pop
## off against the sky: it fades over end +- lod_fade_m. Godot's visibility-range fade alpha-blends the
## instance (not a dither), which turned trunks into translucent ghosts at the LOD0 -> 1 switch
## (review-sweep-N), so the other switches stay hard, with lod_margin_m hysteresis. 0 = no fade.
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
## the sun (the hymn_sun_direction global, via ShaderGlobals) once placed, and again whenever
## ShaderGlobals writes a new sun: a hit on `shelter_mask` means sheltered. OPEN keeps the floor.
@export var shelter: Shelter = Shelter.AUTO
## Physics layers the shelter probe tests (the world's solids: buildings, cliffs).
@export_flags_3d_physics var shelter_mask: int = 1

## The sun the last AUTO probe aimed at (zero before the first).
var _probed_sun := Vector3.ZERO


func _ready() -> void:
	apply()
	match shelter:
		Shelter.AUTO:
			# Re-probe when the sun moves (a time-of-day change or a test restoring the sun, M1-ENV-09).
			add_to_group(ShaderGlobals.LISTENERS_GROUP)
			request_shelter_probe()
		Shelter.OPEN:
			set_shelter(0.0)
		Shelter.SHELTERED:
			set_shelter(1.0)


## AUTO shelter: probe toward the sun on the next physics frame. Several requests in one frame (a sun
## written every frame) coalesce into one probe.
func request_shelter_probe() -> void:
	if not is_inside_tree() or get_tree().physics_frame.is_connected(probe_shelter):
		return
	# The physics space is only queryable once the scene's bodies have been placed. A signal
	# connection (not an await) dies with the plant if it is freed first.
	get_tree().physics_frame.connect(probe_shelter, CONNECT_ONE_SHOT)


## AUTO shelter now: one ray toward the sun sets the shelter weight.
func probe_shelter() -> void:
	if is_inside_tree() and shelter == Shelter.AUTO:
		_probed_sun = sun_direction()
		set_shelter(1.0 if is_sheltered() else 0.0)


## ShaderGlobals listener: a sun that turned more than SHELTER_REPROBE_DEG since the last probe.
func _on_shader_global_changed(global: StringName, _value: Variant) -> void:
	if global != SUN_GLOBAL or shelter != Shelter.AUTO:
		return
	if _probed_sun == Vector3.ZERO or rad_to_deg(_probed_sun.angle_to(sun_direction())) > SHELTER_REPROBE_DEG:
		request_shelter_probe()


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


## Unit vector toward the sun: the hymn_sun_direction global as last written (ShaderGlobals), else its
## project default, else up.
func sun_direction() -> Vector3:
	var sun: Variant = ShaderGlobals.get_value(SUN_GLOBAL)
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
	mi.visibility_parent = NodePath()
	if force_lod >= 0:
		mi.visible = lod == force_lod
		mi.visibility_range_begin = 0.0
		mi.visibility_range_end = 0.0
		return
	mi.visible = lod < lod_end_m.size()
	if not mi.visible:
		return
	LodChain.apply(mi, lod, lod_end_m, lod_margin_m, lod_fade_m, lod_mesh(mi, lod + 1))
	if shadow_lod_max >= 0 and lod > shadow_lod_max:
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF


## The sibling `<base>-lod<lod>` of `mi`'s chain (saltgrass_clumps holds two chains), else null.
static func lod_mesh(mi: MeshInstance3D, lod: int) -> MeshInstance3D:
	return LodChain.sibling(mi, lod, LOD_SUFFIX)


## LOD `lod`'s visibility range (M1-ENV-08/09): LodChain.range_for, which documents the chain.
static func lod_range(lod: int, ends: PackedFloat32Array, margin: float, fade: float, chained: bool) -> Dictionary:
	return LodChain.range_for(lod, ends, margin, fade, chained)

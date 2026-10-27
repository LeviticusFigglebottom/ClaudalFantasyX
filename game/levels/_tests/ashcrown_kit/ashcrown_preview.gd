class_name AshcrownPreview
extends HalunaMood
## The Ashcrown temple kit preview (M3-ENV-09; docs/kb/art/environments/ashcrown.md). HalunaMood does the
## sun placement, the hymn_* globals and the capture determinism (sub-frame `ch05_temple`: 13:00, the sun
## 66 deg / 200 deg through the ash veil); HalunaDresser places the kit from the layout. This rig adds
## what the layout holds beyond HalunaDresser's format, once the dresser has dressed the zone:
## - "borrowed": pieces of another kit by .glb path (the Pemakar kit's ash_plume, open-hand gate and lamp
##   pillars, read-only), each {"glb", "at": [x, y, z], "yaw_deg", "scale", "materials": {slot: .tres}};
## - "lights": OmniLight3Ds {"at", "color", "energy", "range"} (the hall's lamps, the forge trough, the
##   vent's glow), shadowless, never lighting a FogVolume (the Lead's fog-lamp rule).
## The anvil hall's interior ambient is the scene's ReflectionProbe (ashcrown.md §0 GI recommendation);
## `interior` is the `ch05_temple_int` sub-frame's exposure (1.05 against the day's 0.72), which the hall's
## shots set through their capture setup.

const BORROWED := &"Borrowed"
const LIGHTS := &"Lamps"
## ch05_temple_int exposure / ch05_temple exposure (ashcrown.md §0).
const INTERIOR_EXPOSURE_RATIO := 1.05 / 0.72
const META_BASE_EXPOSURE := &"ashcrown_base_exposure"

## The hall's sub-frame (`ch05_temple_int`): the same light, the exposure opened for the interior.
@export var interior: bool = false:
	set(value):
		interior = value
		if is_node_ready():
			apply_exposure()

var _borrowed: Node3D
var _lights: Node3D


func _ready() -> void:
	# apply_exposure writes into the Environment: work on this scene's own copy of the .tres.
	if world_environment != null and world_environment.environment != null:
		world_environment.environment = world_environment.environment.duplicate()
	super._ready()
	apply_exposure()
	if dresser == null:
		return
	if dresser.layout.is_empty():
		dresser.dressed.connect(_on_dressed, CONNECT_ONE_SHOT)
	else:
		_on_dressed()


func _on_dressed() -> void:
	_borrowed = build_borrowed(dresser.layout)
	add_child(_borrowed)
	_lights = build_lights(dresser.layout)
	add_child(_lights)


## The layout's "borrowed" pieces (not added to the tree). A missing .glb is skipped with a warning.
static func build_borrowed(layout: Dictionary) -> Node3D:
	var root := Node3D.new()
	root.name = BORROWED
	for spec: Dictionary in layout.get("borrowed", []):
		var path := String(spec.get("glb", ""))
		if not ResourceLoader.exists(path):
			push_warning("AshcrownPreview: no borrowed piece %s" % path)
			continue
		var node := (load(path) as PackedScene).instantiate() as Node3D
		node.name = path.get_file().get_basename()
		var at: Array = spec.get("at", [0.0, 0.0, 0.0])
		var s := float(spec.get("scale", 1.0))
		var basis := Basis(Vector3.UP, deg_to_rad(float(spec.get("yaw_deg", 0.0)))).scaled(Vector3.ONE * s)
		node.transform = Transform3D(basis, Vector3(float(at[0]), float(at[1]), float(at[2])))
		var overrides: Dictionary = spec.get("materials", {})
		if not overrides.is_empty():
			apply_overrides(node, overrides)
		if spec.has("lod1_from_m"):
			chain_lods(
				node,
				float(spec["lod1_from_m"]),
				float(layout.get("lod_end_m", 4000.0)),
				float(layout.get("lod_margin_m", 2.0))
			)
		root.add_child(node)
	return root


## Sets surface override materials by glTF slot name on every mesh under `node`.
static func apply_overrides(node: Node, overrides: Dictionary) -> void:
	for child: Node in node.find_children("*", "MeshInstance3D", true, false):
		var mi := child as MeshInstance3D
		if mi.mesh == null:
			continue
		for i in mi.mesh.get_surface_count():
			var surf := mi.mesh.surface_get_material(i)
			var slot := String(surf.resource_name) if surf != null else ""
			if overrides.has(slot) and ResourceLoader.exists(String(overrides[slot])):
				mi.set_surface_override_material(i, load(String(overrides[slot])) as Material)


## Re-chains a borrowed piece's `<piece>` / `<piece>-lod1` (LodChain, as HalunaDresser does) with LOD1 from
## `lod1_from_m`: a skyline piece's own import ends LOD0 at 70 m from its middle, far too soon up close.
static func chain_lods(node: Node, lod1_from_m: float, end_m: float, margin: float) -> void:
	var ends := PackedFloat32Array([lod1_from_m, end_m])
	for child: Node in node.find_children("*", "MeshInstance3D", true, false):
		var mi := child as MeshInstance3D
		var lod := 1 if String(mi.name).ends_with("-lod1") else 0
		LodChain.apply(mi, lod, ends, margin, 0.0, LodChain.sibling(mi, lod + 1))


## The layout's "lights" as shadowless OmniLight3Ds that never light a FogVolume (not added to the tree).
static func build_lights(layout: Dictionary) -> Node3D:
	var root := Node3D.new()
	root.name = LIGHTS
	for spec: Dictionary in layout.get("lights", []):
		var light := OmniLight3D.new()
		var at: Array = spec["at"]
		light.position = Vector3(float(at[0]), float(at[1]), float(at[2]))
		light.light_color = Color.html(String(spec.get("color", "#FFFFFF")))
		light.light_energy = float(spec.get("energy", 1.0))
		light.omni_range = float(spec.get("range", 4.0))
		light.shadow_enabled = false
		light.light_volumetric_fog_energy = 0.0
		root.add_child(light)
	return root


## Sets the Environment's exposure for the day or the hall's sub-frame.
func apply_exposure() -> void:
	if world_environment == null or world_environment.environment == null:
		return
	var env := world_environment.environment
	if not env.has_meta(META_BASE_EXPOSURE):
		env.set_meta(META_BASE_EXPOSURE, env.tonemap_exposure)
	var base := float(env.get_meta(META_BASE_EXPOSURE))
	env.tonemap_exposure = base * (INTERIOR_EXPOSURE_RATIO if interior else 1.0)


func borrowed_root() -> Node3D:
	return _borrowed


func lights_root() -> Node3D:
	return _lights

class_name BrightwaterFerryPreview
extends HalunaMood
## The Brightwater ferry kit preview (M3-ENV-08; docs/kb/art/environments/brightwater_ferry.md). HalunaMood does
## the moon placement, the night mood (the `night_sea` look, sea-glow, the night Environment), the hymn_* globals
## and the capture determinism; this rig only lights the deck lanterns:
## - the colour script's `ch04` frame is HalunaMood's night mood with this scene's values (the Moon #9DB4D9 at
##   0.28, setting at 18 deg in the WSW; sea-glow 0.12; the ch04 Environment with `lut_ch04_wake`);
## - one OmniLight3D per layout "lamps" entry [x, y, z, energy, range, shadow] in "lamp_color" (oil_lamp
##   #FFB16E, the ch04 lamp key 1.2), added once the dresser has dressed the scene. Every lamp sets
##   `light_volumetric_fog_energy` to 0 (the Lead's fog-lamp rule, tools/tests/test_fog_lamps.py): the GPU
##   tiers' volumetric fog must not be lit by the lanterns.

const LAMPS := &"Lamps"
const LAMP_ENERGY_META := &"base_energy"


func _ready() -> void:
	# The night mood swaps Environments: work on this scene's own copy of the .tres.
	if night_environment != null:
		night_environment = night_environment.duplicate()
	super._ready()
	if dresser != null:
		if dresser.layout.is_empty():
			dresser.dressed.connect(_on_dressed, CONNECT_ONE_SHOT)
		else:
			_on_dressed()


func _on_dressed() -> void:
	if get_node_or_null(NodePath(String(LAMPS))) == null:
		add_child(build_lamps(dresser.layout))


## The deck lanterns' lights for a layout (not added to the tree).
static func build_lamps(layout: Dictionary) -> Node3D:
	var root := Node3D.new()
	root.name = LAMPS
	var color := Color.html(str(layout.get("lamp_color", "#FFB16E")))
	var attenuation := float(layout.get("lamp_attenuation", 1.0))
	for entry: Array in layout.get("lamps", []):
		var light := OmniLight3D.new()
		light.light_color = color
		light.position = Vector3(float(entry[0]), float(entry[1]), float(entry[2]))
		light.light_energy = float(entry[3])
		light.omni_range = float(entry[4])
		light.omni_attenuation = attenuation
		light.shadow_enabled = bool(entry[5]) if entry.size() > 5 else false
		light.shadow_bias = 0.05
		light.light_volumetric_fog_energy = 0.0
		light.set_meta(LAMP_ENERGY_META, float(entry[3]))
		root.add_child(light)
	return root


## The lanterns' container (null until the dresser has dressed the scene).
func lamps() -> Node3D:
	return get_node_or_null(NodePath(String(LAMPS))) as Node3D

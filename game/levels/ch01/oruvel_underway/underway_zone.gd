class_name Ch01UnderwayZone
extends Ch01Zone
## Ch1's drowned tower under Oruvel, `ch01/oruvel_underway` (M3-C01-02; act1_ch01.md C1-02 to C1-07):
## a Ch01Zone with Rhen's oil lantern and its shutter (C1-04, the chapter's own mechanic). The numbers
## are game/data/flow/ch01_field.json "lantern"; what the open light finds is the layout's "lantern":
## {"reveals": [trigger ids], "curtains": [block ids]}.
##   narrow (the default) is quiet: a small pool of light, the base encounter rate.
##   open (the shutter action held) widens the light, finds what the reveals and curtains hide (the
##        coral curtain falls away and the old tin's trigger can be used, for good), and multiplies the
##        encounter rate (encounter_rate_mult(), for the shared field encounters, M2-FP-25, to read).
## No fuel. Weighted divers walk the floors (the ordinary field controller); tether points and the
## bell-rooms' rests are story beats in the chapter file. The underwater look in the field is a
## stand-in (the layout's dark sun, environment and fog) until the kit brings an UnderwaterRig.

## The lamp on Rhen's shoulder.
var lantern: OmniLight3D
## True while the shutter is open.
var shutter_open := false
## True once the open light has found what the layout's lantern block hides.
var revealed := false

var _lamp: Dictionary = {}


func build() -> void:
	if hint != null:
		return
	super()
	_lamp = field.get("lantern", {})
	FieldInput.add_actions(_lamp.get("actions", {}) as Dictionary, float(_lamp.get("deadzone", 0.0)))
	lantern = OmniLight3D.new()
	lantern.name = "Lantern"
	lantern.light_color = Color.html(str(_lamp.get("color", "#ffffff")))
	lantern.position.y = float(_lamp.get("height_m", 0.0))
	player.add_child(lantern)
	for id: Variant in _lantern_layout().get("reveals", []):
		var it := _trigger(str(id))
		if it != null:
			it.remove_from_group(Interactable.GROUP)
	set_shutter(false)


func _ready() -> void:
	# Interactable._ready adds every trigger to the field group; hidden ones leave it again.
	if not revealed:
		for id: Variant in _lantern_layout().get("reveals", []):
			var it := _trigger(str(id))
			if it != null and it.is_in_group(Interactable.GROUP):
				it.remove_from_group(Interactable.GROUP)


func _process(_delta: float) -> void:
	var action := StringName(str(_lamp.get("action", "")))
	if action == &"" or not InputMap.has_action(action):
		return
	var held := player.accepts_input and Input.is_action_pressed(action)
	if held != shutter_open:
		set_shutter(held)


## Opens or narrows the shutter. Opening the first time reveals the layout's lantern block for good.
func set_shutter(open: bool) -> void:
	shutter_open = open
	var row: Dictionary = _lamp.get("open" if open else "narrow", {})
	lantern.omni_range = float(row.get("range_m", 0.0))
	lantern.light_energy = float(row.get("energy", 0.0))
	if open and not revealed:
		_reveal()


## The encounter-rate multiplier of the current shutter (1.0 when the data has none).
func encounter_rate_mult() -> float:
	var row: Dictionary = _lamp.get("open" if shutter_open else "narrow", {})
	return float(row.get("encounter_rate_mult", 1.0))


func _reveal() -> void:
	revealed = true
	var lay := _lantern_layout()
	for id: Variant in lay.get("curtains", []):
		hide_block(str(id))
	for id: Variant in lay.get("reveals", []):
		var it := _trigger(str(id))
		if it != null and not it.is_in_group(Interactable.GROUP):
			it.add_to_group(Interactable.GROUP)


func _lantern_layout() -> Dictionary:
	return layout.get("lantern", {})


func _trigger(id: String) -> Interactable:
	return get_node_or_null(NodePath("%s/%s" % [TRIGGERS, id])) as Interactable

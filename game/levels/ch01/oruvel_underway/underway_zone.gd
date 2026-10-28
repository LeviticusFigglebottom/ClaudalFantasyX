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
## bell-rooms' rests are story beats in the chapter file.
## M3-C01-101: env-art's drowned-tower kit dresses the rooms (Dressing, a ZoneKitDressing) under a sea at the
## Tide's height, with an UnderwaterRig (`Underwater`, whose halo follows this zone's lantern). The rooms sit side
## by side at y 0, so the layout's "underwater" block lights the room Rhen is in as it would be lit at its real
## depth in the tower (oruvel_underway.md §0; the kit preview's arithmetic):
##   {"fill": the ambient colour before the water takes its share, "glimmer": hymn_glimmer for the dive (the
##    low lights' motes), "lighting": {name: [ambient energy, the rig's in-scatter scale]},
##    "rooms": [{"id", "rect": [x0, z0, x1, z1], "lighting", "depth_m"}] (the first that holds Rhen wins)}.
##   The sun and the ambient are tinted by the rig's transmittance over depth_m.
## "swaps": [{"flag", "from", "to"}]: block `from` shows until the flag is set, then `to` (the cut gauge wheel).
## "environment_res": the kit's ch01 Environment for the zone (env-art's dressing keeps the layout's murk; M3-ENV-742).

const KEY_UNDERWATER := "underwater"
const KEY_SWAPS := "swaps"
const KEY_ENVIRONMENT_RES := "environment_res"
const RIG := ^"Underwater"
const GLOBAL_GLIMMER := &"hymn_glimmer"
const OPTICS := "optics"
const LIGHT_REFERENCE := "light_reference"
const TRANSMIT_DISTANCE := "transmit_distance_m"
const MIN_TRANSMIT := 1e-3
const MIN_SCALE := 0.01

## The lamp on Rhen's shoulder.
var lantern: OmniLight3D
## True while the shutter is open.
var shutter_open := false
## True once the open light has found what the layout's lantern block hides.
var revealed := false
## The id of the "underwater" room Rhen is in (&"" before the first).
var room: StringName = &""

var _rig: UnderwaterRig
var _key_color := Color.WHITE
var _base_light_reference := 0.0

var _lamp: Dictionary = {}


func build() -> void:
	if hint != null:
		return
	super()
	var env_res := str(layout.get(KEY_ENVIRONMENT_RES, ""))
	if env_res != "":  # the rooms' lighting (apply_lighting) then tints this frame, not the greybox's colours
		(get_node(^"WorldEnvironment") as WorldEnvironment).environment = (load(env_res) as Environment).duplicate()
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
	super()
	# Interactable._ready adds every trigger to the field group; hidden ones leave it again.
	if not revealed:
		for id: Variant in _lantern_layout().get("reveals", []):
			var it := _trigger(str(id))
			if it != null and it.is_in_group(Interactable.GROUP):
				it.remove_from_group(Interactable.GROUP)
	_rig = get_node_or_null(RIG) as UnderwaterRig
	if _rig != null:
		_rig.data = _rig.data.duplicate(true)  # the rooms scale the in-scatter: a private copy of the shared cache
		_rig.lantern = lantern
	_key_color = sun.light_color
	var g: Array = _underwater().get("glimmer", [])
	if g.size() == 4:
		ShaderGlobals.set_value(GLOBAL_GLIMMER, Vector4(float(g[0]), float(g[1]), float(g[2]), float(g[3])))
	apply_swaps()
	EventBus.flag_changed.connect(_on_flag_changed)
	update_room()


func _process(_delta: float) -> void:
	update_room()
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


## Lights the room the player stands in (once per room change).
func update_room() -> void:
	var r := room_at(player.position)
	var id := StringName(str(r.get("id", "")))
	if r.is_empty() or id == room:
		return
	room = id
	apply_lighting(str(r.get("lighting", "")), float(r.get("depth_m", 0.0)))


## The layout's "underwater" room holding `p` ({} outside every room).
func room_at(p: Vector3) -> Dictionary:
	for v: Variant in _underwater().get("rooms", []):
		var r := v as Dictionary
		var rect: Array = r.get("rect", [])
		if rect.size() == 4 and p.x >= float(rect[0]) and p.x <= float(rect[2]):
			if p.z >= float(rect[1]) and p.z <= float(rect[3]):
				return r
	return {}


## The sun and the ambient as they reach `depth_m` of water, and the "lighting" row's ambient energy and in-scatter.
func apply_lighting(lighting: String, depth_m: float) -> void:
	var uw := _underwater()
	var a: Array = (uw.get("lighting", {}) as Dictionary).get(lighting, [1.0, 1.0])
	var t := transmittance(depth_m)
	sun.light_color = tinted(_key_color, t)
	var env := (get_node(^"WorldEnvironment") as WorldEnvironment).environment
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = tinted(Color.html(str(uw.get("fill", "#ffffff"))), t)
	env.ambient_light_energy = float(a[0])
	if _rig == null or _rig.data.is_empty():
		return
	var optics: Dictionary = _rig.data.get(OPTICS, {})
	if _base_light_reference <= 0.0:
		_base_light_reference = float(optics.get(LIGHT_REFERENCE, 1.0))
	optics[LIGHT_REFERENCE] = _base_light_reference / maxf(float(a[1]), MIN_SCALE)


## The rig's per-channel transmittance over `metres` of water (linear RGB), from its data's transmit colour.
func transmittance(metres: float) -> Vector3:
	var data: Dictionary = _rig.data if _rig != null else UnderwaterRig.load_data()
	var c := Color(str((data.get("colors", {}) as Dictionary).get("transmit", "#ffffff"))).srgb_to_linear()
	var dist := maxf(float((data.get(OPTICS, {}) as Dictionary).get(TRANSMIT_DISTANCE, 1.0)), MIN_SCALE)
	var sigma := (
		Vector3(-log(maxf(c.r, MIN_TRANSMIT)), -log(maxf(c.g, MIN_TRANSMIT)), -log(maxf(c.b, MIN_TRANSMIT))) / dist
	)
	return Vector3(exp(-sigma.x * metres), exp(-sigma.y * metres), exp(-sigma.z * metres))


## A colour seen through `t` (linear transmittance), back in sRGB.
static func tinted(color: Color, t: Vector3) -> Color:
	var lin := color.srgb_to_linear()
	return Color(lin.r * t.x, lin.g * t.y, lin.b * t.z, 1.0).linear_to_srgb()


## Shows each swap's `from` block until its flag is set, then its `to` block.
func apply_swaps() -> void:
	for v: Variant in layout.get(KEY_SWAPS, []):
		var row := v as Dictionary
		var done := bool(Game.get_flag(StringName(str(row.get("flag", "")))))
		_set_block(str(row.get("from", "")), not done)
		_set_block(str(row.get("to", "")), done)


func _on_flag_changed(_flag: StringName, _value: Variant) -> void:
	apply_swaps()


func _underwater() -> Dictionary:
	return layout.get(KEY_UNDERWATER, {})

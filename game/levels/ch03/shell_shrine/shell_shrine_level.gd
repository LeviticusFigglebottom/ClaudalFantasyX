class_name ShellShrineLevel
extends Node3D
## The Shell Shrine trial level (M2-FP-16; vertical_slice.md B07; README.md beside this file). A view
## of ShellShrineTrial: it builds the greybox room from game/data/trials/shell_shrine.json (until
## Environment's shrine kit exists), turns a basin when Rhen uses it, lights the channels the water
## runs through, raises the inner pool, sinks the door, empties the side pool and offers the
## net-float charm. Through the open door, the exit trigger hands off to Cutscene B
## (first_playable.json "shell_shrine" next_scene).
##
## Hooks (VFX, audio, HUD): the trial's own signals (`trial.rotated`, `flow_changed`, `pool_filled`,
## `side_pool_drained`, `hint_due`) plus `charm_taken` here. Time passes only through advance(delta),
## which _process calls; tests call it directly.

signal charm_taken

const KEY_ROTATE := "rotate"
const KEY_ITEM := "item"
const KEY_EXIT := "exit"
const SIDE_DIRS: Array[Vector3] = [Vector3.FORWARD, Vector3.RIGHT, Vector3.BACK, Vector3.LEFT]

## The overview (S03) frames the room; these are the inserts (S04 water, S05 the side pool).
@export var insert_pool: CameraShot
@export var insert_side: CameraShot
## Hand off on the exit trigger only when this is the current scene (tests turn it off).
@export var autostart := true

var trial: ShellShrineTrial
var cfg: Dictionary = {}
## Tests record the hand-off here instead of changing scene: (target: String).
var hand_off: Callable = Callable()
var hint: CutsceneSequencer
## basin id -> the Node3D that turns (its lip points at the outlet).
var basin_pivots: Dictionary = {}
## "<from>><to>" -> MeshInstance3D: every channel the water can run along.
var channels: Dictionary = {}
var pool_water: MeshInstance3D
var side_water: MeshInstance3D
var door: StaticBody3D
var charm: Node3D
var handed_off := false

var _g: Dictionary = {}
var _layout: Dictionary = {}
var _lit: StandardMaterial3D
var _dim: StandardMaterial3D
var _insert_left := 0.0
var _water_seen := false
var _door_tween: Tween

@onready var player: FieldController = $Player
@onready var director: FieldCameraDirector = $CameraDirector
@onready var field_camera: Camera3D = $FieldCamera


func _ready() -> void:
	cfg = FirstPlayableConfig.section(FirstPlayableConfig.SECTION_SHELL_SHRINE)
	trial = ShellShrineTrial.new()
	_g = trial.data.get("greybox", {})
	_layout = trial.data.get("layout", {})
	field_camera.make_current()
	_build()
	trial.rotated.connect(_on_rotated)
	trial.flow_changed.connect(_on_flow_changed)
	trial.pool_filled.connect(_on_pool_filled)
	trial.side_pool_drained.connect(_on_side_drained)
	trial.hint_due.connect(_on_hint_due)
	hint = CutsceneSequencer.new()
	hint.name = "Hint"
	hint.hold_player = false
	hint.auto_advance = true
	add_child(hint)
	FieldEvents.connect_interacted(_on_interacted)
	FieldEvents.connect_trigger(_on_trigger)
	_restore()
	_relight(trial.trace())


func _exit_tree() -> void:
	for pair: Array in [[FieldEvents.INTERACTED, _on_interacted], [FieldEvents.TRIGGER_ENTERED, _on_trigger]]:
		if EventBus.is_connected(pair[0], pair[1]):
			EventBus.disconnect(pair[0], pair[1])


func _process(delta: float) -> void:
	advance(delta)


## Runs the trial and the timed presentation (the pool level, an insert in progress).
func advance(delta: float) -> void:
	trial.advance(delta)
	_place_water(pool_water, trial.pool_level, float(_g["pool_low"]), float(_g["pool_high"]))
	if _insert_left > 0.0:
		_insert_left -= delta
		if _insert_left <= 0.0:
			_end_insert()


func basin_yaw(basin: StringName) -> float:
	var p := basin_pivots.get(basin) as Node3D
	return p.rotation.y if p != null else 0.0


## Where the outlet `basin` faces now sits (the yaw its lip turns to).
func outlet_point(basin: StringName) -> Vector3:
	return _target_point(basin, trial.outlet(basin), int(trial.rotations[basin]))


func is_channel_lit(key: String) -> bool:
	var m := channels.get(key) as MeshInstance3D
	return m != null and m.material_override == _lit


func is_inserting() -> bool:
	return _insert_left > 0.0


# --- reactions -------------------------------------------------------------------------------------


func _on_interacted(_id: StringName, _kind: StringName, payload: Dictionary) -> void:
	if payload.has(KEY_ROTATE) and not is_inserting():
		trial.rotate(StringName(str(payload[KEY_ROTATE])))
	elif payload.has(KEY_ITEM):
		Inventory.new(ItemDB.load_default(), Game.state.inventory).add(StringName(str(payload[KEY_ITEM])), 1)
		if charm != null:
			charm.visible = false
		charm_taken.emit()


func _on_trigger(_id: StringName, payload: Dictionary) -> void:
	if not payload.has(KEY_EXIT) or handed_off:
		return
	handed_off = true
	var target := str(cfg.get("next_scene", ""))
	if hand_off.is_valid():
		hand_off.call(target)
	elif autostart and is_inside_tree() and get_tree().current_scene == self:
		FlowRouting.change_scene(target)


func _on_rotated(basin: StringName, _rotation: int) -> void:
	var pivot := basin_pivots.get(basin) as Node3D
	if pivot == null:
		return
	var to := _yaw_to(pivot.global_position, outlet_point(basin))
	var target := pivot.rotation.y + angle_difference(pivot.rotation.y, to)
	if is_inside_tree() and not _fast():
		var tw := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		tw.tween_property(pivot, "rotation:y", target, float(trial.data.get("turn_sec", 0.0)))
	else:
		pivot.rotation.y = target


func _on_flow_changed(path: Array[StringName]) -> void:
	_relight(path)
	if not _water_seen and not path.is_empty() and path.back() == trial.goal():
		_water_seen = true
		_insert(insert_pool)


func _on_pool_filled() -> void:
	Game.set_flag(StringName(str(trial.data.get("door_flag", ""))), true)
	_open_door(false)


func _on_side_drained() -> void:
	Game.set_flag(StringName(str(trial.data.get("drained_flag", ""))), true)
	_place_water(side_water, 0.0, float(_g["side_low"]), float(_g["side_high"]))
	charm.visible = not bool(Game.get_flag(&"ch03_found_net_float"))
	_insert(insert_side)


func _on_hint_due() -> void:
	var scene := StringName(str(trial.data.get("hint_scene", "")))
	if scene != &"" and not hint.is_playing():
		hint.play(scene, null)


## A reload after the trial (a save inside, a test): the door and the side pool as the flags say.
func _restore() -> void:
	if bool(Game.get_flag(StringName(str(trial.data.get("door_flag", ""))))):
		trial.door_open = true
		trial.pool_level = 1.0
		_open_door(true)
	if bool(Game.get_flag(StringName(str(trial.data.get("drained_flag", ""))))):
		trial.side_drained = true
		_place_water(side_water, 0.0, float(_g["side_low"]), float(_g["side_high"]))
		charm.visible = not bool(Game.get_flag(&"ch03_found_net_float"))


func _open_door(instant: bool) -> void:
	var down := Vector3(door.position.x, float(_g["door_sink"]), door.position.z)
	(door.get_node(^"Shape") as CollisionShape3D).disabled = true
	if instant or _fast() or not is_inside_tree():
		door.position = down
		return
	_door_tween = create_tween().set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	_door_tween.tween_property(door, "position", down, float(trial.data.get("door_sink_sec", 0.0)))


func _insert(shot: CameraShot) -> void:
	if shot == null or director == null:
		return
	player.accepts_input = false
	player.velocity = Vector3.ZERO
	director.play_shot(shot, 0.0)
	_insert_left = float(trial.data.get("insert_sec", 0.0))
	if _insert_left <= 0.0:
		_end_insert()


func _end_insert() -> void:
	_insert_left = 0.0
	director.release(0.0)
	player.accepts_input = true


func _fast() -> bool:
	return not is_processing()


# --- the greybox -------------------------------------------------------------------------------------


func _build() -> void:
	var root := Node3D.new()
	root.name = "Greybox"
	add_child(root)
	_lit = _mat("water", true)
	_dim = _mat("channel", false)
	var floor_sz: Array = _g["floor"]
	var fx := float(floor_sz[0])
	var fz := float(floor_sz[1])
	var ft := float(_g["floor_t"])
	_solid(root, "Floor", Vector3(fx, ft, fz), Vector3(0.0, -ft * 0.5, 0.0), _mat("stone", false))
	_build_walls(root, fx, fz)
	for id in trial.basin_ids():
		_build_basin(root, id)
	_build_channels(root)
	pool_water = _build_pool(root, "InnerPool", _xz(trial.goal()), _g["pool"], float(_g["pool_low"]))
	_place_water(pool_water, 0.0, float(_g["pool_low"]), float(_g["pool_high"]))
	side_water = _build_pool(root, "SidePool", _xz(&"side_pool"), _g["side_pool"], float(_g["side_high"]))
	_build_door(root)
	_build_charm(root)


func _build_walls(root: Node3D, fx: float, fz: float) -> void:
	var h := float(_g["wall_h"])
	var t := float(_g["wall_t"])
	var stone := _mat("stone", false)
	_solid(root, "WallNorth", Vector3(fx, h, t), Vector3(0.0, h * 0.5, -fz * 0.5), stone)
	_solid(root, "WallSouth", Vector3(fx, h, t), Vector3(0.0, h * 0.5, fz * 0.5), stone)
	for side: Array in [["WallWest", -fx * 0.5, float(_g["entrance_w"])], ["WallEast", fx * 0.5, float(_g["door_w"])]]:
		var seg := (fz - float(side[2])) * 0.5
		for sgn: float in [-1.0, 1.0]:
			var z := sgn * (float(side[2]) * 0.5 + seg * 0.5)
			_solid(
				root,
				"%s%s" % [side[0], "N" if sgn < 0.0 else "S"],
				Vector3(t, h, seg),
				Vector3(side[1], h * 0.5, z),
				stone
			)


func _build_basin(root: Node3D, id: StringName) -> void:
	var at := _xz(id)
	var r := float(_g["basin_r"])
	var h := float(_g["basin_h"])
	var body := StaticBody3D.new()
	body.name = "Basin_%s" % id
	body.position = at
	root.add_child(body)
	var cyl := CylinderMesh.new()
	cyl.top_radius = r
	cyl.bottom_radius = r * float(_g["basin_foot"])
	cyl.height = h
	var mesh := MeshInstance3D.new()
	mesh.mesh = cyl
	mesh.material_override = _mat("basin", false)
	mesh.position.y = h * 0.5
	body.add_child(mesh)
	var shape := CollisionShape3D.new()
	var cs := CylinderShape3D.new()
	cs.radius = r
	cs.height = h
	shape.shape = cs
	shape.position.y = h * 0.5
	body.add_child(shape)
	var pivot := Node3D.new()
	pivot.name = "Lip"
	pivot.position.y = h
	body.add_child(pivot)
	var lip_sz: Array = _g["lip"]
	var lip := _mesh(pivot, "Spout", Vector3(lip_sz[0], lip_sz[1], lip_sz[2]), _mat("lip", false))
	lip.position = Vector3(0.0, 0.0, -r)
	basin_pivots[id] = pivot
	pivot.rotation.y = _yaw_to(at, outlet_point(id))
	var it := Interactable.new()
	it.name = "Use_%s" % id
	it.id = StringName("basin_%s" % id)
	it.prompt_key = "FIELD_PROMPT_TURN"
	it.payload = {KEY_ROTATE: String(id)}
	it.position = at + Vector3.UP * h
	var sphere := SphereShape3D.new()
	sphere.radius = r + float(_g["reach_m"])
	var ishape := CollisionShape3D.new()
	ishape.shape = sphere
	it.add_child(ishape)
	root.add_child(it)


func _build_channels(root: Node3D) -> void:
	var src: Array = _layout["source"]
	var into := StringName(str(trial.data.get("source_into", "")))
	_channel(root, "source>%s" % into, Vector3(float(src[0]), 0.0, float(src[1])), _xz(into))
	for id in trial.basin_ids():
		var outs: Array = (trial.basins()[String(id)] as Dictionary).get("outlets", [])
		for i in outs.size():
			var to := StringName(str(outs[i]))
			var key := _channel_key(id, to, i)
			if not channels.has(key):
				_channel(root, key, _xz(id), _target_point(id, to, i))


func _channel(root: Node3D, key: String, from: Vector3, to: Vector3) -> void:
	var w := float(_g["channel_w"])
	var ch := float(_g["channel_h"])
	var flat := Vector3(to.x - from.x, 0.0, to.z - from.z)
	var m := _mesh(root, "Channel_%s" % key.replace(">", "_to_"), Vector3(w, ch, flat.length()), _dim)
	m.position = (from + to) * 0.5 + Vector3.UP * ch * 0.5
	m.rotation.y = _yaw_to(from, to)
	channels[key] = m


func _build_pool(root: Node3D, node_name: String, at: Vector3, size: Array, level: float) -> MeshInstance3D:
	var sx := float(size[0])
	var sz := float(size[1])
	var rh := float(_g["rim_h"])
	var rt := float(_g["rim_t"])
	var stone := _mat("stone", false)
	for e: Array in [[Vector3(sx, rh, rt), Vector3(0, 0, -sz * 0.5)], [Vector3(sx, rh, rt), Vector3(0, 0, sz * 0.5)]]:
		_solid(root, "%sRim" % node_name, e[0], at + e[1] + Vector3.UP * rh * 0.5, stone)
	for e: Array in [[Vector3(rt, rh, sz), Vector3(-sx * 0.5, 0, 0)], [Vector3(rt, rh, sz), Vector3(sx * 0.5, 0, 0)]]:
		_solid(root, "%sRim" % node_name, e[0], at + e[1] + Vector3.UP * rh * 0.5, stone)
	var water := _mesh(
		root, "%sWater" % node_name, Vector3(sx - rt, float(_g["water_t"]), sz - rt), _mat("water", true, true)
	)
	water.position = Vector3(at.x, level, at.z)
	return water


func _build_door(root: Node3D) -> void:
	var sz: Array = _g["door"]
	door = _solid(
		root, "Door", Vector3(sz[0], sz[1], sz[2]), _xz(&"door") + Vector3.UP * float(sz[1]) * 0.5, _mat("door", false)
	)
	var exit := Interactable.new()
	exit.name = "Exit"
	exit.id = &"shrine_exit"
	exit.activation = Interactable.Activation.TOUCH
	exit.requires_flag = StringName(str(trial.data.get("door_flag", "")))
	exit.payload = {KEY_EXIT: true}
	exit.position = _xz(&"door") + Vector3.UP * float(sz[1]) * 0.5
	var box := BoxShape3D.new()
	box.size = Vector3(float(_g["exit_depth_m"]), float(sz[1]), float(sz[2]))
	var shape := CollisionShape3D.new()
	shape.shape = box
	exit.add_child(shape)
	root.add_child(exit)


func _build_charm(root: Node3D) -> void:
	var at := _xz(&"side_pool") + Vector3.UP * float(_g["side_low"])
	charm = Node3D.new()
	charm.name = "Charm"
	charm.position = at
	charm.visible = false
	root.add_child(charm)
	var sphere := SphereMesh.new()
	sphere.radius = float(_g["charm_r"])
	sphere.height = sphere.radius * 2.0
	var m := MeshInstance3D.new()
	m.mesh = sphere
	m.material_override = _mat("charm", true)
	charm.add_child(m)
	var it := Interactable.new()
	it.name = "Take"
	it.id = &"net_float_charm"
	it.prompt_key = "FIELD_PROMPT_TAKE"
	it.requires_flag = StringName(str(trial.data.get("drained_flag", "")))
	it.sets_flag = &"ch03_found_net_float"
	it.once = true
	it.payload = {KEY_ITEM: "net_float_charm"}
	it.position = at
	var ss := SphereShape3D.new()
	ss.radius = float((_g["side_pool"] as Array)[0]) * 0.5 + float(_g["reach_m"])
	var shape := CollisionShape3D.new()
	shape.shape = ss
	it.add_child(shape)
	root.add_child(it)


# --- helpers ------------------------------------------------------------------------------------------


func _relight(path: Array[StringName]) -> void:
	for m: MeshInstance3D in channels.values():
		m.material_override = _dim
	var src_key := "source>%s" % trial.data.get("source_into", "")
	if channels.has(src_key):
		(channels[src_key] as MeshInstance3D).material_override = _lit
	for i in range(path.size() - 1):
		var from := path[i]
		if not trial.rotations.has(from):
			continue
		var key := _channel_key(from, path[i + 1], int(trial.rotations[from]))
		if channels.has(key):
			(channels[key] as MeshInstance3D).material_override = _lit


## A spill channel is one per lip direction; every other channel is one per target.
func _channel_key(from: StringName, to: StringName, side: int) -> String:
	return "%s>%s%d" % [from, to, side] if to == StringName(str(trial.data.get("spill", ""))) else "%s>%s" % [from, to]


func _target_point(from: StringName, to: StringName, side: int) -> Vector3:
	if to == StringName(str(trial.data.get("spill", ""))):
		return _xz(from) + SIDE_DIRS[side % SIDE_DIRS.size()] * float(_layout.get("spill_len_m", 1.0))
	return _xz(to)


func _xz(node: StringName) -> Vector3:
	var p: Array = _layout.get(String(node), [0.0, 0.0])
	return Vector3(float(p[0]), 0.0, float(p[1]))


static func _yaw_to(from: Vector3, to: Vector3) -> float:
	return atan2(-(to.x - from.x), -(to.z - from.z))


func _place_water(m: MeshInstance3D, level: float, low: float, high: float) -> void:
	if m != null:
		m.position.y = lerpf(low, high, clampf(level, 0.0, 1.0))
		m.visible = level > 0.0  # an empty pool shows its floor, not a film of water


func _solid(root: Node3D, node_name: String, size: Vector3, at: Vector3, mat: Material) -> StaticBody3D:
	var body := StaticBody3D.new()
	body.name = node_name
	body.position = at
	root.add_child(body)
	_mesh(body, "Mesh", size, mat)
	var box := BoxShape3D.new()
	box.size = size
	var shape := CollisionShape3D.new()
	shape.name = "Shape"
	shape.shape = box
	body.add_child(shape)
	return body


func _mesh(parent: Node3D, node_name: String, size: Vector3, mat: Material) -> MeshInstance3D:
	var bm := BoxMesh.new()
	bm.size = size
	var m := MeshInstance3D.new()
	m.name = node_name
	m.mesh = bm
	m.material_override = mat
	parent.add_child(m)
	return m


func _mat(color_key: String, glow: bool, clear: bool = false) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	var c := Color.html(str((_g.get("colors", {}) as Dictionary).get(color_key, "#FFFFFF")))
	m.albedo_color = c
	if glow:
		m.emission_enabled = true
		m.emission = c
		m.emission_energy_multiplier = float(_g.get("water_emission", 0.0))
	if clear:
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		m.albedo_color.a = float(_g.get("water_alpha", 1.0))
	return m

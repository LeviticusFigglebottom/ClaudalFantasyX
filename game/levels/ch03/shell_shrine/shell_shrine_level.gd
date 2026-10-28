class_name ShellShrineLevel
extends Node3D
## The Shell Shrine trial level (M2-FP-16; vertical_slice.md B07; README.md beside this file). A view
## of ShellShrineTrial. The hall itself (walls, vault, roof, floor, steps, islet) is the dressing
## scene; this script places the trial's working parts from game/data/trials/shell_shrine.json
## ("layout" and "room"), all kit pieces from M2-ENV-03 (assets/environments/kits/haluna/shrine_*):
## the spring, each basin's pedestal and turning bowl, the carved channels and their flowmap water,
## the inner pool and its water, the shell-valve door, the side pool and its water, the net-float
## charm, the collision proxies and interactables; a piece that fails to load is a same-size primitive (warned).
##
## It turns a basin when Rhen uses it, runs water down the channels on the water's path (the water
## shows, the nacre shimmers, the lips pour), raises the inner pool, sinks the door, empties the side
## pool and offers the charm. Through the open door, the exit trigger hands off to Cutscene B
## (first_playable.json "shell_shrine" next_scene).
## M2-FP-27: a location (Spawns/Entry, Spawns/Exit, place_at). Filling the pool moves the respawn to the
## open door and requests a checkpoint autosave, so a Drownbell loss resumes past the trial.
##
## Hooks (VFX, audio, HUD): the trial's own signals (`trial.rotated`, `flow_changed`, `pool_filled`,
## `side_pool_drained`, `hint_due`) plus `charm_taken` here. Time passes only through advance(delta),
## which _process calls; tests call it directly.

signal charm_taken

const KEY_ROTATE := "rotate"
const KEY_ITEM := "item"
const KEY_EXIT := "exit"
const SIDE_DIRS: Array[Vector3] = [Vector3.FORWARD, Vector3.RIGHT, Vector3.BACK, Vector3.LEFT]
## The nacre's per-instance water shimmer (env_nacre_inlay.gdshader).
const SHIMMER := &"inst_shimmer"
## Texels round the flow-direction wheel (tex_flow): a channel's UV.x picks its flow direction.
const FLOW_WHEEL_TEXELS := 64
## Wall collision: segments per half-round.
const WALL_ARC_SEGMENTS := 30
const KERB_RING_SEGMENTS := 12
const SPILL_ROWS := 8
const SPILL_COLS := 4
const DISC_SEGMENTS := 32
const OCTAGON := 8

## The overview (S03) frames the room; these are the inserts (S04 water, S05 the side pool).
@export var insert_pool: CameraShot
@export var insert_side: CameraShot
## Hand off on the exit trigger only when this is the current scene (tests turn it off).
@export var autostart := true
## The hall's GI (a VoxelGI in the graphics presets' gi_voxel group), in two lighting states (the door
## up, and down after the flood). M2-ENV-10 (ADR 0029): the states ship as baked VoxelGIData
## (room.gi_data, made by tools/shrine/bake_shrine_gi.gd) and are only loaded at entry; baking them
## took ~1.8 s each in one main-thread frame.
@export var gi: VoxelGI
## Bake the states at load when the shipped data is missing (a development fallback, never the game:
## it costs the entry ~3.6 s). The bake tool turns it off.
@export var bake_at_load := false

var trial: ShellShrineTrial
var cfg: Dictionary = {}
## Tests record the hand-off here instead of changing scene: (target: String).
var hand_off: Callable = Callable()
var hint: CutsceneSequencer
## basin id -> the Node3D that turns (its lip points at the outlet).
var basin_pivots: Dictionary = {}
## "<from>><to>" -> Node3D: every channel the water can run along (its trough modules and water).
var channels: Dictionary = {}
var pool_water: Node3D
var side_water: Node3D
var door: StaticBody3D
var charm: Node3D
var handed_off := false
## The room's parts, built from the JSON (the hall itself is the dressing scene).
var room: Node3D
## Kit pieces that failed to load (fell back to a primitive).
var missing_pieces: Array[String] = []
## The last GI bake's wall time (ms, both states), -1 before any bake.
var gi_bake_ms := -1
## prebuild() built the hall off the tree (M2-ENV-12), and how long it took (ms, -1 when not).
var prebuilt := false
var prebuild_msec := -1
var gi_load_ms := -1  # bake_gi()'s ms at entry (the shipped states' load, or the fallback bake)
## "closed" / "open" -> the VoxelGIData baked with the door up / down.
var gi_states: Dictionary = {}

var _g: Dictionary = {}
var _layout: Dictionary = {}
var _lit: Dictionary = {}
## channel key -> WaterSurface on top of it.
var _channel_water: Dictionary = {}
## basin id -> [the water in its bowl, the sheet pouring off its lip, the bowl instance].
var _basin_parts: Dictionary = {}
var _pool_inlet: Node3D
var _channel_mat: ShaderMaterial
var _still_mat: ShaderMaterial
var _spill_mat: Material
var _scene_cache: Dictionary = {}
var _insert_left := 0.0
var _water_seen := false
var _door_tween: Tween

@onready var player: FieldController = $Player
@onready var director: FieldCameraDirector = $CameraDirector
@onready var field_camera: Camera3D = $FieldCamera


## M2-ENV-12: on a worker-thread instantiate (the router, the first-run warm-up's harvest) the hall is
## built off the tree, so the warm-up can stage its meshes; a main-thread instance builds in _ready.
func _notification(what: int) -> void:
	if what == NOTIFICATION_SCENE_INSTANTIATED and OS.get_thread_caller_id() != OS.get_main_thread_id():
		prebuild()


## Loads the trial data and builds the hall while off the tree (touches no node in the tree). Once.
func prebuild() -> void:
	if prebuilt or is_inside_tree():
		return
	var t0 := Time.get_ticks_msec()
	_load_trial()
	_build()
	prebuild_msec = Time.get_ticks_msec() - t0
	prebuilt = true


func _ready() -> void:
	if not prebuilt:
		_load_trial()
		_build()
	field_camera.make_current()
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
	bake_gi()


func _load_trial() -> void:
	cfg = FirstPlayableConfig.section(FirstPlayableConfig.SECTION_SHELL_SHRINE)
	trial = ShellShrineTrial.new()
	_g = trial.data.get("room", {})
	_layout = trial.data.get("layout", {})


## Loads the two shipped lighting states and shows the current one (ShrineLighting, M2-ENV-10).
func bake_gi() -> void:
	if gi == null:
		return
	var t0 := Time.get_ticks_msec()
	gi_states = ShrineLighting.load_states(gi_data_paths())
	if gi_states.size() < gi_data_paths().size() and bake_at_load and RenderingServer.get_rendering_device() != null:
		gi_states["open"] = bake_state(true)
		if not trial.door_open:
			gi_states["closed"] = bake_state(false)
		gi_bake_ms = Time.get_ticks_msec() - t0
		print("ShellShrineLevel: GI baked (%d states) in %d ms" % [gi_states.size(), gi_bake_ms])
	gi_load_ms = Time.get_ticks_msec() - t0
	_show_gi_state()


## The shipped lighting states: state ("open", "closed") -> res path (room.gi_data).
func gi_data_paths() -> Dictionary:
	return (trial.data.get("room", {}) as Dictionary).get("gi_data", {})


## Bakes one lighting state (the door down when `open`) on the hall's VoxelGI and returns its data.
func bake_state(open: bool) -> VoxelGIData:
	var keep := door.position
	door.position = Vector3(keep.x, ShrineLighting.door_height(_g, open), keep.z)
	gi.bake()
	door.position = keep
	return ShrineLighting.tune(gi.data, _g)


func _show_gi_state() -> void:
	var data := gi_states.get("open" if trial.door_open else "closed") as VoxelGIData
	if gi != null and data != null:
		gi.data = data


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
	return bool(_lit.get(key, false))


## The channel's water surface (null for an unknown key).
func channel_water(key: String) -> WaterSurface:
	return _channel_water.get(key) as WaterSurface


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
	_relight(trial.trace())  # a loop and a spill trace alike, but the water runs on different channels
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
	var loc := StringName(str(cfg.get("checkpoint_location", "")))
	if loc != &"":
		Game.state.respawn_location_id = loc
		Game.state.respawn_spawn = StringName(str(cfg.get("checkpoint_spawn", "")))
		SaveSystem.request_autosave(StringName(str(cfg.get("checkpoint_reason", SaveSystem.REASON_CHAPTER))))


## Moves Rhen to Spawns/<spawn> facing `yaw_deg` and snaps the camera (WorldReturn, Continue).
func place_at(spawn: StringName, yaw_deg: float = 0.0) -> bool:
	var marker := get_node_or_null(NodePath("Spawns/%s" % spawn)) as Marker3D
	if marker == null:
		push_warning("ShellShrineLevel: no spawn '%s'" % spawn)
		return false
	player.position = marker.position
	player.rotation.y = deg_to_rad(yaw_deg)
	player.velocity = Vector3.ZERO
	if player.motor != null:
		player.motor.facing_yaw = player.rotation.y
	if director.is_inside_tree():
		director.snap()
	return true


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
		_place_water(pool_water, 1.0, float(_g["pool_low"]), float(_g["pool_high"]))
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
		_show_gi_state()
		return
	_door_tween = create_tween().set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	_door_tween.tween_property(door, "position", down, float(trial.data.get("door_sink_sec", 0.0)))
	_door_tween.finished.connect(_show_gi_state)


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


# --- the room's working parts ------------------------------------------------------------------------


func _build() -> void:
	room = Node3D.new()
	room.name = "Room"
	add_child(room)
	_load_materials()
	_build_collision()
	_build_spring()
	for id in trial.basin_ids():
		_build_basin(id)
	_build_channels()
	ShrineChannelCurbs.build(channels, ShrineChannelCurbs.load_config())  # M2-FP-24
	pool_water = _build_inner_pool()
	_place_water(pool_water, 0.0, float(_g["pool_low"]), float(_g["pool_high"]))
	side_water = _build_side_pool()
	_build_door()
	_build_charm()
	# M3-NAR-01: the Words at the Basin Steps, on the first step inside the entrance, read on the way in.
	room.add_child(CodexRecordSpot.make("basin_steps", _xz(&"basin_steps"), float(_g["reach_m"])))


func _load_materials() -> void:
	var base := load(str(_g.get("water_material", ""))) as ShaderMaterial
	if base == null:
		push_warning("ShellShrineLevel: no water material; channels use a plain one")
		base = ShaderMaterial.new()
	_channel_mat = base.duplicate() as ShaderMaterial
	_channel_mat.set_shader_parameter(&"tex_flow", flow_wheel())
	_still_mat = base.duplicate() as ShaderMaterial
	_still_mat.set_shader_parameter(&"tex_flow", _still_flow())
	_spill_mat = load(str(_g.get("spill_material", ""))) as Material


## A kit piece (assets/environments/kits/haluna/<name>.glb), or `fallback` when it does not load.
func _piece(key: String, fallback: Mesh) -> Node3D:
	var piece := str((_g.get("pieces", {}) as Dictionary).get(key, ""))
	var path := str(_g.get("kit_dir", "")) + piece + ".glb"
	if not _scene_cache.has(path):
		_scene_cache[path] = load(path) as PackedScene if piece != "" and ResourceLoader.exists(path) else null
	var packed := _scene_cache[path] as PackedScene
	if packed != null:
		var node := packed.instantiate() as Node3D
		if node != null:
			node.name = piece
			return node
	if not missing_pieces.has(key):
		missing_pieces.append(key)
		push_warning("ShellShrineLevel: kit piece '%s' (%s) missing; a primitive stands in" % [key, path])
	var mi := MeshInstance3D.new()
	mi.name = "Fallback_%s" % key
	mi.mesh = fallback
	return mi


func _build_spring() -> void:
	var into := StringName(str(trial.data.get("source_into", "")))
	var at := _source_point()
	var spring := _piece("spring", _cylinder(0.62, 0.55, Vector3.UP * 0.275))
	spring.position = at
	spring.rotation.y = _yaw_to(at, _xz(into))
	room.add_child(spring)
	_static_cylinder("SpringBody", at, 0.66, 0.55)
	var spout: Array = _g.get("spring_spout", [0.72, 0.5])
	var sheet := _spill_sheet(
		Vector3(0.0, float(spout[1]), -float(spout[0])),
		Vector3(0.0, float(_g["channel_water"]), -float(spout[0]) - 0.14),
	)
	sheet.name = "Pour"
	spring.add_child(sheet)
	var well := _water_disc("SpringWater", at + Vector3.UP * 0.45, 0.47, DISC_SEGMENTS)
	well.visible = true


func _build_basin(id: StringName) -> void:
	var at := _xz(id)
	var r := float(_g["basin_r"])
	var h := float(_g["basin_h"])
	var ped_h := float(_g["pedestal_h"])
	var body := StaticBody3D.new()
	body.name = "Basin_%s" % id
	body.position = at
	room.add_child(body)
	body.add_child(_piece("pedestal", _cylinder(0.6, ped_h, Vector3.UP * ped_h * 0.5)))
	var shape := CollisionShape3D.new()
	var cs := CylinderShape3D.new()
	cs.radius = r
	cs.height = h
	shape.shape = cs
	shape.position.y = h * 0.5
	body.add_child(shape)
	var pivot := Node3D.new()
	pivot.name = "Lip"
	pivot.position.y = ped_h
	body.add_child(pivot)
	var bowl := _piece("bowl", _cylinder(r, h - ped_h, Vector3.UP * (h - ped_h) * 0.5))
	pivot.add_child(bowl)
	var reach := float(_g["lip_reach_m"])
	var sheet := _spill_sheet(
		Vector3(0.0, float(_g["spout_y"]), -reach),
		Vector3(0.0, float(_g["channel_water"]) - ped_h, -reach - 0.16),
	)
	sheet.name = "Pour"
	pivot.add_child(sheet)
	var water := _water_disc("Water_%s" % id, at + Vector3.UP * (ped_h + float(_g["bowl_water"])), 0.98, DISC_SEGMENTS)
	_basin_parts[id] = [water, sheet, bowl]
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
	room.add_child(it)


func _build_channels() -> void:
	var into := StringName(str(trial.data.get("source_into", "")))
	var spout: Array = _g.get("spring_spout", [0.72, 0.5])
	var src := _source_point()
	var dir := (_xz(into) - src).normalized()
	_channel("source>%s" % into, src + dir * float(spout[0]), _xz(into) - dir * float(_g["foot_m"]), &"")
	for id in trial.basin_ids():
		var outs: Array = (trial.basins()[String(id)] as Dictionary).get("outlets", [])
		for i in outs.size():
			var to := StringName(str(outs[i]))
			var key := _channel_key(id, to, i)
			if channels.has(key):
				continue
			var reverse := "%s>%s" % [to, id]
			if channels.has(reverse):  # both ways along one trough: share it, water each way on its own
				_share_channel(key, reverse, id, to)
				continue
			var from := _xz(id)
			var end := _target_point(id, to, i)
			var d := (end - from).normalized()
			_channel(key, from + d * float(_g["foot_m"]), _channel_end(id, to, end, d), to)


## The point a channel from `from` toward `to` ends at: a basin's foot, the inner pool's kerb, the
## sluice gate's trough, or (a spill) the grate.
func _channel_end(_from: StringName, to: StringName, end: Vector3, d: Vector3) -> Vector3:
	if trial.basins().has(String(to)):
		return end - d * float(_g["foot_m"])
	if to == trial.goal():
		return _xz(to) - d * (_octagon_reach(d, float((_g["pool"] as Array)[0]) * 0.5) + float(_g["rim_t"]))
	if to == trial.drain():
		return end - d * float(_g["sluice_m"])
	return end - d * float(_g["spillway_m"])


func _channel(key: String, a: Vector3, b: Vector3, to: StringName) -> void:
	var node := Node3D.new()
	node.name = "Channel_%s" % key.replace(">", "_to_")
	node.position = a
	node.rotation.y = _yaw_to(a, b)
	room.add_child(node)
	var length := Vector2(b.x - a.x, b.z - a.z).length()
	node.set_meta(ShrineChannelCurbs.LENGTH_META, length)
	var module := float(_g["module_m"])
	var n := maxi(1, roundi(length / module))
	var scale_z := length / (n * module)
	for k in n:
		var m := _piece("channel", _box(Vector3(0.7, 0.3, module), Vector3(0.0, 0.15, -module * 0.5)))
		m.position = Vector3(0.0, 0.0, -k * module * scale_z)
		m.scale = Vector3(1.0, 1.0, scale_z)
		node.add_child(m)
	var spill := StringName(str(trial.data.get("spill", "")))
	if to == spill:
		var grate := _piece("spillway", _box(Vector3(0.9, 0.08, 1.25), Vector3(0.0, 0.04, -0.62)))
		grate.position = Vector3(0.0, 0.0, -length)
		node.add_child(grate)
	elif to == trial.drain():
		var gate := _piece("sluice", _box(Vector3(0.8, 1.0, 0.3), Vector3(0.0, 0.5, 0.0)))
		gate.position = Vector3(0.0, 0.0, -length - float(_g["sluice_m"]))
		node.add_child(gate)
	elif to == trial.goal():
		_pool_inlet = _spill_sheet(
			Vector3(0.0, float(_g["channel_water"]), -length - float(_g["rim_t"])),
			Vector3(0.0, float(_g["pool_low"]) + 0.05, -length - float(_g["rim_t"]) - 0.25),
		)
		_pool_inlet.name = "PoolInlet"
		node.add_child(_pool_inlet)
	var extra := float(_g["sluice_m"]) if to == trial.drain() else (float(_g["rim_t"]) if to == trial.goal() else 0.0)
	var water := _water_strip(
		"Water_%s" % key.replace(">", "_to_"), a, b + (b - a).normalized() * extra, float(_g["channel_w"])
	)
	channels[key] = node
	_channel_water[key] = water


## `key` runs the same trough as `reverse`, the other way: one trough, a water surface of its own.
func _share_channel(key: String, reverse: String, from: StringName, to: StringName) -> void:
	var a := _xz(from)
	var b := _xz(to)
	var d := (b - a).normalized()
	channels[key] = channels[reverse]
	_channel_water[key] = _water_strip(
		"Water_%s" % key.replace(">", "_to_"),
		a + d * float(_g["foot_m"]),
		b - d * float(_g["foot_m"]),
		float(_g["channel_w"])
	)


func _build_inner_pool() -> Node3D:
	var at := _xz(trial.goal())
	var across := float((_g["pool"] as Array)[0])
	var pool := _piece("inner_pool", _box(Vector3(across, 0.2, across), Vector3(0.0, -0.1, 0.0)))
	pool.position = at
	room.add_child(pool)
	var ap := across * 0.5
	for i in OCTAGON:
		var n := Vector3.FORWARD.rotated(Vector3.UP, TAU * i / OCTAGON)
		var side := 2.0 * (ap + float(_g["rim_t"])) * tan(PI / OCTAGON)
		_static_box(
			"InnerPoolRim%d" % i,
			at + n * (ap + float(_g["rim_t"]) * 0.5) + Vector3.UP * float(_g["rim_h"]) * 0.5,
			Vector3(side, float(_g["rim_h"]), float(_g["rim_t"])),
			atan2(-n.x, -n.z)
		)
	var water := _water_octagon("InnerPoolWater", Vector3(at.x, float(_g["pool_low"]), at.z), ap)
	water.add_child(_pool_bounce())
	return water


func _build_side_pool() -> Node3D:
	var at := _xz(&"side_pool")
	var r := float((_g["side_pool"] as Array)[0]) * 0.5
	var pool := _piece("side_pool", _cylinder(r, 0.2, Vector3.UP * 0.1))
	pool.position = at
	room.add_child(pool)
	for i in KERB_RING_SEGMENTS:
		var n := Vector3.FORWARD.rotated(Vector3.UP, TAU * i / KERB_RING_SEGMENTS)
		var side := 2.0 * (r + float(_g["rim_t"])) * tan(PI / KERB_RING_SEGMENTS)
		_static_box(
			"SidePoolRim%d" % i,
			at + n * (r + float(_g["rim_t"]) * 0.5) + Vector3.UP * float(_g["rim_h"]) * 0.5,
			Vector3(side, float(_g["rim_h"]), float(_g["rim_t"])),
			atan2(-n.x, -n.z)
		)
	var water := _water_disc("SidePoolWater", Vector3(at.x, float(_g["side_high"]), at.z), r, DISC_SEGMENTS)
	water.visible = true
	water.add_child(_pool_bounce())
	return water


## The teal bounce off a pool's water (colour script ch03_shrine_int: #3FD0C9 at 0.4). A child of the
## water, so it rises with the pool and goes out when the pool is empty or drained.
func _pool_bounce() -> OmniLight3D:
	var cfg_b := _g.get("pool_bounce", {}) as Dictionary
	var light := OmniLight3D.new()
	light.name = "Bounce"
	light.light_color = Color.html(str(cfg_b.get("color", "#FFFFFF")))
	light.light_energy = float(cfg_b.get("energy", 0.0))
	light.omni_range = float(cfg_b.get("range_m", 1.0))
	light.position.y = float(cfg_b.get("height_m", 0.0))
	light.light_volumetric_fog_energy = 0.0  # M3-ARC-04: a lamp in ShaftFog never lights the volume
	return light


func _build_door() -> void:
	var sz: Array = _g["door"]
	var at := _xz(&"door")
	door = _static_box("Door", at + Vector3.UP * float(sz[1]) * 0.5, Vector3(sz[0], sz[1], sz[2]), 0.0)
	var valve := _piece(
		"door", _box(Vector3(float(sz[2]), float(sz[1]), float(sz[0])), Vector3.UP * float(sz[1]) * 0.5)
	)
	valve.position = Vector3.DOWN * float(sz[1]) * 0.5
	var inward := (Vector3.ZERO - at).normalized()
	valve.rotation.y = atan2(inward.x, inward.z)  # the carved face (+Z) toward the hall
	door.add_child(valve)
	var exit := Interactable.new()
	exit.name = "Exit"
	exit.id = &"shrine_exit"
	exit.activation = Interactable.Activation.TOUCH
	exit.requires_flag = StringName(str(trial.data.get("door_flag", "")))
	exit.payload = {KEY_EXIT: true}
	exit.position = at + Vector3.UP * float(sz[1]) * 0.5
	var box := BoxShape3D.new()
	box.size = Vector3(float(_g["exit_depth_m"]), float(sz[1]), float(sz[2]))
	var shape := CollisionShape3D.new()
	shape.shape = box
	exit.add_child(shape)
	room.add_child(exit)


func _build_charm() -> void:
	var at := _xz(&"side_pool") + Vector3.UP * float(_g["charm_rest"])
	charm = Node3D.new()
	charm.name = "Charm"
	charm.position = at
	charm.visible = false
	room.add_child(charm)
	var r := float(_g["charm_r"])
	var sphere := SphereMesh.new()
	sphere.radius = r
	sphere.height = r * 2.0
	var piece := _piece("charm", sphere)
	charm.add_child(piece)
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
	room.add_child(it)


## The floor, the stadium wall (open only at the door), the closed entrance and a stop behind the door.
func _build_collision() -> void:
	var half := float(_g["hall_half_m"])
	var r := float(_g["hall_r_m"])
	var t := float(_g["wall_t"])
	var h := float(_g["wall_h"])
	var ft := float(_g["floor_t"])
	_static_box("FloorBody", Vector3(0.0, -ft * 0.5, 0.0), Vector3(2.0 * (half + r + t), ft, 2.0 * (r + t)), 0.0)
	for sz: float in [-1.0, 1.0]:
		_static_box(
			"WallRun%s" % ("N" if sz < 0.0 else "S"),
			Vector3(0.0, h * 0.5, sz * (r + t * 0.5)),
			Vector3(2.0 * half, h, t),
			0.0
		)
	var door_at := _xz(&"door")
	var gap := float(_g["door_w"]) * 0.5
	for sx: float in [-1.0, 1.0]:
		var c := Vector3(sx * half, 0.0, 0.0)
		for i in WALL_ARC_SEGMENTS:
			var a := (float(i) + 0.5) / WALL_ARC_SEGMENTS * PI
			var n := Vector3(sx * sin(a), 0.0, -cos(a))
			var mid := c + n * (r + t * 0.5)
			if Vector2(mid.x - door_at.x, mid.z - door_at.z).length() < gap:
				continue
			var chord := 2.0 * (r + t) * sin(PI / WALL_ARC_SEGMENTS * 0.5) + 0.05
			_static_box(
				"WallArc%d" % (i if sx < 0.0 else i + WALL_ARC_SEGMENTS),
				mid + Vector3.UP * h * 0.5,
				Vector3(chord, h, t),
				atan2(-n.x, -n.z)
			)
	# The passage behind the door: its floor, sides and end, so the open door leads nowhere but the exit.
	var out := Vector3(door_at.x, 0.0, door_at.z).normalized()
	var depth := float(_g["exit_depth_m"]) + t
	var yaw := atan2(-out.x, -out.z) + PI * 0.5
	var across := out.cross(Vector3.UP)
	_static_box(
		"PassageFloor",
		door_at + out * depth * 0.5 + Vector3.DOWN * ft * 0.5,
		Vector3(depth, ft, float(_g["door_w"]) + 2.0 * t),
		yaw
	)
	_static_box(
		"PassageEnd", door_at + out * depth + Vector3.UP * h * 0.5, Vector3(t, h, float(_g["door_w"]) + 2.0 * t), yaw
	)
	for s: float in [-1.0, 1.0]:
		_static_box(
			"PassageSide%d" % (0 if s < 0.0 else 1),
			door_at + out * depth * 0.5 + across * s * (gap + t * 0.5) + Vector3.UP * h * 0.5,
			Vector3(depth, h, t),
			yaw
		)


# --- water ---------------------------------------------------------------------------------------------


func _relight(path: Array[StringName]) -> void:
	_lit.clear()
	var src_key := "source>%s" % trial.data.get("source_into", "")
	_lit[src_key] = true
	var wet: Dictionary = {}
	for node in path:
		if trial.rotations.has(node) and not wet.has(node):
			wet[node] = true
			var key := _channel_key(node, trial.outlet(node), int(trial.rotations[node]))
			_lit[key] = true
	for key: String in channels:
		var on := is_channel_lit(key)
		var water := _channel_water.get(key) as Node3D
		if water != null:
			water.visible = on
	# A shared trough shimmers when either of its waters runs.
	var troughs: Dictionary = {}
	for key: String in channels:
		var node := channels[key] as Node3D
		troughs[node] = bool(troughs.get(node, false)) or is_channel_lit(key)
	for node: Node3D in troughs:
		_shimmer(node, 1.0 if troughs[node] else 0.0)
	for id: StringName in _basin_parts:
		var parts: Array = _basin_parts[id]
		var on := wet.has(id)
		(parts[0] as Node3D).visible = on
		(parts[1] as Node3D).visible = on
		_shimmer(parts[2] as Node3D, 1.0 if on else 0.0)
	if _pool_inlet != null:
		_pool_inlet.visible = not path.is_empty() and path.back() == trial.goal()


func _shimmer(node: Node3D, value: float) -> void:
	if node == null:
		return
	for mi: Node in node.find_children("*", "GeometryInstance3D", true, false):
		(mi as GeometryInstance3D).set_instance_shader_parameter(SHIMMER, value)


## The flow-direction wheel: texel i holds the unit direction at angle 2*PI*i/N, encoded RG = d*0.5+0.5
## (the river shader's tex_flow, world XZ). A channel's UV.x = its angle / TAU picks its direction.
static func flow_wheel() -> ImageTexture:
	var img := Image.create(FLOW_WHEEL_TEXELS, 1, false, Image.FORMAT_RGB8)
	for i in FLOW_WHEEL_TEXELS:
		var a := TAU * float(i) / FLOW_WHEEL_TEXELS
		img.set_pixel(i, 0, Color(0.5 + 0.5 * cos(a), 0.5 + 0.5 * sin(a), 0.0))
	return ImageTexture.create_from_image(img)


static func flow_u(dir: Vector3) -> float:
	return fposmod(atan2(dir.z, dir.x) / TAU, 1.0) + 0.5 / FLOW_WHEEL_TEXELS


static func _still_flow() -> ImageTexture:
	var img := Image.create(1, 1, false, Image.FORMAT_RGB8)
	img.set_pixel(0, 0, Color(0.5, 0.5, 0.0))
	return ImageTexture.create_from_image(img)


func _water_surface(node_name: String, at: Vector3, mesh: Mesh, mat: ShaderMaterial) -> WaterSurface:
	var w := WaterSurface.new()
	w.name = node_name
	w.river = true
	w.material = mat
	w.surface_mesh = mesh
	w.position = at
	w.visible = false
	room.add_child(w)
	return w


func _water_strip(node_name: String, a: Vector3, b: Vector3, width: float) -> WaterSurface:
	var d := Vector3(b.x - a.x, 0.0, b.z - a.z)
	var side := d.normalized().cross(Vector3.UP) * width * 0.5
	var u := flow_u(d.normalized())
	var verts := PackedVector3Array([-side, side, d + side, d - side])
	var uvs := PackedVector2Array([Vector2(u, 0.0), Vector2(u, 0.0), Vector2(u, 1.0), Vector2(u, 1.0)])
	var idx := PackedInt32Array([0, 2, 1, 0, 3, 2])
	var at := Vector3(a.x, float(_g["channel_water"]), a.z)
	return _water_surface(node_name, at, _flat_mesh(verts, uvs, idx), _channel_mat)


func _water_disc(node_name: String, at: Vector3, radius: float, segments: int, phase: float = 0.0) -> WaterSurface:
	var verts := PackedVector3Array([Vector3.ZERO])
	var uvs := PackedVector2Array([Vector2(0.5, 0.5)])
	var idx := PackedInt32Array()
	for i in segments:
		var a := TAU * float(i) / segments + phase
		verts.append(Vector3(sin(a), 0.0, -cos(a)) * radius)
		uvs.append(Vector2(0.5, 0.5))
		idx.append_array([0, 1 + i, 1 + (i + 1) % segments])
	return _water_surface(node_name, at, _flat_mesh(verts, uvs, idx), _still_mat)


## The octagon's water, its flats facing the compass points as the kit's pool does.
func _water_octagon(node_name: String, at: Vector3, apothem: float) -> WaterSurface:
	return _water_disc(node_name, at, apothem / cos(PI / OCTAGON), OCTAGON, PI / OCTAGON)


static func _flat_mesh(verts: PackedVector3Array, uvs: PackedVector2Array, idx: PackedInt32Array) -> ArrayMesh:
	var normals := PackedVector3Array()
	normals.resize(verts.size())
	normals.fill(Vector3.UP)
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = verts
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_TEX_UV] = uvs
	arrays[Mesh.ARRAY_INDEX] = idx
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	return mesh


## A falling sheet from `top` to `bottom` (local), bowed a little toward the fall: UV.x across, UV.y down.
func _spill_sheet(top: Vector3, bottom: Vector3) -> MeshInstance3D:
	var w := float(_g["spill_width_m"])
	var verts := PackedVector3Array()
	var uvs := PackedVector2Array()
	var idx := PackedInt32Array()
	for row in SPILL_ROWS + 1:
		var t := float(row) / SPILL_ROWS
		var p := Vector3(top.x, lerpf(top.y, bottom.y, t * t), lerpf(top.z, bottom.z, sqrt(t)))
		for col in SPILL_COLS + 1:
			var s := float(col) / SPILL_COLS
			var bow := sin(PI * s) * w * 0.25
			verts.append(p + Vector3((s - 0.5) * w, 0.0, -bow))
			uvs.append(Vector2(s, t))
	for row in SPILL_ROWS:
		for col in SPILL_COLS:
			var a := row * (SPILL_COLS + 1) + col
			idx.append_array([a, a + 1, a + SPILL_COLS + 2, a, a + SPILL_COLS + 2, a + SPILL_COLS + 1])
	var normals := PackedVector3Array()
	normals.resize(verts.size())
	normals.fill(Vector3.BACK)
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = verts
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_TEX_UV] = uvs
	arrays[Mesh.ARRAY_INDEX] = idx
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = _spill_mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.visible = false
	return mi


# --- helpers ------------------------------------------------------------------------------------------


## A spill channel is one per lip direction; every other channel is one per target.
func _channel_key(from: StringName, to: StringName, side: int) -> String:
	return "%s>%s%d" % [from, to, side] if to == StringName(str(trial.data.get("spill", ""))) else "%s>%s" % [from, to]


func _target_point(from: StringName, to: StringName, side: int) -> Vector3:
	if to == StringName(str(trial.data.get("spill", ""))):
		return _xz(from) + spill_dir(from, side) * float(_layout.get("spill_len_m", 1.0))
	return _xz(to)


## The direction a spill lip faces: layout.spill_bearing_deg[basin][rotation] (compass degrees), or
## the rotation's compass point.
func spill_dir(basin: StringName, side: int) -> Vector3:
	var bearings := (_layout.get("spill_bearing_deg", {}) as Dictionary).get(String(basin), {}) as Dictionary
	if bearings.has(str(side)):
		var b := deg_to_rad(float(bearings[str(side)]))
		return Vector3(sin(b), 0.0, -cos(b))
	return SIDE_DIRS[side % SIDE_DIRS.size()]


func _source_point() -> Vector3:
	var src: Array = _layout["source"]
	return Vector3(float(src[0]), 0.0, float(src[1]))


func _xz(node: StringName) -> Vector3:
	var p: Array = _layout.get(String(node), [0.0, 0.0])
	return Vector3(float(p[0]), 0.0, float(p[1]))


static func _yaw_to(from: Vector3, to: Vector3) -> float:
	return atan2(-(to.x - from.x), -(to.z - from.z))


## Distance from an octagon's centre (flats facing the compass points) to its edge along `d`.
static func _octagon_reach(d: Vector3, apothem: float) -> float:
	var best := 0.0
	for i in OCTAGON:
		var n := Vector3.FORWARD.rotated(Vector3.UP, TAU * i / OCTAGON)
		best = maxf(best, d.dot(n))
	return apothem / maxf(best, 0.001)


func _place_water(m: Node3D, level: float, low: float, high: float) -> void:
	if m != null:
		m.position.y = lerpf(low, high, clampf(level, 0.0, 1.0))
		m.visible = level > 0.0  # an empty pool shows its floor, not a film of water


func _static_box(node_name: String, at: Vector3, size: Vector3, yaw: float) -> StaticBody3D:
	var body := StaticBody3D.new()
	body.name = node_name
	body.position = at
	body.rotation.y = yaw
	room.add_child(body)
	var box := BoxShape3D.new()
	box.size = size
	var shape := CollisionShape3D.new()
	shape.name = "Shape"
	shape.shape = box
	body.add_child(shape)
	return body


func _static_cylinder(node_name: String, at: Vector3, radius: float, height: float) -> void:
	var body := StaticBody3D.new()
	body.name = node_name
	body.position = at
	room.add_child(body)
	var cs := CylinderShape3D.new()
	cs.radius = radius
	cs.height = height
	var shape := CollisionShape3D.new()
	shape.shape = cs
	shape.position.y = height * 0.5
	body.add_child(shape)


static func _box(size: Vector3, offset: Vector3) -> Mesh:
	var bm := BoxMesh.new()
	bm.size = size
	return _offset(bm, offset)


static func _cylinder(radius: float, height: float, offset: Vector3) -> Mesh:
	var cm := CylinderMesh.new()
	cm.top_radius = radius
	cm.bottom_radius = radius
	cm.height = height
	return _offset(cm, offset)


## A fallback primitive moved so it sits where the kit piece would (kit origins are on the floor).
static func _offset(prim: PrimitiveMesh, offset: Vector3) -> Mesh:
	var st := SurfaceTool.new()
	st.create_from(prim, 0)
	st.set_material(StandardMaterial3D.new())
	var mesh := st.commit()
	var arrays := mesh.surface_get_arrays(0)
	var verts := arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array
	for i in verts.size():
		verts[i] += offset
	arrays[Mesh.ARRAY_VERTEX] = verts
	var out := ArrayMesh.new()
	out.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	return out

extends Node3D
## Stills of a scripted walk (the Lead's 10-29 walk audit, item 4): walks one route of
## tests/integration/qa_walk_routes.json exactly as test_qa_walk_audit.gd does (the real FieldController, HeroStairs,
## the party and the camera director) and saves the frame every `every` frames as <out>/<route>_<frame>.png.
## Render it with the software renderer (lavapipe, like the screenshots):
##   godot-render --path . res://tools/hero/walk_stills.tscn -- --route=haluna_lane --every=90 --out=/abs/dir
## Viewing them is the check (camera clearance, followers on their spots, feet on the steps); nothing is compared.

const AUDIT := preload("res://tests/integration/test_qa_walk_audit.gd")
const ROUTES := "res://tests/integration/qa_walk_routes.json"
const DT := 1.0 / 60.0
const SETTLE_FRAMES := 30
const ARRIVE_M := 0.35
const MAX_FRAMES := 7200
const TAIL_FRAMES := 60

var _args := {}
var _player: FieldController
var _party: HeroFieldParty
var _points: Array[Vector3] = []
var _leg := 0
var _frame := 0
var _tail := 0
var _run := true
var _busy := false


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		_args[kv[0]] = kv[1] if kv.size() > 1 else ""
	var data := AUDIT._json(ROUTES)
	var route := (data.get("routes", {}) as Dictionary).get(str(_args.get("route", "")), {}) as Dictionary
	if route.is_empty():
		push_error("walk_stills: no route '%s'" % _args.get("route", ""))
		get_tree().quit(2)
		return
	Game.new_game()
	Game.state.party_ids.assign(
		(data.get("party", []) as Array).map(func(s: Variant) -> StringName: return StringName(str(s)))
	)
	Game.state.reserve_ids.assign(
		(data.get("reserve", []) as Array).map(func(s: Variant) -> StringName: return StringName(str(s)))
	)
	for f: Variant in route.get("flags", []):
		Game.set_flag(StringName(str(f)))
	var zone := (load(str(route["scene"])) as PackedScene).instantiate() as Node3D
	var story := zone.get(&"story") as ZoneStory if "story" in zone else null
	if story != null:
		story.autostart = false
	if "autoplay" in zone:
		zone.set(&"autoplay", false)
	add_child(zone)
	_player = AUDIT._controller(zone)
	_party = _player.get_node(NodePath(String(HeroFieldParty.NAME))) as HeroFieldParty
	_player.set_physics_process(false)
	_player.set_process_unhandled_input(false)
	_party.set_physics_process(false)
	if _player.director != null:
		_player.director.auto_update = false
	var stairs := _player.get_node_or_null(NodePath(String(HeroStairs.NAME))) as HeroStairs
	if stairs != null:
		stairs.set_physics_process(false)
		stairs.build_from_layout()
	for block: Variant in route.get("hide_blocks", []):
		zone.call(&"hide_block", str(block))
	_points = AUDIT._route_points(route, zone, _player)
	_run = bool(route.get("run", true))
	_party.catch_up()
	for i in SETTLE_FRAMES:
		AUDIT._frame(_player, _player.director, _party, Vector2.ZERO, false)


## Simulates up to the next still (or the walk's end), then lets one frame render and saves it: the software
## renderer draws only the frames that are kept, so a long route takes minutes, not an hour.
func _process(_delta: float) -> void:
	if _points.is_empty() or _player == null or _busy:
		return
	_busy = true
	var every := maxi(int(_args.get("every", "60")), 1)
	while true:
		_step()
		if _frame % every == 0 or _tail >= TAIL_FRAMES:
			break
	await RenderingServer.frame_post_draw
	var out := str(_args.get("out", OS.get_user_data_dir()))
	DirAccess.make_dir_recursive_absolute(out)
	get_viewport().get_texture().get_image().save_png(
		out.path_join("%s_%05d.png" % [_args.get("route", "walk"), _frame])
	)
	if _tail >= TAIL_FRAMES:
		get_tree().quit(0)
		return
	_busy = false


## One simulated frame of the walk, as test_qa_walk_audit.gd steps it.
func _step() -> void:
	_frame += 1
	var stick := Vector2.ZERO
	if _leg < _points.size() and _frame < MAX_FRAMES:
		var to := _points[_leg]
		var flat := Vector3(to.x - _player.global_position.x, 0.0, to.z - _player.global_position.z)
		if flat.length() <= ARRIVE_M:
			_leg += 1
		else:
			stick = AUDIT._stick_toward(_player, _player.director, flat)
	else:
		_tail += 1
	for b: HeroFieldActor in AUDIT._bodies(_player, _party):
		b.set_process(false)  # the rig advances every body itself, once a frame (followers spawn late)
	AUDIT._frame(_player, _player.director, _party, stick, not _run)

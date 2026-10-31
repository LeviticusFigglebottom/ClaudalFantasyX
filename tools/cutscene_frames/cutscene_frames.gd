extends Node
## Renders a slice cutscene or zone beat to PNG frames so a person (or an agent) can VIEW it
## (M2-FP-102; docs/kb/tech/cutscenes.md "Viewing a cutscene"). Software Forward+ (lavapipe):
##   godot-render --path . --audio-driver Dummy --fixed-fps 30 --resolution 960x540 \
##     res://tools/cutscene_frames/cutscene_frames.tscn -- --location=ch02/haluna --spawn=Beach \
##     --flags=prologue_seen --every=1.0 --max-sec=150 --out=/abs/dir [--choice=0] [--tour=Spawn:sec,...]
## It travels to --location at --spawn through SceneRouter.world_return (as the game does: the
## real fade, prewarm and arrival beats), with the --flags set first and every other flag clear.
## Dialogue advances by itself (the Accessibility "dialogue_auto" setting, M2-UI-25) and every choice
## takes option --choice. A frame is written every --every seconds of game time as
## <out>/f_<seconds*10>.png, plus a line per spoken line in <out>/lines.txt with its time, so a
## frame can be matched to its line. --tour places the party at each named spawn of the current scene
## (place_at) at that game time, to view a long route section by section. It quits after --max-sec.
## M2-FP-119: --cut-frames=N also writes the N frames that follow any camera jump of more than
## CUT_JUMP_M (a cut), every frame, as <out>/cut_<milliseconds>.png, so what a cut shows can be seen
## frame by frame. --no-taa turns the viewport's TAA off (to tell temporal history from staging). --log-player adds a
## line per written frame with the player's and the camera's positions (where the staging really put them).
## Nothing is saved (autosaves held). The resident shaders are warmed first, as boot does (a cold travel can fail to load
## a zone whose shaders the resident loads share).

const DEFAULT_EVERY_SEC := 1.0
const DEFAULT_MAX_SEC := 120.0
## The pause before a choice is taken, so the frame with the choices up is written.
const CHOICE_HOLD_SEC := 1.5
const FRAME_NAME_SCALE := 10.0
## A camera move larger than this in one frame counts as a cut (--cut-frames).
const CUT_JUMP_M := 5.0
const CUT_NAME_SCALE := 1000.0

var _every := DEFAULT_EVERY_SEC
var _max_sec := DEFAULT_MAX_SEC
var _out := ""
var _choice := 0
var _location := &""
var _spawn := &""
var _flags: Array[StringName] = []
var _elapsed := 0.0
var _next_frame := 0.0
var _choice_wait := 0.0
var _last_line := ""
var _lines: PackedStringArray = []
var _started := false
## [[spawn, sec], ...] still to visit (--tour), in time order.
var _tour: Array = []
var _cut_frames := 0
var _cut_left := 0
var _no_taa := false
var _log_player := false
var _last_cam := Vector3.INF


func _ready() -> void:
	for arg: String in OS.get_cmdline_user_args():
		var kv := arg.trim_prefix("--").split("=", true, 1)
		var value := kv[1] if kv.size() > 1 else ""
		match kv[0]:
			"location":
				_location = StringName(value)
			"spawn":
				_spawn = StringName(value)
			"flags":
				for f: String in value.split(",", false):
					_flags.append(StringName(f))
			"every":
				_every = float(value)
			"max-sec":
				_max_sec = float(value)
			"out":
				_out = value
			"choice":
				_choice = int(value)
			"cut-frames":
				_cut_frames = int(value)
			"no-taa":
				_no_taa = true
			"log-player":
				_log_player = true
			"tour":
				for stop: String in value.split(",", false):
					var pair := stop.split(":")
					_tour.append([StringName(pair[0]), float(pair[1]) if pair.size() > 1 else 0.0])
	if _out == "" or _location == &"":
		push_error("CutsceneFrames: --location and --out are required")
		get_tree().quit(2)
		return
	DirAccess.make_dir_recursive_absolute(_out)
	UiSettings.shared().set_value(UiSettings.DIALOGUE_AUTO, true)
	Game.state = GameStateData.new()
	for f: StringName in _flags:
		Game.set_flag(f)
	SaveSystem.hold_autosave(self)
	# The router frees the current scene on a change, so this node moves to the root first.
	_reparent_and_go.call_deferred()


func _reparent_and_go() -> void:
	var tree := get_tree()
	get_parent().remove_child(self)
	tree.root.add_child(self)
	tree.current_scene = null
	# As boot does (M2-ARC-03): the resident shaders first. Without them the zone's threaded loads and the resident
	# loads race on the shared character and water shaders, and a zone (Haluna, Oruvel) fails to load: a black run.
	var warm := GraphicsRuntime.warm_resident_shaders(tree.root)
	while warm != null and is_instance_valid(warm) and warm.is_running():
		await tree.process_frame
	if not SceneRouter.world_return.go_to(_location, _spawn):
		push_error("CutsceneFrames: could not travel to %s/%s" % [_location, _spawn])
		tree.quit(2)
		return
	_started = true


func _process(delta: float) -> void:
	if not _started:
		return
	_elapsed += delta
	if not _tour.is_empty() and _elapsed >= float(_tour[0][1]):
		var stop: Array = _tour.pop_front()
		var scene := get_tree().current_scene
		if scene != null and scene.has_method(&"place_at"):
			scene.call(&"place_at", stop[0])
			_lines.append("%06.1f TOUR %s" % [_elapsed, stop[0]])
	_watch_line()
	_watch_choices(delta)
	_watch_cut()
	if _elapsed >= _next_frame:
		_next_frame += _every
		var img := get_viewport().get_texture().get_image()
		img.save_png("%s/f_%04d.png" % [_out, int(round(_elapsed * FRAME_NAME_SCALE))])
		if _log_player:
			_lines.append("%06.1f POS %s" % [_elapsed, _positions()])
	if _elapsed >= _max_sec:
		var f := FileAccess.open("%s/lines.txt" % _out, FileAccess.WRITE)
		if f != null:
			f.store_string("\n".join(_lines) + "\n")
		get_tree().quit(0)


## --cut-frames: writes every frame for a while after the camera jumps (a cut).
func _watch_cut() -> void:
	if _no_taa:
		get_viewport().use_taa = false
	if _cut_frames <= 0:
		return
	var cam := get_viewport().get_camera_3d()
	if cam != null:
		if _last_cam != Vector3.INF and _last_cam.distance_to(cam.global_position) > CUT_JUMP_M:
			_cut_left = _cut_frames
		_last_cam = cam.global_position
	if _cut_left > 0:
		_cut_left -= 1
		var img := get_viewport().get_texture().get_image()
		img.save_png("%s/cut_%06d.png" % [_out, int(round(_elapsed * CUT_NAME_SCALE))])


## "player=<pos> visible=<bool> cam=<pos>" for --log-player.
func _positions() -> String:
	var found := get_tree().root.find_children("*", "FieldController", true, false)
	var player := found[0] as Node3D if not found.is_empty() else null
	var cam := player.get_viewport().get_camera_3d() if player != null else null
	return (
		"player=%s visible=%s cam=%s"
		% [
			player.global_position if player != null else null,
			player.is_visible_in_tree() if player != null else null,
			cam.global_position if cam != null else null,
		]
	)


func _watch_line() -> void:
	for box: Node in get_tree().root.find_children("*", "DialogueBox", true, false):
		var b := box as DialogueBox
		if b.visible and b.shown_text() != "" and b.shown_text() != _last_line and not b.is_revealing():
			_last_line = b.shown_text()
			_lines.append("%06.1f %s: %s" % [_elapsed, b.speaker_name(), _last_line])


func _watch_choices(delta: float) -> void:
	for node: Node in get_tree().root.find_children("*", "CutsceneChoices", true, false):
		var c := node as CutsceneChoices
		if c.is_visible_in_tree() and not c.option_texts().is_empty():
			_choice_wait += delta
			if _choice_wait >= CHOICE_HOLD_SEC:
				_choice_wait = 0.0
				_lines.append("%06.1f CHOICE %d of %s" % [_elapsed, _choice, c.option_texts()])
				c.pick(mini(_choice, c.option_texts().size() - 1))
			return
	_choice_wait = 0.0

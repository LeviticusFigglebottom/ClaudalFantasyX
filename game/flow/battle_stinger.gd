class_name BattleStinger
extends CanvasLayer
## The encounter stinger (M2-BPR-05; docs/kb/tech/battle_presentation.md "Encounter transition"): the
## short beat in the field between a battle being asked for and SceneRouter's opaque fade. A tide line
## of dark water rises from the bottom edge with a thin foam crest (battle_tideline.gdshader), the field
## above it dims and greys, the player stops, it holds, and only then does the router start its change.
## The router's fade and hidden build are untouched, so ADR 0029's entry and hidden-frame budgets
## (measured from change_scene()) never include it.
##
## Every time, colour and shape is game/data/flow/battle_transition.json. Reduced motion (UiSettings)
## replaces the rise and the ripple with a plain cross-fade to the deep colour. Nothing flashes: the
## foam crest stays under battle_vfx's flash cap (tested).
##
## BattleRequest.submit awaits play() (the one hook); tests drive make() + advance() by hand.
##
## A lead-in bark (Lead's intro audit): an encounter with a `barks.rows` entry shows its line over the water while
## the tide rises, holds hold_extra_sec longer so it can be read, and announces it on
## EventBus.dialogue_event(BARK_EVENT, [encounter, line_key, speaker_key]) for audio (a voice line or a stinger).

signal finished

const DATA_PATH := "res://game/data/flow/battle_transition.json"
const ROOT_KEY := "battle_transition"
const KEY_REDUCED := "reduced_motion"
const ROUTER_PATH := ^"SceneRouter"
const PLAYER_GROUP := &"player"
## Data keys passed to the shader as float uniforms of the same name.
const FLOAT_UNIFORMS: Array[String] = [
	"crest",
	"wave_amplitude",
	"wave_frequency",
	"wave_speed",
	"wave_detail",
	"wave_detail_weight",
	"foam_width",
	"foam_alpha",
	"water_alpha_top",
	"water_alpha",
	"refract",
	"refract_frequency",
	"dim",
	"desaturate",
]
## Data keys passed to the shader as colour uniforms of the same name (palette swatches).
const COLOR_UNIFORMS: Array[String] = ["water_deep", "water_edge", "foam"]
const U_PROGRESS := &"progress"
const KEY_BARKS := "barks"
const BARK_EVENT := &"battle_bark"
const U_PHASE := &"phase"

## The battle_transition block (load_config()).
var cfg: Dictionary = {}
var reduced_motion := false
## Seconds since the stinger started.
var elapsed := 0.0
## True once the rise and the hold are over (finished has fired).
var done := false
## The encounter's lead-in bark row ({} when it has none).
var bark: Dictionary = {}

var _rect: ColorRect
var _mat: ShaderMaterial
var _player: FieldController
var _player_input_was := true


## The battle_transition block ({} with an error when it is missing).
static func load_config(path: String = DATA_PATH) -> Dictionary:
	var parsed: Variant = null
	if FileAccess.file_exists(path):
		parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get(ROOT_KEY)) != TYPE_DICTIONARY:
		push_error("BattleStinger: could not read '%s' from %s" % [ROOT_KEY, path])
		return {}
	return (parsed as Dictionary)[ROOT_KEY] as Dictionary


## How long the stinger plays before the router's change starts: rise + hold, or cross-fade + hold.
static func duration(c: Dictionary, reduced: bool, with_bark: Dictionary = {}) -> float:
	var extra := float(with_bark.get("hold_extra_sec", 0.0))
	if reduced:
		var rm := c.get(KEY_REDUCED, {}) as Dictionary
		return float(rm.get("crossfade_sec", 0.0)) + float(rm.get("hold_sec", 0.0)) + extra
	return float(c.get("rise_sec", 0.0)) + float(c.get("hold_sec", 0.0)) + extra


## Encounter `encounter`'s lead-in bark ({line_key, speaker_key, hold_extra_sec}; {} for none).
static func bark_for(c: Dictionary, encounter: StringName) -> Dictionary:
	var rows := (c.get(KEY_BARKS, {}) as Dictionary).get("rows", {}) as Dictionary
	return rows.get(String(encounter), {}) as Dictionary


## The tide line's eased rise at `t` seconds, 0..1 (1 through the hold).
static func rise_at(c: Dictionary, t: float) -> float:
	var rise := float(c.get("rise_sec", 0.0))
	var x := 1.0 if rise <= 0.0 else clampf(t / rise, 0.0, 1.0)
	return ease(x, float(c.get("rise_ease", 1.0)))


## The reduced-motion cross-fade's overlay alpha at `t` seconds (linear, then held).
static func crossfade_alpha_at(c: Dictionary, t: float) -> float:
	var rm := c.get(KEY_REDUCED, {}) as Dictionary
	var sec := float(rm.get("crossfade_sec", 0.0))
	var x := 1.0 if sec <= 0.0 else clampf(t / sec, 0.0, 1.0)
	return x * float(rm.get("alpha", 0.0))


## A stinger ready to add to the tree (`c` empty = the data file).
static func make(reduced: bool, c: Dictionary = {}, encounter: StringName = &"") -> BattleStinger:
	var s := BattleStinger.new()
	s.name = "BattleStinger"
	s.cfg = c if not c.is_empty() else load_config()
	s.reduced_motion = reduced
	s.bark = bark_for(s.cfg, encounter)
	s.set_meta(&"encounter", encounter)
	return s


## Plays the stinger over the current scene and returns when it is done (await it). Returns at once
## when there is nothing to play over or the screen is already covered: no tree, the router busy (its
## fade is up or coming), or the data turned off. The stinger stays on screen until the router
## unloads the field under its opaque fade (it is a child of the current scene, and goes on the
## router's scene_swapping when it had to sit on the root).
static func play(tree: SceneTree = null, encounter: StringName = &"") -> void:
	var t := tree if tree != null else Engine.get_main_loop() as SceneTree
	if t == null or t.root == null:
		return
	var router := t.root.get_node_or_null(ROUTER_PATH)
	if router != null and bool(router.call(&"is_busy")):
		return
	var c := load_config()
	if c.is_empty() or not bool(c.get("enabled", false)):
		return
	var s := make(UiSettings.shared().reduced_motion(), c, encounter)
	var host: Node = t.current_scene if t.current_scene != null else t.root
	s.freeze_player(t)
	if router != null:
		router.connect(&"scene_swapping", s._on_scene_swapping, CONNECT_ONE_SHOT)
	host.add_child.call_deferred(s)
	await s.finished


func _ready() -> void:
	layer = int(cfg.get("layer", layer))
	_rect = ColorRect.new()
	_rect.name = "Tide"
	_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	if reduced_motion:
		var col := Color(str(cfg.get(str((cfg.get(KEY_REDUCED, {}) as Dictionary).get("color", "")), "")))
		col.a = 0.0
		_rect.color = col
	else:
		_mat = ShaderMaterial.new()
		_mat.shader = load(str(cfg.get("shader", ""))) as Shader
		for key in FLOAT_UNIFORMS:
			_mat.set_shader_parameter(StringName(key), float(cfg.get(key, 0.0)))
		for key in COLOR_UNIFORMS:
			_mat.set_shader_parameter(StringName(key), Color(str(cfg.get(key, ""))))
		_rect.material = _mat
	add_child(_rect)
	if not bark.is_empty():
		_show_bark()
	advance(0.0)


func _process(delta: float) -> void:
	advance(delta)


## Moves the stinger on by `delta` seconds (tests call it directly); fires finished once at the end.
func advance(delta: float) -> void:
	elapsed += delta
	if _mat != null:
		_mat.set_shader_parameter(U_PROGRESS, rise_at(cfg, elapsed))
		_mat.set_shader_parameter(U_PHASE, elapsed)
	elif _rect != null:
		_rect.color.a = crossfade_alpha_at(cfg, elapsed)
	if not done and elapsed >= duration(cfg, reduced_motion, bark):
		done = true
		finished.emit()


## The bark's line over the water (the UI theme's dialogue look), announced for audio.
func _show_bark() -> void:
	var b := cfg.get(KEY_BARKS, {}) as Dictionary
	var label := Label.new()
	label.name = "Bark"
	label.theme = load(str(b.get("theme", ""))) as Theme
	label.text = tr("BARK_LINE_FMT").format(
		{"name": tr(str(bark.get("speaker_key", ""))), "line": tr(str(bark.get("line_key", "")))}
	)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	label.offset_top = -float(b.get("bottom_px", 0.0))
	label.offset_bottom = -float(b.get("bottom_px", 0.0)) + float(b.get("height_px", 0.0))
	add_child(label)
	var bus := get_node_or_null(^"/root/EventBus")
	if bus != null:
		bus.emit_signal(
			&"dialogue_event", BARK_EVENT, [get_meta(&"encounter", &""), bark["line_key"], bark.get("speaker_key", "")]
		)


## The bark's label (null when the encounter has none, or before _ready).
func bark_label() -> Label:
	return get_node_or_null(^"Bark") as Label


## How far it has covered the field: the rise (0..1), or under reduced motion the overlay alpha.
func coverage() -> float:
	return crossfade_alpha_at(cfg, elapsed) if reduced_motion else rise_at(cfg, elapsed)


## The material drawing the tide line (null under reduced motion, or before _ready).
func material_in_use() -> ShaderMaterial:
	return _mat


## The overlay rect (the plain cross-fade under reduced motion).
func overlay() -> ColorRect:
	return _rect


## Stops the field player where they stand for the stinger (the field freezes); handed back if the
## stinger leaves the tree with the player still there (a change that never came).
func freeze_player(tree: SceneTree) -> void:
	var p := tree.get_first_node_in_group(PLAYER_GROUP) as FieldController if tree != null else null
	if p == null:
		return
	_player = p
	_player_input_was = p.accepts_input
	p.accepts_input = false
	p.velocity = Vector3.ZERO


func _exit_tree() -> void:
	if is_instance_valid(_player) and _player.is_inside_tree() and not _player.is_queued_for_deletion():
		_player.accepts_input = _player_input_was
	_player = null


func _on_scene_swapping(_scene_path: String) -> void:
	if not is_queued_for_deletion():
		queue_free()

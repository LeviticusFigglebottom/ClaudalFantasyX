extends TestCase
## ADR 0042 §4 (Act I scene changes keep their hidden frames covered): every scene change in the game goes
## through SceneRouter, whose swap and hidden frames sit under its opaque fade, and nothing draws above that
## fade. The fade's alpha is recorded per swap (SceneRouter.judge_cover: `covered`); the scene-swap probe
## test checks it on a real change, and tools/loading/act1_swap_sweep.py on every Act I zone and a battle.

const GAME_DIR := "res://game"
const DATA_DIR := "res://game/data"
## Only the router itself and the debug probes may change scene directly.
const DIRECT_CHANGE_ALLOWED: Array[String] = ["res://game/core/scene_router.gd", "res://game/core/debug/"]
const DIRECT_CHANGE_CALLS: Array[String] = [
	"change_scene_to_file(",
	"change_scene_to_packed(",
	"change_scene_to_node(",
	"unload_current_scene(",
]
## Data keys that name a CanvasLayer's layer.
const LAYER_KEYS: Array[String] = ["canvas_layer", "layer"]
const TSCN_CANVAS_LAYER := 'type="CanvasLayer"'
const TSCN_LAYER_PREFIX := "layer = "


func test_a_swap_counts_as_covered_only_when_every_hidden_frame_is_opaque() -> void:
	var stats := {}
	var opaque: Array[float] = [1.0, 1.0, 1.0, 1.0, 1.0]
	assert_true(SceneRouter.judge_cover(stats, opaque).is_empty())
	assert_true(bool(stats["covered"]))
	assert_eq(float(stats["cover_alpha_min"]), 1.0)
	var lifting: Array[float] = [1.0, 1.0, 0.8, 1.0, 1.0]
	var warnings := SceneRouter.judge_cover(stats, lifting)
	assert_false(bool(stats["covered"]), "a frame under a lifting fade is not covered")
	assert_eq(float(stats["cover_alpha_min"]), 0.8)
	assert_eq(warnings.size(), 1)
	SceneRouter.judge_cover(stats, [] as Array[float])
	assert_false(bool(stats["covered"]), "no samples: not proven covered")


func test_the_router_is_clear_at_rest() -> void:
	assert_false(SceneRouter.is_busy())
	assert_eq(SceneRouter.fade_alpha(), 0.0, "no change running: the fade is clear")


func test_no_game_code_changes_scene_around_the_router() -> void:
	var files: Array[String] = []
	_collect(GAME_DIR, ".gd", files)
	assert_true(files.size() > 100, "the scan found the game's scripts")
	for path in files:
		if _allowed(path):
			continue
		var text := FileAccess.get_file_as_string(path)
		for call in DIRECT_CHANGE_CALLS:
			assert_false(
				text.contains(call), "%s calls %s: change scene through SceneRouter/FlowRouting" % [path, call]
			)


func test_nothing_draws_above_the_fade() -> void:
	var fade := SceneRouter.FADE_LAYER
	var scenes: Array[String] = []
	_collect(GAME_DIR, ".tscn", scenes)
	for path in scenes:
		var in_canvas_layer := false
		for line in FileAccess.get_file_as_string(path).split("\n"):
			if line.begins_with("["):
				in_canvas_layer = line.contains(TSCN_CANVAS_LAYER)
			elif in_canvas_layer and line.begins_with(TSCN_LAYER_PREFIX):
				var layer := line.trim_prefix(TSCN_LAYER_PREFIX).to_int()
				assert_true(layer < fade, "%s: a CanvasLayer at %d draws over the fade (%d)" % [path, layer, fade])
	var tables: Array[String] = []
	_collect(DATA_DIR, ".json", tables)
	for path in tables:
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
		for found: Array in _layer_values(parsed, path):
			assert_true(int(found[1]) < fade, "%s: %s draws over the fade (%d)" % [found[0], found[1], fade])


static func _allowed(path: String) -> bool:
	for prefix in DIRECT_CHANGE_ALLOWED:
		if path.begins_with(prefix):
			return true
	return false


static func _collect(dir_path: String, ext: String, out: Array[String]) -> void:
	for f in DirAccess.get_files_at(dir_path):
		if f.ends_with(ext):
			out.append(dir_path.path_join(f))
	for d in DirAccess.get_directories_at(dir_path):
		_collect(dir_path.path_join(d), ext, out)


## [[where, value]] for every LAYER_KEYS number in a parsed JSON table.
static func _layer_values(v: Variant, where: String) -> Array:
	var out: Array = []
	if v is Dictionary:
		for k: Variant in v:
			var item: Variant = (v as Dictionary)[k]
			if LAYER_KEYS.has(str(k)) and (item is float or item is int):
				out.append(["%s.%s" % [where, k], int(item)])
			else:
				out.append_array(_layer_values(item, "%s.%s" % [where, k]))
	elif v is Array:
		for i in (v as Array).size():
			out.append_array(_layer_values((v as Array)[i], "%s[%d]" % [where, i]))
	return out

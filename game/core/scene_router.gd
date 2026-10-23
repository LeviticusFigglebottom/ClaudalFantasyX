extends Node
## Autoload "SceneRouter": async scene loading behind a fade, with a shader-prewarm hook.
##
## Public API (stable since M0): change_scene(path), is_busy(), signal prewarm_requested(path), FADE_SEC.
## M1-ARC-06: change_scene(path, spawn) also places the player on Spawns/<spawn> once the new scene
## is in the tree (still under the opaque fade), and `world_return` (a WorldReturn child) returns
## the party to its respawn point on EventBus.game_loaded once boot.gd arms it.
## Added in the M1-RND-06 fix: signal swap_measured(stats) and last_swap_stats (see below).
## M1-ARC-15: when the new scene's root is ready (main thread, in the tree, before its first draw),
## the player's graphics settings are applied to it (attach_graphics_hook; only after boot armed it).
##
## SPEC §4.2 allows no frame over 50 ms in a transition, so the expensive steps are kept out of the
## frame that shows the new scene (docs/kb/tech/architecture.md, "Scene-swap hitch"):
##   1. The threaded load runs while the screen fades out. Meanwhile, the theme's fonts are
##      rasterized a few (font, size) pairs per frame under the opaque fade (FontWarmer), because
##      first-use glyph rasterization was the largest CPU cost of a cold swap.
##   2. prewarm_requested fires before the swap, so the ShaderPrewarm stage is built (scene load,
##      material load, shader front-end compile) in a frame of its own. The stage then feeds its draws
##      in a few per frame (M1-RND-15); the router waits while it is staging, up to
##      PREWARM_WAIT_MAX_FRAMES, so pipelines compile in small slices under the opaque fade.
##   3. The PackedScene is instantiated on a WorkerThreadPool thread (the node is not in the tree
##      yet, which Godot 4 allows), never on the main thread.
##   4. The old scene is unloaded one frame before the new one is added, so freeing it and
##      entering the new scene's _ready never share a frame.
## Each swap records its phase costs and frame times in last_swap_stats, emits swap_measured, and
## warns when the swap frame exceeds SWAP_BUDGET_MS.

signal prewarm_requested(scene_path: String)
## Emitted after each successful swap with the same dictionary stored in last_swap_stats.
signal swap_measured(stats: Dictionary)

const FADE_SEC := 0.35
const FADE_LAYER := 128
## SPEC §4.2: no hitch over 50 ms during transitions.
const SWAP_BUDGET_MS := 50.0
## Frames measured after the new scene is handed to the tree (its _ready and first draw land here).
const MEASURE_FRAMES := 4
## Upper bound on frames spent waiting for a time-sliced ShaderPrewarm stage (M1-RND-15).
const PREWARM_WAIT_MAX_FRAMES := 120
const USEC_PER_MSEC := 1000.0
const LOG_PREFIX := "SceneRouter"

## Tuning switches (all on in the game; tests and the profiler flip them to compare).
var instantiate_on_thread := true
var warm_fonts := true
var split_swap := true
## Last swap: {scene_path, instantiate_ms, instantiated_on_thread, unload_ms, prewarm_ms, fonts_warmed,
## font_warm_ms, frame_ms: Array[float] (MEASURE_FRAMES frames from the swap), max_frame_ms,
## budget_ms, over_budget}.
var last_swap_stats: Dictionary = {}
## Return-to-world on load (M1-ARC-06). Disabled until boot.gd sets world_return.enabled.
var world_return: WorldReturn

var _fade_layer: CanvasLayer
var _fade_rect: ColorRect
var _busy := false
var _font_warmer: FontWarmer
var _fonts_warm := false


func _ready() -> void:
	_fade_layer = CanvasLayer.new()
	_fade_layer.layer = FADE_LAYER
	add_child(_fade_layer)
	_fade_rect = ColorRect.new()
	_fade_rect.color = Color(0, 0, 0, 0)
	_fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_fade_layer.add_child(_fade_rect)
	ShaderPrewarm.install(self)
	world_return = WorldReturn.new()
	world_return.name = "WorldReturn"
	add_child(world_return)


func is_busy() -> bool:
	return _busy


## `spawn` (optional): a marker under the new scene's Spawns node to place the player on
## (WorldReturn.place_player) before the fade lifts.
func change_scene(scene_path: String, spawn: StringName = &"") -> void:
	if _busy:
		push_warning("SceneRouter: change already in progress, ignoring %s" % scene_path)
		return
	_busy = true
	var stats := {"scene_path": scene_path, "budget_ms": SWAP_BUDGET_MS}
	ResourceLoader.load_threaded_request(scene_path)
	_start_font_warm(stats)
	await _fade_to(1.0)
	while ResourceLoader.load_threaded_get_status(scene_path) == ResourceLoader.THREAD_LOAD_IN_PROGRESS:
		await get_tree().process_frame
	var packed := ResourceLoader.load_threaded_get(scene_path) as PackedScene
	if packed == null:
		push_error("SceneRouter: failed to load %s" % scene_path)
	else:
		await _swap(packed, scene_path, stats, spawn)
	await _fade_to(0.0)
	_busy = false


## With split_swap off this reproduces the M0 router (prewarm, instantiate, free and add in one
## frame), which the profiler uses as the "before" case.
func _swap(packed: PackedScene, scene_path: String, stats: Dictionary, spawn: StringName = &"") -> void:
	while _font_warmer != null and not _font_warmer.done:
		await get_tree().process_frame
	var t := Time.get_ticks_usec()
	var swap_frame_start := t
	prewarm_requested.emit(scene_path)
	stats["prewarm_ms"] = _ms_since(t)
	if split_swap:
		await get_tree().process_frame
	var node := await _instantiate(packed, stats)
	if node == null:
		push_error("SceneRouter: failed to instantiate %s" % scene_path)
		return
	var waited := 0
	while waited < PREWARM_WAIT_MAX_FRAMES and ShaderPrewarm.is_staging_under(self):
		await get_tree().process_frame
		waited += 1
	stats["prewarm_wait_frames"] = waited
	if split_swap:
		if get_tree().current_scene != null:
			t = Time.get_ticks_usec()
			get_tree().unload_current_scene()
			await get_tree().process_frame
			stats["unload_ms"] = _ms_since(t)
		await get_tree().process_frame
		swap_frame_start = Time.get_ticks_usec()
	var frames: Array[float] = []
	t = swap_frame_start
	# Zone render globals (M1-RND-15): the new zone starts from the project defaults, so one that never
	# writes them does not inherit the last zone's night sea-glow or tide line.
	GlimmerField.clear_scene_sea_glow()
	WaterSurface.clear_water_level()
	attach_graphics_hook(node, stats)
	get_tree().change_scene_to_node(node)
	for i in MEASURE_FRAMES:
		await get_tree().process_frame
		var now := Time.get_ticks_usec()
		frames.append((now - t) / USEC_PER_MSEC)
		t = now
		if i == 0:
			if spawn != &"" and node.is_inside_tree():
				WorldReturn.place_player(node, spawn)
			EventBus.scene_changed.emit(scene_path)
	_record(stats, frames)


## M1-ARC-15: applies the graphics settings' per-scene part to `node` when its root is ready, i.e. in
## the tree, on the main thread, after every child's _ready (HalunaZone has finished its worker-thread
## prebuild by then) and before the first frame draws it. No-op until boot arms GraphicsRuntime.
## Records the operation count in stats["graphics_ops"].
func attach_graphics_hook(node: Node, stats: Dictionary) -> void:
	node.ready.connect(func() -> void: stats["graphics_ops"] = GraphicsRuntime.on_scene_entered(node), CONNECT_ONE_SHOT)


## Instantiates off the main thread when allowed; falls back to the main thread otherwise.
func _instantiate(packed: PackedScene, stats: Dictionary) -> Node:
	var t := Time.get_ticks_usec()
	var holder: Array[Node] = []
	stats["instantiated_on_thread"] = instantiate_on_thread
	if instantiate_on_thread:
		var task := WorkerThreadPool.add_task(func() -> void: holder.append(packed.instantiate()))
		while not WorkerThreadPool.is_task_completed(task):
			await get_tree().process_frame
		WorkerThreadPool.wait_for_task_completion(task)
	else:
		holder.append(packed.instantiate())
	stats["instantiate_ms"] = _ms_since(t)
	return holder[0] if not holder.is_empty() else null


func _record(stats: Dictionary, frames: Array[float]) -> void:
	var worst := 0.0
	for f in frames:
		worst = maxf(worst, f)
	stats["frame_ms"] = frames
	stats["max_frame_ms"] = worst
	stats["over_budget"] = worst > SWAP_BUDGET_MS
	stats["fonts_warmed"] = _fonts_warm
	last_swap_stats = stats
	if worst > SWAP_BUDGET_MS:
		push_warning("%s: swap frame %.1f ms over the %.0f ms budget: %s" % [LOG_PREFIX, worst, SWAP_BUDGET_MS, stats])
	swap_measured.emit(stats)


## Starts rasterizing the project theme's fonts under the fade (once per run; spread over frames).
func _start_font_warm(stats: Dictionary) -> void:
	if not warm_fonts or _fonts_warm or _font_warmer != null:
		return
	_font_warmer = FontWarmer.new()
	_font_warmer.pairs = FontWarmer.theme_pairs(ThemeDB.get_project_theme())
	_font_warmer.finished.connect(_on_fonts_warm.bind(stats))
	_fade_layer.add_child(_font_warmer)
	_fade_layer.move_child(_font_warmer, 0)


func _on_fonts_warm(total_ms: float, stats: Dictionary) -> void:
	stats["font_warm_ms"] = total_ms
	_fonts_warm = true
	_font_warmer.queue_free()
	_font_warmer = null


func _fade_to(alpha: float) -> void:
	var tween := create_tween()
	tween.tween_property(_fade_rect, "color:a", alpha, FADE_SEC)
	await tween.finished


static func _ms_since(t_usec: int) -> float:
	return (Time.get_ticks_usec() - t_usec) / USEC_PER_MSEC


## Draws every (font, size, outline) the project theme uses with a fixed character set, in small
## units (one CHUNK_CHARS slice of one pair) until FRAME_BUDGET_USEC is spent each frame, so the
## TextServer glyph cache is filled before a scene needs it. It sits under the fade rect with zero
## alpha, so nothing it draws is ever seen. MSDF fonts are skipped: msdfgen costs ~7 ms per glyph on
## this CPU, far too slow to warm inside a transition (see architecture.md, "Scene-swap hitch").
class FontWarmer:
	extends Control

	signal finished(total_ms: float)

	## Printable ASCII plus the typographic marks the loc tables use.
	const CHARSET := (
		" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
		+ "\u2026\u2014\u2013\u2018\u2019\u201C\u201D\u00B7\u00D7\u00E9"
	)
	const CHUNK_CHARS := 16
	const FRAME_BUDGET_USEC := 4000
	const OUTLINE_CONSTANT := "outline_size"

	var pairs: Array[Dictionary] = []
	var done := false
	var _units: Array[Dictionary] = []
	var _next := 0
	var _spent_usec := 0

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE
		self_modulate = Color(1, 1, 1, 0)
		_units = units_for(pairs)
		if _units.is_empty():
			_finish.call_deferred()

	func _process(_delta: float) -> void:
		if not done:
			queue_redraw()

	func _draw() -> void:
		var start := Time.get_ticks_usec()
		while _next < _units.size() and Time.get_ticks_usec() - start < FRAME_BUDGET_USEC:
			var u := _units[_next]
			var font := u["font"] as Font
			var size := int(u["size"])
			var text := String(u["text"])
			var at := Vector2(0, size)
			draw_string(font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size)
			if int(u["outline"]) > 0:
				draw_string_outline(font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, int(u["outline"]))
			_next += 1
		_spent_usec += Time.get_ticks_usec() - start
		if _next >= _units.size() and not done:
			_finish.call_deferred()

	func _finish() -> void:
		if done:
			return
		done = true
		finished.emit(_spent_usec / USEC_PER_MSEC)

	## Splits each pair into CHARSET slices so no single unit can blow the frame budget.
	static func units_for(warm_pairs: Array[Dictionary]) -> Array[Dictionary]:
		var out: Array[Dictionary] = []
		for p in warm_pairs:
			for i in range(0, CHARSET.length(), CHUNK_CHARS):
				var u := p.duplicate()
				u["text"] = CHARSET.substr(i, CHUNK_CHARS)
				out.append(u)
		return out

	## Every distinct non-MSDF (font, size, outline) a theme can produce: each type's fonts paired
	## with that type's sizes and outline constant, plus the theme defaults. The engine fallback font
	## is included only when the theme has no default font (themed Controls never reach it).
	static func theme_pairs(theme: Theme) -> Array[Dictionary]:
		var out: Array[Dictionary] = []
		var seen: Dictionary = {}
		if theme == null or not theme.has_default_font():
			_add(out, seen, ThemeDB.fallback_font, ThemeDB.fallback_font_size, 0)
		if theme == null:
			return out
		var default_font: Font = theme.default_font if theme.has_default_font() else ThemeDB.fallback_font
		var default_size := theme.default_font_size if theme.has_default_font_size() else ThemeDB.fallback_font_size
		_add(out, seen, default_font, default_size, 0)
		for type in theme.get_type_list():
			var fonts: Array[Font] = []
			for fname in theme.get_font_list(type):
				fonts.append(theme.get_font(fname, type))
			if fonts.is_empty():
				fonts.append(default_font)
			var sizes: Array[int] = []
			for sname in theme.get_font_size_list(type):
				sizes.append(theme.get_font_size(sname, type))
			if sizes.is_empty():
				sizes.append(default_size)
			var outline := (
				theme.get_constant(OUTLINE_CONSTANT, type) if theme.has_constant(OUTLINE_CONSTANT, type) else 0
			)
			for f in fonts:
				for sz in sizes:
					_add(out, seen, f, sz, outline)
		return out

	## True for a font whose glyphs are multichannel signed distance fields (directly or via a
	## FontVariation chain).
	static func is_msdf(font: Font) -> bool:
		var f := font
		while f is FontVariation:
			f = (f as FontVariation).base_font
		return f is FontFile and (f as FontFile).multichannel_signed_distance_field

	static func _add(out: Array[Dictionary], seen: Dictionary, font: Font, size: int, outline: int) -> void:
		if font == null or size <= 0 or is_msdf(font):
			return
		var key := "%d:%d:%d" % [font.get_instance_id(), size, outline]
		if seen.has(key):
			return
		seen[key] = true
		out.append({"font": font, "size": size, "outline": outline})

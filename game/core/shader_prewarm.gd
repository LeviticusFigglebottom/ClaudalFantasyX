class_name ShaderPrewarm
extends Node
## Shader-cache warmup (SPEC §4.2 "no hitch over 50 ms", task M1-RND-06).
##
## During a scene transition, draws one quad (or particle system, sky, fog volume, canvas rect)
## per registered material inside an off-screen SubViewport for a few frames so the GPU pipelines
## are compiled before the new scene shows them, then frees itself. While alive it measures frame
## times; when done it emits `finished(stats)` and logs the max frame time of the transition.
##
## Registry and tuning: game/data/settings/prewarm_materials.json. Each entry is
## {"path": res path of a Material or Shader, "scenes": [scene paths] (empty = every transition)},
## plus optional keys (M1-RND-07) so the stage compiles the pipeline the zone really uses:
##   "mesh": a Mesh resource, or a scene (.glb/.tscn) whose first MeshInstance3D (or "mesh_node")
##           supplies it: the real vertex format (vertex colours, UV2, no tangents...)
##   "multimesh": true  draw it through a MultiMeshInstance3D (colours and custom data on)
##   "draw_material": for a particles material, the draw pass's material (billboard pipelines)
## The stage viewport copies the game viewport's AA (TAA, MSAA, screen-space AA, 3D scaling mode),
## so motion-vector and upscaler pipeline variants are compiled too. A cutscene that will push a
## scoped graphics override (M1-RND-16) sets `viewport_state` to GraphicsSettings.override_state(...)
## first (or uses spawn_with_state), so the stage compiles the pipeline the override will select.
## With "scene_materials": true the incoming scene itself is instanced off-tree (no _ready runs) and
## every material on its geometry is drawn on that geometry's own mesh (or MultiMesh), plus its
## WorldEnvironment sky: inline sub-resource materials and real vertex formats need no registry
## entry. Materials scenes build at runtime in _ready still need their registry entries.
##
## Time slicing (M1-RND-15, SPEC §4.2 "no hitch over 50 ms during battle transitions"): the stage is
## built at start but its draws enter the viewport at most "materials_per_frame" per frame (0 = all at
## once), because a pipeline compiles on the first frame that draws it and staging everything in one
## frame cost 121-150 ms on an RX 9070 XT. When a frame comes in over "slice_budget_ms" the batch is
## halved (never below 1), so slower cards self-tune. The stage is cleared "frames_to_render" frames
## after the last batch went in. While staging, the stage holds its parent's swap (hold_swap /
## release_swap, M1-RND-23), so a SceneRouter parent waits before showing the new scene; any other
## parent (a cutscene's spawn_with_state) is not held.
##
## Hidden frames (ADR 0029, M1-RND-27): a transition behind the router's fade, and the boot run under
## the boot screen, count as loading time: no single frame over 1 s.
## - Boot bring-up: the process's first 3D render of a stage with TAA and an upscaler compiles all of
##   their pipelines in one frame (0.96-1.2 s cold on an RX 9070 XT). A boot run draws its stage plain
##   first and turns the game viewport's AA and scaling on one feature a frame before any draw is staged.
## - Resident entries load in their batch, as transition entries do (a load compiles the shader on the
##   CPU), and are held from there, not all in the spawn frame.
## - The Undertow's body (registry "compute_twin"): on a tier that marches it in compute (M2-RND-01,
##   ADR 0028) the spatial shader never draws, so its compute pipeline is created instead
##   (UndertowBodyEffect.warm_pipeline, on the render thread).
## - Scene harvest reads the incoming scene's SceneState (no instance, no nodes), and the SceneStates of
##   the scenes it instances.
## - Threaded loading (ResourceLoader.load_threaded_request) is rejected: it crashed Godot 4.6.3 on Haluna
##   in 3 of 6 runs (docs/kb/qa/gpu/2026-10-24-rnd-22-prewarm.md).
## - materials_per_frame stays 2 for Undertow-class scenes: measured cold on the storm scene (High), 2
##   gives a worst frame of 79-127 ms over 15 frames and 12 gives 133-142 ms over 6. Both are far under the
##   1 s limit; 2 keeps the worst frame lower (docs/kb/qa/gpu/2026-10-24-rnd-27-prewarm.md).
##
## Hook-up (autoload-free): `ShaderPrewarm.install(SceneRouter)` connects to
## SceneRouter.prewarm_requested and spawns this scene as a child of the router (which survives the
## scene change). Headless-safe: the dummy renderer simply draws nothing.

signal finished(stats: Dictionary)

const SCENE_PATH := "res://game/core/shader_prewarm.tscn"
const REGISTRY_PATH := "res://game/data/settings/prewarm_materials.json"
const ROUTER_SIGNAL := &"prewarm_requested"
const HOOK_META := &"shader_prewarm_hook"
const HOLD_METHOD := &"hold_swap"
const RELEASE_METHOD := &"release_swap"
const MSEC_PER_SEC := 1000.0
const USEC_PER_MSEC := 1000.0
const LOG_PREFIX := "ShaderPrewarm"
const MODE_UNSUPPORTED := -1
## How deep the scene harvest follows instanced scenes (M1-RND-27).
const HARVEST_MAX_DEPTH := 8
## Viewport features a boot run turns on one a frame before it stages anything (M1-RND-27), in order.
const BRING_UP_PROPS: Array[StringName] = [&"use_taa", &"scaling_3d_mode", &"msaa_3d", &"screen_space_aa"]
## Their values for the plain first frame.
const BRING_UP_PLAIN := {
	&"use_taa": false,
	&"scaling_3d_mode": Viewport.SCALING_3D_MODE_BILINEAR,
	&"msaa_3d": Viewport.MSAA_DISABLED,
	&"screen_space_aa": Viewport.SCREEN_SPACE_AA_DISABLED,
}

## Shaders and materials loaded at boot and held for the session (M1-RND-22, registry "resident"): their
## load compiles the shader, 75-220 ms each, so it happens once under the boot screen instead of in a
## transition. They are held by a node under the tree root (RESIDENT_HOLDER), not a static array: the
## tree frees it on every exit, a quit in the middle of a warm-up included, so nothing is still in use at
## exit (a static array outlived Godot's exit check: 225 resources on a headless boot, M1-RND-29 fix).
const RESIDENT_HOLDER := "ShaderPrewarmResident"
## A holder added (deferred) but not yet in the tree; a plain weak handle (is_instance_valid-checked).
static var _pending_holder: Node = null

var registry_path: String = REGISTRY_PATH
var config: Dictionary = {}
var scene_path: String = ""
var stats: Dictionary = {}
## Viewport properties laid over the game viewport's when the stage copies them (match_viewport):
## the state a planned GraphicsSettings override will set (M1-RND-16). Empty: the game's own.
var viewport_state: Dictionary = {}
## The preset whose tier variants are staged (M1-RND-22, registry "preset_tier"). "" = the player's
## (GraphicsRuntime); a tool or test may set it before start().
var preset_id: String = ""
## Boot run (M1-RND-22): stage every "resident" entry, whatever its scenes, and nothing else.
var resident_only := false
## First-run boot (M1-RND-29): on a launch with no pipeline cache yet for this engine, GPU, driver and preset
## (needs_first_run), the boot run stages every entry the preset wants, whatever its scenes, and harvests
## the registry's "first_run_scenes" too, so a fresh install builds its pipelines behind the boot card,
## not in its first zone entries. It writes the "first_run_marker" when it finishes.
var first_run := false
## Diagnosis (M1-RND-27, tools/gpu_bench/prewarm_bench): when true, `trace` gets one row per frame,
## [frame_ms, the paths staged on the frame before it], so a slow frame names the draws that cost it.
var record_trace := false
var trace: Array = []

var _running := false
# M2-RND-15: the first run's live scenes (first_run_live_scenes), instanced on worker threads: [task id, [instance]].
var _live_tasks: Array = []
# Their threaded loads in flight (M2-RND-910).
var _live_loading: PackedStringArray = PackedStringArray()
var _live_seen := {}
# A first run's live scenes start once the regular staging has drained: started with it, their worker-thread
# instancing (loads, dressing) piled onto the boot's heaviest frames (2.9 s against 1.05 on a cold driver).
var _live_pending := false
# A first run's first_run_scenes, harvested one at a time before the stage's batches (M2-RND-18), each through
# ResourceLoader's threaded request (M2-RND-910); _harvest_requested while the queue's head is loading.
var _harvest_queue: PackedStringArray = PackedStringArray()
var _harvest_requested := false
# ADR 0111 amendment 4: the zone's runtime materials and scenes, staged as they load (PrewarmZoneFeed); null when off.
var _zone: PrewarmZoneFeed
var _last_frame_usec := 0
var _stage_alive := false
var _frames_to_render := 0
var _measure_frames := 0
var _frames_measured := 0
var _max_frame_ms := 0.0
var _total_ms := 0.0
var _instanced := 0
var _skipped := 0
var _filtered := 0
var _spawned: Array[Node] = []
## Draws waiting for the stage: [material, mesh, multimesh] harvested from the scene, or registry entries;
## both are built and loaded in their batch.
var _pending: Array = []
var _batch := 0
var _min_batch_seen := 0
var _batches := 0
var _frames_since_batch := 0
var _stage_env: Environment
## The parent whose swap this stage holds while staging (null when the parent has no hold_swap).
var _held: Node
var _last_batch_paths := PackedStringArray()
## [property, value] the boot bring-up still has to turn on, one a frame (M1-RND-27).
var _bring_up: Array = []
## Compute pipelines warmed instead of a spatial draw (registry "compute_twin").
var _computes := 0
## M2-ARC-08: the draws and bring-up steps start() queued, for progress_fraction().
var _draws_total := 0
var _bring_up_total := 0

@onready var _viewport: SubViewport = $Viewport
@onready var _stage_3d: Node3D = $Viewport/Stage3D
@onready var _camera: Camera3D = $Viewport/Stage3D/Camera3D
@onready var _stage_2d: Control = $Viewport/Stage2D


## Connects the warmup to a router's prewarm_requested(scene_path) signal. Idempotent.
static func install(router: Node) -> bool:
	if router.has_meta(HOOK_META) or not router.has_signal(ROUTER_SIGNAL):
		return false
	var hook: Callable = spawn.bind(router)
	router.connect(ROUTER_SIGNAL, hook)
	router.set_meta(HOOK_META, hook)
	return true


static func uninstall(router: Node) -> void:
	if not router.has_meta(HOOK_META):
		return
	var hook: Callable = router.get_meta(HOOK_META)
	if router.is_connected(ROUTER_SIGNAL, hook):
		router.disconnect(ROUTER_SIGNAL, hook)
	router.remove_meta(HOOK_META)


## Instances the warmup scene under `parent` and starts it for `for_scene`.
static func spawn(for_scene: String, parent: Node) -> ShaderPrewarm:
	var node := (load(SCENE_PATH) as PackedScene).instantiate() as ShaderPrewarm
	parent.add_child(node)
	node.start(for_scene)
	return node


## spawn() for a pipeline state the game viewport does not have yet: `state` is
## GraphicsSettings.override_state(values) of an override a cutscene will push at its cut.
static func spawn_with_state(for_scene: String, parent: Node, state: Dictionary) -> ShaderPrewarm:
	var node := (load(SCENE_PATH) as PackedScene).instantiate() as ShaderPrewarm
	node.viewport_state = state.duplicate()
	parent.add_child(node)
	node.start(for_scene)
	return node


## Builds the off-screen stage for every registry entry matching `for_scene` (all when "").
## Returns the number of materials instanced. Must be called once the node is in the tree.
func start(for_scene: String = "") -> int:
	if not is_node_ready():
		push_error("%s: start() needs the node in the scene tree" % LOG_PREFIX)
		return 0
	if _running:
		push_warning("%s: start() called twice; ignored" % LOG_PREFIX)
		return 0
	# The first frame measured includes start() itself (it builds the stage in this frame).
	_last_frame_usec = Time.get_ticks_usec()
	config = _load_registry(registry_path)
	scene_path = for_scene
	_frames_to_render = int(config.get("frames_to_render", 0))
	_measure_frames = maxi(int(config.get("measure_frames", 0)), _frames_to_render)
	var width := int(config.get("viewport_width", _viewport.size.x))
	var height := int(config.get("viewport_height", _viewport.size.y))
	_viewport.size = Vector2i(width, height)
	match_viewport(get_viewport())
	# Registry entries are only listed here and loaded in their batch (M1-RND-15): loading a material
	# compiles its shader on the CPU, up to ~35 ms each on an RX 9070 XT. Loading them all at start put
	# 0.2 s into one frame however small the batches were.
	var preset := active_preset()
	for entry: Variant in config.get("materials", []):
		var e := entry as Dictionary
		var scenes := e.get("scenes", []) as Array
		if resident_only:
			if not first_run and not entry_resident(e, preset):
				continue
		elif not (scenes.is_empty() or scenes.has(for_scene)):
			continue
		# Another preset's tier variant compiles a pipeline this game never draws: 75 ms a shader on an
		# RX 9070 XT, in the transition (M1-RND-22).
		if not entry_wanted(e, preset):
			_filtered += 1
			continue
		if ResourceLoader.exists(str(e.get("path", ""))):
			_pending.append(e)
			_instanced += 1
		else:
			push_warning("%s: registered material not found: %s" % [LOG_PREFIX, e.get("path", "")])
			_skipped += 1
	if first_run:
		# M2-RND-18: harvested one scene per frame (_harvest_next_first_run_scene), not here: loading all five
		# scenes' meshes and materials in start() compiled their pipelines in one frame (2.65 s on a cold High).
		for path: Variant in config.get("first_run_scenes", []):
			if ResourceLoader.exists(str(path)):
				_harvest_queue.append(str(path))
		_live_pending = true
	if bool(config.get("scene_materials", false)) and for_scene != "" and ResourceLoader.exists(for_scene):
		_instanced += _instance_scene_materials(for_scene, int(config.get("max_scene_materials", 0)))
	# M2-RND-18: a first run on an empty driver cache compiles every pass of a material at once (up to ~1.3 s for
	# one), so its batches start at first_run_materials_per_frame: two to a batch made the boot's worst hidden
	# frame 1.7 s on Low and 3.0 s on High, which froze the boot card.
	var per_frame := int(config.get("materials_per_frame", 0))
	if first_run and config.has("first_run_materials_per_frame"):
		per_frame = int(config["first_run_materials_per_frame"])
	_zone = PrewarmZoneFeed.for_transition(config, for_scene, resident_only or first_run)
	per_frame = maxi(per_frame, _zone.per_frame()) if _zone != null else per_frame
	_batch = per_frame if per_frame > 0 else maxi(_pending.size(), 1)
	_min_batch_seen = _batch
	_draws_total = _pending.size()
	_viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	_running = true
	_stage_alive = true
	_hold_parent_swap()
	if resident_only:
		_begin_bring_up()
	else:
		_stage_next_batch()
	return _instanced


## The preset the stage warms tier variants for: preset_id, else the player's (GraphicsRuntime).
func active_preset() -> String:
	if preset_id != "":
		return preset_id
	var gs := GraphicsRuntime.settings()
	return gs.preset_id if gs != null else ""


## Loads every registry entry marked "resident" that `preset` stages and keeps it loaded for the session
## (boot, and GraphicsRuntime on a preset change). Returns how many it loaded now (already held: 0).
static func load_resident(preset: String, path: String = REGISTRY_PATH) -> int:
	var count := 0
	for entry: Variant in _load_registry(path).get("materials", []):
		var e := entry as Dictionary
		if not entry_resident(e, preset) or not entry_wanted(e, preset):
			continue
		var res_path := str(e.get("path", ""))
		if not ResourceLoader.exists(res_path):
			continue
		var res := load(res_path)
		if res != null:
			_hold(res)
			count += 1
	return count


## The boot warm-up (M1-RND-22): stages the resident entries once under `parent`, so their shader
## variants compile under the boot screen, and holds each as its batch loads it (M1-RND-27: loading
## them all here put 0.1 s into the spawn frame). A held Shader keeps its compiled variants, and a
## transition then only builds pipelines (Godot compiles a shader variant the first time a material
## that uses it is drawn).
static func spawn_resident(parent: Node, preset: String, with_trace := false) -> ShaderPrewarm:
	var node := (load(SCENE_PATH) as PackedScene).instantiate() as ShaderPrewarm
	node.resident_only = true
	node.preset_id = preset
	node.first_run = needs_first_run(preset)
	node.record_trace = with_trace
	parent.add_child(node)
	node.start("")
	return node


## The first-run key (M1-RND-29): what a pipeline cache depends on. Godot rebuilds its pipelines for another
## engine, GPU or driver, and another preset stages other tier variants.
static func first_run_key(preset: String) -> String:
	return (
		"%s|%s|%s|%s"
		% [
			Engine.get_version_info().get("string", ""),
			RenderingServer.get_video_adapter_name(),
			RenderingServer.get_video_adapter_api_version(),
			preset,
		]
	)


## True under the headless display server, whose dummy renderer compiles and draws nothing.
static func is_headless() -> bool:
	return DisplayServer.get_name() == "headless"


## True when this launch has not finished a first-run warm-up for first_run_key (M1-RND-29).
static func needs_first_run(preset: String, path: String = REGISTRY_PATH) -> bool:
	# Headless (the dummy renderer) builds no pipelines and the run would never write its marker, so every
	# headless boot (CI's smoke test, tools) would stage and harvest the whole first launch for nothing.
	if is_headless():
		return false
	return str(_load_registry(path).get("first_run_marker", "")) != "" and not marker_current(preset, path)


## Whether the registry's first_run_marker holds this engine, GPU, driver and preset's key (the key logic
## of needs_first_run, without its headless guard; M2-RND-11 tests it headless).
static func marker_current(preset: String, path: String = REGISTRY_PATH) -> bool:
	var marker := str(_load_registry(path).get("first_run_marker", ""))
	if marker == "":
		return false
	var cfg := ConfigFile.new()
	return cfg.load(marker) == OK and str(cfg.get_value("pipelines", "key", "")) == first_run_key(preset)


func _write_first_run_marker() -> void:
	var marker := str(config.get("first_run_marker", ""))
	if marker == "":
		return
	var cfg := ConfigFile.new()
	cfg.set_value("pipelines", "key", first_run_key(active_preset()))
	cfg.save(marker)


## Holds `res` for the session on the holder node (created under the tree root on first use).
static func _hold(res: Resource) -> void:
	var h := _holder(true)
	if h != null and not h.held.has(res):
		h.held.append(res)


static func _holder(create: bool) -> ResidentHolder:
	var tree := Engine.get_main_loop() as SceneTree
	if tree == null or tree.root == null:
		return null
	var h := tree.root.get_node_or_null(NodePath(RESIDENT_HOLDER)) as ResidentHolder
	if h == null and is_instance_valid(_pending_holder):
		h = _pending_holder as ResidentHolder
	if h == null and create:
		h = ResidentHolder.new()
		h.name = RESIDENT_HOLDER
		# Deferred: the root may still be adding its children (boot). Until it lands, _pending_holder finds it.
		tree.root.add_child.call_deferred(h)
		_pending_holder = h
	return h


## The resources load_resident() holds (tests).
static func resident_count() -> int:
	var h := _holder(false)
	return h.held.size() if h != null else 0


## Whether a registry entry is held from boot on `preset`: "resident" true, and `preset` in its optional
## "resident_presets" (absent = every preset). Data, so a tier's VRAM can opt out without code (the heroes'
## materials, gpu/hero-materials-resident).
static func entry_resident(entry: Dictionary, preset: String) -> bool:
	if not bool(entry.get("resident", false)):
		return false
	var only: Variant = entry.get("resident_presets")
	return typeof(only) != TYPE_ARRAY or preset == "" or (only as Array).has(preset)


## Whether a registry entry is staged for `preset`: an entry with "preset_tier" {system, tier} only when
## that preset selects that tier; every other entry (and every entry when `preset` is "") always.
static func entry_wanted(entry: Dictionary, preset: String) -> bool:
	var pt: Variant = entry.get("preset_tier")
	if typeof(pt) != TYPE_DICTIONARY or preset == "":
		return true
	var system := str((pt as Dictionary).get("system", ""))
	var want := ""
	match system:
		"character":
			want = CharacterShaderTiers.tier_for_preset(preset)
		"undertow":
			want = preset
		_:
			want = GraphicsSettings.preset_tier(preset, system)
	return want == "" or want == str((pt as Dictionary).get("tier", ""))


## True when `preset`'s storm tier marches the body in compute (M2-RND-01: a RenderingDevice, and a
## body_scale under 1), so its spatial body shader never draws and its compute twin is warmed instead.
static func undertow_uses_compute(preset: String) -> bool:
	if RenderingServer.get_rendering_device() == null:
		return false
	var state := UndertowState.new()
	return state.set_quality(preset) and float(state.quality_plan()["body_scale"]) < UndertowState.MAX_BODY_SCALE


## Copies the AA and 3D scaling state of the game viewport onto the stage, so the pipelines
## that state selects (TAA motion vectors, FSR2, MSAA, FXAA/SMAA) are the ones compiled.
func match_viewport(game: Viewport) -> void:
	if game == null:
		return
	_viewport.use_taa = game.use_taa
	_viewport.msaa_3d = game.msaa_3d
	_viewport.screen_space_aa = game.screen_space_aa
	_viewport.scaling_3d_mode = game.scaling_3d_mode
	_viewport.scaling_3d_scale = game.scaling_3d_scale
	for prop: Variant in viewport_state:
		_viewport.set(str(prop), viewport_state[prop])
	# FSR2 fails on a tiny target ("uavMip ... FFX_ERROR_INVALID_ARGUMENT" every frame at 64 px; M1-RND-22),
	# so an FSR2 stage is at least fsr2_min_size px (the stage's size doesn't change its cost: M1-RND-15).
	if _viewport.scaling_3d_mode == Viewport.SCALING_3D_MODE_FSR2:
		var m := int(config.get("fsr2_min_size", 0))
		_viewport.size = Vector2i(maxi(_viewport.size.x, m), maxi(_viewport.size.y, m))


func is_running() -> bool:
	return _running


## True while draws are still entering or rendering in the stage: the incoming scene should wait.
func is_staging() -> bool:
	return _running and _stage_alive


## Number of warmup draw nodes currently in the stage (pending batches excluded).
func stage_node_count() -> int:
	return _spawned.size()


## Draws built but not yet in the stage.
func pending_count() -> int:
	return _pending.size()


## Draws that enter the stage on the next frame (halved after an over-budget frame).
func batch_size() -> int:
	return _batch


## M2-ARC-08 (BootCard, SceneRouter's reveal hold): a count that moves while the warm-up moves. Every tick
## advances it by one step of a finite run (a bring-up feature, a batch, a render or measure frame), so a
## warm-up that still ticks is progressing however slow its frames; it stalls only if its ticks stop.
func wait_progress() -> int:
	return _frames_measured


## ADR 0111 amendment 4: the zone draws staged so far, while this transition stages the zone's runtime loads (a
## loading holder's progress: SceneRouter waits on while it rises); -1 otherwise (frames are not work, amendment 2).
func swap_wait_progress() -> int:
	return _zone.staged if _zone != null and _stage_alive else -1


## How far the staging is, 0..1: bring-up steps and draws staged over those queued (1 once the stage is cleared).
func progress_fraction() -> float:
	if not _running or not _stage_alive:
		return 1.0
	var total := _bring_up_total + _draws_total
	if total <= 0:
		return 1.0
	var done := (_bring_up_total - _bring_up.size()) + (_draws_total - _pending.size())
	return clampf(float(done) / total, 0.0, 1.0)


## M2-ARC-08: stops a warm-up a waiter gave up on (BootCard's stall or safety cap), so nothing stages under the
## title once it shows. The stage is cleared and the swap hold released; no `finished`, and a first run writes
## no marker, so the next launch runs it again. It frees itself.
func cancel() -> void:
	if not _running:
		return
	push_warning(
		(
			"%s: warm-up cancelled after %d frame(s), %d draw(s) still pending (first run: %s)"
			% [LOG_PREFIX, _frames_measured, _pending.size(), first_run]
		)
	)
	_clear_stage()
	_running = false
	queue_free()


## Records one frame of the transition. Called from _process; tests call it directly.
func tick(frame_ms: float) -> void:
	if not _running:
		return
	_frames_measured += 1
	_max_frame_ms = maxf(_max_frame_ms, frame_ms)
	if record_trace:
		trace.append([frame_ms, _last_batch_paths])
		_last_batch_paths = PackedStringArray()
	_total_ms += frame_ms
	if _stage_alive and not _bring_up.is_empty():
		var step: Array = _bring_up.pop_front()
		_viewport.set(step[0], step[1])
		# M2-RND-18: a first run keeps one frame empty after the bring-up, so the renderer's own first use (its
		# passes with every feature on) doesn't share a frame with the first material's pipelines.
		if _bring_up.is_empty() and not first_run:
			_stage_next_batch()
	elif _stage_alive and not _harvest_queue.is_empty():
		_harvest_next_scene()
	elif _stage_alive:
		var pulled := _zone.pull(self, int(config.get("max_scene_materials", 0))) if _zone != null else 0
		_instanced += pulled
		_draws_total += pulled
		if not _pending.is_empty():
			# The first frame also carries start() and the stage's set-up, so it says nothing about how
			# big a batch the card can take (review-sweep-J S3): never halve on it.
			if frame_ms > float(config.get("slice_budget_ms", INF)) and _batch > 1 and _frames_measured > 1:
				_batch = maxi(floori(_batch / 2.0), 1)
				_min_batch_seen = mini(_min_batch_seen, _batch)
			_stage_next_batch()
		elif not _poll_live_scenes() and not (_zone != null and _zone.pending()):
			_frames_since_batch += 1
			if _frames_since_batch >= _frames_to_render:
				_clear_stage()
	if not _stage_alive and _frames_measured >= _measure_frames:
		_finish()


## M2-RND-15: a zone that builds geometry at runtime (Haluna's dresser, ocean grid, cast materials) has surfaces no
## SceneState lists; cold, its first frame compiled 92 surface pipelines (1.6-1.7 s). A first run instances each
## "first_run_live_scenes" entry off the tree (as SceneRouter does), stages every draw it holds, and frees it.
## M2-RND-910: each loads by ResourceLoader's threaded request (polled), then instances on a worker. A raw load()
## on a worker task could sit in the loader while the main thread waited on it: a quit mid-warm-up never exited.
func _start_live_scenes() -> void:
	for path: Variant in config.get("first_run_live_scenes", []):
		if ResourceLoader.exists(str(path)) and ResourceLoader.load_threaded_request(str(path)) == OK:
			_live_loading.append(str(path))


## Hands every live scene whose threaded load is in to a worker that instances it.
func _poll_live_loads() -> void:
	for i in range(_live_loading.size() - 1, -1, -1):
		var path := _live_loading[i]
		var status := ResourceLoader.load_threaded_get_status(path)
		if status == ResourceLoader.THREAD_LOAD_IN_PROGRESS:
			continue
		_live_loading.remove_at(i)
		var packed := (
			ResourceLoader.load_threaded_get(path) as PackedScene
			if status == ResourceLoader.THREAD_LOAD_LOADED
			else null
		)
		if packed == null:
			continue
		var box := [null]
		_live_tasks.append([WorkerThreadPool.add_task(PrewarmHarvest.instance_live.bind(packed, box)), box])


## Harvests every finished live scene into the pending draws. True while any is still instancing (the stage stays).
func _poll_live_scenes() -> bool:
	if _live_pending:
		_live_pending = false
		_start_live_scenes()
		return not _live_loading.is_empty()
	_poll_live_loads()
	var cap := int(config.get("max_live_materials", 0))
	for i in range(_live_tasks.size() - 1, -1, -1):
		var task: Array = _live_tasks[i]
		if not WorkerThreadPool.is_task_completed(int(task[0])):
			continue
		WorkerThreadPool.wait_for_task_completion(int(task[0]))
		_live_tasks.remove_at(i)
		var inst := (task[1] as Array)[0] as Node
		if inst == null:
			continue
		var added := 0
		var geoms := inst.find_children("*", "GeometryInstance3D", true, false)
		if inst is GeometryInstance3D:
			geoms.append(inst)
		for g in geoms:
			for pair in PrewarmHarvest.live_draws(g as GeometryInstance3D):
				var key := [pair[0], pair[1]]
				if _live_seen.has(key) or added >= cap:
					continue
				_live_seen[key] = true
				_pending.append(pair)
				added += 1
		_draws_total += added
		_instanced += added
		inst.free()
		if added > 0:
			_stage_next_batch()
	return not (_live_tasks.is_empty() and _live_loading.is_empty())


## At quit: a load in flight stays with ResourceLoader; an instancing worker (it only instantiates) is waited for.
func _drop_live_scenes() -> void:
	_live_loading.clear()
	for task: Array in _live_tasks:
		WorkerThreadPool.wait_for_task_completion(int(task[0]))
		var inst := (task[1] as Array)[0] as Node
		if inst != null:
			inst.free()
	_live_tasks.clear()


## M2-RND-18: loading a first_run_scenes entry compiled its mesh pipelines in that frame (1.96 s, cold High). Each
## loads off the main thread, one at a time, and its SceneState is read here once it's in.
func _harvest_next_scene() -> void:
	var path := _harvest_queue[0]
	if not _harvest_requested:
		_harvest_requested = ResourceLoader.load_threaded_request(path) == OK
		if not _harvest_requested:
			_harvest_queue.remove_at(0)
		return
	var status := ResourceLoader.load_threaded_get_status(path)
	if status == ResourceLoader.THREAD_LOAD_IN_PROGRESS:
		return
	var packed := (
		ResourceLoader.load_threaded_get(path) as PackedScene if status == ResourceLoader.THREAD_LOAD_LOADED else null
	)
	_harvest_requested = false
	_harvest_queue.remove_at(0)
	if packed == null:
		return
	var counter := [0]
	_harvest_state(packed.get_state(), {}, {}, int(config.get("max_scene_materials", 0)), counter, 0)
	_instanced += int(counter[0])
	_draws_total += int(counter[0])


## Moves up to one batch of pending draws into the stage; they compile on the frame that draws them.
func _stage_next_batch() -> void:
	var n := mini(_batch, _pending.size())
	if n <= 0:
		return
	var batch := _pending.slice(0, n)
	_pending = _pending.slice(n)
	if _zone != null:
		_zone.staged += n
	for item: Variant in batch:
		var node: Node
		if item is Node:
			node = item as Node
		elif item is Array:
			var it := item as Array
			node = PrewarmHarvest.draw_for(it[0] as Material, it[1] as Mesh, it[2] as MultiMesh, config)
		else:
			node = _build_entry(item as Dictionary)
		if node == null:
			continue
		(_stage_2d if node is Control else _stage_3d).add_child(node)
		_spawned.append(node)
		if record_trace:
			_last_batch_paths.append(_trace_name(item, node))
	_batches += 1
	_frames_since_batch = 0


## Wall time since the last frame (M1-RND-29): Godot 4.6 caps the process `delta` at about 150 ms (a
## 516 ms stall reports 147 ms), so a delta-based max_frame_ms under-reported every long prewarm frame
## and the batch never halved on them.
func _process(_delta: float) -> void:
	var now := Time.get_ticks_usec()
	var frame_ms := float(now - _last_frame_usec) / USEC_PER_MSEC if _last_frame_usec > 0 else 0.0
	_last_frame_usec = now
	tick(frame_ms)


func _notification(what: int) -> void:
	if what == NOTIFICATION_PREDELETE:
		_drop_live_scenes()  # M2-RND-910: never waits on a load
		for n: Variant in _pending:
			if is_instance_valid(n) and n is Node:
				n.free()
		_pending.clear()
		_release_parent_swap()


func _finish() -> void:
	_running = false
	if first_run:
		_write_first_run_marker()
	var budget := float(config.get("hitch_budget_ms", 0.0))
	stats = {
		"scene_path": scene_path,
		"materials": _instanced,
		"skipped": _skipped,
		"filtered": _filtered,
		"frames": _frames_measured,
		"max_frame_ms": _max_frame_ms,
		"total_ms": _total_ms,
		"budget_ms": budget,
		"over_budget": _max_frame_ms > budget,
		"batches": _batches,
		"min_batch": _min_batch_seen,
		"computes": _computes,
		"first_run": first_run,
	}
	var line := (
		"%s: '%s' warmed %d material(s) (%d skipped); max frame %.1f ms over %d frames (budget %.0f ms)"
		% [LOG_PREFIX, scene_path, _instanced, _skipped, _max_frame_ms, _frames_measured, budget]
	)
	print(line)
	if bool(stats["over_budget"]):
		push_warning("%s: transition hitch over budget: %s" % [LOG_PREFIX, line])
	finished.emit(stats)
	queue_free()


func _clear_stage() -> void:
	for n: Variant in _pending + _spawned:
		if is_instance_valid(n) and n is Node:
			n.free()
	_spawned.clear()
	_pending.clear()
	_camera.environment = null
	_stage_env = null
	_viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	_stage_alive = false
	_release_parent_swap()


## Holds the parent's next swap while the stage is alive (duck-typed: the SceneRouter autoload).
func _hold_parent_swap() -> void:
	var parent := get_parent()
	if parent != null and parent.has_method(HOLD_METHOD):
		parent.call(HOLD_METHOD, self)
		_held = parent


func _release_parent_swap() -> void:
	if is_instance_valid(_held) and _held.has_method(RELEASE_METHOD):
		_held.call(RELEASE_METHOD, self)
	_held = null


static func _trace_name(item: Variant, node: Node) -> String:
	if item is Dictionary:
		return str((item as Dictionary).get("path", ""))
	if item is Array:
		var mat := (item as Array)[0] as Material
		return mat.resource_path if mat.resource_path != "" else "%s on %s" % [mat.get_class(), (item as Array)[1]]
	var g := node as GeometryInstance3D
	return g.material_override.resource_path if g != null and g.material_override != null else str(node.name)


static func _load_registry(path: String) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_warning("%s: cannot read registry %s" % [LOG_PREFIX, path])
		return {}
	return parsed as Dictionary


static func _load_material(path: String) -> Material:
	if path.is_empty() or not ResourceLoader.exists(path):
		push_warning("%s: registered material not found: %s" % [LOG_PREFIX, path])
		return null
	var res := load(path)
	if res is Shader:
		var wrapper := ShaderMaterial.new()
		wrapper.shader = res as Shader
		return wrapper
	if res is Material:
		return res as Material
	push_warning("%s: %s is not a Material or Shader" % [LOG_PREFIX, path])
	return null


static func _shader_mode(mat: Material) -> int:
	if mat is ShaderMaterial:
		var shader := (mat as ShaderMaterial).shader
		return shader.get_mode() if shader != null else MODE_UNSUPPORTED
	if mat is ParticleProcessMaterial:
		return Shader.MODE_PARTICLES
	if mat is CanvasItemMaterial:
		return Shader.MODE_CANVAS_ITEM
	if mat is BaseMaterial3D:
		return Shader.MODE_SPATIAL
	return MODE_UNSUPPORTED


## The mesh an entry draws (PrewarmEntryMesh.of): its "mesh" key, else `fallback` (the stage quad).
static func entry_mesh(entry: Dictionary, fallback: Mesh) -> Mesh:
	return PrewarmEntryMesh.of(entry, fallback)


## Draws the stage plain first and queues the game viewport's features to come on one a frame
## (M1-RND-27); a feature the game viewport does not use is not a step.
func _begin_bring_up() -> void:
	var taa_wanted := bool(_viewport.get(&"use_taa"))
	var fsr2 := int(_viewport.get(&"scaling_3d_mode")) == Viewport.SCALING_3D_MODE_FSR2
	for prop in BRING_UP_PROPS:
		var want: Variant = _viewport.get(prop)
		if want != BRING_UP_PLAIN[prop]:
			_bring_up.append([prop, want])
			_viewport.set(prop, BRING_UP_PLAIN[prop])
	# M2-RND-14: Forward+ turns its advanced shader group on lazily, and in 4.6.3 that can deadlock (version_get_shader
	# holds the version mutex while compiles of the same shader fill every worker). With TAA off it hit the Shell
	# Shrine's first post-bake frame. So a boot turns it on here, under the card, with one frame of TAA on the stage
	# right after the plain first frame (with TAA or FSR2 the game already has it).
	if not taa_wanted and not fsr2:
		_bring_up.push_front([&"use_taa", false])
		_bring_up.push_front([&"use_taa", true])
	_bring_up_total = _bring_up.size()
	if _bring_up.is_empty():
		_stage_next_batch()


## Loads a registry entry's material and builds its draw (null when it cannot be drawn, for a sky,
## which goes on the stage environment instead of a node, and for a compute twin, warmed instead).
func _build_entry(entry: Dictionary) -> Node:
	var path := str(entry.get("path", ""))
	if bool(entry.get("compute_twin", false)) and undertow_uses_compute(active_preset()):
		var twin := UndertowBodyEffect.compute_path_for(path)
		if twin != "":
			RenderingServer.call_on_render_thread(UndertowBodyEffect.warm_pipeline.bind(twin))
			# The holder frees the warm pipelines with the tree (M2-RND-11).
			_holder(true)
			_computes += 1
			return null
	if resident_only:
		var res := load(path) if ResourceLoader.exists(path) else null
		if res != null:
			_hold(res)
	var mat := _load_material(path)
	var node: Node = _instance(mat, entry) if mat != null else null
	if mat == null or (node == null and _shader_mode(mat) != Shader.MODE_SKY):
		_instanced -= 1
		_skipped += 1
	return node


## Builds the draw for one material (null for a sky, set on the stage environment, or when the
## material kind is unsupported).
func _instance(mat: Material, entry: Dictionary = {}) -> Node:
	var in_front := Vector3.FORWARD * float(config.get("quad_distance", 0.0))
	var quad := QuadMesh.new()
	var side := float(config.get("quad_size", 0.0))
	quad.size = Vector2(side, side)
	var node: Node
	match _shader_mode(mat):
		Shader.MODE_SPATIAL:
			var draw_mesh := entry_mesh(entry, quad)
			if bool(entry.get("multimesh", false)):
				var mm := MultiMesh.new()
				mm.transform_format = MultiMesh.TRANSFORM_3D
				mm.use_colors = true
				mm.use_custom_data = true
				mm.mesh = draw_mesh
				mm.instance_count = int(config.get("multimesh_instances", 1))
				var mmi := MultiMeshInstance3D.new()
				mmi.multimesh = mm
				mmi.material_override = mat
				mmi.position = in_front
				node = mmi
			else:
				var mesh := MeshInstance3D.new()
				mesh.mesh = draw_mesh
				mesh.material_override = mat
				mesh.position = in_front
				node = mesh
		Shader.MODE_PARTICLES:
			var particles := GPUParticles3D.new()
			particles.amount = int(config.get("particle_amount", 0))
			particles.process_material = mat
			var draw := _load_material(str(entry.get("draw_material", ""))) if entry.has("draw_material") else null
			if draw != null:
				quad.material = draw
			particles.draw_pass_1 = quad
			particles.position = in_front
			node = particles
		Shader.MODE_CANVAS_ITEM:
			var rect := ColorRect.new()
			rect.material = mat
			rect.set_anchors_preset(Control.PRESET_FULL_RECT)
			node = rect
		Shader.MODE_SKY:
			var sky := Sky.new()
			sky.sky_material = mat
			_ensure_stage_env().background_mode = Environment.BG_SKY
			_stage_env.sky = sky
			return null
		Shader.MODE_FOG:
			var fog := FogVolume.new()
			fog.material = mat
			fog.position = in_front
			_ensure_stage_env().volumetric_fog_enabled = true
			node = fog
		_:
			push_warning("%s: unsupported material %s" % [LOG_PREFIX, mat.resource_path])
			return null
	return node


## Draws every (material, mesh) pair on the incoming scene's geometry, and its sky. Returns how
## many draws were staged (capped at `cap`, deduplicated). M1-RND-27: read from the scene's SceneState
## and those of the scenes it instances, without instancing anything (an off-tree instance of Haluna
## built every node and every instanced plant first).
func _instance_scene_materials(path: String, cap: int) -> int:
	var packed := load(path) as PackedScene
	if packed == null:
		return 0
	var seen := {}
	var counter := [0]
	_harvest_state(packed.get_state(), {}, seen, cap, counter, 0)
	return int(counter[0])


## One SceneState's draws. `root_overrides` are the properties an instancing scene sets on this scene's
## root node (they win over the root's own).
func _harvest_state(
	state: SceneState, root_overrides: Dictionary, seen: Dictionary, cap: int, counter: Array, depth: int
) -> void:
	if state == null or depth > HARVEST_MAX_DEPTH:
		return
	for i in state.get_node_count():
		if int(counter[0]) >= cap:
			return
		var props := {}
		for j in state.get_node_property_count(i):
			props[state.get_node_property_name(i, j)] = state.get_node_property_value(i, j)
		if i == 0:
			props.merge(root_overrides, true)
		var sub := state.get_node_instance(i)
		if sub != null:
			_harvest_state(sub.get_state(), props, seen, cap, counter, depth + 1)
			continue
		var type := state.get_node_type(i)
		if type == &"WorldEnvironment":
			var env := props.get(&"environment") as Environment
			if env != null and env.sky != null and env.sky.sky_material != null:
				var sky := Sky.new()
				sky.sky_material = env.sky.sky_material
				_ensure_stage_env().background_mode = Environment.BG_SKY
				_stage_env.sky = sky
			continue
		for pair in PrewarmHarvest.state_draws(props):
			var key := [pair[0], pair[1]]
			if seen.has(key) or int(counter[0]) >= cap:
				continue
			seen[key] = true
			# Built in its batch: assigning a PrimitiveMesh generates it and compiles its StandardMaterial3D
			# (about 75 ms each), which belongs in a batch frame, not in start().
			_pending.append(pair)
			counter[0] = int(counter[0]) + 1


func _ensure_stage_env() -> Environment:
	if _stage_env == null:
		_stage_env = Environment.new()
		_camera.environment = _stage_env
	return _stage_env


## The node that holds the resident resources (RESIDENT_HOLDER). Its references go when the tree frees it,
## and so do the warm compute pipelines (UndertowBodyEffect.release_warm; M2-RND-11).
class ResidentHolder:
	extends Node
	var held: Array[Resource] = []

	func _notification(what: int) -> void:
		if what == NOTIFICATION_PREDELETE:
			held.clear()
			# At exit the render thread no longer takes queued calls: the main thread frees them (single-safe
			# threading, the project default, renders on it).
			UndertowBodyEffect.release_warm()

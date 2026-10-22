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
## {"path": res path of a Material or Shader, "scenes": [scene paths] (empty = every transition)}.
##
## Hook-up (autoload-free): `ShaderPrewarm.install(SceneRouter)` connects to
## SceneRouter.prewarm_requested and spawns this scene as a child of the router (which survives the
## scene change). Headless-safe: the dummy renderer simply draws nothing.

signal finished(stats: Dictionary)

const SCENE_PATH := "res://game/core/shader_prewarm.tscn"
const REGISTRY_PATH := "res://game/data/settings/prewarm_materials.json"
const ROUTER_SIGNAL := &"prewarm_requested"
const HOOK_META := &"shader_prewarm_hook"
const MSEC_PER_SEC := 1000.0
const LOG_PREFIX := "ShaderPrewarm"
const MODE_UNSUPPORTED := -1

var registry_path: String = REGISTRY_PATH
var config: Dictionary = {}
var scene_path: String = ""
var stats: Dictionary = {}

var _running := false
var _stage_alive := false
var _frames_to_render := 0
var _measure_frames := 0
var _frames_measured := 0
var _max_frame_ms := 0.0
var _total_ms := 0.0
var _instanced := 0
var _skipped := 0
var _spawned: Array[Node] = []
var _stage_env: Environment

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


## Builds the off-screen stage for every registry entry matching `for_scene` (all when "").
## Returns the number of materials instanced. Must be called once the node is in the tree.
func start(for_scene: String = "") -> int:
	if not is_node_ready():
		push_error("%s: start() needs the node in the scene tree" % LOG_PREFIX)
		return 0
	config = _load_registry(registry_path)
	scene_path = for_scene
	_frames_to_render = int(config.get("frames_to_render", 0))
	_measure_frames = maxi(int(config.get("measure_frames", 0)), _frames_to_render)
	var width := int(config.get("viewport_width", _viewport.size.x))
	var height := int(config.get("viewport_height", _viewport.size.y))
	_viewport.size = Vector2i(width, height)
	for entry: Variant in config.get("materials", []):
		var e := entry as Dictionary
		var scenes := e.get("scenes", []) as Array
		if not (scenes.is_empty() or scenes.has(for_scene)):
			continue
		var mat := _load_material(str(e.get("path", "")))
		if mat != null and _instance(mat):
			_instanced += 1
		else:
			_skipped += 1
	_viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	_running = true
	_stage_alive = true
	return _instanced


func is_running() -> bool:
	return _running


## Number of warmup draw nodes currently alive in the stage.
func stage_node_count() -> int:
	return _spawned.size()


## Records one frame of the transition. Called from _process; tests call it directly.
func tick(frame_ms: float) -> void:
	if not _running:
		return
	_frames_measured += 1
	_max_frame_ms = maxf(_max_frame_ms, frame_ms)
	_total_ms += frame_ms
	if _stage_alive and _frames_measured >= _frames_to_render:
		_clear_stage()
	if _frames_measured >= _measure_frames:
		_finish()


func _process(delta: float) -> void:
	tick(delta * MSEC_PER_SEC)


func _finish() -> void:
	_running = false
	var budget := float(config.get("hitch_budget_ms", 0.0))
	stats = {
		"scene_path": scene_path,
		"materials": _instanced,
		"skipped": _skipped,
		"frames": _frames_measured,
		"max_frame_ms": _max_frame_ms,
		"total_ms": _total_ms,
		"budget_ms": budget,
		"over_budget": _max_frame_ms > budget,
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
	for n in _spawned:
		if is_instance_valid(n):
			n.free()
	_spawned.clear()
	_camera.environment = null
	_stage_env = null
	_viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	_stage_alive = false


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


func _instance(mat: Material) -> bool:
	var in_front := Vector3.FORWARD * float(config.get("quad_distance", 0.0))
	var quad := QuadMesh.new()
	var side := float(config.get("quad_size", 0.0))
	quad.size = Vector2(side, side)
	var node: Node
	match _shader_mode(mat):
		Shader.MODE_SPATIAL:
			var mesh := MeshInstance3D.new()
			mesh.mesh = quad
			mesh.material_override = mat
			mesh.position = in_front
			node = mesh
		Shader.MODE_PARTICLES:
			var particles := GPUParticles3D.new()
			particles.amount = int(config.get("particle_amount", 0))
			particles.process_material = mat
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
			return true
		Shader.MODE_FOG:
			var fog := FogVolume.new()
			fog.material = mat
			fog.position = in_front
			_ensure_stage_env().volumetric_fog_enabled = true
			node = fog
		_:
			push_warning("%s: unsupported material %s" % [LOG_PREFIX, mat.resource_path])
			return false
	(_stage_2d if node is Control else _stage_3d).add_child(node)
	_spawned.append(node)
	return true


func _ensure_stage_env() -> Environment:
	if _stage_env == null:
		_stage_env = Environment.new()
		_camera.environment = _stage_env
	return _stage_env

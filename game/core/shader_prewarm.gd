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
## so motion-vector and upscaler pipeline variants are compiled too.
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
## after the last batch went in. SceneRouter waits while is_staging() before showing the new scene.
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
var _pending: Array[Node] = []
var _batch := 0
var _min_batch_seen := 0
var _batches := 0
var _frames_since_batch := 0
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
	match_viewport(get_viewport())
	for entry: Variant in config.get("materials", []):
		var e := entry as Dictionary
		var scenes := e.get("scenes", []) as Array
		if not (scenes.is_empty() or scenes.has(for_scene)):
			continue
		var mat := _load_material(str(e.get("path", "")))
		if mat != null and _instance(mat, e):
			_instanced += 1
		else:
			_skipped += 1
	if bool(config.get("scene_materials", false)) and for_scene != "" and ResourceLoader.exists(for_scene):
		_instanced += _instance_scene_materials(for_scene, int(config.get("max_scene_materials", 0)))
	var per_frame := int(config.get("materials_per_frame", 0))
	_batch = per_frame if per_frame > 0 else maxi(_pending.size(), 1)
	_min_batch_seen = _batch
	_viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	_running = true
	_stage_alive = true
	_stage_next_batch()
	return _instanced


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


func is_running() -> bool:
	return _running


## True while draws are still entering or rendering in the stage: the incoming scene should wait.
func is_staging() -> bool:
	return _running and _stage_alive


## True when a ShaderPrewarm child of `router` is still staging (SceneRouter waits on it).
static func is_staging_under(router: Node) -> bool:
	for child in router.get_children():
		if child is ShaderPrewarm and (child as ShaderPrewarm).is_staging():
			return true
	return false


## Number of warmup draw nodes currently in the stage (pending batches excluded).
func stage_node_count() -> int:
	return _spawned.size()


## Draws built but not yet in the stage.
func pending_count() -> int:
	return _pending.size()


## Draws that enter the stage on the next frame (halved after an over-budget frame).
func batch_size() -> int:
	return _batch


## Records one frame of the transition. Called from _process; tests call it directly.
func tick(frame_ms: float) -> void:
	if not _running:
		return
	_frames_measured += 1
	_max_frame_ms = maxf(_max_frame_ms, frame_ms)
	_total_ms += frame_ms
	if _stage_alive:
		if not _pending.is_empty():
			if frame_ms > float(config.get("slice_budget_ms", INF)) and _batch > 1:
				_batch = maxi(floori(_batch / 2.0), 1)
				_min_batch_seen = mini(_min_batch_seen, _batch)
			_stage_next_batch()
		else:
			_frames_since_batch += 1
			if _frames_since_batch >= _frames_to_render:
				_clear_stage()
	if not _stage_alive and _frames_measured >= _measure_frames:
		_finish()


## Moves up to one batch of pending draws into the stage; they compile on the frame that draws them.
func _stage_next_batch() -> void:
	var n := mini(_batch, _pending.size())
	if n <= 0:
		return
	for i in n:
		var node: Node = _pending[i]
		(_stage_2d if node is Control else _stage_3d).add_child(node)
		_spawned.append(node)
	_pending = _pending.slice(n)
	_batches += 1
	_frames_since_batch = 0


func _process(delta: float) -> void:
	tick(delta * MSEC_PER_SEC)


func _notification(what: int) -> void:
	if what == NOTIFICATION_PREDELETE:
		for n in _pending:
			if is_instance_valid(n):
				n.free()
		_pending.clear()


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
		"batches": _batches,
		"min_batch": _min_batch_seen,
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
	for n in _spawned + _pending:
		if is_instance_valid(n):
			n.free()
	_spawned.clear()
	_pending.clear()
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


## The mesh an entry draws: its "mesh" key (a Mesh, or the first/named MeshInstance3D of a scene),
## else the stage quad.
static func entry_mesh(entry: Dictionary, fallback: Mesh) -> Mesh:
	var path := str(entry.get("mesh", ""))
	if path.is_empty() or not ResourceLoader.exists(path):
		if not path.is_empty():
			push_warning("%s: prewarm mesh not found: %s" % [LOG_PREFIX, path])
		return fallback
	var res := load(path)
	if res is Mesh:
		return res as Mesh
	if res is PackedScene:
		var inst := (res as PackedScene).instantiate()
		var want := str(entry.get("mesh_node", ""))
		var mi: MeshInstance3D = null
		if want != "":
			mi = inst.find_child(want, true, false) as MeshInstance3D
		else:
			var found := inst.find_children("*", "MeshInstance3D", true, false)
			mi = (
				(inst as MeshInstance3D)
				if inst is MeshInstance3D
				else (found[0] as MeshInstance3D if found.size() > 0 else null)
			)
		var mesh := mi.mesh if mi != null else null
		inst.free()
		if mesh != null:
			return mesh
	push_warning("%s: %s has no mesh to prewarm with" % [LOG_PREFIX, path])
	return fallback


func _instance(mat: Material, entry: Dictionary = {}) -> bool:
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
	_pending.append(node)
	return true


## Draws every (material, mesh) pair on the incoming scene's geometry, and its sky. Returns how
## many draws were staged (capped at `cap`, deduplicated).
func _instance_scene_materials(path: String, cap: int) -> int:
	var packed := load(path) as PackedScene
	if packed == null:
		return 0
	var inst := packed.instantiate(PackedScene.GEN_EDIT_STATE_DISABLED)
	var seen := {}
	var count := 0
	var in_front := Vector3.FORWARD * float(config.get("quad_distance", 0.0))
	for n in inst.find_children("*", "", true, false) + [inst]:
		if count >= cap:
			break
		if n is WorldEnvironment:
			var env := (n as WorldEnvironment).environment
			if env != null and env.sky != null and env.sky.sky_material != null:
				var sky := Sky.new()
				sky.sky_material = env.sky.sky_material
				_ensure_stage_env().background_mode = Environment.BG_SKY
				_stage_env.sky = sky
			continue
		if not (n is GeometryInstance3D):
			continue
		for pair in _geometry_draws(n as GeometryInstance3D):
			var key := [pair[0], pair[1]]
			if seen.has(key) or count >= cap:
				continue
			seen[key] = true
			var node: GeometryInstance3D
			if n is MultiMeshInstance3D:
				var mm := MultiMesh.new()
				var src := (n as MultiMeshInstance3D).multimesh
				mm.transform_format = src.transform_format
				mm.use_colors = src.use_colors
				mm.use_custom_data = src.use_custom_data
				mm.mesh = pair[1] as Mesh
				mm.instance_count = int(config.get("multimesh_instances", 1))
				var mmi := MultiMeshInstance3D.new()
				mmi.multimesh = mm
				node = mmi
			else:
				var mi := MeshInstance3D.new()
				mi.mesh = pair[1] as Mesh
				node = mi
			node.material_override = pair[0] as Material
			node.position = in_front
			_pending.append(node)
			count += 1
	inst.free()
	return count


## [material, mesh] pairs a GeometryInstance3D draws (override, per-surface overrides, mesh materials).
static func _geometry_draws(g: GeometryInstance3D) -> Array:
	var mesh: Mesh = null
	if g is MeshInstance3D:
		mesh = (g as MeshInstance3D).mesh
	elif g is MultiMeshInstance3D and (g as MultiMeshInstance3D).multimesh != null:
		mesh = (g as MultiMeshInstance3D).multimesh.mesh
	if mesh == null:
		return []
	var out := []
	if g.material_override != null:
		out.append([g.material_override, mesh])
		return out
	for i in mesh.get_surface_count():
		var m: Material = null
		if g is MeshInstance3D:
			m = (g as MeshInstance3D).get_surface_override_material(i)
		if m == null:
			m = mesh.surface_get_material(i)
		if m != null:
			out.append([m, mesh])
	return out


func _ensure_stage_env() -> Environment:
	if _stage_env == null:
		_stage_env = Environment.new()
		_camera.environment = _stage_env
	return _stage_env

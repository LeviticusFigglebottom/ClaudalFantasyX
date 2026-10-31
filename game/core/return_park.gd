class_name ReturnPark
extends RefCounted
## The scene a fight returns to, built while the fight runs (the human's playtest #1, PC pass 7 row 74: the Drownbell
## to Haluna return was 8.2-8.6 s of black; the victory-panel prewarm only had the panel's second or two).
##
## When SceneRouter enters a fight that returns somewhere other than the field kept resident (a scripted fight with a
## cross-zone return: the Drownbell in Ch3's shrine returns to Haluna), it calls start() once the battle is in. That
## loads the return scene and its zone's runtime loads (ResidentLoads.prepare_return, the victory panel's own call)
## on worker threads, then instantiates it on a worker thread as the router's own swap does (the zone's prebuild runs
## there; ShaderGlobals writes are held meanwhile, M3-HER-1151), and keeps the root parked off the tree. The change to
## that scene then takes it (take()) instead of loading and instantiating: what is left under the fade is the add to
## the tree and the zone's reveal holds. Anything else (a loss, a retry's other path, a loaded game) drops it.
## The loads run one family at a time (the scene, then the zone's loads, then the instantiate; PC row 68), and the
## router then sends the parked scene to the shader prewarm during the fight (prewarmed; PC row 74).
##
## A held ShaderGlobals write pauses the arena's wind and shimmer for the instantiate (about a second on the PC).

## The battle-side loads must be in before the instantiate (the zone's load() on a worker thread waits on a threaded
## load of the same file in flight: PC pass 4 row 67); past this many frames the build goes on without them.
const LOADS_WAIT_MAX_FRAMES := 1800
const ARG_NO_PARK := "--no-park"
const ARG_NO_PREWARM := "--no-park-prewarm"

## The parked root (off the tree) and its scene, or null / "".
var node: Node = null
var path := ""
## The scene being built (start() has run and the build has not finished), or "".
var building := ""
## True once the parked scene's pipelines were sent to the shader prewarm (the router's swap-in then skips its own).
var prewarmed := false
## A/B switches for the PC's real-GPU bisects (row 74, big37): `-- --no-park` turns the park off, `-- --no-park-prewarm`
## keeps it but leaves its shader prewarm to the swap-in, as before amendment 1 of ADR 0209.
var enabled := true
var prewarm_in_fight := true
## Bumped by drop(): a build in flight from before it frees its node when it finishes.
var _generation := 0
var _tree: SceneTree


func _init(tree: SceneTree) -> void:
	_tree = tree
	var args := OS.get_cmdline_user_args()
	enabled = not args.has(ARG_NO_PARK)
	prewarm_in_fight = not args.has(ARG_NO_PREWARM)


## Starts building `scene_path` off the tree (see the class comment). `loads` is the session's ResidentLoads, or null
## (a headless run). Await it only to know the build is over.
func start(scene_path: String, loads: ResidentLoads, request: BattleRequest, resident_path: String) -> void:
	drop()
	if scene_path == "" or not ResourceLoader.exists(scene_path):
		return
	var gen := _generation
	building = scene_path
	# One family of loads at a time (PC row 68: a segfault as the Drownbell fight started; "Another resource is loaded
	# from path" for two threaded loads of one model): the scene, then the zone's runtime loads, then the instantiate.
	ResourceLoader.load_threaded_request(scene_path)
	while ResourceLoader.load_threaded_get_status(scene_path) == ResourceLoader.THREAD_LOAD_IN_PROGRESS:
		await _tree.process_frame
	if loads != null and gen == _generation:
		loads.prepare_return(request, resident_path)
	var waited := 0
	while loads != null and not loads.needed_ready() and waited < LOADS_WAIT_MAX_FRAMES:
		await _tree.process_frame
		waited += 1
	var packed := ResourceLoader.load_threaded_get(scene_path) as PackedScene
	if packed == null or gen != _generation:
		building = "" if gen == _generation else building
		return
	var holder: Array[Node] = []
	ShaderGlobals.hold_writes()
	var task := WorkerThreadPool.add_task(func() -> void: holder.append(SceneRouter.built_scene(packed)))
	while not WorkerThreadPool.is_task_completed(task):
		await _tree.process_frame
	WorkerThreadPool.wait_for_task_completion(task)
	ShaderGlobals.release_writes()
	var built: Node = holder[0] if not holder.is_empty() else null
	if gen != _generation:
		if built != null:
			built.free()  # dropped while it was built
		return
	building = ""
	node = built
	path = scene_path if built != null else ""


## The parked root for `scene_path`, waiting for a build of it still in flight; null when there is none (the router
## then loads and instantiates as usual). The park is empty after.
func take(scene_path: String) -> Node:
	while building == scene_path:
		await _tree.process_frame
	if path != scene_path or node == null or not is_instance_valid(node):
		return null
	var out := node
	node = null
	path = ""
	return out


## True while `scene_path` is parked or being built.
func holds(scene_path: String) -> bool:
	return scene_path != "" and (path == scene_path or building == scene_path)


## Frees the parked root and abandons a build in flight.
func drop() -> void:
	_generation += 1
	building = ""
	prewarmed = false
	if node != null and is_instance_valid(node):
		node.free()
	node = null
	path = ""

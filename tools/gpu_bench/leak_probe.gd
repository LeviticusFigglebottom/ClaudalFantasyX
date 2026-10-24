class_name LeakProbe
extends RefCounted
## M2-RND-16: bisects the release build's exit leak ("Resource still in use" at exit, --verbose, after Haluna). A
## release binary takes no scene path, so it runs from the perf build's main scene (slice_sweep, --leak-probe):
##   hymn_perf.exe --verbose -- --leak-probe [--scene=res://...tscn] [--strip=A,B/C] [--frames=120]
## Instances --scene, frees the --strip node paths (relative to its root) before it enters the tree, runs it
## --frames frames, frees it and quits; the engine's exit report says what's still in use.

const DEFAULT_SCENE := "res://game/levels/ch02/haluna/haluna.tscn"


static func run(tree: SceneTree, opts: Dictionary) -> void:
	var packed := load(str(opts.get("scene", DEFAULT_SCENE))) as PackedScene
	# --load-only: the load and nothing else; --no-tree: instanced and freed without entering the tree.
	if opts.has("load-only"):
		packed = null
		print("LEAK_PROBE done")
		tree.quit()
		return
	var inst := packed.instantiate()
	if opts.has("no-tree"):
		inst.free()
		print("LEAK_PROBE done")
		tree.quit()
		return
	for path in str(opts.get("strip", "")).split(",", false):
		var n := inst.get_node_or_null(NodePath(path))
		print("LEAK_PROBE strip %s: %s" % [path, "freed" if n != null else "missing"])
		if n != null:
			n.get_parent().remove_child(n)
			n.free()
	# --unscript=<path>,...: the node keeps its place (other scripts' paths still resolve), without its script.
	for path in str(opts.get("unscript", "")).split(",", false):
		var n := inst if path == "." else inst.get_node_or_null(NodePath(path))
		print("LEAK_PROBE unscript %s: %s" % [path, "done" if n != null else "missing"])
		if n != null:
			n.set_script(null)
	tree.root.add_child(inst)
	for i in int(opts.get("frames", "120")):
		await tree.process_frame
	inst.queue_free()
	for i in 10:
		await tree.process_frame
	for name in str(opts.get("clear", "")).split(",", false):
		_clear(name)
	print("LEAK_PROBE done")
	tree.quit()


## --clear=<name>,...: drops one static before the quit (the bisect of what pins the class graph).
static func _clear(name: String) -> void:
	print("LEAK_PROBE clear %s" % name)
	match name:
		"shrine":
			ShrineNetwork.registry = null
			ShrineNetwork.travel = Callable()
		"flow":
			FlowRouting.busy = Callable()
			FlowRouting.next_frame = Callable()
			FlowRouting.record = Callable()
			FlowRouting._queue.clear()
		"battle_request":
			BattleRequest._pending = null
			BattleRequest.change_scene = Callable()
		"ui":
			UiSettings._shared = null
		"graphics":
			GraphicsRuntime._settings = null
			GraphicsSettings._override_settings = null
			GraphicsSettings._player_settings = null
			GraphicsSettings._override_viewport = null
			GraphicsSettings._override_stack.clear()

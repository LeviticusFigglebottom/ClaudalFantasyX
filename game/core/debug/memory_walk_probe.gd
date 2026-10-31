class_name MemoryWalkProbe
extends Node
## Process memory along a walk of zone changes (PC row 88: 5-7 GB private memory on the Act I budget walk, big18
## under 4 GB). Headless:
##   godot --headless --path . res://game/core/debug/memory_walk_probe.tscn [-- --walk=<id>,<id>,...] [--no-park]
## Each step is a location id (locations.json, SceneRouter.change_scene to its scene) or fight:<encounter>><location>
## (the fight from the current zone, returning to that location: the resident field and a parked
## return). After each step settles it prints MEMWALK <step> rss_mb=<VmRSS> static_mb=<Godot static>
## objects=<count> resources=<count> nodes=<count> orphans=<orphan nodes>. Growth that the walk never gives back
## is what to look for.

const ARG_WALK := "--walk="
const FIGHT_PREFIX := "fight:"
const FIGHT_SEP := ">"
const DEFAULT_WALK := (
	"ch02/haluna,ch03/saltgrass_causeway,ch03/shell_shrine,fight:drownbell>ch02/haluna,ch04/haluna_wake,"
	+ "ch04/brightwater_ferry,ch05/pemakar,ch06/brine_shoals,ch07/tamsule,ch08/corrow,ch02/haluna,ch08/corrow"
)
const SETTLE_FRAMES := 60
const TIMEOUT_FRAMES := 7200
const TAG := "MEMWALK"
const MB := 1048576.0
const KB_PER_MB := 1024.0
const STATUS := "/proc/self/status"


func _ready() -> void:
	if get_tree().current_scene == self:
		var driver: Node = (get_script() as GDScript).new()
		driver.name = "MemoryWalkProbeDriver"
		get_tree().root.add_child.call_deferred(driver)
		return
	_run.call_deferred()


func _run() -> void:
	var walk := DEFAULT_WALK
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with(ARG_WALK):
			walk = arg.trim_prefix(ARG_WALK)
	var registry := LocationRegistry.load_default()
	_report("start")
	for step in walk.split(","):
		if step.begins_with(FIGHT_PREFIX):
			var parts := step.trim_prefix(FIGHT_PREFIX).split(FIGHT_SEP)
			var r := BattleRequest.make(StringName(parts[0]), &"", &"")
			r.return_scene = registry.scene_of(StringName(parts[1])) if parts.size() > 1 else ""
			BattleRequest.change_scene = func(_path: String) -> void: pass
			BattleRequest.submit(r)
			BattleRequest.change_scene = Callable()
			SceneRouter.change_scene(BattleRequest.scene_path())
			await _settle()
			var frames := TIMEOUT_FRAMES
			while SceneRouter.return_park.building != "" and frames > 0:
				frames -= 1
				await get_tree().process_frame
			_report(step + " (in the fight)")
			BattleRequest.clear()
			if r.return_scene != "":
				SceneRouter.change_scene(r.return_scene)
				await _settle()
		else:
			SceneRouter.change_scene(registry.scene_of(StringName(step)))
			await _settle()
		_report(step)
	get_tree().quit()


func _settle() -> void:
	var frames := TIMEOUT_FRAMES
	while (SceneRouter.is_busy() or SceneRouter.is_measuring()) and frames > 0:
		frames -= 1
		await get_tree().process_frame
	for i in SETTLE_FRAMES:
		await get_tree().process_frame


func _report(step: String) -> void:
	var rss := -1.0
	for line in FileAccess.get_file_as_string(STATUS).split("\n"):
		if line.begins_with("VmRSS:"):
			rss = float(line.split(":")[1].strip_edges().split(" ")[0]) / KB_PER_MB
	print(
		(
			"%s %s rss_mb=%.0f static_mb=%.0f objects=%d resources=%d nodes=%d orphans=%d"
			% [
				TAG,
				step,
				rss,
				Performance.get_monitor(Performance.MEMORY_STATIC) / MB,
				Performance.get_monitor(Performance.OBJECT_COUNT),
				Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT),
				Performance.get_monitor(Performance.OBJECT_NODE_COUNT),
				Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT),
			]
		)
	)

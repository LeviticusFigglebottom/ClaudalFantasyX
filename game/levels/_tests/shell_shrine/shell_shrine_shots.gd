class_name ShellShrineShots
extends Node3D
## The Shell Shrine's composed shots S01-S05 (haluna.md §5.3; M2-ENV-03): the level with the trial
## held in one state and the five cameras (Cameras/S0n, each a HalunaShotCamera on the shot resource
## the level's own director uses). tests/screenshots/shots.json picks the state per shot through
## setup.nodes {".": {"state": ...}}; the capture writes it every frame, so applying it is idempotent.
##   "start"    as the trial opens: the water runs round b1 and b4 (S01, S02, S03)
##   "flow"     solved: b3 pours into the inner pool, which is half full (S04)
##   "drained"  the sluice reached: the side pool empty, the charm in the silt (S05)

const STATES: PackedStringArray = ["start", "flow", "drained"]
## How full the pool is in "flow" (0..1 of fill_sec).
const FLOW_FILL := 0.5
## A turn budget for the greedy solver (the shortest solution is 6; see the trial's README).
const MAX_TURNS := 16

@export var state: String = "start":
	set(value):
		state = value
		if is_node_ready():
			_apply()

var _applied := ""

@onready var level: ShellShrineLevel = $Level


func _ready() -> void:
	level.set_process(false)  # time stands still; turns and the door snap
	level.player.set_physics_process(false)
	level.player.visible = false  # the capsule stand-in; Rhen has no model in the room yet
	_apply()


func _apply() -> void:
	if state == _applied or not STATES.has(state):
		return
	_applied = state
	match state:
		"flow":
			_solve(level.trial.goal())
			level.advance(float(level.trial.data.get("fill_sec", 1.0)) * FLOW_FILL)
		"drained":
			_solve(level.trial.drain())
			level.advance(0.0)
	level.director.release(0.0)


func _solve(target: StringName) -> void:
	var guard := 0
	while not level.trial.reaches(target) and guard < MAX_TURNS:
		guard += 1
		var best := &""
		var best_n := 1 << 20
		for b in level.trial.basin_ids():
			var probe := ShellShrineTrial.new(level.trial.data)
			probe.rotations = level.trial.rotations.duplicate()
			probe.rotate(b)
			var n := probe.min_turns_to(target)
			if n >= 0 and n < best_n:
				best_n = n
				best = b
		level.trial.rotate(best)

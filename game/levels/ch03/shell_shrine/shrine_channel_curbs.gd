class_name ShrineChannelCurbs
extends RefCounted
## M2-FP-24: the channels' curbs collide (pillar 4: the water's path is the thing to read, and Rhen walked straight
## through it). Every trough gets a static box the trough's width and height along each side of a crossing at its
## middle (`crossing_m` of open floor, a step across the water), so no basin, the sluice or the door is ever walled
## off; a trough shorter than `crossing_m` + 2 x `min_m` gets none. The field controller has no step-up, so a
## curb is a wall. Data: game/data/trials/shell_shrine_curbs.json "curbs" {h, w, crossing_m, min_m} (not the trial's
## file, which feeds the GI bake's staleness check).

const DATA_PATH := "res://game/data/trials/shell_shrine_curbs.json"
const LENGTH_META := &"channel_length_m"
const BODY := "Curbs"


## The "curbs" row of DATA_PATH ({} when unreadable).
static func load_config() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	return (parsed as Dictionary).get("curbs", {}) if parsed is Dictionary else {}


## Adds the curbs under every channel node in `channels` (shared troughs once); the count of boxes built.
static func build(channels: Dictionary, cfg: Dictionary) -> int:
	var h := float(cfg.get("h", 0.0))
	var w := float(cfg.get("w", 0.0))
	var gap := float(cfg.get("crossing_m", 0.0))
	var min_m := float(cfg.get("min_m", 0.0))
	var done: Array[Node3D] = []
	var boxes := 0
	for key: Variant in channels:
		var node := channels[key] as Node3D
		if node == null or done.has(node) or not node.has_meta(LENGTH_META) or h <= 0.0:
			continue
		done.append(node)
		var length := float(node.get_meta(LENGTH_META))
		var side := (length - gap) * 0.5
		if side < min_m:
			continue
		var body := StaticBody3D.new()
		body.name = BODY
		node.add_child(body)
		for from: float in [0.0, side + gap]:  # local -Z runs down the trough
			var shape := BoxShape3D.new()
			shape.size = Vector3(w, h, side)
			var cs := CollisionShape3D.new()
			cs.shape = shape
			cs.position = Vector3(0.0, h * 0.5, -(from + side * 0.5))
			body.add_child(cs)
			boxes += 1
	return boxes

extends TestCase
## M3-ENV-702: the walk check for M3-ENV-701's set dressing, with the collision rules piece_rules gives it. A
## clutter piece's footprint is the box HalunaCollision builds for it (its rule; boxes from the mesh bounds). Down
## every lane a 3 m path stays clear (layout lane_width_m), each house's door path keeps a 1.8 m gap through the
## yard fences, and the dock keeps its walkway out to the end platform.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"
const LAYOUT := "res://game/levels/ch02/haluna/haluna_layout.json"
## The dressing M3-ENV-701 added that can stand in a path (the houses, the dock and the plants have their own rules).
const CLUTTER: Array[String] = [
	"crate_stack",
	"cargo_sacks",
	"woodpile",
	"yard_fence",
	"wayside_offering",
	"pot_plants",
	"water_jar",
	"basket_set",
	"market_stall",
	"fish_drying_rack",
	"oil_lamp_post",
	"coral_boulder_a",
	"coral_boulder_b",
	"coral_boulder_c",
	"pilgrim_marker_post",
	"pilgrim_marker_post_broken",
	"pilgrim_marker_post_leaning",
	"wreck_rib",
	"rope_coil",
	"sandals",
	"tide_debris",
	"net_heap",
	"net_float_cluster",
	"laundry_line",
]
const HOUSES: Array[String] = ["house_tile_a", "house_tile_b", "house_tile_c"]
const FENCE := "yard_fence"
const DOCK := "dock_haluna"
const SAMPLE_M := 0.5
const SCAN_M := 0.1
## The layout places to the nominal metre (a fence gap of exactly 1.8 m); boxes from mesh bounds add a few cm.
const TOLERANCE_M := 0.1
const DOOR_GAP_M := 1.8
const DOOR_RUN_M := 4.0
## The dock's deck runs along its local +X to the end platform's far rail (dock_haluna's extra_boxes).
const DOCK_RUN_M := 38.0
const DOCK_PATH_M := 0.8
## Inside the rails: the deck is 2.6 m wide, the end platform (from 33.5 m out) 4.4 m.
const DOCK_DECK_HALF_M := 1.3
const DOCK_PLATFORM_HALF_M := 2.2
const DOCK_PLATFORM_X := 33.5

var zone: HalunaZone
var collision: HalunaCollision


func before_each() -> void:
	zone = (load(ZONE) as PackedScene).instantiate() as HalunaZone
	(zone.get_node("Story") as HalunaStory).autostart = false
	_host().add_child(zone)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	collision = zone.get_node("Collision") as HalunaCollision


func _host() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _done() -> void:
	_host().remove_child(zone)
	zone.free()


## The dressed pieces of `kinds` that get collision: [kind, frame (unscaled, in the collision's frame), AABB].
func _footprints(kinds: Array[String]) -> Array:
	var out := []
	for child in collision.dresser.get_children():
		var piece := child as Node3D
		if piece == null or piece is MultiMeshInstance3D:
			continue
		var kind := HalunaCollision.piece_kind(piece)
		if not kind in kinds:
			continue
		var rule: Dictionary = collision.piece_rules.get(kind, collision.default_rule)
		if str(rule.get("shape", HalunaCollision.KIND_BOX)) == HalunaCollision.KIND_NONE:
			continue
		var inset := float(rule.get("inset_m", 0.0))
		var box := HalunaCollision.local_bounds(piece).grow(-inset)
		var frame := HalunaCollision.frame_in(piece, collision.get_parent()).orthonormalized()
		out.append([kind, frame, box])
	return out


## The flat distance from (x, z) to a footprint (0 inside it).
func _distance(at: Vector2, fp: Array) -> float:
	var frame := fp[1] as Transform3D
	var box := fp[2] as AABB
	var local := frame.affine_inverse() * Vector3(at.x, frame.origin.y, at.y)
	var near := Vector2(clampf(local.x, box.position.x, box.end.x), clampf(local.z, box.position.z, box.end.z))
	return near.distance_to(Vector2(local.x, local.z))


## The first footprint within `radius` of `at`, else [].
func _blocker(at: Vector2, radius: float, fps: Array) -> Array:
	for fp: Array in fps:
		if _distance(at, fp) < radius:
			return fp
	return []


func test_every_lane_keeps_a_clear_path() -> void:
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(LAYOUT))
	var width := float(layout["terrain"].get("lane_width_m", 3.0))
	var fps := _footprints(CLUTTER)
	assert_true(fps.size() > 20, "the clutter has collision (%d pieces)" % fps.size())
	for li in (layout["lanes"] as Array).size():
		var lane: Array = layout["lanes"][li]
		var narrowest := INF
		var where := Vector2.ZERO
		for i in lane.size() - 1:
			var a := Vector2(lane[i][0], lane[i][1])
			var b := Vector2(lane[i + 1][0], lane[i + 1][1])
			var across := (b - a).normalized().orthogonal()
			var steps := maxi(1, ceili(a.distance_to(b) / SAMPLE_M))
			for s in steps + 1:
				var p := a.lerp(b, float(s) / steps)
				var w := _clear_width(p, across, width, width * 0.5, fps)
				if w < narrowest:
					narrowest = w
					where = p
		assert_true(narrowest >= width - TOLERANCE_M, "lane %d narrows to %.2f m at %s" % [li, narrowest, where])
	_done()


## The widest clear run across a path at `p` (along `across`, scanning `reach` either side of the line) that
## passes within `band` of the line: the way a walker can take past the clutter there.
func _clear_width(p: Vector2, across: Vector2, reach: float, band: float, fps: Array) -> float:
	var near := []
	for fp: Array in fps:
		if _distance(p, fp) < reach * 2.0:
			near.append(fp)
	var best := 0.0
	var run_from := INF
	var steps := ceili(reach * 2.0 / SCAN_M)
	for k in steps + 1:
		var off := -reach + k * SCAN_M
		var free := _blocker(p + across * off, 0.0001, near).is_empty()
		if free and run_from == INF:
			run_from = off
		var end := not free or k == steps
		if end and run_from != INF:
			var run_to := off if not free else off + SCAN_M
			if run_from <= band and run_to >= -band:
				best = maxf(best, run_to - run_from)
			run_from = INF
	return best


func test_every_door_path_keeps_its_gap_through_the_fences() -> void:
	var fences := _footprints([FENCE])
	assert_true(fences.size() > 0, "the yard fences have collision")
	var doors := 0
	for child in collision.dresser.get_children():
		var house := child as Node3D
		if house == null or not HalunaCollision.piece_kind(house) in HOUSES:
			continue
		var frame := HalunaCollision.frame_in(house, collision.get_parent()).orthonormalized()
		var box := HalunaCollision.local_bounds(house)
		doors += 1
		var steps := ceili(DOOR_RUN_M / SAMPLE_M)
		for s in steps + 1:
			var local := Vector3(box.get_center().x, 0.0, box.end.z + s * SAMPLE_M)
			var w := frame * local
			var hit := _blocker(Vector2(w.x, w.z), DOOR_GAP_M * 0.5 - TOLERANCE_M, fences)
			assert_true(hit.is_empty(), "%s's door path is fenced at %s" % [house.name, Vector2(w.x, w.z)])
			if not hit.is_empty():
				break
	assert_true(doors > 20, "every house checked (%d)" % doors)
	_done()


func test_the_dock_keeps_its_walkway() -> void:
	var fps := _footprints(CLUTTER)
	var dock: Node3D = null
	for child in collision.dresser.get_children():
		if child is Node3D and HalunaCollision.piece_kind(child) == DOCK:
			dock = child
	assert_true(dock != null, "the dock")
	var frame := HalunaCollision.frame_in(dock, collision.get_parent()).orthonormalized()
	var o := frame * Vector3.ZERO
	var along := frame * Vector3.RIGHT - o
	var across := Vector2(along.x, along.z).normalized().orthogonal()
	var steps := ceili(DOCK_RUN_M / SAMPLE_M)
	for s in steps + 1:
		var x := s * SAMPLE_M
		var w := frame * Vector3(x, 0.0, 0.0)
		var reach := DOCK_PLATFORM_HALF_M if x >= DOCK_PLATFORM_X else DOCK_DECK_HALF_M
		var clear := _clear_width(Vector2(w.x, w.z), across, reach, reach, fps)
		assert_true(clear >= DOCK_PATH_M, "the dock narrows to %.2f m at %.1f m out" % [clear, x])
		if clear < DOCK_PATH_M:
			break
	_done()

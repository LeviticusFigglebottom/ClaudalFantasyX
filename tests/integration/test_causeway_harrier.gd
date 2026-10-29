extends TestCase
## The Lead's framing review (big12): C07 ("the flier against the cumulus") showed no flier. The gull harrier now
## circles ahead of its fight: its own model on its idle loop, every point of its circle inside C07's frame and above
## the horizon, and gone once the fight is won.

const ZONE := "res://game/levels/ch03/saltgrass_causeway/saltgrass_causeway.tscn"
const LAYOUT := "res://game/levels/ch03/saltgrass_causeway/saltgrass_causeway_layout.json"
const SHOT := "C07"
const WON := &"ch03_harrier_won"
const ASPECT := 16.0 / 9.0
const SAMPLES := 16
## Keep the bird off the frame's edges and out of the bottom band the dialogue box and the toasts use.
const MARGIN := 0.85

var saved: GameStateData


func before_each() -> void:
	saved = Game.state
	Game.state = GameStateData.new()


func _zone() -> Node3D:
	var zone := (load(ZONE) as PackedScene).instantiate() as Node3D
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(zone)
	return zone


func _done(zone: Node3D) -> void:
	zone.get_parent().remove_child(zone)
	zone.free()
	Game.state = saved


func _shot() -> Dictionary:
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(LAYOUT))
	for key: String in layout:
		if layout[key] is Array:
			for row: Variant in layout[key]:
				if row is Dictionary and str((row as Dictionary).get("id", "")) == SHOT and row.has("look_at"):
					return row
	return {}


func test_the_harrier_circles_in_c07_until_it_is_beaten() -> void:
	var zone := _zone()
	var harrier := zone.get_node(^"Harrier") as CausewayHarrier
	assert_true(harrier.visible and harrier.model != null, "it flies before the fight")
	var shot := _shot()
	assert_false(shot.is_empty(), "C07 is in the layout")
	var pos := Vector3(shot["pos"][0], shot["pos"][1], shot["pos"][2])
	var look := Vector3(shot["look_at"][0], shot["look_at"][1], shot["look_at"][2])
	var cam := Transform3D(Basis.looking_at(look - pos, Vector3.UP), pos)
	var half_v := tan(deg_to_rad(float(shot["fov"])) * 0.5)
	for k in SAMPLES:
		harrier.place(harrier.period_sec * k / SAMPLES)
		var local := cam.affine_inverse() * harrier.model.global_position
		assert_true(local.z < 0.0, "in front of the camera")
		var sx := (local.x / -local.z) / (half_v * ASPECT)
		var sy := (local.y / -local.z) / half_v
		assert_true(
			absf(sx) < MARGIN and sy > 0.0 and sy < MARGIN, "in C07's sky at step %d (%.2f, %.2f)" % [k, sx, sy]
		)
		assert_true(harrier.model.global_position.y > pos.y, "above the camera's horizon")
	_done(zone)


func test_it_is_gone_once_the_fight_is_won() -> void:
	Game.set_flag(WON)
	var zone := _zone()
	var harrier := zone.get_node(^"Harrier") as CausewayHarrier
	assert_false(harrier.visible, "the harrier fell")
	assert_true(harrier.model == null, "nothing loaded")
	_done(zone)

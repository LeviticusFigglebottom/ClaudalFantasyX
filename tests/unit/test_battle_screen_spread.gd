extends TestCase
## Creatures' as-played audit (10-30, pillar 4): foes seated one behind the other overlapped on the rest frame (the
## tideline's Eel and Crab, the stair's Tortoises, the tower's Wickfry, the fen's Root Crabs), and the underway fights'
## bottom-left foe sat under the command menu. BattleScreenSpread (choreo.json spacing.screen) spreads them at spawn.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const FIGHTS: Array[StringName] = [
	&"ch02_tideline",
	&"ch05_stair_tortoises",
	&"ch06_flats_crabs",
	&"ch01_underway_shoals",
	&"ch01_underway_limpet",
	&"ch10_fen_roots",
	&"ch03_causeway_shore",
]
## Room over max_share for a pair the cap (max_shift_m) stops short.
const SLACK := 0.05


func test_no_two_foes_cover_each_other_or_the_command_menu_at_rest() -> void:
	var sc := (BattleChoreo.load_data()["spacing"] as Dictionary)["screen"] as Dictionary
	var avoid := BattleScreenSpread.menu_rect(BattleChoreo.load_data())
	var db := BattleDB.load_default()
	for enc in FIGHTS:
		if not db.encounters.has(enc):
			continue
		var ctl := (load(SANDBOX) as PackedScene).instantiate() as BattleController
		ctl.auto_start = false
		ctl.pacing_scale = 0.0
		ctl.persist_progress = false
		var tree := Engine.get_main_loop() as SceneTree
		(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
		ctl.start_battle([&"rhen", &"asha", &"toma"] as Array[StringName], [] as Array[StringName], enc, 20261030)
		var dir := ctl.stage.choreo.camera
		var lens := (ctl.stage.camera.get_parent() as Node3D).global_transform * dir.default_transform
		var boxes: Array[Rect2] = []
		for e in ctl.engine.enemies:
			var f := ctl.stage.stand_in(e.id)
			var b := BattleScreenSpread.screen_box(
				lens, dir.rest_fov(), BattleScreenSpread._shape(f), f.global_position
			)
			boxes.append(b)
			assert_false(b.intersects(avoid), "%s: %s clear of the command menu" % [enc, e.id])
		for i in boxes.size():
			for j in range(i + 1, boxes.size()):
				var s := BattleScreenSpread.share(boxes[i], boxes[j])
				assert_true(s <= float(sc["max_share"]) + SLACK, "%s: foes %d and %d share %.2f" % [enc, i, j, s])
		ctl.get_parent().remove_child(ctl)
		ctl.free()


func test_two_boxes_share_the_smaller_ones_part() -> void:
	var a := Rect2(0, 0, 100, 100)
	assert_between(BattleScreenSpread.share(a, Rect2(50, 0, 10, 10)), 0.999, 1.001, "inside the bigger: all of it")
	assert_between(BattleScreenSpread.share(a, Rect2(90, 0, 20, 100)), 0.499, 0.501)
	assert_eq(BattleScreenSpread.share(a, Rect2(200, 0, 10, 10)), 0.0)


## The sweep (ch04_derelict_leeches): Ilun's net reached under the timeline. A body on a HUD rect steps toward the
## screen's left until clear, at most hud_shift_m.
func test_a_body_on_the_hud_steps_left_until_clear() -> void:
	var ctl := (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_battle([&"rhen"] as Array[StringName], [] as Array[StringName], &"ch02_tideline", 20261030)
	var data := BattleChoreo.load_data()
	var cap := float(((data["spacing"] as Dictionary)["screen"] as Dictionary)["hud_shift_m"])
	var f := ctl.stage.stand_in(&"rhen")
	var dir := ctl.stage.choreo.camera
	var lens := (ctl.stage.camera.get_parent() as Node3D).global_transform * dir.default_transform
	var home := f.global_position
	var box := BattleScreenSpread.screen_box(lens, dir.rest_fov(), BattleScreenSpread._shape(f), home)
	var cover := Rect2(box.position.x + box.size.x * 0.5, 0.0, 1920.0, 1080.0)  # over the body's right half
	BattleScreenSpread.clear_of_hud(f, ctl.stage.camera, dir.default_transform, dir.rest_fov(), [cover], data)
	var moved := f.global_position.distance_to(home)
	assert_true(moved > 0.0 and moved <= cap + 0.01, "it stepped left, at most the cap (%.2f m)" % moved)
	var after := BattleScreenSpread.screen_box(lens, dir.rest_fov(), BattleScreenSpread._shape(f), f.global_position)
	assert_true(after.get_center().x < box.get_center().x, "to the screen's left")
	assert_true(not after.intersects(cover) or moved >= cap - 0.11, "clear, or at the cap")
	ctl.get_parent().remove_child(ctl)
	ctl.free()

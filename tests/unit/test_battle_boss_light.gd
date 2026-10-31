extends TestCase
## The PC's GPU QA row 61: the Undertow's Reach was a dark mass at its rest frame. A boss with an effects.json
## boss_rim_lights row is lit at spawn (BattleBossLight): its lights are its stand-in's children, in a light_color
## palette swatch, a rim behind it as the camera sees it and a key on the lens's side; a foe with no row gets none.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const PALETTE := "res://docs/kb/art/palette.json"


func test_the_reach_is_lit_rim_and_key() -> void:
	var ctl := (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_battle(
		[&"rhen", &"asha", &"liss"] as Array[StringName], [] as Array[StringName], &"undertows_reach", 20261031
	)
	var reach: FighterStandIn = null
	for e in ctl.engine.enemies:
		if String(e.id).begins_with("undertows_reach"):
			reach = ctl.stage.stand_in(e.id)
	assert_true(reach != null, "the Reach stands")
	var lights := reach.find_children("BossRimLight*", "OmniLight3D", false, false)
	assert_eq(lights.size(), 2, "a rim and a key")
	var cam := ctl.stage.camera.global_position
	var near := INF
	var far := -INF
	for l in lights:
		var d := (l as Node3D).global_position.distance_to(cam)
		near = minf(near, d)
		far = maxf(far, d)
	assert_true(far - near > 5.0, "one behind the Reach, one on the lens's side")
	for e in ctl.engine.enemies:
		if not String(e.id).begins_with("undertows_reach"):
			assert_eq(
				ctl.stage.stand_in(e.id).find_children("BossRimLight*", "", false, false).size(), 0, "no row, no light"
			)
	ctl.get_parent().remove_child(ctl)
	ctl.free()


func test_each_light_is_a_light_color_swatch() -> void:
	var palette := JSON.parse_string(FileAccess.get_file_as_string(PALETTE)) as Dictionary
	var swatches := {}
	_collect(palette, swatches)
	var rows := BattleVfx.load_data().get("boss_rim_lights", {}) as Dictionary
	for bid: String in rows:
		if bid == "doc":
			continue
		var row := rows[bid] as Dictionary
		var sw := swatches.get(str(row["swatch"]), {}) as Dictionary
		assert_eq(str(sw.get("input_kind", "")), "light_color", "%s: a light_color swatch" % bid)
		for l: Dictionary in row["lights"]:
			assert_eq(
				str(l["color"]).to_upper(),
				str(sw.get("hex", "")).to_upper(),
				"%s: its light is %s" % [bid, row["swatch"]]
			)


static func _collect(x: Variant, out: Dictionary) -> void:
	if x is Dictionary:
		for k: Variant in x:
			var v: Variant = (x as Dictionary)[k]
			if v is Dictionary and (v as Dictionary).has("hex"):
				out[str(k)] = v
			_collect(v, out)
	elif x is Array:
		for v: Variant in x:
			_collect(v, out)

extends TestCase
## M3-BPR-409, the Pillar 4 clarity pass: the player always knows who acts next and whom an action hits, even under
## a cinematic or heavy VFX. The order (timeline) and the party panel stay on screen through a boss intro; the target
## ring draws after ground VFX (render_priority from battle_sandbox.json ring).

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261027

var ctl: BattleController


func _start(encounter: StringName, party: Array[StringName]) -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	ctl.show_damage_numbers = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var none: Array[StringName] = []
	ctl.start_battle(party, none, encounter, SEED)


func test_the_order_stays_on_screen_through_a_boss_intro() -> void:
	var party: Array[StringName] = [&"rhen"]
	_start(&"ch01_hullgnaw", party)
	var intro := BattleBossIntro.of(ctl.stage)
	intro.live = false
	intro.force_play = true
	intro.play()
	intro.advance(float(intro.cfg["camera_in_sec"]) + float(intro.row["hold_sec"]) * 0.5)
	assert_true(intro.playing(), "mid-intro")
	assert_true(ctl.hud.timeline.is_visible_in_tree(), "who acts next stays on screen")
	assert_true(ctl.hud.party.is_visible_in_tree(), "and the party panel")
	_free()


func test_the_target_ring_draws_over_ground_vfx() -> void:
	var party: Array[StringName] = [&"rhen", &"asha"]
	_start(&"sandbox_reef", party)
	var want := int((BattleStage.config()["ring"] as Dictionary)["render_priority"])
	assert_true(want > 0, "above the default transparent order")
	for c in ctl.engine.enemies + ctl.engine.party_active:
		var f := ctl.stage.stand_in(c.id)
		assert_eq(f._ring_mat.render_priority, want, "%s's ring" % c.id)
	_free()


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()

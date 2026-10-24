extends TestCase
## M3-BPR-02: boss intros. Every Act I boss encounter and the Drownbell has a row whose loc keys exist and whose
## shot frames its boss; the first turn waits for the intro (no enemy acts, the command menu stays hidden); it waits
## for the router's fade and the opening banner; confirm skips it; at instant pacing or with skip animations it never
## plays; reduced motion keeps the camera on the default and the card only fades; the camera is home at the end; a
## retry skips it unless the row says on_retry; the card stays clear of the timeline and the HUD panels.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const EPS := 0.001
const BOSSES := {
	&"ch01_hullgnaw": [&"rhen"],
	&"ch04_bottle_hermit": [&"rhen", &"asha", &"toma"],
	&"ch04_spar_wraith": [&"rhen", &"asha", &"toma"],
	&"ch05_cinder_matron": [&"rhen", &"asha", &"toma"],
	&"drownbell": [&"rhen", &"asha", &"toma"],
}
const SEED := 20261024

var ctl: BattleController
var cfg: Dictionary


func before_each() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	ctl.show_damage_numbers = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	cfg = BattleChoreo.load_data()["boss_intro"] as Dictionary


func _start(encounter: StringName, pacing: float) -> BattleBossIntro:
	ctl.pacing_scale = pacing
	var party: Array[StringName] = []
	party.assign(BOSSES[encounter] as Array)
	var none: Array[StringName] = []
	ctl.start_battle(party, none, encounter, SEED)
	var intro := BattleBossIntro.of(ctl.stage)
	intro.live = false
	ctl.stage.choreo.live = false
	return intro


func _total(intro: BattleBossIntro) -> float:
	return intro.total_sec() / ctl.stage.choreo.speed


# --- data -----------------------------------------------------------------------------------


func test_every_boss_encounter_has_a_row_with_real_keys() -> void:
	var rows := cfg["rows"] as Dictionary
	var db := BattleDB.load_default()
	for enc: StringName in BOSSES:
		assert_true(rows.has(String(enc)), "%s has an intro row" % enc)
		var row := rows[String(enc)] as Dictionary
		assert_true(db.enemies.has(StringName(str(row["enemy"]))), "%s names an enemy" % enc)
		for key: String in ["title_key", "epithet_key"]:
			var k := str(row[key])
			assert_ne(TranslationServer.translate(k), k, "%s %s is translated" % [enc, key])
		assert_false(bool(row.get("on_retry", false)), "Fight again skips it by default")
	_free()


func test_each_row_frames_its_boss() -> void:
	for enc: StringName in BOSSES:
		var intro := _start(enc, 0.0)
		assert_false(intro.holding(), "%s: instant pacing plays nothing" % enc)
		intro.force_play = true
		intro.play()
		assert_true(intro.playing(), "%s plays when forced" % enc)
		assert_eq(intro.shot_id, str(intro.row["shot"]), "%s: the shot frames the boss (safe frame)" % enc)
		assert_eq(String(intro.boss_id).get_slice("#", 0), str(intro.row["enemy"]))
		intro.skip()
	_free()


func test_the_card_stays_clear_of_the_timeline_and_the_panels() -> void:
	var card := HudLayout.rect_of(cfg["card"] as Dictionary)
	for sec: StringName in [&"timeline", &"party", &"help_line", &"target_info", &"opening_banner"]:
		assert_false(card.intersects(HudLayout.rect_of(HudLayout.section(sec))), "the card is clear of %s" % sec)
	_free()


# --- the first turn waits -----------------------------------------------------------------


func test_the_first_turn_waits_for_it() -> void:
	var intro := _start(&"ch01_hullgnaw", 1.0)
	assert_true(intro.playing(), "it plays at the first turn")
	assert_true(ctl.hud.holds_battle(), "it holds the battle")
	assert_eq(ctl.hud.commands.modulate.a, 0.0, "a party turn's menu stays hidden")
	var acted: Array[int] = [0]
	ctl.engine.action_resolved.connect(func(_r: ActionResult) -> void: acted[0] += 1)
	var first := ctl.engine.current
	ctl.tick(30.0)
	assert_eq(acted[0], 0, "nobody acts while it plays")
	assert_eq(ctl.engine.current, first, "the first turn is still the first")
	intro.advance(_total(intro) + EPS)
	assert_true(intro.done(), "it ends on its own")
	assert_false(ctl.hud.holds_battle(), "the battle goes on")
	assert_eq(ctl.hud.commands.modulate.a, 1.0, "the menu is back")
	assert_true(ctl.stage.choreo.camera.at_default(), "the camera is home")
	_free()


func test_it_waits_for_the_fade_and_the_banner() -> void:
	var intro := _start(&"ch01_hullgnaw", 0.0)
	ctl.pacing_scale = 1.0
	var covered: Array[bool] = [true]
	intro.screen_covered = func() -> bool: return covered[0]
	intro._on_first_turn(ctl.engine.current)
	assert_true(intro.holding() and not intro.playing(), "it waits while the screen is covered")
	assert_true(ctl.hud.holds_battle())
	intro.advance(0.5)
	assert_false(intro.playing())
	covered[0] = false
	intro.advance(0.0)
	assert_true(intro.playing(), "it plays once the screen is uncovered")
	intro.skip()
	var banner := ctl.hud.opening_banner()
	banner.show_opening(OpeningBanner.KIND_AMBUSH, false)
	ctl.remove_meta(BattleBossIntro.META_PLAYED)
	intro._on_first_turn(ctl.engine.current)
	assert_false(intro.playing(), "it waits for the opening banner")
	banner.hide_banner()
	intro.advance(0.0)
	assert_true(intro.playing(), "then plays")
	intro.skip()
	covered[0] = true
	ctl.remove_meta(BattleBossIntro.META_PLAYED)
	intro._on_first_turn(ctl.engine.current)
	intro.advance(float(cfg["reveal_wait_max_sec"]) + EPS)
	assert_true(intro.playing(), "it gives up waiting at its cap")
	_free()


func test_confirm_skips_it() -> void:
	var intro := _start(&"ch01_hullgnaw", 1.0)
	intro.advance(float(cfg["camera_in_sec"]))
	assert_true(intro.card() != null, "the card shows")
	var ev := InputEventAction.new()
	ev.action = &"ui_accept"
	ev.pressed = true
	intro._input(ev)
	assert_true(intro.done(), "confirm skips it")
	assert_true(intro.card() == null, "the card is gone")
	assert_true(ctl.stage.choreo.camera.at_default(), "the camera is home")
	assert_false(ctl.hud.holds_battle())
	_free()


# --- instant, reduced motion, retry ---------------------------------------------------------


func test_instant_pacing_and_skip_animations_play_none() -> void:
	var intro := _start(&"ch01_hullgnaw", 0.0)
	assert_false(intro.holding(), "instant pacing")
	assert_false(ctl.hud.holds_battle())
	assert_true(ctl.stage.choreo.camera.at_default())
	ctl.pacing_scale = 1.0
	ctl.remove_meta(BattleBossIntro.META_PLAYED)
	assert_true(intro.wants_play())
	ctl.stage.choreo.skip = true
	assert_false(intro.wants_play(), "skip animations")
	intro.force_play = true
	assert_true(intro.wants_play(), "a capture forces it")
	_free()


func test_reduced_motion_keeps_the_camera_and_the_card_only_fades() -> void:
	var intro := _start(&"ch01_hullgnaw", 0.0)
	ctl.stage.choreo.reduced_motion = true
	intro.force_play = true
	intro.play()
	var at := float(cfg["card_at_sec"]) + float(cfg["card_in_sec"]) * 0.5
	intro.advance(at)
	assert_true(ctl.stage.choreo.camera.at_default(), "reduced motion keeps the default")
	var a := intro.card().modulate.a
	assert_true(a > 0.0 and a < 1.0, "the card fades in")
	var rest := HudLayout.rect_of(cfg["card"] as Dictionary).position.y
	assert_between(intro.card().position.y, rest - EPS, rest + EPS, "no rise")
	_free()


func test_the_camera_frames_the_boss_and_comes_home() -> void:
	var intro := _start(&"ch01_hullgnaw", 0.0)
	intro.force_play = true
	intro.play()
	intro.advance(float(cfg["camera_in_sec"]) + float(intro.row["hold_sec"]) * 0.5)
	assert_false(ctl.stage.choreo.camera.at_default(), "the camera is on the boss")
	assert_between(intro.card().modulate.a, 1.0 - EPS, 1.0 + EPS, "the card is fully shown mid-hold")
	assert_eq(intro.title_text(), str(TranslationServer.translate(str(intro.row["title_key"]))))
	assert_eq(intro.epithet_text(), str(TranslationServer.translate(str(intro.row["epithet_key"]))))
	intro.advance(_total(intro))
	assert_true(intro.done())
	assert_true(ctl.stage.choreo.camera.at_default(), "home at the end")
	_free()


func test_a_retry_skips_it_unless_the_row_says_so() -> void:
	var intro := _start(&"ch01_hullgnaw", 1.0)
	assert_true(intro.playing())
	intro.skip()
	var again := _start(&"ch01_hullgnaw", 1.0)
	assert_ne(again, intro, "a retry builds a new intro")
	assert_false(again.holding(), "Fight again skips it")
	assert_false(ctl.hud.holds_battle())
	again.row = again.row.duplicate()
	again.row["on_retry"] = true
	assert_true(again.wants_play(), "unless the row says on_retry")
	_free()


func test_an_encounter_without_a_row_has_no_intro() -> void:
	ctl.pacing_scale = 1.0
	var party: Array[StringName] = [&"rhen", &"asha"]
	var none: Array[StringName] = []
	ctl.start_battle(party, none, &"ch02_tideline", SEED)
	var intro := BattleBossIntro.of(ctl.stage)
	assert_true(intro.row.is_empty())
	assert_false(intro.holding())
	assert_false(ctl.hud.holds_battle())
	_free()


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()

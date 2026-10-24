extends TestCase
## M2-BPR-08: C10, a Vowbound's first call as an in-battle cinematic. Only the first call of a live story battle
## (the seen-flag unset) plays it, and it sets the flag; the "short" setting, a capture fixture, instant pacing and
## later calls play the short entry. It rises slower in steady bound light, the camera eases to the summon frame and
## home again, reduced motion keeps the camera still, the hand-off waits for it, and confirm skips it.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const EPS := 0.001
const ILUN := &"ilun"
const FLAG := &"ch03_ilun_first_call_seen"

var ctl: BattleController
var choreo: BattleChoreo
var cfg: Dictionary
var _flag_was: Variant


func before_each() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	cfg = BattleChoreo.load_data()["summon_cinematic"] as Dictionary
	_flag_was = Game.get_flag(FLAG)
	Game.set_flag(FLAG, false)
	ctl.start_fixture(BattleFixture.load_fixture(&"choreo_vowbound_rise"))
	choreo = ctl.stage.choreo
	choreo.live = false
	choreo.summon.live = false
	choreo.reduced_motion = false
	choreo.skip = false
	choreo.speed = 1.0


func test_data_names_a_declared_flag_and_a_bound_light() -> void:
	assert_eq(choreo.summon.first_call_flag(ILUN), FLAG)
	assert_eq(choreo.summon.first_call_flag(&"rhen"), &"", "only Vowbound have a first call")
	var palette := JSON.parse_string(FileAccess.get_file_as_string("res://docs/kb/art/palette.json")) as Dictionary
	var bound := ((palette["swatches"] as Dictionary)["glimmer_bound"] as Dictionary)["hex"] as String
	assert_eq(str(cfg["light_color"]).to_upper(), bound.to_upper(), "bound light (color script C10)")
	assert_true(float(cfg["entry"]["sec"]) > float(BattleChoreo.load_data()["vowbound"]["entry"]["sec"]), "slower")
	_free()


func test_a_capture_fixture_or_instant_pacing_plays_the_short_entry() -> void:
	_to_turn_of(&"asha")
	assert_false(choreo.summon.wants_full(ILUN), "instant pacing")
	ctl.pacing_scale = 1.0
	assert_false(choreo.summon.wants_full(ILUN), "a fixture is never the live story")
	choreo.summon.force_full = true
	assert_true(choreo.summon.wants_full(ILUN), "its capture forces it")
	_free()


func test_the_first_live_call_plays_in_full_once_and_sets_the_flag() -> void:
	_to_turn_of(&"asha")
	ctl.pacing_scale = 1.0
	_go_live()
	assert_true(choreo.summon.wants_full(ILUN))
	assert_true(ctl.vow.call_vowbound(ILUN))
	assert_true(choreo.summon.playing(), "the cinematic plays")
	assert_eq(choreo.entering(ILUN)["spec"], cfg["entry"], "the full entrance")
	assert_true(bool(Game.get_flag(FLAG)), "seen")
	assert_false(choreo.summon.wants_full(ILUN), "the next call is short")
	assert_true(ctl.stage.hold_after(0.0) >= choreo.summon.total_sec() - EPS, "the hand-off waits for it")
	_free()


func test_the_three_settings() -> void:
	_to_turn_of(&"asha")
	ctl.pacing_scale = 1.0
	_go_live()
	var s := UiSettings.shared()
	var was: Variant = s.get_value(BattleSummonCinematic.SETTING)
	s.set_value(BattleSummonCinematic.SETTING, BattleSummonCinematic.SETTING_SHORT)
	assert_true(choreo.summon.wants_full(ILUN), "short: the first call in full")
	Game.set_flag(FLAG, true)
	assert_false(choreo.summon.wants_full(ILUN), "short: shortened after")
	s.set_value(BattleSummonCinematic.SETTING, BattleSummonCinematic.SETTING_FULL)
	assert_true(choreo.summon.wants_full(ILUN), "full: every call")
	s.set_value(BattleSummonCinematic.SETTING, BattleSummonCinematic.SETTING_OFF)
	assert_false(choreo.summon.wants_full(ILUN), "off: never")
	assert_eq(choreo.summon.entry_for(ILUN), cfg["off_entry"], "off: no rise")
	assert_true(ctl.vow.call_vowbound(ILUN))
	choreo.advance(0.0)
	assert_false(choreo.is_entering(ILUN), "Ilun is simply there")
	s.set_value(BattleSummonCinematic.SETTING, was)
	_free()


func test_bound_light_and_camera_ease_in_and_home_again() -> void:
	_to_turn_of(&"asha")
	ctl.pacing_scale = 1.0
	choreo.summon.force_full = true
	var cam := ctl.stage.camera
	var home := cam.transform
	ctl.vow.call_vowbound(ILUN)
	var light := choreo.summon.light()
	assert_true(light != null and light.light_energy == 0.0, "dark at first")
	choreo.summon.advance(float(cfg["light_at_sec"]) + float(cfg["light_in_sec"]) * 0.5)
	assert_between(light.light_energy, EPS, float(cfg["light_energy"]) - EPS, "fading in")
	assert_false(cam.transform.is_equal_approx(home), "the camera moved to the summon frame")
	var e1 := light.light_energy
	choreo.summon.advance(float(cfg["light_in_sec"]))
	assert_between(
		light.light_energy, float(cfg["light_energy"]) - EPS, float(cfg["light_energy"]) + EPS, "then steady"
	)
	assert_true(light.light_energy >= e1)
	choreo.summon.advance(choreo.summon.total_sec())
	assert_false(choreo.summon.playing())
	assert_true(cam.transform.is_equal_approx(home), "home again")
	assert_between(light.light_energy, float(cfg["light_energy"]) - EPS, float(cfg["light_energy"]) + EPS, "it stays")
	_free()


func test_reduced_motion_keeps_the_camera_still() -> void:
	_to_turn_of(&"asha")
	ctl.pacing_scale = 1.0
	choreo.summon.force_full = true
	choreo.reduced_motion = true
	var home := ctl.stage.camera.transform
	ctl.vow.call_vowbound(ILUN)
	choreo.summon.advance(float(cfg["camera_in_sec"]))
	assert_true(ctl.stage.camera.transform.is_equal_approx(home))
	_free()


func test_confirm_skips_it() -> void:
	_to_turn_of(&"asha")
	ctl.pacing_scale = 1.0
	choreo.summon.force_full = true
	ctl.vow.call_vowbound(ILUN)
	choreo.summon.advance(0.5)
	choreo.summon.skip()
	assert_false(choreo.summon.playing())
	assert_false(choreo.is_entering(ILUN), "Ilun stands on his mark")
	assert_true(ctl.stage.stand_in(ILUN).visible)
	_free()


func _go_live() -> void:
	ctl.persist_progress = true
	ctl.fixture = null


func _to_turn_of(cid: StringName) -> void:
	var guard := 0
	while ctl.current_actor_id() != cid and guard < 16:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])


func _free() -> void:
	Game.set_flag(FLAG, _flag_was)
	ctl.persist_progress = false
	ctl.get_parent().remove_child(ctl)
	ctl.free()

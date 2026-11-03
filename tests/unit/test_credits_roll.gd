extends TestCase
## M5-A3P-1700: the closing credits (CreditsRollModel, CreditsRoll). The roll is timed to its data, stops and fades for
## a vignette (once), runs faster while Confirm is held, can be skipped only once seen in full, and ends by setting
## credits_seen and opening the next scene. Driven by advance() with the inputs given, and once by a held pad button.

const VIGNETTE_FIXTURE := "res://tests/fixtures/credits/vignette_fixture.tscn"

var scenes: Array[String] = []
var flags: Array[StringName] = []
var made: Array[Node] = []


func before_each() -> void:
	InputDriver.clear_screen()
	UiSettings.set_shared(UiSettings.new())
	scenes = []
	flags = []


func after_each() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()
	UiSettings.set_shared(null)


func test_the_roll_runs_its_data_s_time_with_the_vignette_once() -> void:
	var m := CreditsRollModel.new(_with_vignette_scene())
	var d := m.data
	assert_true(m.rows().size() >= 6, "titles and lines")
	assert_eq(m.alpha(), 0.0, "black first")
	m.advance(float(d["lead_in_sec"]) + 0.01)
	assert_eq(m.phase, CreditsRollModel.Phase.ROLL)
	var vid := &""
	var guard := 0
	while vid == &"" and guard < 100000:
		guard += 1
		vid = m.advance(0.5)
	var v := (d["vignettes"] as Array)[0] as Dictionary
	assert_eq(vid, StringName(str(v["id"])), "the vignette starts at its point")
	assert_between(m.progress, float(v["at"]) - 0.0001, float(v["at"]) + 0.0001)
	m.advance(float(d["fade_sec"]) + 0.01)
	assert_eq(m.alpha(), 0.0, "the roll is out while it plays")
	var at := m.progress
	m.advance(float(v["hold_sec"]) * 0.5, true)
	assert_eq(m.progress, at, "and it holds there, fast or not")
	m.advance(float(v["hold_sec"]))
	assert_eq(m.phase, CreditsRollModel.Phase.ROLL, "then the roll goes on")
	guard = 0
	while not m.is_done() and guard < 100000:
		guard += 1
		assert_eq(m.advance(0.5), &"", "the vignette never comes again")
	assert_true(m.is_done())
	assert_between(m.progress, 1.0 - 0.0001, 1.0 + 0.0001)


func test_confirm_runs_it_faster_and_cancel_skips_only_once_seen() -> void:
	var slow := CreditsRollModel.new()
	var fast := CreditsRollModel.new()
	for m in [slow, fast]:
		m.advance(float(m.data["lead_in_sec"]) + 0.01)
	slow.advance(1.0)
	fast.advance(1.0, true)
	assert_between(
		fast.progress,
		slow.progress * float(slow.data["fast_factor"]) - 0.0001,
		slow.progress * float(slow.data["fast_factor"]) + 0.0001
	)
	var first := CreditsRollModel.new({}, false)
	first.advance(float(first.data["skip_hold_sec"]) * 4.0, false, true)
	assert_false(first.is_done(), "the first time, Cancel doesn't skip")
	var again := CreditsRollModel.new({}, true)
	again.advance(float(again.data["skip_hold_sec"]) * 0.5, false, true)
	assert_false(again.is_done(), "a tap isn't a skip")
	again.advance(float(again.data["skip_hold_sec"]), false, true)
	assert_true(again.is_done(), "held long enough, once seen: skipped")


func test_the_view_climbs_fades_for_the_vignette_and_ends_into_the_next_scene() -> void:
	var roll := _roll(false, _with_vignette_scene())
	assert_true(roll.shown_text().has(tr("CREDITS_GAME")))
	assert_true(roll.shown_text().has(tr("CREDITS_ROLL_GODOT_MADE")))
	assert_false(roll.hint_text().contains("{"), "the hint names its bindings")
	assert_false(roll.hint_text().contains(tr("CREDITS_ROLL_SKIP").get_slice("}", 1)), "no skip offered the first time")
	var started: Array[StringName] = []
	var hosted: Array[bool] = []
	roll.vignette_started.connect(
		func(_id: StringName) -> void:
			hosted.append(roll.vignette_node() != null and roll.vignette_node().get_index() == 0)
	)
	roll.vignette_started.connect(func(id: StringName) -> void: started.append(id))
	roll.advance(float(roll.model.data["lead_in_sec"]) + 0.01)
	var y0 := roll.scroll_y()
	roll.advance(10.0)
	assert_true(roll.scroll_y() < y0, "the column climbs")
	var guard := 0
	while scenes.is_empty() and guard < 100000:
		guard += 1
		roll.advance(0.5)
	assert_eq(started.size(), 1, "the vignette's id once")
	assert_eq(hosted, [true] as Array[bool], "its scene plays behind the roll's black")
	assert_eq(roll.vignette_node(), null, "and is let go after")
	assert_eq(flags, [CreditsRollModel.SEEN_FLAG] as Array[StringName], "credits_seen is set")
	assert_eq(scenes, [CreditsRoll.TITLE_SCENE] as Array[String], "no next_scene: the title")
	after_each()


func test_a_held_pad_button_runs_it_faster() -> void:
	var roll := _roll(true)
	roll.advance(float(roll.model.data["lead_in_sec"]) + 0.01)
	var d := InputDriver.new(InputDriver.Kind.PAD)
	d.hold(&"ui_accept")
	roll._process(1.0)
	d.let_go(&"ui_accept")
	roll._process(0.0)
	assert_false(roll._fast, "let go: normal speed again")
	var held := roll.model.progress
	var plain := CreditsRollModel.new()
	plain.advance(float(plain.data["lead_in_sec"]) + 0.01)
	plain.advance(1.0)
	assert_true(held > plain.progress * 2.0, "the pad's Confirm, held, runs it faster")
	assert_true(roll.hint_text().contains(tr("CREDITS_ROLL_SKIP").get_slice("}", 1)), "seen before: skip offered")
	after_each()


## Ending Cinematics' vignette has no scene until it is built: the roll passes over it, never stopping on black.
func test_a_vignette_with_no_scene_yet_is_passed_over() -> void:
	var d := CreditsRollModel.load_data().duplicate(true)
	for v: Variant in d["vignettes"]:
		(v as Dictionary)["scene"] = ""  # M5-A3P-1701 set the live scene; this checks a vignette without one
	var m := CreditsRollModel.new(d)
	assert_true(m.vignettes().is_empty(), "the beach rite has no scene yet")
	m.advance(float(m.data["lead_in_sec"]) + 0.01)
	var guard := 0
	while not m.is_done() and guard < 100000:
		guard += 1
		assert_eq(m.advance(0.5), &"", "no stop")
	assert_true(m.is_done())


func test_the_ending_can_open_the_credits_as_a_scene() -> void:
	var packed := load(CreditsRoll.SCENE) as PackedScene
	assert_true(packed != null, "credits_roll.tscn loads")
	var roll := packed.instantiate() as CreditsRoll
	assert_true(roll != null, "and is the roll")
	roll.free()


func _with_vignette_scene() -> Dictionary:
	var d := CreditsRollModel.load_data().duplicate(true)
	for v: Variant in d["vignettes"]:
		(v as Dictionary)["scene"] = VIGNETTE_FIXTURE
	d["next_scene"] = ""  # M5-A3P-1701 set the live hook (post-credits); this checks the no-next_scene default
	return d


func _roll(seen: bool, config: Dictionary = {}) -> CreditsRoll:
	var roll := CreditsRoll.new()
	roll.model = CreditsRollModel.new(config, seen)
	roll.change_scene = func(p: String) -> void: scenes.append(p)
	roll.set_flag = func(f: StringName) -> void: flags.append(f)
	roll.set_process(false)
	ParityHost.scene_root().add_child(roll)
	made.append(roll)
	return roll


## The Lead (11-03): facts only. The title, what was made for the game, Godot's MIT notice in full (with FreeType's
## credit), the OFL fonts; no person on the project named, and the Made by section left out until a name is added.
func test_the_credits_hold_the_required_notices_and_no_one_s_name_yet() -> void:
	var m := CreditsRollModel.new()
	var keys: Array[String] = []
	for r in m.rows():
		keys.append(str(r["key"]))
	for need: String in [
		"CREDITS_GAME",
		"CREDITS_ROLL_MUSIC",
		"CREDITS_ROLL_ART",
		"CREDITS_ROLL_CODE",
		"CREDITS_ROLL_GODOT_MADE",
		"CREDITS_ROLL_GODOT_COPYRIGHT_1",
		"CREDITS_ROLL_MIT_GRANT",
		"CREDITS_ROLL_MIT_NOTICE",
		"CREDITS_ROLL_MIT_WARRANTY",
		"CREDITS_ROLL_FONT_GARAMOND",
		"CREDITS_ROLL_FONT_SOURCE",
		"CREDITS_ROLL_OFL",
	]:
		assert_true(keys.has(need), "%s is in the roll" % need)
		assert_ne(tr(need), need, "%s is translated" % need)
	assert_false(keys.has("CREDITS_ROLL_MADE_BY_TITLE"), "no Made by section while it names no one")
	var data := CreditsRollModel.load_data()
	for s: Variant in data["sections"]:
		if str((s as Dictionary)["title_key"]) == "CREDITS_ROLL_MADE_BY_TITLE":
			(s as Dictionary)["lines"] = ["CREDITS_THANKS"]
	var named := CreditsRollModel.new(data)
	assert_true(named.rows().any(func(r: Dictionary) -> bool: return r["key"] == "CREDITS_ROLL_MADE_BY_TITLE"))
	var licence := m.rows().filter(func(r: Dictionary) -> bool: return r["key"] == "CREDITS_ROLL_MIT_GRANT")
	assert_true(bool(licence[0]["notice"]), "licence text is set small")


func test_a_long_line_wraps_into_its_own_height() -> void:
	var roll := _roll(false)
	var grant: Label = null
	var next: Label = null
	for i in roll._labels.size():
		if roll._labels[i].text == tr("CREDITS_ROLL_MIT_GRANT"):
			grant = roll._labels[i]
			next = roll._labels[i + 1]
	assert_true(grant != null, "the grant is on the roll")
	assert_true(grant.size.y > float(CreditsRollModel.load_data()["column"]["line_height"]), "it takes several lines")
	assert_true(next.position.y >= grant.position.y + grant.size.y, "the next line starts below it")
	after_each()

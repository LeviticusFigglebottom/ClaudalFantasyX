extends TestCase
## M3-UI-100: what Ch8's set-piece battles show beyond a normal fight (M3-CMB-01; set_piece_battles.md). The
## Climb and the Surge have timeline chips of their own; the stair meter counts groups up against the quota;
## Toma, holding the stair, can't be swapped out and the help line says why; Kerrid is listed on the reserve page,
## greyed, "Not with the party"; intercepts, counters and Storm-Call withdrawals say so with floats.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261027
const WAVE := &"ch08_stair_hold_1"

var ctl: BattleController


func test_the_entries_have_timeline_chips_of_their_own() -> void:
	_start(WAVE)
	var climb: Dictionary = ctl.hud.timeline._identity.get(&"the_climb", {})
	var surge: Dictionary = ctl.hud.timeline._identity.get(&"the_surge", {})
	assert_true(bool(climb.get("entry", false)), "the Climb is an entry, not a fighter")
	assert_eq(str(climb.get("label", "")), tr("ENTRY_CH08_FISHER_STAIR"), "named, not its raw id")
	assert_true(bool(surge.get("entry", false)))
	var foe: Dictionary = ctl.hud.timeline._identity.get(ctl.engine.enemies[0].id, {})
	assert_false(bool(foe.get("entry", false)), "a foe stays a foe")
	var chip := TimelineChip.new()
	chip.setup(HudLayout.section(&"timeline"))
	var slot := {"id": &"the_climb", "team": &"party", "ghost": false, "skipped": false, "moved": 0}
	chip.apply(slot, climb, false)
	assert_true(chip.entry, "the chip draws it apart")
	chip.free()
	_free()


func test_the_stair_meter_counts_groups_up_against_the_quota() -> void:
	_start(WAVE)
	var meter := ctl.set_piece.meter
	assert_true(meter != null and meter.visible, "an objective shows the meter")
	assert_eq(meter.quota, 3)
	assert_eq(meter.title_text(), tr("ENTRY_CH08_FISHER_STAIR"), "titled with the ward's name")
	assert_true(meter.count_text().begins_with(tr("HUD_OBJECTIVE_COUNT_FMT").format({"count": 0, "quota": 3})))
	ctl.engine.objective_count = 2
	ctl.set_piece.refresh()
	assert_eq(meter.count, 2)
	var line := tr("HUD_OBJECTIVE_COUNT_FMT").format({"count": 2, "quota": 3})
	assert_true(meter.count_text().begins_with(line), "spelled out too")
	_free()


func test_the_meter_sits_below_a_two_line_tutorial() -> void:
	_start(WAVE)
	ctl.hud.set_help(tr("TUT_CH08_WAVE_HOLD") + " " + tr("TUT_CH08_WAVE_HOLD"))
	assert_true(ctl.hud.help_wraps(), "the help line wraps onto its second line")
	var help := ctl.hud.get_node("%HelpLine") as Control
	var bottom := (
		help.global_position.y + help.get_combined_minimum_size().y * help.get_global_transform().get_scale().y
	)
	assert_true(
		ctl.set_piece.meter.global_position.y >= bottom,
		"clear of it (%s >= %s)" % [ctl.set_piece.meter.global_position.y, bottom]
	)
	_free()


func test_the_meter_carries_the_running_total_across_the_waves() -> void:
	var before: Variant = Game.get_flag(&"ch08_stair_groups_up", 0)
	Game.set_flag(&"ch08_stair_groups_up", 5)  # the flow's count after the earlier waves
	_start(WAVE)
	ctl.engine.objective_count = 2
	ctl.set_piece.refresh()
	assert_eq(ctl.set_piece.carried_total(), 7, "the flag plus this wave")
	assert_eq(ctl.set_piece.meter.total, 7)
	assert_true(ctl.set_piece.meter.count_text().contains("7"), "spelled out")
	assert_eq(Game.get_flag(&"ch08_stair_groups_up", 0), 5, "read only: the flow raises it")
	Game.set_flag(&"ch08_stair_groups_up", before)
	_free()


func test_an_ordinary_battle_adds_nothing() -> void:
	_start(&"sandbox_reef")
	assert_true(ctl.set_piece.meter == null, "no meter")
	assert_false(ctl.hud.has_node(^"ObjectiveMeter"))
	_free()


func test_toma_holding_the_stair_cannot_be_swapped_out_and_the_help_says_why() -> void:
	_start(WAVE)
	var why := ctl.menus.swap_lock_text(ctl.engine, &"toma")
	assert_true(why.contains(tr("HUD_SWAP_CH08_HOLDING_THE_STAIR")), "the reason (%s)" % why)
	assert_eq(ctl.menus.swap_lock_text(ctl.engine, &"rhen"), "", "the others may swap")
	assert_true(
		ctl.menus.swap_out_help(ctl.engine.find(&"ysolde"), ctl.engine, &"toma") == why, "the pick's help names it"
	)
	assert_false(ctl.swap_members(&"toma", &"ysolde"), "refused")
	assert_eq(ctl.hud.help_text(), why, "and the help line says why")
	_free()


func test_an_unavailable_hero_is_listed_greyed_with_the_reason() -> void:
	_start(WAVE)
	var rows := ctl.menus.reserve_rows(ctl.engine)
	var kerrid: Dictionary = {}
	for r in rows:
		if StringName(str(r["id"])) == &"kerrid":
			kerrid = r
	assert_false(kerrid.is_empty(), "Kerrid is on the reserve page")
	assert_false(bool(kerrid["enabled"]), "greyed")
	assert_eq(str(kerrid["right"]), tr("HUD_PARTY_CH08_NOT_WITH_PARTY"))
	_free()


func test_intercepts_counters_and_withdrawals_float_their_words() -> void:
	_start(WAVE)
	var layer := ctl.hud.get_node(^"%DamageLayer") as Control
	var before := layer.get_child_count()
	var r := ActionResult.new()
	r.actor_id = ctl.engine.enemies[0].id
	r.skill_id = &"attack"
	r.intercepted_by = &"toma"
	r.hits = [
		{"target_id": &"toma", "amount": 5, "hit": true, "crit": false},
		{"target_id": r.actor_id, "amount": 3, "hit": true, "crit": false, "counter_by": &"toma"},
		{"target_id": r.actor_id, "amount": 0, "hit": true, "crit": false, "withdrawn": true},
	]
	ctl.show_damage_numbers = true
	ctl.floats.show_hits(r, false)
	var words: Array[String] = []
	for i in range(before, layer.get_child_count()):
		words.append(str(layer.get_child(i).get(&"text")))
	for key in ["HUD_FLOAT_INTERCEPTED", "HUD_FLOAT_COUNTER", "HUD_FLOAT_WITHDRAWN"]:
		assert_true(words.has(tr(key)), "%s floats (%s)" % [key, words])
	_free()


func _start(encounter: StringName) -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var active: Array[StringName] = [&"rhen", &"asha", &"toma"]
	var reserve: Array[StringName] = [&"ysolde", &"kerrid"]
	ctl.start_battle(active, reserve, encounter, SEED)
	ctl.stage.choreo.live = false


func _free() -> void:
	ctl.get_tree().paused = false
	ctl.get_parent().remove_child(ctl)
	ctl.free()

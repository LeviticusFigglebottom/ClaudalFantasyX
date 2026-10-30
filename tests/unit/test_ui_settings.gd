extends TestCase
## UiSettings (M1-UI-02): the data-driven accessibility layer behind the future settings menu,
## and how the battle HUD follows it (reduced motion, text size, colorblind palette).

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const THEME_PATH := "res://game/ui/theme/hymn_theme.tres"
const MIN_FONT_PX := 22

var cfg_path := ""


func before_each() -> void:
	cfg_path = "user://test_ui_settings_%d.cfg" % Time.get_ticks_usec()


func test_defaults_come_from_the_data_file() -> void:
	var s := UiSettings.new()
	assert_eq(
		s.settings(),
		(
			[
				&"reduced_motion",
				&"text_scale",
				&"palette",
				&"timing_assist",
				&"text_speed",
				&"dialogue_backing",
				&"objective_cue",
				&"tutorial_tips",
				&"battle_speed",
				&"battle_animations",
				&"summon_cinematic",
				&"dialogue_auto",
				&"reduced_audio",
				&"master_volume",
				&"music_volume",
				&"sfx_volume",
				&"voice_volume",
				&"screen_shake"
			]
			as Array[StringName]
		)
	)
	assert_false(s.reduced_motion())
	assert_eq(s.text_scale(), 1.0)
	assert_eq(s.palette(), &"standard")
	assert_true(s.is_default())
	assert_eq(s.options(UiSettings.REDUCED_MOTION), [false, true])
	assert_eq(s.options(UiSettings.TEXT_SCALE), [1.0, 1.15, 1.3], "art/ui.md §4.2: 100 / 115 / 130%")
	assert_eq(s.palette_ids(), [&"standard", &"colorblind"] as Array[StringName])


func test_every_setting_and_option_has_loc_keys() -> void:
	var s := UiSettings.new()
	for key in s.settings():
		var row := s.setting_row(key)
		for k: String in ["label_key", "help_key"]:
			var lk := str(row.get(k, ""))
			assert_ne(tr(lk), lk, "%s.%s '%s' is localized" % [key, k, lk])
		var opt_keys: Array = row.get("option_keys", [])
		if str(row.get("type", "")) == UiSettings.KIND_ENUM:
			assert_eq(opt_keys.size(), s.options(key).size(), "%s: one label per option" % key)
		for ok: Variant in opt_keys:
			assert_ne(tr(str(ok)), str(ok), "%s option label %s is localized" % [key, ok])


func test_set_value_validates_against_the_options() -> void:
	var s := UiSettings.new()
	var seen: Array[StringName] = []
	s.changed.connect(func(k: StringName) -> void: seen.append(k))
	assert_true(s.set_value(UiSettings.TEXT_SCALE, 1.3))
	assert_eq(s.text_scale(), 1.3)
	assert_false(s.set_value(UiSettings.TEXT_SCALE, 2.0), "2.0 is not an option")
	assert_eq(s.text_scale(), 1.3, "a refused value changes nothing")
	assert_false(s.set_value(UiSettings.PALETTE, "neon"))
	assert_false(s.set_value(&"no_such_setting", true))
	assert_true(s.set_value(UiSettings.PALETTE, &"colorblind"))
	assert_eq(s.palette(), &"colorblind")
	assert_true(s.set_value(UiSettings.REDUCED_MOTION, true))
	assert_true(s.set_value(UiSettings.REDUCED_MOTION, true), "same value: accepted")
	assert_eq(seen, [&"text_scale", &"palette", &"reduced_motion"] as Array[StringName], "changed fires on change only")
	assert_false(s.is_default())
	s.reset()
	assert_true(s.is_default())


func test_motion_answers_follow_reduced_motion() -> void:
	var s := UiSettings.new()
	assert_true(s.animations_enabled())
	assert_eq(s.motion_scale(), 1.0)
	s.set_value(UiSettings.REDUCED_MOTION, true)
	assert_false(s.animations_enabled(), "no slides, pulses or shake")
	assert_eq(s.motion_scale(), 0.5, "art/ui.md §5: translations halved")
	assert_true(s.crossfade_sec() > 0.0, "a short cross-fade replaces the slide")


func test_save_and_load_round_trip_and_keep_other_sections() -> void:
	var other := ConfigFile.new()
	other.set_value("graphics", "preset", "high")
	other.save(cfg_path)
	var s := UiSettings.new()
	s.set_value(UiSettings.REDUCED_MOTION, true)
	s.set_value(UiSettings.TEXT_SCALE, 1.15)
	s.set_value(UiSettings.PALETTE, &"colorblind")
	assert_eq(s.save_to(cfg_path), OK)
	var back := UiSettings.new()
	back.load_from(cfg_path)
	assert_true(back.reduced_motion())
	assert_eq(back.text_scale(), 1.15)
	assert_eq(back.palette(), &"colorblind")
	var raw := ConfigFile.new()
	raw.load(cfg_path)
	assert_eq(raw.get_value("graphics", "preset", ""), "high", "GraphicsSettings' section survives")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(cfg_path))


func test_load_ignores_values_outside_the_options() -> void:
	var raw := ConfigFile.new()
	raw.set_value("accessibility", "text_scale", 9.0)
	raw.set_value("accessibility", "palette", "neon")
	raw.set_value("accessibility", "reduced_motion", true)
	raw.save(cfg_path)
	var s := UiSettings.new()
	s.load_from(cfg_path)
	assert_eq(s.text_scale(), 1.0)
	assert_eq(s.palette(), &"standard")
	assert_true(s.reduced_motion())
	DirAccess.remove_absolute(ProjectSettings.globalize_path(cfg_path))


func test_colorblind_palette_swaps_danger_and_enemy_fill() -> void:
	var s := UiSettings.new()
	var base := load(THEME_PATH) as Theme
	assert_eq(s.theme_for(base), base, "the defaults use the saved theme itself")
	s.set_value(UiSettings.PALETTE, &"colorblind")
	var t := s.theme_for(base)
	assert_ne(t, base)
	assert_eq(
		t.get_color(&"danger", &"Hymn").to_html(false).to_upper(), "C76E10", "art/ui.md §9 as amended by M2-UI-11"
	)
	assert_eq(
		t.get_color(&"enemy_chip", &"Hymn").to_html(false).to_upper(), "2A2414", "art/ui.md §9 as amended by M2-UI-11"
	)
	assert_eq(t.get_color(&"focus", &"Hymn"), base.get_color(&"focus", &"Hymn"), "buffs and allies keep ui_focus")
	assert_eq(s.theme_for(base), t, "built once per palette and scale")


func test_text_scale_scales_every_font_size_and_keeps_the_minimum() -> void:
	var s := UiSettings.new()
	var base := load(THEME_PATH) as Theme
	s.set_value(UiSettings.TEXT_SCALE, 1.3)
	var t := s.theme_for(base)
	assert_eq(t.default_font_size, roundi(base.default_font_size * 1.3))
	for type in base.get_font_size_type_list():
		for fname in base.get_font_size_list(type):
			var want := roundi(base.get_font_size(fname, type) * 1.3)
			assert_eq(t.get_font_size(fname, type), want, "%s/%s scaled" % [type, fname])
			assert_true(t.get_font_size(fname, type) >= MIN_FONT_PX)


func test_hud_follows_the_settings_live() -> void:
	var ctl := _sandbox()
	var s := UiSettings.new()
	ctl.hud.apply_settings(s)
	var base := ctl.hud.theme
	s.set_value(UiSettings.REDUCED_MOTION, true)
	assert_true(ctl.hud.timeline.reduced_motion, "timeline chips stop sliding")
	assert_true(ctl.hud.commands.reduced_motion)
	assert_true(ctl.hud.target_cursor.reduced_motion)
	assert_eq(ctl.hud.result.motion_scale, 0.5)
	s.set_value(UiSettings.PALETTE, &"colorblind")
	assert_ne(ctl.hud.theme, base, "palette swap re-themes the HUD")
	assert_eq(ctl.hud.get_theme_color(&"danger", &"Hymn").to_html(false).to_upper(), "C76E10")
	s.reset()
	assert_eq(ctl.hud.theme, base, "back to the defaults: the saved theme again")
	assert_false(ctl.hud.timeline.reduced_motion)
	_free(ctl)


func test_reduced_motion_snaps_chips_without_sliding() -> void:
	var ctl := _sandbox()
	var s := UiSettings.new()
	s.set_value(UiSettings.REDUCED_MOTION, true)
	ctl.hud.apply_settings(s)
	_start(ctl)
	ctl.hud.commands.select(BattleMenus.ROW_SKILLS)
	ctl.hud.commands.select(BattleMenus.ROW_ATTACK)
	for slot in ctl.hud.timeline.slots:
		var chip := ctl.hud.timeline.chip_for_key(str(slot["key"]))
		var r := ctl.hud.timeline.slot_rect(int(slot["slot"]))
		assert_eq(chip.position, r.position, "chip %s is already in its slot (no slide)" % slot["key"])
		assert_eq(chip.scale, Vector2.ONE, "no pulse")
	_free(ctl)


func test_reduced_motion_skips_the_camera_shake() -> void:
	var ctl := _sandbox()
	ctl.show_damage_numbers = true
	var calm := UiSettings.new()
	calm.set_value(UiSettings.REDUCED_MOTION, true)
	ctl.hud.apply_settings(calm)
	_start(ctl)
	var crit := ActionResult.new()
	crit.actor_id = ctl.current_actor_id()
	crit.skill_id = &"attack"
	var foe := ctl.engine.living_foes_of(ctl.engine.current)[0]
	crit.hits.append({"target_id": foe.id, "hit": true, "crit": true, "amount": 1, "statuses_added": []})
	ctl.floats.on_action_resolved(crit)
	assert_eq(ctl.stage.shakes_started, 0, "reduced motion: no screen shake")
	ctl.hud.apply_settings(UiSettings.new())
	ctl.floats.on_action_resolved(crit)
	assert_eq(ctl.stage.shakes_started, 1, "a critical hit shakes the camera otherwise")
	_free(ctl)


# --- helpers -----------------------------------------------------------------------------


func _sandbox() -> BattleController:
	var ctl := (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	return ctl


func _start(ctl: BattleController) -> void:
	ctl.start_fixture(BattleFixture.load_fixture(&"player_preview"))


func _free(ctl: BattleController) -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()


## The Lead's battle-return check (2026-10-30): a field zone kept resident through a random fight leaves the tree and
## comes back without _ready. Its prompts keep following: a change made while it was away (the battle pause's text
## size) shows on its return, and later changes still reach it.
func test_a_control_out_of_the_tree_catches_up_and_keeps_following() -> void:
	var s := UiSettings.new()
	var c := Control.new()
	var tree := Engine.get_main_loop() as SceneTree
	var host: Node = tree.current_scene if tree.current_scene != null else tree.root
	host.add_child(c)
	assert_true(c.is_inside_tree())
	s.follow(c)
	var at_100 := c.theme
	host.remove_child(c)
	s.set_value(UiSettings.TEXT_SCALE, 1.3)
	assert_eq(c.theme, at_100, "out of the tree it does not listen")
	host.add_child(c)
	var at_130 := c.theme
	assert_ne(at_130, at_100, "back in the tree it takes the size set while it was away")
	s.set_value(UiSettings.TEXT_SCALE, 1.15)
	assert_ne(c.theme, at_130, "and follows the next change")
	host.remove_child(c)
	c.free()

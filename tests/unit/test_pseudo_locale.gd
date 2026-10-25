extends TestCase
## Localization readiness. M2-UI-15 started it with a pseudo-locale built here from strings.csv;
## M2-UI-28 moved the generator into the game's debug tools (PseudoLoc, game/core/debug/: every loc
## CSV, about 40% longer, accented, {placeholders}, %-formats, BBCode and newlines kept), and the
## screen walks into test_pseudo_loc_screens.gd (TextFitProbe). This file checks the generator, the
## switch (launch flag, environment, debug overlay) and that release builds never reach it.

const OVERLAY_DATA := "res://game/data/debug/debug_overlay.json"
const THEME_PATH := "res://game/ui/theme/hymn_theme.tres"
const GAME_DIR := "res://game"
const DEBUG_DIR := "res://game/core/debug"


func before_each() -> void:
	PseudoLoc.disable()


func test_pseudo_accents_pads_and_brackets() -> void:
	var cfg := PseudoLoc.config()
	var p := PseudoLoc.pseudo("Settings")
	assert_true(p.begins_with(str(cfg["prefix"])) and p.ends_with(str(cfg["suffix"])), p)
	assert_true(p.contains("Šéţţîñĝš"), "accented: " + p)
	var dots := p.count(str(cfg["pad_char"]))
	assert_eq(dots, ceili("Settings".length() * float(cfg["expansion"])), "padded by the expansion: " + p)
	var long := "The tide turns twice before the bell rings over the drowned quarter."
	assert_true(PseudoLoc.pseudo(long).length() >= long.length() * (1.0 + float(cfg["expansion"])), "about 40% longer")


func test_pseudo_keeps_placeholders_formats_bbcode_and_newlines() -> void:
	var src := "Not enough lume: {cost} costs %d, [b]%s[/b] holds %.1f%%\nPress {ui_cancel}"
	var p := PseudoLoc.pseudo(src)
	for kept: String in ["{cost}", "%d", "[b]", "%s", "[/b]", "%.1f", "%%", "{ui_cancel}"]:
		assert_true(p.contains(kept), "%s kept in %s" % [kept, p])
	assert_eq(p.count("\n"), 1, "the newline stays: " + p)
	assert_true(p.contains("Ñöţ"), "the words around them are accented")
	assert_eq(p.format({"cost": "12"}).contains("12"), true, "String.format still finds its placeholder")
	var lines := p.split("\n")
	assert_true(lines[0].contains(str(PseudoLoc.config()["pad_char"])), "each line is padded on its own")
	assert_true(lines[1].contains(str(PseudoLoc.config()["pad_char"])), "each line is padded on its own")
	assert_eq(PseudoLoc.pseudo(""), str(PseudoLoc.config()["prefix"]) + str(PseudoLoc.config()["suffix"]))


func test_the_padding_breaks_into_groups_a_wrap_can_split() -> void:
	var cfg := PseudoLoc.config()
	var p := PseudoLoc.pseudo("x".repeat(100))
	var group := str(cfg["pad_char"]).repeat(int(cfg["pad_group"]))
	assert_false(p.contains(group + str(cfg["pad_char"])), "no run longer than pad_group: " + p)


func test_every_loc_csv_reaches_the_pseudo_translation() -> void:
	var csvs := PseudoLoc.source_csvs()
	assert_true(csvs.size() >= 2, "strings.csv and the per-domain CSVs")
	assert_true(csvs.has("res://game/data/loc/strings.csv"))
	assert_true(csvs.has("res://game/data/loc/dialogue.csv"))
	var t := PseudoLoc.build()
	assert_eq(t.locale, PseudoLoc.locale())
	assert_eq(str(t.get_message("FIELD_MENU_TITLE")), PseudoLoc.pseudo(TranslationServer.translate("FIELD_MENU_TITLE")))


func test_enable_switches_the_locale_and_disable_puts_it_back() -> void:
	var was := TranslationServer.get_locale()
	var english := tr("FIELD_MENU_TITLE")
	assert_true(PseudoLoc.enable(), "debug builds (the test runner) may turn it on")
	assert_true(PseudoLoc.is_enabled())
	assert_eq(TranslationServer.get_locale(), PseudoLoc.locale())
	assert_eq(tr("FIELD_MENU_TITLE"), PseudoLoc.pseudo(english))
	assert_eq(tr("NO_SUCH_KEY_ANYWHERE"), "NO_SUCH_KEY_ANYWHERE", "an unknown key stays itself")
	assert_false(PseudoLoc.toggle(), "toggle turns it off")
	assert_eq(TranslationServer.get_locale(), was)
	assert_eq(tr("FIELD_MENU_TITLE"), english)
	assert_true(PseudoLoc.toggle(), "and on again")
	PseudoLoc.disable()
	assert_eq(TranslationServer.get_locale(), was)


func test_the_launch_flag_and_the_environment_turn_it_on() -> void:
	var cfg := PseudoLoc.config()
	assert_true(PseudoLoc.wanted(PackedStringArray([str(cfg["flag"])]), ""), "--pseudo-loc")
	assert_true(PseudoLoc.wanted(PackedStringArray(), "1"), "HYMN_PSEUDO_LOC=1")
	for off: String in ["", "0", "false", "OFF"]:
		assert_false(PseudoLoc.wanted(PackedStringArray(["--other"]), off), "'%s' leaves it off" % off)


func test_the_debug_overlay_toggles_it_on_f10() -> void:
	var cfg: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(OVERLAY_DATA))
	var keys: Array = ((cfg["actions"] as Dictionary)[String(DebugOverlay.ACTION_PSEUDO_LOC)] as Dictionary)["keys"]
	assert_eq(keys, ["F10"])
	var overlay := DebugOverlay.install(ParityHost.scene_root())
	assert_true(overlay.toggle_pseudo_loc(), "F10 turns it on")
	assert_eq(TranslationServer.get_locale(), PseudoLoc.locale())
	assert_true(overlay.last_message.contains("on"), overlay.last_message)
	assert_true("\n".join(overlay.render_page(DebugOverlay.PAGE_HELP)).contains("pseudo-localisation (on)"))
	assert_false(overlay.toggle_pseudo_loc(), "and off")
	overlay.get_parent().remove_child(overlay)
	overlay.free()


## Every accent the pseudo-locale draws is in the theme's fonts, so a missing glyph never shows as a
## box (and the width the screen walks measure is the real one).
func test_the_theme_fonts_have_every_accent() -> void:
	var theme := load(THEME_PATH) as Theme
	var fonts: Array[Font] = [theme.default_font]
	for type in theme.get_font_type_list():
		for fname in theme.get_font_list(type):
			fonts.append(theme.get_font(fname, type))
	var accents: Dictionary = PseudoLoc.config()["accents"]
	var chars: Array = accents.values() + [str(PseudoLoc.config()["pad_char"])]
	for f in fonts:
		if f == null:
			continue
		for ch: String in chars:
			assert_true(f.has_char(ch.unicode_at(0)), "%s has %s" % [f.get_font_name(), ch])


## Release exports leave game/core/debug/ out: no game script outside it may name PseudoLoc (UiInput
## loads it by path).
func test_no_game_code_names_the_debug_tool() -> void:
	var code_ref := RegEx.create_from_string('(?<!["\\w/])PseudoLoc(?!["\\w])')
	for path in _scripts(GAME_DIR):
		if path.begins_with(DEBUG_DIR):
			continue
		assert_true(code_ref.search(FileAccess.get_file_as_string(path)) == null, "%s names PseudoLoc" % path)


func _scripts(dir: String) -> PackedStringArray:
	var out := PackedStringArray()
	for f in DirAccess.get_files_at(dir):
		if f.ends_with(".gd"):
			out.append(dir.path_join(f))
	for d in DirAccess.get_directories_at(dir):
		out.append_array(_scripts(dir.path_join(d)))
	return out

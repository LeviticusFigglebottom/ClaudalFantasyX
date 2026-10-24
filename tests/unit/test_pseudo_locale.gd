extends TestCase
## M2-UI-15: localization readiness. A pseudo-locale ("xx") built from strings.csv makes every
## string about 35% longer and accented, keeping its {placeholders} and %-formats. Each menu is
## built under it through its capture driver (the shots' own staging), and every visible Label must
## fit its rect, or wrap or ellipsize; silent overflow fails, naming the label and its text.

const STRINGS := "res://game/data/loc/strings.csv"
const PSEUDO_LOCALE := "xx"
const GROWTH := 0.35
const ACCENTS := {
	"a": "á",
	"e": "é",
	"i": "í",
	"o": "ö",
	"u": "ü",
	"y": "ý",
	"c": "ç",
	"n": "ñ",
	"s": "š",
	"A": "Å",
	"E": "É",
	"I": "Í",
	"O": "Ö",
	"U": "Ü",
	"C": "Ç",
	"N": "Ñ",
	"S": "Š",
}
## Capture drivers that stage a menu: scene path -> what it shows.
const DRIVERS := {
	"res://game/ui/field_menu/shots/field_menu.tscn": "field menu",
	"res://game/ui/field_menu/shots/field_menu_swell_modes.tscn": "field menu, Swell modes",
	"res://game/ui/bestiary/shots/bestiary_menu.tscn": "bestiary",
	"res://game/ui/settings/shots/settings_hub.tscn": "settings hub",
	"res://game/ui/settings/shots/settings_accessibility.tscn": "accessibility page",
	"res://game/ui/shop/shots/shop_buy.tscn": "shop, buy",
	"res://game/ui/shop/shots/shop_sell.tscn": "shop, sell",
	"res://game/ui/shop/shots/inn.tscn": "inn",
}
## Battle fixtures whose capture states show the HUD's pages and panels.
const BATTLE_STATES: Array[StringName] = [
	&"player_preview", &"swap_menu", &"read_panel", &"swell_chant", &"swell_brace", &"vowbound_call"
]

var _pseudo: Translation
var _was_locale := ""


func before_each() -> void:
	if _pseudo == null:
		_pseudo = make_pseudo()
	_was_locale = TranslationServer.get_locale()
	TranslationServer.add_translation(_pseudo)
	TranslationServer.set_locale(PSEUDO_LOCALE)


## The pseudo-locale translation of every strings.csv key.
static func make_pseudo() -> Translation:
	var t := Translation.new()
	t.locale = PSEUDO_LOCALE
	var f := FileAccess.open(STRINGS, FileAccess.READ)
	f.get_csv_line()  # keys,en
	while not f.eof_reached():
		var row := f.get_csv_line()
		if row.size() >= 2 and row[0] != "":
			t.add_message(row[0], pseudo(row[1]))
	return t


## `text` accented and padded about GROWTH longer, in brackets; {placeholders} and %-formats kept.
static func pseudo(text: String) -> String:
	var out := ""
	var depth := 0
	var i := 0
	while i < text.length():
		var ch := text[i]
		if ch == "{":
			depth += 1
		elif ch == "}":
			depth -= 1
		if ch == "%" and i + 1 < text.length():
			out += text.substr(i, 2)
			i += 2
			continue
		out += ch if depth > 0 else str(ACCENTS.get(ch, ch))
		i += 1
	return "[" + out + " " + "~".repeat(ceili(text.length() * GROWTH)) + "]"


func test_pseudo_keeps_placeholders_and_grows() -> void:
	var p := pseudo("Not enough lume: {cost} costs %d")
	assert_true(p.contains("{cost}") and p.contains("%d"), p)
	assert_true(p.length() >= ceili("Not enough lume: {cost} costs %d".length() * (1.0 + GROWTH)))
	assert_true(p.contains("Ñöt"), "accented")
	assert_eq(tr("FIELD_MENU_TITLE"), pseudo(_english("FIELD_MENU_TITLE")), "the locale is live")
	_done()


func test_every_menu_fits_the_pseudo_locale() -> void:
	var problems: PackedStringArray = []
	for path: String in DRIVERS:
		var packed := load(path) as PackedScene
		if packed == null:
			problems.append("%s: no driver scene" % path)
			continue
		var root := packed.instantiate()
		_host().add_child(root)
		problems.append_array(overflows(root, str(DRIVERS[path])))
		root.get_parent().remove_child(root)
		root.free()
		(Engine.get_main_loop() as SceneTree).paused = false
	UiSettings.set_shared(null)
	assert_eq(problems, PackedStringArray(), "labels overflow in the pseudo-locale:\n" + "\n".join(problems))
	_done()


func test_the_battle_hud_fits_the_pseudo_locale() -> void:
	var problems: PackedStringArray = []
	for sid in BATTLE_STATES:
		var ctl := (
			(load("res://game/battle/scene/battle_sandbox.tscn") as PackedScene).instantiate() as BattleController
		)
		ctl.auto_start = false
		ctl.pacing_scale = 0.0
		ctl.persist_progress = false
		ctl.show_damage_numbers = false
		_host().add_child(ctl)
		ctl.run_script(sid)
		problems.append_array(overflows(ctl.hud, "battle " + String(sid)))
		ctl.get_parent().remove_child(ctl)
		ctl.free()
	assert_eq(problems, PackedStringArray(), "HUD labels overflow in the pseudo-locale:\n" + "\n".join(problems))
	_done()


## Every visible Label under `root` that is wider (one line) or taller (wrapped) than its rect,
## with no ellipsis, clip or line limit to absorb it.
static func overflows(root: Node, what: String) -> PackedStringArray:
	var out: PackedStringArray = []
	for n in root.find_children("*", "Label", true, false):
		var l := n as Label
		if not l.is_visible_in_tree() or l.text.strip_edges() == "" or l.clip_text:
			continue
		if l.get_parent() is Container:
			continue  # a container sizes it to its text (the container grows instead; the shots show it)
		if l.text_overrun_behavior != TextServer.OVERRUN_NO_TRIMMING:
			continue
		var font := l.get_theme_font(&"font")
		var fsize := l.get_theme_font_size(&"font_size")
		if l.autowrap_mode == TextServer.AUTOWRAP_OFF:
			var w := font.get_multiline_string_size(l.text, HORIZONTAL_ALIGNMENT_LEFT, -1, fsize).x
			if w > l.size.x + 1.0:
				out.append("%s: %s (%d > %d px): %s" % [what, l.name, int(w), int(l.size.x), l.text])
			continue
		if l.max_lines_visible >= 0:
			continue
		var h := font.get_multiline_string_size(l.text, HORIZONTAL_ALIGNMENT_LEFT, l.size.x, fsize).y
		if h > l.size.y + 1.0:
			out.append("%s: %s wraps to %d px in %d: %s" % [what, l.name, int(h), int(l.size.y), l.text])
	return out


func _english(key: String) -> String:
	TranslationServer.set_locale("en")
	var s := tr(key)
	TranslationServer.set_locale(PSEUDO_LOCALE)
	return s


func _host() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


## Back to English (the runner has no after_each).
func _done() -> void:
	TranslationServer.remove_translation(_pseudo)
	TranslationServer.set_locale(_was_locale if _was_locale != "" else "en")

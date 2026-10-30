class_name EnemyPageView
extends VBoxContainer
## Lays out one EnemyPage (M2-UI-02): the name and level on a header line, HP and MP, the eight
## stats in a grid, the affinity rows (label in dim small caps, the elements in body text), delay,
## statuses, the lore in italics and the defeat count. Shared by ReadPanel and BestiaryMenu, so a
## Read in battle and the bestiary page read the same way. Rows a page leaves empty are hidden.
## Metrics: battle_hud.json "enemy_page" (1920x1080 reference). A view only.

var page: Dictionary = {}
## The widest the page may be: its panel's inner width (0 = no limit). When stat_columns pairs a
## row would not fit (a longer language, a larger text size), the stat grid takes fewer pairs a
## row and more rows, instead of pushing the panel past its frame (M2-UI-28).
var max_width := 0.0

var _m: Dictionary = {}
var _title: Label
var _level: Label
var _vitals: Label
var _stats: GridContainer
var _facts: GridContainer
var _lore: Label
var _defeated: Label
var _rules: Array[HSeparator] = []


func _init() -> void:
	_m = HudLayout.section(&"enemy_page")
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_theme_constant_override(&"separation", int(HudLayout.num(_m, "gap")))
	var head := HBoxContainer.new()
	head.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(head)
	_title = _label(&"HeaderLabel")
	_title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_title.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	head.add_child(_title)
	_level = _label(&"DimLabel")
	_level.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
	head.add_child(_level)
	_vitals = _label(&"HudNumber")
	add_child(_vitals)
	_rules.append(_rule())
	_stats = GridContainer.new()
	_stats.columns = int(HudLayout.num(_m, "stat_columns")) * 2
	_stats.add_theme_constant_override(&"h_separation", int(HudLayout.num(_m, "stat_gap")))
	_stats.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_stats)
	_rules.append(_rule())
	_facts = GridContainer.new()
	_facts.columns = 2
	_facts.add_theme_constant_override(&"h_separation", int(HudLayout.num(_m, "fact_gap")))
	_facts.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_facts)
	_lore = _label(&"FlavorLabel")
	_lore.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_lore.max_lines_visible = int(HudLayout.num(_m, "lore_lines"))
	_lore.custom_minimum_size = Vector2(HudLayout.num(_m, "min_width"), 0.0)
	add_child(_lore)
	_defeated = _label(&"SmallLabel")
	add_child(_defeated)


## Shows `p` (an EnemyPage dictionary).
func show_page(p: Dictionary) -> void:
	page = p
	_title.text = str(p.get("title", ""))
	_level.text = str(p.get("level", ""))
	_vitals.text = str(p.get("vitals", ""))
	_vitals.visible = _vitals.text != ""
	_clear(_stats)
	for pair: Variant in p.get("stats", []):
		var name_label := _label(&"DimLabel")
		name_label.text = str((pair as Array)[0])
		_stats.add_child(name_label)
		var value := _label(&"HudNumber")
		value.text = str((pair as Array)[1])
		value.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		value.custom_minimum_size = Vector2(HudLayout.num(_m, "stat_value_width"), 0.0)
		_stats.add_child(value)
	_stats.visible = _stats.get_child_count() > 0
	_fit_stat_columns()
	_clear(_facts)
	for row: Variant in p.get("affinities", []):
		var d := row as Dictionary
		_fact(str(d.get("label", "")), str(d.get("text", "")), bool(d.get("empty", false)))
	if str(p.get("delay", "")) != "":
		_fact(tr("HUD_READ_DELAY"), str(p["delay"]), false)
	if str(p.get("statuses", "")) != "":
		_fact(tr("HUD_READ_STATUSES"), str(p["statuses"]), false)
	if str(p.get("parts", "")) != "":  # M4-A2P-083: a part broken and not yet mended
		_fact(tr("HUD_READ_PARTS"), str(p["parts"]), false)
	_facts.visible = _facts.get_child_count() > 0
	for r in _rules:
		r.visible = bool(p.get("read", false))
	_lore.text = str(p.get("lore", ""))
	_lore.visible = _lore.text != ""
	_defeated.text = str(p.get("defeated", ""))
	_defeated.visible = _defeated.text != ""


## The text of every visible label, in order (tests and debug readouts).
func shown_text() -> PackedStringArray:
	var out: PackedStringArray = []
	_collect(self, out)
	return out


## stat_columns pairs a row, halved until the grid fits max_width (one pair a row at the least).
func _fit_stat_columns() -> void:
	var pairs := int(HudLayout.num(_m, "stat_columns"))
	_stats.columns = pairs * 2
	while max_width > 0.0 and pairs > 1 and _stats.get_combined_minimum_size().x > max_width:
		pairs = ceili(pairs / 2.0)
		_stats.columns = pairs * 2


func _fact(label_text: String, text: String, empty: bool) -> void:
	var l := _label(&"DimLabel")
	l.text = label_text
	_facts.add_child(l)
	var v := _label(&"HudName")
	v.text = text
	v.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	if empty:
		v.theme_type_variation = &"DimLabel"
	_facts.add_child(v)


func _collect(node: Node, out: PackedStringArray) -> void:
	for ch in node.get_children():
		var l := ch as Label
		if l != null and l.visible and l.text != "":
			out.append(l.text)
		var c := ch as Control
		if c != null and c.visible:
			_collect(ch, out)


func _rule() -> HSeparator:
	var s := HSeparator.new()
	s.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(s)
	return s


func _label(variation: StringName) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


static func _clear(box: Container) -> void:
	for ch in box.get_children():
		box.remove_child(ch)
		ch.queue_free()

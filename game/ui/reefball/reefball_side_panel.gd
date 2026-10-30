class_name ReefballSidePanel
extends PanelContainer
## One side's divers on the Reefball HUD (M3-UI-01): a header, an optional read line (the opponent
## read), and a row per diver: name, band, breath gauge and count, and a tag (holds the float,
## winded, resting, or the role it plays in the choice under the cursor: receives the pass, takes
## the float on a miss). A view only: ReefballHud hands it rows built from ReefballMatch.snapshot().
## Metrics: game/data/ui/reefball_hud.json, the "side" and "read" sections.
## A row is {id, name, band, breath, max_breath, low_fraction, tag, tag_role}.

var _m: Dictionary = {}
var _box: VBoxContainer
var _header: Label
var _read: Label
var _rows: Array[HBoxContainer] = []
var _row_ids: Array[StringName] = []


func setup(metrics: Dictionary) -> void:
	_m = metrics
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	HudLayout.place(self, _m)
	_box = VBoxContainer.new()
	_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_box.add_theme_constant_override(&"separation", int(HudLayout.num(_m, "gap")))
	add_child(_box)
	_header = _label(&"HeaderLabel")
	_header.custom_minimum_size.y = HudLayout.num(_m, "header_height")
	_header.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
	_box.add_child(_header)
	_read = _label(&"HelpDimLabel")
	_read.text_overrun_behavior = TextServer.OVERRUN_NO_TRIMMING
	_read.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_read.visible = false
	_box.add_child(_read)


func set_header(text: String) -> void:
	_header.text = text


## The read line under the header ("" hides it).
func set_read(text: String) -> void:
	_read.text = text
	_read.visible = text != ""
	_read.custom_minimum_size.x = _inner_width()
	_fit_read()


func header_text() -> String:
	return _header.text


func read_text() -> String:
	return _read.text if _read.visible else ""


## Replaces the rows (one per diver, in order).
func set_rows(rows: Array[Dictionary]) -> void:
	if rows.size() != _rows.size():
		for r in _rows:
			r.queue_free()
			_box.remove_child(r)
		_rows.clear()
		for _i in rows.size():
			_rows.append(_build_row())
	_row_ids.clear()
	for i in rows.size():
		_fill(_rows[i], rows[i])
		_row_ids.append(StringName(str(rows[i].get("id", ""))))
	_fit_read()


## The tag shown on diver `id`'s row ("" when none or no such row).
func tag_of(id: StringName) -> String:
	var i := _row_ids.find(id)
	return (_rows[i].get_child(4) as Label).text if i >= 0 else ""


## The band shown on diver `id`'s row.
func band_of(id: StringName) -> String:
	var i := _row_ids.find(id)
	return (_rows[i].get_child(1) as Label).text if i >= 0 else ""


## The breath count shown on diver `id`'s row.
func breath_of(id: StringName) -> String:
	var i := _row_ids.find(id)
	return (_rows[i].get_child(3) as Label).text if i >= 0 else ""


func row_count() -> int:
	return _rows.size()


func _build_row() -> HBoxContainer:
	var row := HBoxContainer.new()
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.custom_minimum_size.y = HudLayout.num(_m, "row_height")
	_box.add_child(row)
	var name_l := _label(&"HudName")
	name_l.custom_minimum_size.x = HudLayout.num(_m, "name_width")
	row.add_child(name_l)
	var band := _label(&"DimLabel")
	band.custom_minimum_size.x = HudLayout.num(_m, "band_width")
	row.add_child(band)
	var gauge := HudGauge.new(&"mp")
	gauge.custom_minimum_size = Vector2(HudLayout.num(_m, "gauge_width"), HudLayout.num(_m, "gauge_px"))
	gauge.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(gauge)
	var count := _label(&"HudNumber")
	count.custom_minimum_size.x = HudLayout.num(_m, "number_width")
	count.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	row.add_child(count)
	var tag := _label(&"SmallLabel")
	tag.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tag.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	row.add_child(tag)
	return row


func _fill(row: HBoxContainer, d: Dictionary) -> void:
	(row.get_child(0) as Label).text = str(d.get("name", ""))
	(row.get_child(1) as Label).text = str(d.get("band", ""))
	var gauge := row.get_child(2) as HudGauge
	gauge.low_fraction = float(d.get("low_fraction", 0.0))
	gauge.set_value(int(d.get("breath", 0)), int(d.get("max_breath", 1)))
	(row.get_child(3) as Label).text = tr("RBL_HUD_BREATH").format(
		{"b": int(d.get("breath", 0)), "max": int(d.get("max_breath", 0))}
	)
	var tag := row.get_child(4) as Label
	tag.text = str(d.get("tag", ""))
	_fit_row(row)
	var role := StringName(str(d.get("tag_role", "")))
	if role == &"":
		tag.remove_theme_color_override(&"font_color")
	else:
		tag.add_theme_color_override(&"font_color", get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE))


## Fixed cells sized for 100 % text: at 130 % a long name, band, count or tag shrinks a little to fit (the Lead's
## final-quality pass); the tag fits what the fixed cells leave of the panel's inner width.
func _fit_row(row: HBoxContainer) -> void:
	for i: int in [0, 1, 3]:
		HudLayout.fit_label(row.get_child(i) as Label, (row.get_child(i) as Control).custom_minimum_size.x)
	var used := 0.0
	for i in 4:
		used += (row.get_child(i) as Control).custom_minimum_size.x + row.get_theme_constant(&"separation")
	HudLayout.fit_label(row.get_child(4) as Label, _inner_width() - used)


func _notification(what: int) -> void:
	if what == NOTIFICATION_THEME_CHANGED:
		for row in _rows:
			_fit_row(row)
		_fit_read()


## At 130 % text the rows grow, and the panel grew past its rect into the drop panel below. The wrapped read line
## takes what the header and rows leave of the rect, its font shrinking a little to fit (HudLayout.fit_lines).
func _fit_read() -> void:
	if _read == null or not _read.visible:
		return
	_read.remove_theme_font_size_override(&"font_size")
	_read.size.x = _inner_width()
	var sb := get_theme_stylebox(&"panel")
	var sep := float(_box.get_theme_constant(&"separation"))
	var others := _box.get_combined_minimum_size().y - _read.get_combined_minimum_size().y - sep
	var room := HudLayout.rect_of(_m).size.y - (sb.get_minimum_size().y if sb != null else 0.0) - others
	HudLayout.fit_lines(_read, room)


func _label(variation: StringName) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


func _inner_width() -> float:
	var sb := get_theme_stylebox(&"panel")
	return HudLayout.rect_of(_m).size.x - (sb.get_minimum_size().x if sb != null else 0.0)

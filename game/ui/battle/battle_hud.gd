class_name BattleHud
extends Control
## The battle HUD (SPEC §7.6, docs/kb/art/ui.md §6): timeline right, party bars bottom right,
## commands bottom left, target info and help line on top. A view only: BattleController feeds
## it engine data and routes its menu signals; nothing here changes combat state.
## Accessibility (UiSettings): apply_settings() swaps in the palette/text-size theme and hands
## reduced motion to every animated component; the shared settings are followed live.

## Damage numbers spawned this battle (tests read it).
var damage_numbers_shown := 0
## The most recent numbers: [{text, kind, on_ally, crit}] (tests and debug overlays).
var recent_numbers: Array[Dictionary] = []
## The most recent non-empty help lines, oldest first (tests and debug overlays).
var help_history: PackedStringArray = []
## The accessibility settings in force (UiSettings.shared() unless a caller applies others).
var settings: UiSettings
## The palette role the help line is drawn in (&"" = the theme's own text color).
var help_role: StringName = &""
## A hero's Swell input (Rhen's lantern ring, M1-CMB-04), hidden until a technique opens it.
var swell_ring: SwellRingView
## Presentation that holds the battle while it plays (M3-BPR-02: a boss intro): name -> () -> bool. A freed
## owner's Callable is no longer valid and holds nothing.
var holds: Dictionary = {}

var _damage_m: Dictionary = {}
var _float_m: Dictionary = {}
var _base_theme: Theme
## Built on first use (M2-UI-02), so the staged battle build (M1-UI-03) never pays for them.
var _read_panel: ReadPanel
var _banner: OpeningBanner

@onready var timeline: TurnTimeline = %TurnTimeline
@onready var party: PartyPanel = %PartyPanel
@onready var commands: CommandMenu = %CommandMenu
@onready var target_cursor: TargetCursor = %TargetCursor
@onready var result: BattleResultPanel = %ResultPanel
@onready var _help_panel: PanelContainer = %HelpLine
@onready var _help_label: Label = %HelpText
@onready var _damage_layer: Control = %DamageLayer


func _ready() -> void:
	_damage_m = HudLayout.section(&"damage")
	_float_m = HudLayout.section(&"float_text")
	_base_theme = theme
	var help_m := HudLayout.section(&"help_line")
	HudLayout.place(_help_panel, help_m)
	_help_label.max_lines_visible = int(HudLayout.num(help_m, "max_lines"))
	swell_ring = SwellRingView.new()
	swell_ring.name = &"SwellRing"
	add_child(swell_ring)
	set_help("")
	if settings == null:
		apply_settings(UiSettings.shared())


## Uses `s` from now on (and follows its `changed` signal): theme, text size, motion.
func apply_settings(s: UiSettings) -> void:
	if settings != null and settings != s and settings.changed.is_connected(_on_settings_changed):
		settings.changed.disconnect(_on_settings_changed)
	settings = s
	if not s.changed.is_connected(_on_settings_changed):
		s.changed.connect(_on_settings_changed)
	_refresh_settings()


func motion_scale() -> float:
	return settings.motion_scale() if settings != null else 1.0


func animations_enabled() -> bool:
	return settings == null or settings.animations_enabled()


## The battle presentation speed (UiSettings.battle_speed, M2-UI-23; 1.0 without settings). The
## controller's waits and every float divide their durations by it.
func battle_speed() -> float:
	return settings.battle_speed() if settings != null else 1.0


## Shows `text` on the help line. `role` draws it in a palette role instead of the theme's text
## color (the item menu's defeat warning uses &"danger"); the next plain call resets it.
func set_help(text: String, role: StringName = &"") -> void:
	help_role = role
	_apply_help_role()
	_help_label.text = text
	_help_panel.visible = text != ""
	# Wrap onto a second line only when one line cannot hold the text, then let the panel fit it
	# (a Control grows to its minimum size but never shrinks back by itself).
	_help_label.remove_theme_font_size_override(&"font_size")
	var wraps := _help_width(text) > _help_room()
	_help_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART if wraps else TextServer.AUTOWRAP_OFF
	if wraps:
		_fit_help_lines()
	_help_panel.size = Vector2(_help_panel.size.x, 0.0)
	if text != "" and (help_history.is_empty() or help_history[-1] != text):
		help_history.append(text)
		if help_history.size() > CtbTimeline.PREVIEW_LENGTH:
			help_history.remove_at(0)


## A help text past its max_lines_visible at a large text size (130 %) shrinks its font a little (to
## HudLayout.FIT_MIN_FONT_SCALE) rather than lose its end (the Lead's final-quality pass: a Vowbound's call line).
func _fit_help_lines() -> void:
	var fs := _help_label.get_theme_font_size(&"font_size")
	var floor_fs := ceili(fs * HudLayout.FIT_MIN_FONT_SCALE)
	var size := fs
	while size > floor_fs and _help_label.get_line_count() > _help_label.max_lines_visible:
		size -= 1
		_help_label.add_theme_font_size_override(&"font_size", size)


## True when the current help needs its second line (tests).
func help_wraps() -> bool:
	return _help_label.autowrap_mode != TextServer.AUTOWRAP_OFF


func _help_width(text: String) -> float:
	var font := _help_label.get_theme_font(&"font")
	var px := _help_label.get_theme_font_size(&"font_size")
	return font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x if font != null else 0.0


func _help_room() -> float:
	var sb := _help_panel.get_theme_stylebox(&"panel")
	return _help_panel.size.x - (sb.get_minimum_size().x if sb != null else 0.0)


func _apply_help_role() -> void:
	if help_role == &"":
		_help_label.remove_theme_color_override(&"font_color")
	else:
		_help_label.add_theme_color_override(&"font_color", get_theme_color(help_role, HymnThemeBuilder.PALETTE_TYPE))


func help_text() -> String:
	return _help_label.text if _help_panel.visible else ""


## Pops a number at `at` (HUD coordinates). `stack` offsets simultaneous numbers on one target.
func pop_number(text: String, at: Vector2, kind: StringName, on_ally: bool, crit: bool, stack: int = 0) -> void:
	var n := DamageNumber.new()
	_damage_layer.add_child(n)
	var p := at - Vector2(0.0, HudLayout.num(_damage_m, "stack_px") * stack)
	n.pop(text, p, kind, on_ally, crit, _damage_m, motion_scale(), &"", battle_speed())
	_note_number(text, kind, on_ally, crit)


## Floats a word above `at` ("Reflected", "Heal turns to harm"), in palette role `role`.
func pop_info(text: String, at: Vector2, role: StringName = &"text_dim") -> void:
	var n := DamageNumber.new()
	_damage_layer.add_child(n)
	var p := at - Vector2(0.0, HudLayout.num(_float_m, "lift_px"))
	n.pop(text, p, DamageNumber.KIND_INFO, false, false, _float_m, motion_scale(), role, battle_speed())
	_note_number(text, DamageNumber.KIND_INFO, false, false)


## The Read panel (M2-UI-02), built the first time a Read lands.
func read_panel() -> ReadPanel:
	if _read_panel == null:
		_read_panel = ReadPanel.new()
		_read_panel.name = &"ReadPanel"
		add_child(_read_panel)
		_refresh_settings()
	return _read_panel


## The preemptive / ambush banner (M2-UI-02), built the first time an opening needs it.
func opening_banner() -> OpeningBanner:
	if _banner == null:
		_banner = OpeningBanner.new()
		_banner.name = &"OpeningBanner"
		add_child(_banner)
		move_child(_banner, _damage_layer.get_index())  # under the floats, the menus and panels
		_refresh_settings()
	return _banner


## True while a modal HUD panel (the Read panel) is open: BattleController.tick() then holds every
## wait, so the battle does not move on under it and the panel costs no battle time. M2-BPR-05: also
## while the opening banner waits for the router's fade to lift (OpeningBanner.is_pending). M3-BPR-02: also while
## any of `holds` says so (a boss intro).
func holds_battle() -> bool:
	for hold: Callable in holds.values():
		if hold.is_valid() and bool(hold.call()):
			return true
	return (_read_panel != null and _read_panel.is_open()) or (_banner != null and _banner.is_pending())


## Closes the Read panel and the opening banner (a new battle, the result screen).
func close_overlays() -> void:
	if _read_panel != null:
		_read_panel.close()
	if _banner != null:
		_banner.hide_banner()


func set_combat_ui_visible(on: bool) -> void:
	for c: CanvasItem in [timeline, party, commands, _help_panel]:
		c.visible = on
	if not on:
		close_overlays()
		swell_ring.close()
		target_cursor.clear()
		target_cursor.show_actor(Vector2.ZERO, false)
		target_cursor.show_provoker(Vector2.ZERO, false)


func _note_number(text: String, kind: StringName, on_ally: bool, crit: bool) -> void:
	damage_numbers_shown += 1
	recent_numbers.append({"text": text, "kind": kind, "on_ally": on_ally, "crit": crit})
	if recent_numbers.size() > CtbTimeline.PREVIEW_LENGTH:
		recent_numbers.pop_front()


func _on_settings_changed(_key: StringName) -> void:
	_refresh_settings()


func _refresh_settings() -> void:
	if settings == null or timeline == null:
		return
	if _base_theme != null:
		theme = settings.theme_for(_base_theme)
	var reduced := settings.reduced_motion()
	timeline.reduced_motion = reduced
	timeline.crossfade_sec = settings.crossfade_sec()
	timeline.crossfade_from_alpha = settings.crossfade_from_alpha()
	commands.reduced_motion = reduced
	target_cursor.set_reduced_motion(reduced)
	result.motion_scale = settings.motion_scale()
	party.set_reduced_motion(reduced)
	swell_ring.reduced_motion = reduced
	var assist_key := settings.timing_assist_tag_key()
	swell_ring.set_assist_text(tr(assist_key) if assist_key != "" else "")
	if _read_panel != null:
		_read_panel.motion_scale = settings.motion_scale()
	if _banner != null:
		_banner.reduced_motion = reduced
	party.refresh()
	_apply_help_role()  # a palette switch recolors a warning already on screen

class_name UiSettings
extends RefCounted
## Accessibility settings for every UI screen (SPEC §6.11, docs/kb/tech/ui.md § Accessibility):
## reduced motion, a text-size scale, and a colorblind palette. Data-driven: the settings, their
## options, their loc keys and the palette overrides live in game/data/ui/accessibility.json, so
## the future settings menu only lists settings() and calls set_value().
##
## One shared instance (shared()) is what the HUD listens to; it loads user://settings.cfg once.
## Tests and captures build their own with UiSettings.new(), which always starts at the defaults.
## Views ask it questions (animations_enabled(), motion_scale(), theme_for()) instead of reading
## raw values, so a new setting never needs a change in every component.

signal changed(key: StringName)

const DATA_PATH := "res://game/data/ui/accessibility.json"
const CONFIG_PATH := "user://settings.cfg"
const REDUCED_MOTION := &"reduced_motion"
const TEXT_SCALE := &"text_scale"
const PALETTE := &"palette"
const TIMING_ASSIST := &"timing_assist"
const TEXT_SPEED := &"text_speed"
const DIALOGUE_BACKING := &"dialogue_backing"
const OBJECTIVE_CUE := &"objective_cue"
const TUTORIAL_TIPS := &"tutorial_tips"
const BATTLE_SPEED := &"battle_speed"
const SUMMON_CINEMATIC := &"summon_cinematic"
## The cuts summon_cinematic_cut() answers (accessibility.json "summon_cinematics").
const CUT_FULL := &"full"
const CUT_SHORT := &"short"
const CUT_NONE := &"none"
const DIALOGUE_AUTO := &"dialogue_auto"
const KIND_BOOL := "bool"
const KIND_ENUM := "enum"
const PALETTE_STANDARD := &"standard"
## The theme a followed root starts from when it sets none of its own (follow()).
const BASE_THEME_PATH := "res://game/ui/theme/hymn_theme.tres"
const META_BASE_THEME := &"hymn_base_theme"

static var _shared: UiSettings

var data: Dictionary = {}

var _values: Dictionary = {}
var _rows: Dictionary = {}
var _order: Array[StringName] = []
var _theme_cache: Dictionary = {}


func _init(data_path: String = DATA_PATH) -> void:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(data_path))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("accessibility")) != TYPE_DICTIONARY:
		push_error("UiSettings: could not read 'accessibility' from %s" % data_path)
		return
	data = (parsed as Dictionary)["accessibility"] as Dictionary
	for raw: Variant in data.get("settings", []):
		var row := raw as Dictionary
		var sid := StringName(str(row.get("id", "")))
		_rows[sid] = row
		_order.append(sid)
	reset()


## The instance the game uses (loaded from user://settings.cfg on first use).
static func shared() -> UiSettings:
	if _shared == null:
		_shared = UiSettings.new()
		_shared.load_from(CONFIG_PATH)
	return _shared


## Replaces the shared instance (tests; null makes the next shared() reload from disk).
static func set_shared(s: UiSettings) -> void:
	_shared = s


# --- the generic layer the settings menu calls --------------------------------------------


## Setting ids in menu order.
func settings() -> Array[StringName]:
	return _order.duplicate()


## The data row of one setting: {id, type, default, options?, option_keys?, label_key, help_key}.
func setting_row(key: StringName) -> Dictionary:
	return _rows.get(key, {}) as Dictionary


## Allowed values in display order ([false, true] for a bool).
func options(key: StringName) -> Array:
	var row := setting_row(key)
	if str(row.get("type", "")) == KIND_BOOL:
		return [false, true]
	return (row.get("options", []) as Array).duplicate()


func default_value(key: StringName) -> Variant:
	return _coerce(key, setting_row(key).get("default"))


func get_value(key: StringName) -> Variant:
	return _values.get(key, default_value(key))


## Sets one setting. Returns false (and changes nothing) for an unknown key or a value that is
## not one of its options. Emits `changed` only when the value really changes.
func set_value(key: StringName, value: Variant) -> bool:
	if not _rows.has(key):
		return false
	var v: Variant = _coerce(key, value)
	if v == null or not _has_option(key, v):
		return false
	if _values.get(key) == v:
		return true
	_values[key] = v
	changed.emit(key)
	return true


## Back to the defaults; emits `changed` for every setting that moved.
func reset() -> void:
	for key in _order:
		var was: Variant = _values.get(key)
		_values[key] = default_value(key)
		if was != null and was != _values[key]:
			changed.emit(key)


func is_default() -> bool:
	for key in _order:
		if get_value(key) != default_value(key):
			return false
	return true


# --- what views ask -----------------------------------------------------------------------


func reduced_motion() -> bool:
	return bool(get_value(REDUCED_MOTION))


func text_scale() -> float:
	return float(get_value(TEXT_SCALE))


func palette() -> StringName:
	return StringName(str(get_value(PALETTE)))


func timing_assist() -> StringName:
	return StringName(str(get_value(TIMING_ASSIST)))


## The dialogue reveal speed for this text_speed (M2-UI-12): `default_cps` times the option's
## multiplier (accessibility.json "text_speeds"), clamped to [min_cps, max_cps]; 0 = instant.
func dialogue_chars_per_sec(default_cps: float, min_cps: float, max_cps: float) -> float:
	var k := float((data.get("text_speeds", {}) as Dictionary).get(str(get_value(TEXT_SPEED)), 1.0))
	if k <= 0.0:
		return 0.0
	return clampf(default_cps * k, min_cps, max_cps)


## The alpha of the band behind dialogue and cutscene lines (M2-UI-12; 0 = no band).
func dialogue_backing_alpha() -> float:
	return float((data.get("dialogue_backings", {}) as Dictionary).get(str(get_value(DIALOGUE_BACKING)), 0.0))


## True when the field shows the destination cue toward the objective (M2-UI-19).
func objective_cue_enabled() -> bool:
	return bool(get_value(OBJECTIVE_CUE))


## True when the field shows first-time tips (M2-UI-24).
func tutorial_tips_enabled() -> bool:
	return bool(get_value(TUTORIAL_TIPS))


## The battle presentation speed (M2-UI-23): the battle_speed option, a multiplier (1.0 = normal),
## clamped to accessibility.json "battle_speed" min/max. BattleChoreo (M2-BPR-03) reads the same value.
func battle_speed() -> float:
	var lim := data.get("battle_speed", {}) as Dictionary
	return clampf(float(get_value(BATTLE_SPEED)), float(lim.get("min", 1.0)), float(lim.get("max", 1.0)))


## What every battle presentation duration is multiplied by (1 / battle_speed()): the controller's
## pacing waits, damage numbers and float words, the camera shake and the hit recoil. It never reaches
## the engine or a Swell input window (SwellRingClock, SwellInput run in real time).
func battle_time_scale() -> float:
	return 1.0 / battle_speed()


## The cut a Vowbound's call cinematic plays (M2-UI-23; SPEC §6.3): CUT_FULL, CUT_SHORT (skip the
## middle beats) or CUT_NONE (straight to the effect), for that Vowbound's first call or a later one
## (accessibility.json "summon_cinematics"). The cinematic that reads it is BattleSummonCinematic (M2-BPR-08/09).
func summon_cinematic_cut(first_call: bool) -> StringName:
	var row := (data.get("summon_cinematics", {}) as Dictionary).get(str(get_value(SUMMON_CINEMATIC)), {}) as Dictionary
	return StringName(str(row.get("first" if first_call else "again", CUT_FULL)))


## True when a fully revealed dialogue line advances by itself after a hold (M2-UI-25).
func dialogue_auto_enabled() -> bool:
	return bool(get_value(DIALOGUE_AUTO))


## The short on-screen tag of the timing assist in force (its "tag_key"; "" when it is off).
func timing_assist_tag_key() -> String:
	return str(_assist().get("tag_key", ""))


## A Swell input row (swell.json "inputs", any kind) as the timing assist plays it (M2-UI-01).
## The assist is applied to the row, never in the grading code, and the result still passes the
## validator's rules for its kind:
##   "wide" scales the windows by window_scale: perfect_sec and good_sec (ring, chant, brace), each
##   clamped (ring: inside the beat; chant: half the closest note gap; brace: before the counter's
##   window would reach the last blow), or window_sec (glyph: within max_duration_sec);
##   "auto" sets assist_floor ("good"): a miss records the step's good grade (SwellInput._record);
##   "hold" (M2-UI-14) sets it too, with assist_hold: only while Confirm is held.
## A copy; off returns it as is.
func timing_input(row: Dictionary) -> Dictionary:
	var out := row.duplicate(true)
	var assist := _assist()
	if assist.has("window_scale"):
		_widen(out, float(assist["window_scale"]))
	if assist.has("assist_floor"):
		out["assist_floor"] = str(assist["assist_floor"])
	if bool(assist.get("assist_hold", false)):
		out["assist_hold"] = true
	return out


## False under reduced motion: chips snap (with a short cross-fade) instead of sliding, pulses,
## bobbing and breathing stop, and the camera never shakes.
func animations_enabled() -> bool:
	return not reduced_motion()


## Multiplier for any translation a view animates (art/ui.md §5: halved under reduced motion).
func motion_scale() -> float:
	return float(_motion().get("translate_scale_reduced", 1.0)) if reduced_motion() else 1.0


## The cross-fade that replaces a slide under reduced motion.
func crossfade_sec() -> float:
	return float(_motion().get("crossfade_sec", 0.0))


func crossfade_from_alpha() -> float:
	return float(_motion().get("crossfade_from_alpha", 0.0))


## Palette ids in display order.
func palette_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for p: Variant in options(PALETTE):
		out.append(StringName(str(p)))
	return out


## Theme role -> [swatch or "#RRGGBB", alpha] overrides of the active palette.
func color_overrides() -> Dictionary:
	return ((data.get("palettes", {}) as Dictionary).get(String(palette()), {}) as Dictionary).duplicate(true)


## The theme recipe (game/data/ui/theme.json) with this palette's colors and every font size
## scaled by text_scale() (rounded; scale >= 1, so the 22 px minimum holds).
func theme_config(base_cfg: Dictionary = {}) -> Dictionary:
	var cfg := (base_cfg if not base_cfg.is_empty() else HymnThemeBuilder.load_config()).duplicate(true)
	var colors: Dictionary = cfg.get("colors", {})
	var over := color_overrides()
	for role: Variant in over:
		colors[role] = over[role]
	var s := text_scale()
	cfg["default_font_size"] = roundi(float(cfg.get("default_font_size", 0)) * s)
	var variations: Dictionary = cfg.get("variations", {})
	for vname: Variant in variations:
		var v: Dictionary = variations[vname]
		if v.has("size"):
			v["size"] = roundi(float(v["size"]) * s)
	return cfg


## The theme a UI root should use: `base` itself at the defaults (so nothing is rebuilt and the
## saved hymn_theme.tres stays authoritative), otherwise a theme built from theme_config().
## Built themes are cached per (palette, scale).
func theme_for(base: Theme) -> Theme:
	if palette() == PALETTE_STANDARD and is_equal_approx(text_scale(), 1.0):
		return base
	var key := "%s@%.2f" % [palette(), text_scale()]
	if not _theme_cache.has(key):
		_theme_cache[key] = HymnThemeBuilder.build(theme_config())
	return _theme_cache[key] as Theme


## Gives `root` this palette and text size now (theme_for over its own theme, or the Hymn theme
## when it sets none) and again on every later change while it is in the tree. Every menu
## outside battle calls it in _ready (M2-UI-09); BattleHud has its own apply_settings().
## Out of the tree it stops listening; back in, it catches up and listens again. A field zone kept resident through a
## random fight (SceneRouter.keep_field_resident) comes back without _ready, so its prompts must not stop following
## (the Lead's battle-return check, 2026-10-30: a text size set in the battle pause never reached the field again).
func follow(root: Control) -> void:
	apply_to(root)
	var on_change := func(_key: StringName) -> void:
		if is_instance_valid(root):
			apply_to(root)
	changed.connect(on_change)
	root.tree_exited.connect(
		func() -> void:
			if changed.is_connected(on_change):
				changed.disconnect(on_change)
	)
	root.tree_entered.connect(
		func() -> void:
			apply_to(root)
			if not changed.is_connected(on_change):
				changed.connect(on_change)
	)


## Sets `root`'s theme for the current palette and text size once.
func apply_to(root: Control) -> void:
	if not root.has_meta(META_BASE_THEME):
		var base := root.theme if root.theme != null else load(BASE_THEME_PATH) as Theme
		root.set_meta(META_BASE_THEME, base)
	root.theme = theme_for(root.get_meta(META_BASE_THEME) as Theme)


# --- persistence (the same user://settings.cfg as GraphicsSettings, its own section) -------


func save_to(path: String = CONFIG_PATH) -> Error:
	var cfg := ConfigFile.new()
	cfg.load(path)  # keep the other sections (graphics, audio, ...); a missing file is fine
	for key in _order:
		cfg.set_value(_section(), String(key), get_value(key))
	return cfg.save(path)


## Loads saved values; unknown keys and values outside the options are ignored.
func load_from(path: String = CONFIG_PATH) -> void:
	var cfg := ConfigFile.new()
	if cfg.load(path) != OK:
		return
	for key in _order:
		if cfg.has_section_key(_section(), String(key)):
			var v: Variant = _coerce(key, cfg.get_value(_section(), String(key)))
			if v != null and _has_option(key, v):
				_values[key] = v


# --- internals ----------------------------------------------------------------------------


func _section() -> String:
	return str(data.get("config_section", "accessibility"))


func _widen(row: Dictionary, k: float) -> void:
	var kind := StringName(str(row.get("kind", "")))
	if kind == SwellInput.KIND_GLYPH:
		var longest := float(_assist_data().get("max_duration_sec", 0.0)) - float(row.get("lead_in_sec", 0.0))
		row["window_sec"] = minf(float(row.get("window_sec", 0.0)) * k, longest)
		return
	var room := INF
	match kind:
		SwellInput.KIND_TIMING_RING:
			var beat := float(row.get("beat_sec", 0.0))
			var peak := float(row.get("peak_at", 0.0)) * beat
			room = minf(peak, beat - peak)
		SwellInput.KIND_CHANT:
			var at: Array[float] = []
			for n: Variant in row.get("notes", []):
				at.append(float((n as Dictionary).get("at", 0.0)))
			for i in range(1, at.size()):
				room = minf(room, (at[i] - at[i - 1]) * 0.5)
		SwellInput.KIND_BRACE:
			var last := 0.0
			for t: Variant in row.get("impacts", []):
				last = maxf(last, float(t))
			room = float(row.get("counter_at", 0.0)) - last - float(_assist_data().get("edge_margin_sec", 0.0))
	row["good_sec"] = minf(float(row.get("good_sec", 0.0)) * k, room)
	row["perfect_sec"] = minf(float(row.get("perfect_sec", 0.0)) * k, float(row["good_sec"]))


func _assist_data() -> Dictionary:
	return data.get("timing_assist", {}) as Dictionary


func _assist() -> Dictionary:
	return _assist_data().get(String(timing_assist()), {}) as Dictionary


func _motion() -> Dictionary:
	return data.get("motion", {}) as Dictionary


func _has_option(key: StringName, v: Variant) -> bool:
	for o: Variant in options(key):
		if _coerce(key, o) == v:
			return true
	return false


## Normalizes a raw value to the setting's type (null when it cannot be one).
func _coerce(key: StringName, value: Variant) -> Variant:
	var row := setting_row(key)
	var t := typeof(value)
	if str(row.get("type", "")) == KIND_BOOL:
		return bool(value) if t in [TYPE_BOOL, TYPE_INT, TYPE_FLOAT] else null
	var opts: Array = row.get("options", [])
	if opts.is_empty():
		return null
	if typeof(opts[0]) in [TYPE_INT, TYPE_FLOAT]:
		return _snap_number(opts, value) if t in [TYPE_INT, TYPE_FLOAT] else null
	return str(value) if t in [TYPE_STRING, TYPE_STRING_NAME] else null


## A number as the matching option (so 1.15 from a file equals the 1.15 option exactly).
static func _snap_number(opts: Array, value: Variant) -> float:
	for o: Variant in opts:
		if is_equal_approx(float(o), float(value)):
			return float(o)
	return float(value)

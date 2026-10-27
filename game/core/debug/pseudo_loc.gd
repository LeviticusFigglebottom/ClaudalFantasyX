class_name PseudoLoc
extends RefCounted
## Debug pseudo-localisation (M2-UI-28; docs/kb/tech/ui.md 'Pseudo-localisation'). Builds a
## Translation for a pseudo locale (game/data/debug/pseudo_loc.json) from every loc CSV: each
## string accented and about 40% longer, in brackets, so a screen shows at a glance which text is
## not localized (no brackets), which text is cut (no closing bracket) and which box is too small
## for a longer language. "Settings" becomes "[Šéţţîñĝš ····]".
## {placeholders}, %-formats, BBCode tags and newlines are copied as they are, so String.format,
## the % operator and RichTextLabel markup keep working.
##
## Debug builds only: it lives in game/core/debug/ (release exports strip it), nothing in game code
## names it (UiInput and the overlay load it by path), and enable() refuses outside a debug build.
## Turned on at launch by `--pseudo-loc` or HYMN_PSEUDO_LOC=1 (apply_launch_options, called by
## UiInput before the first scene), and toggled by F10 in the debug overlay. Text already on screen
## keeps its old locale until its screen is built again (reopen the menu).

const DATA_PATH := "res://game/data/debug/pseudo_loc.json"
## Matches a %-format (%d, %s, %05.1f, %%) at the start of the string.
const FORMAT_RE := "^%[-+ 0#]*[0-9*]*(\\.[0-9*]+)?[a-zA-Z%]"
## Matches a BBCode tag ([b], [/b], [color=#fff], [img=32]...) at the start of the string.
const TAG_RE := "^\\[/?[a-zA-Z_][^\\[\\]\\n]*\\]"
const PROJECT_TRANSLATIONS := "internationalization/locale/translations"

static var _cfg: Dictionary = {}
static var _format_re: RegEx
static var _tag_re: RegEx
static var _translation: Translation
static var _previous_locale := ""


## The data file (cached).
static func config() -> Dictionary:
	if _cfg.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if typeof(parsed) != TYPE_DICTIONARY:
			push_error("PseudoLoc: could not read %s" % DATA_PATH)
			return {}
		_cfg = parsed as Dictionary
	return _cfg


static func locale() -> String:
	return str(config().get("locale", ""))


## `text` pseudo-localized: accented, each line padded by `expansion` of its visible length, the
## whole between prefix and suffix; {placeholders}, %-formats, BBCode tags and newlines kept.
static func pseudo(text: String) -> String:
	var cfg := config()
	var out := PackedStringArray()
	for line in text.split("\n"):
		out.append(_pseudo_line(line, cfg))
	return str(cfg.get("prefix", "")) + "\n".join(out) + str(cfg.get("suffix", ""))


static func _pseudo_line(line: String, cfg: Dictionary) -> String:
	if _format_re == null:
		_format_re = RegEx.create_from_string(FORMAT_RE)
		_tag_re = RegEx.create_from_string(TAG_RE)
	var accents: Dictionary = cfg.get("accents", {})
	var out := ""
	var shown := 0
	var i := 0
	while i < line.length():
		var keep := _kept_token(line, i)
		if keep > 0:
			out += line.substr(i, keep)
			i += keep
			continue
		var ch := line[i]
		out += str(accents.get(ch, ch))
		if ch != " ":
			shown += 1
		i += 1
	return out + _padding(shown, cfg)


## The length of the token at `at` that is copied untouched ({name}, %d, [b]), or 0.
static func _kept_token(line: String, at: int) -> int:
	var ch := line[at]
	if ch == "{":
		var close := line.find("}", at)
		return close - at + 1 if close > at else 0
	if ch == "%" or ch == "[":
		var m := (_format_re if ch == "%" else _tag_re).search(line.substr(at))
		return m.get_end() if m != null else 0
	return 0


## " ····· ··" for `shown` visible characters: groups of pad_group so word wrapping can break it.
static func _padding(shown: int, cfg: Dictionary) -> String:
	if shown <= 0:
		return ""
	var n := ceili(shown * float(cfg.get("expansion", 0.0)))
	var group := maxi(int(cfg.get("pad_group", 1)), 1)
	var dot := str(cfg.get("pad_char", ""))
	var out := ""
	while n > 0:
		out += " " + dot.repeat(mini(n, group))
		n -= group
	return out


## The loc CSVs the project's translations are imported from (game/data/loc/*.csv).
static func source_csvs() -> PackedStringArray:
	var out := PackedStringArray()
	for path: String in ProjectSettings.get_setting(PROJECT_TRANSLATIONS, PackedStringArray()):
		var csv := path.get_base_dir().path_join(path.get_file().get_slice(".", 0) + ".csv")
		if FileAccess.file_exists(csv) and not out.has(csv):
			out.append(csv)
	var dir := str(config().get("loc_dir", ""))
	for f in DirAccess.get_files_at(dir):
		if f.get_extension() == "csv" and not out.has(dir.path_join(f)):
			out.append(dir.path_join(f))
	return out


## The pseudo locale's Translation: every key of every loc CSV, its source-locale text pseudo'd.
static func build() -> Translation:
	var t := Translation.new()
	t.locale = locale()
	var source := str(config().get("source_locale", ""))
	for csv in source_csvs():
		var f := FileAccess.open(csv, FileAccess.READ)
		if f == null:
			continue
		var col := Array(f.get_csv_line()).find(source)
		while col > 0 and not f.eof_reached():
			var row := f.get_csv_line()
			if row.size() > col and row[0] != "":
				t.add_message(row[0], pseudo(row[col]))
	return t


static func is_enabled() -> bool:
	return _translation != null


## Adds the pseudo translation and switches to its locale. Debug builds only; false in release.
static func enable() -> bool:
	if not OS.is_debug_build():
		return false
	if _translation == null:
		_translation = build()
		_previous_locale = TranslationServer.get_locale()
		TranslationServer.add_translation(_translation)
	TranslationServer.set_locale(locale())
	return true


## Back to the locale before enable(), without the pseudo translation.
static func disable() -> void:
	if _translation == null:
		return
	TranslationServer.remove_translation(_translation)
	_translation = null
	var back := _previous_locale if _previous_locale != "" else str(config().get("source_locale", ""))
	TranslationServer.set_locale(back)


## Flips it. Returns whether it is on now.
static func toggle() -> bool:
	if is_enabled():
		disable()
		return false
	return enable()


## True when the launch asks for it: `flag` among `args`, or `env` set to anything but an off word.
static func wanted(args: PackedStringArray, env: String) -> bool:
	var cfg := config()
	if args.has(str(cfg.get("flag", ""))):
		return true
	return not (cfg.get("env_off", []) as Array).has(env.strip_edges().to_lower())


## Turns it on when the command line or the environment asks (UiInput calls this at startup).
static func apply_launch_options() -> bool:
	var args := OS.get_cmdline_user_args() + OS.get_cmdline_args()
	if not wanted(args, OS.get_environment(str(config().get("env_var", "")))):
		return false
	return enable()

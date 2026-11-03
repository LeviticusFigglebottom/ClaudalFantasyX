class_name StatusHelpModel
extends RefCounted
## What every status is and how it goes away (the human's playtest FAST-TRACK, 2026-11-03), node-free.
## Data: game/data/ui/status_help.json (its doc names every source). The words come from the game's own
## tables, so a new cure item, a new cleansing skill or a changed duration shows here with no edit:
##   statuses.json         name_key, name_key + "_DESC", category (beneficial = a buff), default_duration
##   items.json            consumables whose battle effects "cure" the status ("field": false = in battle only)
##   characters.json       each hero's starting skills; the Lattice's ability nodes; vowbound.json skills
##   skills.json           a party skill's "cleanses" list
##   party_rest.json       carried_statuses (outlast a battle) and shrine_cures (a save shrine's rest)
## The views: StatusHelpPanel (battle and field), StatusTipCard (the first time), StatusGlyph's callout (a
## chip's one line) and the Codex's Afflictions entries (CodexModel.body). Tests build it from tables.

const DATA_PATH := "res://game/data/ui/status_help.json"
const STATUSES_PATH := "res://game/data/battle/statuses.json"
const SKILLS_PATH := "res://game/data/battle/skills.json"
const CHARACTERS_PATH := "res://game/data/battle/characters.json"
const ITEMS_PATH := "res://game/data/items/items.json"
const LATTICE_PATH := "res://game/data/progression/lattice_standard.json"
const VOWBOUND_PATH := "res://game/data/battle/vowbound.json"
const DESC_SUFFIX := "_DESC"
const BUFF_CATEGORY := "beneficial"
const UNTIL_CURED := -1
const EFFECT_CURE := "cure"

const LASTS_TURNS_KEY := "STATUS_HELP_LASTS_TURNS_FMT"
const LASTS_CURED_KEY := "STATUS_HELP_LASTS_CURED"
const ENDS_BATTLE_KEY := "STATUS_HELP_ENDS_WITH_BATTLE"
const CARRIED_KEY := "STATUS_HELP_CARRIED"
const ITEMS_KEY := "STATUS_HELP_ITEMS_FMT"
const ABILITIES_KEY := "STATUS_HELP_ABILITIES_FMT"
const SHRINE_KEY := "STATUS_HELP_SHRINE"
const BATTLE_ONLY_KEY := "STATUS_HELP_IN_BATTLE_FMT"
const BY_KEY := "STATUS_HELP_BY_FMT"
const JOIN_KEY := "STATUS_HELP_JOIN"
const ONE_LINE_KEY := "STATUS_HELP_ONE_LINE_FMT"
const BUFF_KEY := "STATUS_HELP_KIND_BUFF"
const AILMENT_KEY := "STATUS_HELP_KIND_AILMENT"
const NO_CURE_KEY := "STATUS_HELP_NO_CURE"

static var _shared: StatusHelpModel

## statuses.json rows in data order.
var rows: Array[Dictionary] = []
## Item rows in items.json order ({id, name_key, battle, field}).
var item_rows: Array[Dictionary] = []
## skills.json: id -> row.
var skills: Dictionary = {}
## Party skill sources in order: [{skill, by_key, flag}] (flag "" = always known).
var sources: Array[Dictionary] = []
var carried: Array[StringName] = []
var shrine_cures: Array[StringName] = []
## status id -> loc key of its one-off way out (status_help.json notes).
var notes: Dictionary = {}
## status id -> loc key of its own time line (status_help.json lasts: Last Tide counts down, it never wears off).
var lasts_keys: Dictionary = {}
var met_prefix := "status_"

var _is_set: Callable


## `tables`: {statuses, items, skills, characters, lattice_nodes, vowbound, carried, shrine, notes,
## met_prefix} (arrays of rows as in the data files). `flag_check`: Callable(flag) -> bool (default
## Game.get_flag): a Vowbound's skills count only once its bound flag is set.
func _init(tables: Dictionary = {}, flag_check: Callable = Callable()) -> void:
	_is_set = flag_check if flag_check.is_valid() else func(f: StringName) -> bool: return bool(Game.get_flag(f))
	for r: Variant in tables.get("statuses", []):
		rows.append(r as Dictionary)
	for r: Variant in tables.get("items", []):
		item_rows.append(r as Dictionary)
	for r: Variant in tables.get("skills", []):
		skills[StringName(str((r as Dictionary).get("id", "")))] = r
	for c: Variant in tables.get("characters", []):
		var cd := c as Dictionary
		for s: Variant in cd.get("skills", []):
			sources.append({"skill": StringName(str(s)), "by_key": str(cd.get("name_key", "")), "flag": ""})
	var char_keys := {}
	for c: Variant in tables.get("characters", []):
		char_keys[str((c as Dictionary).get("id", ""))] = str((c as Dictionary).get("name_key", ""))
	for n: Variant in tables.get("lattice_nodes", []):
		var nd := n as Dictionary
		if nd.has("skill"):
			var by := str(char_keys.get(str(nd.get("region", "")), ""))
			sources.append({"skill": StringName(str(nd["skill"])), "by_key": by, "flag": ""})
	for v: Variant in tables.get("vowbound", []):
		var vd := v as Dictionary
		for s: Variant in vd.get("skills", []):
			var src := {"skill": StringName(str(s)), "by_key": str(vd.get("name_key", ""))}
			src["flag"] = str(vd.get("bound_flag", ""))
			sources.append(src)
	carried = _ids(tables.get("carried", []))
	shrine_cures = _ids(tables.get("shrine", []))
	notes = tables.get("notes", {}) as Dictionary
	lasts_keys = tables.get("lasts", {}) as Dictionary
	met_prefix = str(tables.get("met_prefix", met_prefix))


## The live model over the game's data files and flags.
static func from_game() -> StatusHelpModel:
	var help := load_data()
	var tables := {
		"statuses": _json(STATUSES_PATH).get("statuses", []),
		"items": _json(ITEMS_PATH).get("items", []),
		"skills": _json(SKILLS_PATH).get("skills", []),
		"characters": _json(CHARACTERS_PATH).get("characters", []),
		"lattice_nodes": _json(LATTICE_PATH).get("nodes", []),
		"vowbound": _json(VOWBOUND_PATH).get("vowbound", []),
		"carried": Game.carried_statuses(),
		"shrine": Game.shrine_cures(),
		"notes": help.get("notes", {}),
		"lasts": help.get("lasts", {}),
		"met_prefix": help.get("met_prefix", "status_"),
	}
	return StatusHelpModel.new(tables)


## One live model for the chips' one-line help (built on first use; the tables never change in play,
## and a Vowbound's flag is read when asked). Tests may replace it.
static func shared() -> StatusHelpModel:
	if _shared == null:
		_shared = from_game()
	return _shared


static func set_shared(m: StatusHelpModel) -> void:
	_shared = m


static func load_data() -> Dictionary:
	return _json(DATA_PATH).get("status_help", {}) as Dictionary


## The status help key (status_help.json action), added when the InputMap lacks it.
static func ensure_action() -> void:
	FieldInput.add_actions(load_data().get("action", {}) as Dictionary, 0.0)


## The declared flag set the first time `sid` lands on a party member.
func met_flag(sid: StringName) -> StringName:
	return StringName("%s%s_met" % [met_prefix, sid])


## Every status id, in statuses.json order.
func ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for r in rows:
		out.append(StringName(str(r.get("id", ""))))
	return out


func has(sid: StringName) -> bool:
	return not row(sid).is_empty()


func row(sid: StringName) -> Dictionary:
	for r in rows:
		if StringName(str(r.get("id", ""))) == sid:
			return r
	return {}


func is_buff(sid: StringName) -> bool:
	return str(row(sid).get("category", "")) == BUFF_CATEGORY


func name_key(sid: StringName) -> String:
	return str(row(sid).get("name_key", ""))


func desc_key(sid: StringName) -> String:
	var k := name_key(sid)
	return k + DESC_SUFFIX if k != "" else ""


func name_of(sid: StringName) -> String:
	return _tr(name_key(sid))


func desc_of(sid: StringName) -> String:
	return _tr(desc_key(sid))


## "Ailment" or "Buff" (its polarity in words: the glyph's backing shape says it too).
func kind_of(sid: StringName) -> String:
	return _tr(BUFF_KEY if is_buff(sid) else AILMENT_KEY)


func duration_of(sid: StringName) -> int:
	return int(row(sid).get("default_duration", UNTIL_CURED))


func is_carried(sid: StringName) -> bool:
	return carried.has(sid)


## "Lasts about 3 of their turns, then wears off." / "Lasts until it is cured."
func lasts(sid: StringName) -> String:
	var turns := duration_of(sid)
	if lasts_keys.has(String(sid)):
		return _tr(str(lasts_keys[String(sid)])).format({"turns": turns})
	if turns > 0:
		return _tr(LASTS_TURNS_KEY).format({"turns": turns})
	return _tr(LASTS_CURED_KEY)


## "Stays after the battle until it is cured." / "Ends when the battle ends."
func after_battle(sid: StringName) -> String:
	return _tr(CARRIED_KEY if is_carried(sid) else ENDS_BATTLE_KEY)


## The consumables that cure `sid`, in items.json order: [{id, name, field}].
func cure_items(sid: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for it in item_rows:
		var battle := it.get("battle", {}) as Dictionary
		for e: Variant in battle.get("effects", []):
			var ed := e as Dictionary
			if str(ed.get("type", "")) == EFFECT_CURE and _ids(ed.get("statuses", [])).has(sid):
				var iid := StringName(str(it.get("id", "")))
				out.append({"id": iid, "name": _tr(str(it.get("name_key", ""))), "field": bool(it.get("field", false))})
				break
	return out


## The party skills (heroes, the Lattice, bound Vowbound) that lift `sid`: [{id, name, by}], once each.
func cure_abilities(sid: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var seen := {}
	for src in sources:
		var skill := StringName(str(src["skill"]))
		if seen.has(skill):
			continue
		var flag := str(src.get("flag", ""))
		if flag != "" and not bool(_is_set.call(StringName(flag))):
			continue
		var sk := skills.get(skill, {}) as Dictionary
		if not _ids(sk.get("cleanses", [])).has(sid):
			continue
		seen[skill] = true
		out.append({"id": skill, "name": _tr(str(sk.get("name_key", ""))), "by": _tr(str(src.get("by_key", "")))})
	return out


func cured_by_shrine(sid: StringName) -> bool:
	return shrine_cures.has(sid)


## The status's one-off way out (status_help.json notes), or "".
func note(sid: StringName) -> String:
	return _tr(str(notes.get(String(sid), "")))


## How it ends, a line each: its time, the battle's end, items, abilities, a shrine, its own way.
func removal_lines(sid: StringName) -> PackedStringArray:
	var out := PackedStringArray([lasts(sid), after_battle(sid)])
	var join := _tr(JOIN_KEY)
	var names := PackedStringArray()
	for it in cure_items(sid):
		var n := str(it["name"])
		names.append(n if bool(it["field"]) else _tr(BATTLE_ONLY_KEY).format({"item": n}))
	if not names.is_empty():
		out.append(_tr(ITEMS_KEY).format({"items": join.join(names)}))
	names = PackedStringArray()
	for ab in cure_abilities(sid):
		var by := str(ab["by"])
		names.append(_tr(BY_KEY).format({"skill": ab["name"], "by": by}) if by != "" else str(ab["name"]))
	if not names.is_empty():
		out.append(_tr(ABILITIES_KEY).format({"abilities": join.join(names)}))
	if cured_by_shrine(sid):
		out.append(_tr(SHRINE_KEY))
	var n := note(sid)
	if n != "":
		out.append(n)
	elif not is_buff(sid) and duration_of(sid) <= 0 and not is_carried(sid) and out.size() == 2:
		out.append(_tr(NO_CURE_KEY))
	return out


## "Poison: Loses a tenth of their health at the end of each of their turns." (a chip's hover line).
func one_line(sid: StringName) -> String:
	return _tr(ONE_LINE_KEY).format({"name": name_of(sid), "desc": desc_of(sid)})


## The whole page as text: what it does, then how it ends (the Codex entry and the tip card's body).
func body(sid: StringName) -> String:
	var lines := PackedStringArray([desc_of(sid)])
	lines.append_array(removal_lines(sid))
	return "\n".join(lines)


## `present` first (in their own order, known ones only), then every other status in data order.
func ordered(present: Array[StringName] = []) -> Array[StringName]:
	var out: Array[StringName] = []
	for sid in present:
		if has(sid) and not out.has(sid):
			out.append(sid)
	for sid in ids():
		if not out.has(sid):
			out.append(sid)
	return out


static func _json(path: String) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("StatusHelpModel: could not read %s" % path)
		return {}
	return parsed as Dictionary


static func _ids(list: Variant) -> Array[StringName]:
	var out: Array[StringName] = []
	if list is Array:
		for v: Variant in list:
			out.append(StringName(str(v)))
	return out


static func _tr(key: String) -> String:
	return TranslationServer.translate(key) if key != "" else ""

class_name FormationMenuModel
extends RefCounted
## The words and rules of the party formation page (M2-MNU-07, SPEC §6.1 and §6.11), Node-free,
## over a PartySheet. The view is FormationMenu. Loc keys: game/data/loc/menus_formation.csv, plus
## the hero names and HUD_HP_FMT / MENUS_MP_FMT.
##
## The formation is the save's own line: GameStateData.party_ids (the active line, in order, at most
## BattleEngine.MAX_ACTIVE) and reserve_ids. Every move writes both at once, and the next live
## battle starts from them (BattleRequest.make, ZoneStory's battles). A spot is a line (LINE_ACTIVE
## or LINE_RESERVE) and an index; past the last hero of a line is an open place (the active line
## shows MAX_ACTIVE places, the reserve one more than it holds), so a hero can step back or come in
## without a partner.
##
## Rules (pillar 4: refused in words, never silently):
##   - nothing changes until the party has gathered (party_ids empty: the field menus then show the
##     first playable's stand-in, which is not the player's own line);
##   - the active line never drops below `min_active` (formation_menu.json rules);
##   - a move that would leave nobody standing in the active line, while someone could stand there,
##     is refused (a battle whose whole active line has fallen is lost before it begins);
##   - a fallen hero may stand in the active line: the plan says so in words (warning).

const LINE_ACTIVE := &"active"
const LINE_RESERVE := &"reserve"
const DATA_PATH := "res://game/data/ui/formation_menu.json"
const DATA_SECTION := "formation_menu"
## The least the active line may hold when formation_menu.json says nothing (a battle needs one).
const DEFAULT_MIN_ACTIVE := 1

const ERR_NONE := &""
const ERR_NOT_GATHERED := &"not_gathered"
const ERR_OPEN_PLACE := &"open_place"
const ERR_TOO_FEW := &"too_few"
const ERR_NONE_STANDING := &"none_standing"
const ERR_KEYS := {
	ERR_NOT_GATHERED: "FORMATION_MENU_ERR_NOT_GATHERED",
	ERR_OPEN_PLACE: "FORMATION_MENU_ERR_OPEN_PLACE",
	ERR_TOO_FEW: "FORMATION_MENU_ERR_TOO_FEW_FMT",
	ERR_NONE_STANDING: "FORMATION_MENU_ERR_NONE_STANDING",
}

## What a move does (plan and result words).
const KIND_KEEP := &"keep"
const KIND_SWAP_ACTIVE := &"swap_active"
const KIND_SWAP_RESERVE := &"swap_reserve"
const KIND_SWAP_IN_OUT := &"swap_in_out"
const KIND_TO_ACTIVE := &"to_active"
const KIND_TO_RESERVE := &"to_reserve"
const PLAN_KEYS := {
	KIND_SWAP_ACTIVE: "FORMATION_MENU_PLAN_SWAP_ACTIVE_FMT",
	KIND_SWAP_RESERVE: "FORMATION_MENU_PLAN_SWAP_RESERVE_FMT",
	KIND_SWAP_IN_OUT: "FORMATION_MENU_PLAN_SWAP_IN_OUT_FMT",
	KIND_TO_ACTIVE: "FORMATION_MENU_PLAN_TO_ACTIVE_FMT",
	KIND_TO_RESERVE: "FORMATION_MENU_PLAN_TO_RESERVE_FMT",
}
const DONE_KEYS := {
	KIND_SWAP_ACTIVE: "FORMATION_MENU_DONE_SWAP_ACTIVE_FMT",
	KIND_SWAP_RESERVE: "FORMATION_MENU_DONE_SWAP_RESERVE_FMT",
	KIND_SWAP_IN_OUT: "FORMATION_MENU_DONE_SWAP_IN_OUT_FMT",
	KIND_TO_ACTIVE: "FORMATION_MENU_DONE_TO_ACTIVE_FMT",
	KIND_TO_RESERVE: "FORMATION_MENU_DONE_TO_RESERVE_FMT",
}
const OPEN_KEY := "FORMATION_MENU_OPEN"
const FALLEN_TAG_KEY := "FORMATION_MENU_FALLEN_TAG_FMT"
const ACTIVE_TITLE_KEY := "FORMATION_MENU_ACTIVE_TITLE_FMT"
const RESERVE_TITLE_KEY := "FORMATION_MENU_RESERVE_TITLE_FMT"
const PLACE_ACTIVE_KEY := "FORMATION_MENU_PLACE_ACTIVE_FMT"
const PLACE_RESERVE_KEY := "FORMATION_MENU_PLACE_RESERVE_FMT"
const CHOSEN_KEY := "FORMATION_MENU_CHOSEN_FMT"
const PICK_KEY := "FORMATION_MENU_PLAN_PICK_FMT"
const KEEP_KEY := "FORMATION_MENU_PLAN_KEEP_FMT"
const WARN_ONE_KEY := "FORMATION_MENU_WARN_FALLEN_ONE_FMT"
const WARN_MANY_KEY := "FORMATION_MENU_WARN_FALLEN_MANY_FMT"
const NAMES_JOIN_KEY := "FORMATION_MENU_NAMES_JOIN"
const HP_KEY := "HUD_HP_FMT"
const MP_KEY := "MENUS_MP_FMT"

var sheet: PartySheet
## The active line as it stands (written to state.party_ids on every move).
var active: Array[StringName] = []
## The reserve as it stands (written to state.reserve_ids on every move).
var reserve: Array[StringName] = []
## The least the active line may hold (formation_menu.json rules.min_active).
var min_active := DEFAULT_MIN_ACTIVE


func _init(with_sheet: PartySheet, rules: Dictionary = {}) -> void:
	sheet = with_sheet
	min_active = maxi(int(rules.get("min_active", DEFAULT_MIN_ACTIVE)), DEFAULT_MIN_ACTIVE)
	_read_line()


## formation_menu.json "rules" ({} when unreadable).
static func load_rules() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY:
		return {}
	var block: Variant = (parsed as Dictionary).get(DATA_SECTION, {})
	return (block as Dictionary).get("rules", {}) if typeof(block) == TYPE_DICTIONARY else {}


## The places in the active line (SPEC §6.1: three active fighters; BattleEngine.MAX_ACTIVE).
static func places() -> int:
	return BattleEngine.MAX_ACTIVE


## True once the save holds the player's own line (party_ids filled by the story).
func gathered() -> bool:
	return not sheet.state.party_ids.is_empty()


## The hero at `index` of `line`, or &"" for an open place.
func hero_at(line: StringName, index: int) -> StringName:
	var ids := active if line == LINE_ACTIVE else reserve
	return ids[index] if index >= 0 and index < ids.size() else &""


## How many spots `line` shows: every active place, or each reserve hero and one open place.
func spot_count(line: StringName) -> int:
	return maxi(places(), active.size()) if line == LINE_ACTIVE else reserve.size() + 1


## Where `cid` stands: {line, index}, or {} when they are in neither line.
func spot_of(cid: StringName) -> Dictionary:
	if active.has(cid):
		return {"line": LINE_ACTIVE, "index": active.find(cid)}
	if reserve.has(cid):
		return {"line": LINE_RESERVE, "index": reserve.find(cid)}
	return {}


## MenuPage rows for `line`: name (tagged when fallen), HP in the cost column and MP in the rank
## column; an open place says so. Every row is choosable, so the cursor can rest on a refused one.
func rows(line: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for i in spot_count(line):
		var cid := hero_at(line, i)
		var row := {"id": StringName("%s_%d" % [line, i]), "line": line, "index": i, "hero": cid, "enabled": true}
		if cid == &"":
			row["label"] = _tr(OPEN_KEY)
			row["right"] = ""
		else:
			var v := vitals(cid)
			var hero_name := sheet.hero_name(cid)
			row["label"] = _tr(FALLEN_TAG_KEY).format({"name": hero_name}) if bool(v["fallen"]) else hero_name
			row["mp"] = _tr(HP_KEY).format({"hp": v["hp"], "max": v["max_hp"]})
			row["right"] = _tr(MP_KEY).format({"mp": v["mp"], "max": v["max_mp"]})
			row["right_role"] = &"text_dim"
		out.append(row)
	return out


## The page title of `line` ("Active line · 3 of 3", "Reserve · 1").
func title(line: StringName) -> String:
	if line == LINE_ACTIVE:
		return _tr(ACTIVE_TITLE_KEY).format({"count": active.size(), "max": places()})
	return _tr(RESERVE_TITLE_KEY).format({"count": reserve.size()})


## "Active line, place 2 of 3" / "Reserve, place 1".
func place_text(line: StringName, index: int) -> String:
	if line == LINE_ACTIVE:
		return _tr(PLACE_ACTIVE_KEY).format({"place": index + 1, "max": places()})
	return _tr(PLACE_RESERVE_KEY).format({"place": index + 1})


## {hp, max_hp, mp, max_mp, fallen} of `cid` as the next fight would have them (PartySheet).
func vitals(cid: StringName) -> Dictionary:
	var c := sheet.combatant(cid)
	if c == null:
		return {"hp": 0, "max_hp": 0, "mp": 0, "max_mp": 0, "fallen": false}
	return {"hp": c.hp, "max_hp": c.max_hp, "mp": c.mp, "max_mp": c.max_mp, "fallen": not c.is_alive()}


func is_fallen(cid: StringName) -> bool:
	return cid != &"" and bool(vitals(cid)["fallen"])


## "Moving Asha. Choose where they go." for a picked hero.
func chosen_text(cid: StringName) -> String:
	return _tr(CHOSEN_KEY).format({"name": sheet.hero_name(cid)})


## Why Confirm on (`to_line`, `to_index`) would be refused (ERR_*), or ERR_NONE. With no hero
## picked (`from_line` &"") it is a pick; else a move of the picked hero there.
func error(from_line: StringName, from_index: int, to_line: StringName, to_index: int) -> StringName:
	if not gathered():
		return ERR_NOT_GATHERED
	if from_line == &"":
		return ERR_OPEN_PLACE if hero_at(to_line, to_index) == &"" else ERR_NONE
	if move_kind(from_line, from_index, to_line, to_index) == KIND_KEEP:
		return ERR_NONE
	var lines := _after(from_line, from_index, to_line, to_index)
	var next_active: Array[StringName] = lines[0]
	if next_active.size() < min_active:
		return ERR_TOO_FEW
	if _standing(next_active) == 0 and _standing(active) > 0:
		return ERR_NONE_STANDING
	return ERR_NONE


## What Confirm on (`to_line`, `to_index`) would do: {ok, text, warn, kind}. `text` says what
## happens or why not; `warn` (may be "") names the fallen who would stand in the active line.
## With no hero picked (`from_line` &"") it previews the pick.
func plan(from_line: StringName, from_index: int, to_line: StringName, to_index: int) -> Dictionary:
	var err := error(from_line, from_index, to_line, to_index)
	var moving := hero_at(from_line, from_index) if from_line != &"" else hero_at(to_line, to_index)
	if err != ERR_NONE:
		return {"ok": false, "text": error_text(err, moving), "warn": "", "kind": &""}
	if from_line == &"":
		var warn := _warn([moving] as Array[StringName]) if to_line == LINE_ACTIVE else ""
		var pick := _tr(PICK_KEY).format({"name": sheet.hero_name(moving)})
		return {"ok": true, "text": pick, "warn": warn, "kind": &""}
	var kind := move_kind(from_line, from_index, to_line, to_index)
	if kind == KIND_KEEP:
		return {"ok": true, "text": _tr(KEEP_KEY).format({"name": sheet.hero_name(moving)}), "warn": "", "kind": kind}
	var lines := _after(from_line, from_index, to_line, to_index)
	var words := _move_words(PLAN_KEYS, kind, from_line, from_index, to_line, to_index)
	return {"ok": true, "text": words, "warn": _warn(lines[0]), "kind": kind}


## Moves the hero at (`from_line`, `from_index`) to (`to_line`, `to_index`): a swap with the hero
## there, or into an open place (the end of that line). Writes party_ids and reserve_ids. Returns
## {ok, text, warn, kind}: what happened, or why it was refused (nothing changes then).
func move(from_line: StringName, from_index: int, to_line: StringName, to_index: int) -> Dictionary:
	var err := error(from_line, from_index, to_line, to_index)
	var moving := hero_at(from_line, from_index)
	if err == ERR_NONE and moving == &"":
		err = ERR_OPEN_PLACE
	if err != ERR_NONE:
		return {"ok": false, "text": error_text(err, moving), "warn": "", "kind": &""}
	var kind := move_kind(from_line, from_index, to_line, to_index)
	if kind == KIND_KEEP:
		return {"ok": true, "text": _tr(KEEP_KEY).format({"name": sheet.hero_name(moving)}), "warn": "", "kind": kind}
	var words := _move_words(DONE_KEYS, kind, from_line, from_index, to_line, to_index)
	var lines := _after(from_line, from_index, to_line, to_index)
	active = lines[0]
	reserve = lines[1]
	save()
	return {"ok": true, "text": words, "warn": _warn(active), "kind": kind}


## Writes the line as it stands into the save (party_ids, reserve_ids).
func save() -> void:
	sheet.state.party_ids = active.duplicate()
	sheet.state.reserve_ids = reserve.duplicate()


## What moving (`from`) to (`to`) is: KIND_KEEP (the same spot, or an open place in its own line:
## order within a line changes by swapping), a swap of two heroes, or a step into an open place.
func move_kind(from_line: StringName, from_index: int, to_line: StringName, to_index: int) -> StringName:
	var other := hero_at(to_line, to_index)
	if from_line == to_line and (from_index == to_index or other == &""):
		return KIND_KEEP
	if other != &"":
		if from_line != to_line:
			return KIND_SWAP_IN_OUT
		return KIND_SWAP_ACTIVE if from_line == LINE_ACTIVE else KIND_SWAP_RESERVE
	return KIND_TO_ACTIVE if to_line == LINE_ACTIVE else KIND_TO_RESERVE


## The refusal in words (`cid`: the hero it concerns).
func error_text(err: StringName, cid: StringName) -> String:
	var key := str(ERR_KEYS.get(err, ""))
	return _tr(key).format({"min": min_active, "name": sheet.hero_name(cid) if cid != &"" else ""})


## [active, reserve] after the move (the model unchanged).
func _after(from_line: StringName, from_index: int, to_line: StringName, to_index: int) -> Array:
	var a := active.duplicate()
	var r := reserve.duplicate()
	var moving := hero_at(from_line, from_index)
	var other := hero_at(to_line, to_index)
	if moving == &"" or move_kind(from_line, from_index, to_line, to_index) == KIND_KEEP:
		return [a, r]
	var src: Array[StringName] = a if from_line == LINE_ACTIVE else r
	var dst: Array[StringName] = a if to_line == LINE_ACTIVE else r
	if other != &"":
		src[from_index] = other
		dst[to_index] = moving
	else:
		src.remove_at(from_index)
		dst.append(moving)
	return [a, r]


func _move_words(
	keys: Dictionary, kind: StringName, from_line: StringName, from_index: int, to_line: StringName, to_index: int
) -> String:
	var a := sheet.hero_name(hero_at(from_line, from_index))
	var b_id := hero_at(to_line, to_index)
	var b := sheet.hero_name(b_id) if b_id != &"" else ""
	var coming_in := a if from_line == LINE_RESERVE else b
	var going_out := b if from_line == LINE_RESERVE else a
	return _tr(str(keys[kind])).format({"a": a, "b": b, "name": a, "in": coming_in, "out": going_out})


## The warning for the fallen in `line` ("" when everyone there stands).
func _warn(line: Array[StringName]) -> String:
	var names: Array[String] = []
	for cid in line:
		if is_fallen(cid):
			names.append(sheet.hero_name(cid))
	if names.is_empty():
		return ""
	if names.size() == 1:
		return _tr(WARN_ONE_KEY).format({"name": names[0]})
	return _tr(WARN_MANY_KEY).format({"names": _tr(NAMES_JOIN_KEY).join(PackedStringArray(names))})


func _standing(line: Array[StringName]) -> int:
	var n := 0
	for cid in line:
		if not is_fallen(cid):
			n += 1
	return n


## The save's line, each hero once: the active line first (at most places(); any more go to the
## head of the reserve), then the reserve. Before the party gathers, the sheet's heroes stand in.
func _read_line() -> void:
	active.clear()
	reserve.clear()
	var first: Array[StringName] = sheet.state.party_ids if gathered() else sheet.heroes.slice(0, places())
	var rest: Array[StringName] = sheet.state.reserve_ids if gathered() else sheet.heroes.slice(places())
	for cid in first:
		if active.has(cid):
			continue
		if active.size() < places():
			active.append(cid)
		elif not reserve.has(cid):
			reserve.append(cid)
	for cid in rest:
		if not active.has(cid) and not reserve.has(cid):
			reserve.append(cid)


static func _tr(key: String) -> String:
	return TranslationServer.translate(key) if key != "" else ""

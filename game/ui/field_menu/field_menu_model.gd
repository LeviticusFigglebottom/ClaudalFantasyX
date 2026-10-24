class_name FieldMenuModel
extends RefCounted
## The words and choices of the field menu (M2-UI-04), Node-free: the root rows, the heroes with a
## Swell gauge, and each hero's choosable fill modes (BattleSwellCarry over a GameStateData). The
## view is FieldMenu. Every string is a loc key from game/data/loc/strings.csv.
##
## Heroes: everyone who has joined (PartyGoods.joined_members). The first playable starts its
## party from first_playable.json "field_battle" and never writes Game.state.party_ids, so when no
## one has joined, that party stands in (FirstPlayableConfig; remove the fallback once the flow
## fills party_ids).

const ROW_BESTIARY := &"bestiary"
const ROW_SWELL := &"swell"
const ROW_SETTINGS := &"settings"
const ROW_CLOSE := &"close"
const ROOT_IDS: Array[StringName] = [ROW_BESTIARY, ROW_SWELL, ROW_SETTINGS, ROW_CLOSE]
const ROOT_LABEL_KEYS := {
	ROW_BESTIARY: "FIELD_MENU_BESTIARY",
	ROW_SWELL: "FIELD_MENU_SWELL",
	ROW_SETTINGS: "FIELD_MENU_SETTINGS",
	ROW_CLOSE: "FIELD_MENU_CLOSE",
}
const ROOT_DESC_KEYS := {
	ROW_BESTIARY: "FIELD_MENU_BESTIARY_DESC",
	ROW_SWELL: "FIELD_MENU_SWELL_DESC",
	ROW_SETTINGS: "FIELD_MENU_SETTINGS_DESC",
	ROW_CLOSE: "FIELD_MENU_CLOSE_DESC",
}
const NO_SWELL_KEY := "FIELD_MENU_SWELL_NONE"
const HERO_DESC_KEY := "FIELD_MENU_SWELL_HERO_FMT"
const MODE_DESC_KEY := "FIELD_MENU_SWELL_MODE_FMT"
const MODE_CURRENT_DESC_KEY := "FIELD_MENU_SWELL_MODE_CURRENT_FMT"
const MODE_SET_KEY := "FIELD_MENU_SWELL_SET_FMT"
const MODES_TITLE_KEY := "FIELD_MENU_SWELL_MODES_TITLE_FMT"
const HEROES_TITLE_KEY := "FIELD_MENU_SWELL_HEROES_TITLE"
const IN_USE_KEY := "HUD_SWELL_MODE_IN_USE"

## The save the choices read and write (Game.state for the live menu).
var state: GameStateData
## Heroes in party order, before the no-Swell ones are dropped.
var heroes: Array[StringName] = []
## Hero id -> name loc key (characters.json).
var name_keys: Dictionary = {}


func _init(with_state: GameStateData = null, hero_ids: Array[StringName] = [], hero_name_keys: Dictionary = {}) -> void:
	state = with_state if with_state != null else GameStateData.new()
	heroes = hero_ids
	name_keys = hero_name_keys


## The live menu: Game.state, the joined heroes (or the first playable's party), their names.
static func from_game() -> FieldMenuModel:
	var ids := PartyGoods.joined_members(Game.state)
	if ids.is_empty():
		var cfg := FirstPlayableConfig.section(FirstPlayableConfig.SECTION_FIELD_BATTLE)
		ids = FirstPlayableConfig.ids(cfg.get("active", [])) + FirstPlayableConfig.ids(cfg.get("reserve", []))
	return FieldMenuModel.new(Game.state, ids, name_keys_from(BattleDB.load_default().characters))


## {hero id: name_key} from a characters table (BattleDB.characters).
static func name_keys_from(characters: Dictionary) -> Dictionary:
	var out := {}
	for cid: Variant in characters:
		out[StringName(str(cid))] = str((characters[cid] as Dictionary).get("name_key", ""))
	return out


## MenuPage rows for the root: Bestiary, Swell (off when no hero has a gauge), Settings, Close.
func root_rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for id in ROOT_IDS:
		var on := id != ROW_SWELL or not swell_heroes().is_empty()
		out.append({"id": id, "label": _tr(ROOT_LABEL_KEYS[id]), "enabled": on})
	return out


## What the highlighted root row opens, in words.
func root_desc(id: StringName) -> String:
	if id == ROW_SWELL and swell_heroes().is_empty():
		return _tr(NO_SWELL_KEY)
	return _tr(str(ROOT_DESC_KEYS.get(id, "")))


## The heroes that have a Swell gauge and at least one choosable mode, in party order.
func swell_heroes() -> Array[StringName]:
	var out: Array[StringName] = []
	for cid in heroes:
		if not out.has(cid) and not mode_rows(cid).is_empty():
			out.append(cid)
	return out


## MenuPage rows for the hero list: name, and the mode in use on the right.
func hero_rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for cid in swell_heroes():
		var cur := current_mode_row(cid)
		(
			out
			. append(
				{
					"id": cid,
					"label": hero_name(cid),
					"right": _tr(str(cur.get("name_key", ""))),
					"right_role": &"text_dim",
					"enabled": true,
				}
			)
		)
	return out


func hero_desc(cid: StringName) -> String:
	var cur := current_mode_row(cid)
	return (
		_tr(HERO_DESC_KEY)
		. format(
			{
				"name": hero_name(cid),
				"mode": _tr(str(cur.get("name_key", ""))),
				"desc": _tr(str(cur.get("desc_key", ""))),
			}
		)
	)


## BattleSwellCarry.mode_rows for `cid`: [{id, name_key, desc_key, trigger, current}].
func mode_rows(cid: StringName) -> Array[Dictionary]:
	return BattleSwellCarry.mode_rows(cid, state)


## MenuPage rows for one hero's modes: name, and "In use" on the current one, in the swell color
## as on the battle Swell page (M2-UI-09).
func mode_page_rows(cid: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for m in mode_rows(cid):
		var cur := bool(m["current"])
		(
			out
			. append(
				{
					"id": m["id"],
					"label": _tr(str(m["name_key"])),
					"right": _tr(IN_USE_KEY) if cur else "",
					"right_role": &"swell",
					"enabled": true,
				}
			)
		)
	return out


func mode_desc(cid: StringName, mode: StringName) -> String:
	for m in mode_rows(cid):
		if StringName(str(m["id"])) == mode:
			var key := MODE_CURRENT_DESC_KEY if bool(m["current"]) else MODE_DESC_KEY
			return _tr(key).format({"mode": _tr(str(m["name_key"])), "desc": _tr(str(m["desc_key"]))})
	return ""


func modes_title(cid: StringName) -> String:
	return _tr(MODES_TITLE_KEY).format({"name": hero_name(cid)})


func heroes_title() -> String:
	return _tr(HEROES_TITLE_KEY)


## Saves `mode` for `cid` (BattleSwellCarry.set_mode). Returns the line to show, "" if refused.
func choose_mode(cid: StringName, mode: StringName) -> String:
	if not BattleSwellCarry.set_mode(cid, mode, state):
		return ""
	var cur := current_mode_row(cid)
	return _tr(MODE_SET_KEY).format({"name": hero_name(cid), "mode": _tr(str(cur.get("name_key", "")))})


## The row of `cid`'s mode in use ({} when it has none).
func current_mode_row(cid: StringName) -> Dictionary:
	for m in mode_rows(cid):
		if bool(m["current"]):
			return m
	return {}


func hero_name(cid: StringName) -> String:
	var key := str(name_keys.get(cid, ""))
	return _tr(key) if key != "" else String(cid)


static func _tr(key: String) -> String:
	return TranslationServer.translate(key) if key != "" else ""

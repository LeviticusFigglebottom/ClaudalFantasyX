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
##
## Map (M2-UI-18): `map` is the zone map's MapModel. The live menu builds it from the field when it
## opens (`live_map`); a zone with no map, or no model, turns the row off and says why on it.
##
## Codex (M3-UI-03): after Bestiary, it opens the lore codex (CodexMenu) over `codex`, or the
## game's codex (CodexModel.from_game) when that is null. Shots and tests set a scratch one.
##
## Kite (M3-UI-205): after Map, the Kite's world map (KiteMapMenu over `kite`). The row is not there at
## all until the Kite flies (`kite` null, or its open flag unset): it would name Act III's ship early.

## M2-MNU-01..04 (the Menus track) added the party's pages: Items, Equip, Lattice, Status (each a
## FieldSubmenu in game/ui/menus/), and Quit to the title behind a confirm.
const ROW_ITEMS := &"items"
const ROW_EQUIP := &"equip"
const ROW_LATTICE := &"lattice"
const ROW_STATUS := &"status"
## M2-MNU-07: the party formation page (FormationMenu).
const ROW_FORMATION := &"formation"
const ROW_BESTIARY := &"bestiary"
const ROW_CODEX := &"codex"
const ROW_SWELL := &"swell"
const ROW_MAP := &"map"
const ROW_KITE := &"kite"
const ROW_SETTINGS := &"settings"
const ROW_QUIT := &"quit"
const ROW_CLOSE := &"close"
const ROOT_IDS: Array[StringName] = [
	ROW_ITEMS,
	ROW_EQUIP,
	ROW_LATTICE,
	ROW_STATUS,
	ROW_FORMATION,
	ROW_SWELL,
	ROW_MAP,
	ROW_BESTIARY,
	ROW_CODEX,
	ROW_SETTINGS,
	ROW_QUIT,
	ROW_CLOSE,
]
## Rows that need a hero in the party (off, with NO_HEROES_KEY, when there is none).
const PARTY_ROWS: Array[StringName] = [ROW_EQUIP, ROW_LATTICE, ROW_STATUS, ROW_FORMATION]
const ROOT_LABEL_KEYS := {
	ROW_ITEMS: "FIELD_MENU_ITEMS",
	ROW_EQUIP: "FIELD_MENU_EQUIP",
	ROW_LATTICE: "FIELD_MENU_LATTICE",
	ROW_STATUS: "FIELD_MENU_STATUS",
	ROW_FORMATION: "FIELD_MENU_FORMATION",
	ROW_BESTIARY: "FIELD_MENU_BESTIARY",
	ROW_CODEX: "FIELD_MENU_CODEX",
	ROW_SWELL: "FIELD_MENU_SWELL",
	ROW_MAP: "FIELD_MENU_MAP",
	ROW_KITE: "FIELD_MENU_KITE",
	ROW_SETTINGS: "FIELD_MENU_SETTINGS",
	ROW_QUIT: "FIELD_MENU_QUIT",
	ROW_CLOSE: "FIELD_MENU_CLOSE",
}
const ROOT_DESC_KEYS := {
	ROW_ITEMS: "FIELD_MENU_ITEMS_DESC",
	ROW_EQUIP: "FIELD_MENU_EQUIP_DESC",
	ROW_LATTICE: "FIELD_MENU_LATTICE_DESC",
	ROW_STATUS: "FIELD_MENU_STATUS_DESC",
	ROW_FORMATION: "FIELD_MENU_FORMATION_DESC",
	ROW_BESTIARY: "FIELD_MENU_BESTIARY_DESC",
	ROW_CODEX: "FIELD_MENU_CODEX_DESC",
	ROW_SWELL: "FIELD_MENU_SWELL_DESC",
	ROW_MAP: "FIELD_MENU_MAP_DESC",
	ROW_KITE: "FIELD_MENU_KITE_DESC",
	ROW_SETTINGS: "FIELD_MENU_SETTINGS_DESC",
	ROW_QUIT: "FIELD_MENU_QUIT_DESC",
	ROW_CLOSE: "FIELD_MENU_CLOSE_DESC",
}
const NO_HEROES_KEY := "FIELD_MENU_NO_HEROES"
const LAST_SAVE_HEAD_KEY := "FIELD_MENU_LAST_SAVE_HEAD"
const LAST_SAVE_FMT_KEY := "FIELD_MENU_LAST_SAVE_FMT"
const NOT_SAVED_KEY := "FIELD_MENU_NOT_SAVED"
const SAVE_HINT_KEY := "FIELD_MENU_SAVE_HINT"
## The Quit confirm (FieldMenu Level.QUIT): Stay first, so a stray Confirm never quits.
const QUIT_STAY := &"stay"
const QUIT_GO := &"quit_go"
const QUIT_TITLE_KEY := "FIELD_MENU_QUIT_TITLE"
const QUIT_STAY_KEY := "FIELD_MENU_QUIT_STAY"
const QUIT_GO_KEY := "FIELD_MENU_QUIT_GO"
const QUIT_WARN_KEY := "FIELD_MENU_QUIT_WARN"
const QUIT_STAY_DESC_KEY := "FIELD_MENU_QUIT_STAY_DESC"
const NO_SWELL_KEY := "FIELD_MENU_SWELL_NONE"
const NO_MAP_KEY := "FIELD_MENU_MAP_NONE"
const NO_MAP_TAG_KEY := "FIELD_MENU_MAP_NONE_TAG"
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
## The zone map (null = none yet). FieldMenu fills it from the field when `live_map` is set.
var map: MapModel
var live_map := false
## The lore codex the Codex row opens (null = the game's).
var codex: CodexModel
## The Kite's world map the Kite row opens (null: no row; from_game sets the game's).
var kite: KiteMapModel
## M2-MNU-300: the save system the root's Last saved block reads (null: the block is hidden). from_game
## sets the SaveSystem autoload. There is no save row: saving stays at shrines and chapter autosaves.
var save_system: Node
## Minutes east of UTC for the last save's time (from_game: the system's zone; tests and captures: 0).
var time_bias_min := 0


func _init(with_state: GameStateData = null, hero_ids: Array[StringName] = [], hero_name_keys: Dictionary = {}) -> void:
	state = with_state if with_state != null else GameStateData.new()
	heroes = hero_ids
	name_keys = hero_name_keys


## The live menu: Game.state, the joined heroes (or the first playable's party), their names.
static func from_game() -> FieldMenuModel:
	var m := FieldMenuModel.new(Game.state, field_heroes(), name_keys_from(BattleDB.load_default().characters))
	m.live_map = true
	m.kite = KiteMapModel.from_game()
	m.save_system = (Engine.get_main_loop() as SceneTree).root.get_node_or_null(^"SaveSystem")
	m.time_bias_min = int(Time.get_time_zone_from_system().get("bias", 0))
	return m


## The heroes the field menus show: everyone who joined Game.state, or the first playable's party
## (see the class comment). PartySheet.from_game uses it too.
static func field_heroes() -> Array[StringName]:
	var ids := PartyGoods.joined_members(Game.state)
	if ids.is_empty():
		var cfg := FirstPlayableConfig.section(FirstPlayableConfig.SECTION_FIELD_BATTLE)
		ids = FirstPlayableConfig.ids(cfg.get("active", [])) + FirstPlayableConfig.ids(cfg.get("reserve", []))
	return ids


## {hero id: name_key} from a characters table (BattleDB.characters).
static func name_keys_from(characters: Dictionary) -> Dictionary:
	var out := {}
	for cid: Variant in characters:
		out[StringName(str(cid))] = str((characters[cid] as Dictionary).get("name_key", ""))
	return out


## MenuPage rows for the root (ROOT_IDS): Swell is off when no hero has a gauge, the party
## pages (PARTY_ROWS) when nobody has joined, and Map where the zone has no map ("No map" on the
## row: a row that is off can't be highlighted to read why).
func root_rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for id in root_ids():
		var row := {"id": id, "label": _tr(ROOT_LABEL_KEYS[id]), "enabled": root_enabled(id)}
		if id == ROW_MAP and not has_map():
			row["right"] = _tr(NO_MAP_TAG_KEY)
		out.append(row)
	return out


## True when the zone the party is in has a map.
func has_map() -> bool:
	return map != null and map.has_map()


## The root's row ids: ROOT_IDS, with Kite after Map once the Kite flies (it is kept out of ROOT_IDS so
## every other row keeps its place there).
func root_ids() -> Array[StringName]:
	var out: Array[StringName] = ROOT_IDS.duplicate()
	if has_kite():
		out.insert(out.find(ROW_MAP) + 1, ROW_KITE)
	return out


## True when the Kite flies, so the root lists its row.
func has_kite() -> bool:
	return kite != null and kite.is_open()


func root_enabled(id: StringName) -> bool:
	if id == ROW_MAP:
		return has_map()
	if id == ROW_SWELL:
		return not swell_heroes().is_empty()
	if PARTY_ROWS.has(id):
		return not heroes.is_empty()
	return true


## The current objective in words for the root's Objective block (M2-UI-17), or "" where the zone
## has no map (test rooms, shots): the same line the field's ObjectiveHud shows.
func objective_line() -> String:
	if not has_map():
		return ""
	return map.tracker.line(map.zone_id)


## The newest readable save (the one Continue would load), or null when there is none or no save system.
func last_save() -> SaveSlotInfo:
	if save_system == null:
		return null
	var slot := TitleSaveEntry.continue_slot(save_system)
	if slot < 0:
		return null
	return SaveSlotInfo.from_dict(save_system.call(&"slot_info", slot) as Dictionary)


## The root's Last saved line: the place and the time of the newest save, or "Not saved yet"; "" without a
## save system (the block is hidden).
func last_save_line() -> String:
	if save_system == null:
		return ""
	var info := last_save()
	if info == null:
		return _tr(NOT_SAVED_KEY)
	return _tr(LAST_SAVE_FMT_KEY).format({"place": info.location_name(), "when": info.timestamp_text(time_bias_min)})


## What the highlighted root row opens, in words (or why it is off).
func root_desc(id: StringName) -> String:
	if id == ROW_SWELL and swell_heroes().is_empty():
		return _tr(NO_SWELL_KEY)
	if id == ROW_MAP and not has_map():
		return _tr(NO_MAP_KEY)
	if not root_enabled(id):
		return _tr(NO_HEROES_KEY)
	return _tr(str(ROOT_DESC_KEYS.get(id, "")))


## MenuPage rows for the Quit confirm: Stay, then Quit to the title.
func quit_rows() -> Array[Dictionary]:
	return [
		{"id": QUIT_STAY, "label": _tr(QUIT_STAY_KEY), "enabled": true},
		{"id": QUIT_GO, "label": _tr(QUIT_GO_KEY), "enabled": true},
	]


func quit_title() -> String:
	return _tr(QUIT_TITLE_KEY)


## The line under the confirm: what quitting costs (pillar 4).
func quit_desc(id: StringName) -> String:
	return _tr(QUIT_WARN_KEY) if id == QUIT_GO else _tr(QUIT_STAY_DESC_KEY)


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
	return CharacterNames.display(cid, str(name_keys.get(cid, "")))  # "The Kirru" until named (M3-C09-05)


static func _tr(key: String) -> String:
	return TranslationServer.translate(key) if key != "" else ""

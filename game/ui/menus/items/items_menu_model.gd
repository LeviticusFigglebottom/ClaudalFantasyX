class_name ItemsMenuModel
extends RefCounted
## The words and rules of the field Items page (M2-MNU-03), Node-free, over a PartySheet. The view
## is ItemsMenu. Every string is a loc key (game/data/loc/menus_items.csv, plus the item, category,
## hero and status names that already exist).
##
## The bag: Inventory.ids() re-sorted by `sort` (kind = ItemDB.sort_rank, name, count), one row per
## held item: {id, label (name), mp (its category), right ("×N"), right_role, enabled}. Every row is
## choosable, so the cursor can rest on a key item and the line under the page says why it can't be
## used (pillar 4).
##
## Field use: an item is usable here when its items.json row says "field": true and its battle
## block targets allies (ItemBattleAction.for_item / targets_allies). The effect is the battle
## item's own: ItemBattleAction.resolve_on runs on PartySheet.combatant(cid) (base, Lattice, gear,
## saved vitals), so a Salt Tonic heals the same amount here as in a fight. The result is written
## back with GameStateData.record_vitals, keeping the hero's saved Swell gauge and fill mode and
## only the carried statuses (party_rest.json). An all_allies item applies to every hero it helps.

const SORT_KIND := &"kind"
const SORT_NAME := &"name"
const SORT_COUNT := &"count"
const SORTS: Array[StringName] = [SORT_KIND, SORT_NAME, SORT_COUNT]
const SORT_KEYS := {
	SORT_KIND: "ITEMS_MENU_SORT_KIND",
	SORT_NAME: "ITEMS_MENU_SORT_NAME",
	SORT_COUNT: "ITEMS_MENU_SORT_COUNT",
}
## The page's views (M3-MNU-03): the bag (everything but key items, sortable) and the key items
## (kept, never used: each with its description; items.json says nothing more about where one came
## from or what it opens, so the page invents nothing).
const VIEW_BAG := &"bag"
const VIEW_KEY := &"key"
const VIEWS: Array[StringName] = [VIEW_BAG, VIEW_KEY]
const VIEW_KEYS := {VIEW_BAG: "ITEMS_MENU_VIEW_BAG", VIEW_KEY: "ITEMS_MENU_VIEW_KEY"}
const CATEGORY_KEYS := {
	ItemDB.CATEGORY_CONSUMABLE: "ITEM_CATEGORY_CONSUMABLE",
	ItemDB.CATEGORY_MATERIAL: "ITEM_CATEGORY_MATERIAL",
	ItemDB.CATEGORY_FACET: "ITEM_CATEGORY_FACET",
	ItemDB.CATEGORY_KEY: "ITEM_CATEGORY_KEY",
}

const RESULT_OK := &"ok"
const ERR_NONE_LEFT := &"none_left"
const ERR_KEY := &"key_item"
const ERR_MATERIAL := &"material"
const ERR_FACET := &"facet"
const ERR_BATTLE_ONLY := &"battle_only"
const ERR_UNKNOWN_HERO := &"unknown_hero"
const ERR_FALLEN := &"fallen"
const ERR_NOT_FALLEN := &"not_fallen"
const ERR_PETRIFIED := &"petrified"
const ERR_FULL_HP := &"full_hp"
const ERR_FULL_MP := &"full_mp"
const ERR_NOTHING_TO_CURE := &"nothing_to_cure"
const ERR_WOULD_HURT := &"would_hurt"
const ERR_NO_EFFECT := &"no_effect"
const ERR_NO_ONE := &"no_one"
## ERR_* -> the loc key that says it ({item}, {name} filled in where the line uses them).
const REFUSAL_KEYS := {
	ERR_NONE_LEFT: "ITEMS_MENU_ERR_NONE_LEFT_FMT",
	ERR_KEY: "ITEMS_MENU_ERR_KEY_FMT",
	ERR_MATERIAL: "ITEMS_MENU_ERR_MATERIAL_FMT",
	ERR_FACET: "ITEMS_MENU_ERR_FACET_FMT",
	ERR_BATTLE_ONLY: "ITEMS_MENU_ERR_BATTLE_ONLY_FMT",
	ERR_UNKNOWN_HERO: "ITEMS_MENU_ERR_NO_EFFECT_FMT",
	ERR_FALLEN: "ITEMS_MENU_ERR_FALLEN_FMT",
	ERR_NOT_FALLEN: "ITEMS_MENU_ERR_NOT_FALLEN_FMT",
	ERR_PETRIFIED: "ITEMS_MENU_ERR_PETRIFIED_FMT",
	ERR_FULL_HP: "ITEMS_MENU_ERR_FULL_HP_FMT",
	ERR_FULL_MP: "ITEMS_MENU_ERR_FULL_MP_FMT",
	ERR_NOTHING_TO_CURE: "ITEMS_MENU_ERR_NOTHING_TO_CURE_FMT",
	ERR_WOULD_HURT: "ITEMS_MENU_ERR_WOULD_HURT_FMT",
	ERR_NO_EFFECT: "ITEMS_MENU_ERR_NO_EFFECT_FMT",
	ERR_NO_ONE: "ITEMS_MENU_ERR_NO_ONE_FMT",
}
const COUNT_KEY := "ITEMS_MENU_COUNT_FMT"
const HELD_KEY := "ITEMS_MENU_HELD_FMT"
const SORT_LINE_KEY := "ITEMS_MENU_SORT_FMT"
const USE_HINT_KEY := "ITEMS_MENU_USE_HINT"
const EMPTY_KEY := "ITEMS_MENU_EMPTY"
const PICK_TITLE_KEY := "ITEMS_MENU_PICK_TITLE_FMT"
const PICK_ALL_TITLE_KEY := "ITEMS_MENU_PICK_ALL_TITLE_FMT"
const HP_KEY := "HUD_HP_FMT"
const MP_KEY := "MENUS_MP_FMT"
const PREVIEW_KEY := "ITEMS_MENU_PREVIEW_FMT"
const PREVIEW_HP_KEY := "ITEMS_MENU_PREVIEW_HP_FMT"
const PREVIEW_MP_KEY := "ITEMS_MENU_PREVIEW_MP_FMT"
const PREVIEW_CURE_KEY := "ITEMS_MENU_PREVIEW_CURE_FMT"
const PREVIEW_JOIN_KEY := "ITEMS_MENU_PREVIEW_JOIN"
const LIST_JOIN_KEY := "ITEMS_MENU_LIST_JOIN"
const USED_KEY := "ITEMS_MENU_USED_FMT"
const FALLEN_TAG_KEY := "ITEMS_MENU_FALLEN_TAG"
const KEY_NOTE_KEY := "ITEMS_MENU_KEY_NOTE"
const KEY_EMPTY_KEY := "ITEMS_MENU_KEY_EMPTY"

var sheet: PartySheet
## Statuses that outlast a battle (Game.carried_statuses()): the only ones a field use may save.
var carried: Array[StringName] = []
var sort: StringName = SORT_KIND
var view: StringName = VIEW_BAG


func _init(with_sheet: PartySheet, carried_statuses: Array[StringName] = []) -> void:
	sheet = with_sheet
	carried = carried_statuses.duplicate()


## The live page: the sheet over Game.state with the game's carried statuses.
static func from_sheet(with_sheet: PartySheet) -> ItemsMenuModel:
	return ItemsMenuModel.new(with_sheet, Game.carried_statuses())


func db() -> ItemDB:
	return sheet.item_db


func inventory() -> Inventory:
	return sheet.goods.inventory


# --- the bag --------------------------------------------------------------------------------------


## Held item ids in the current view and sort. The key view lists key items in data order; the bag
## lists the rest in `sort`. Ties keep the listing order (ItemDB.sort_rank).
func item_ids() -> Array[StringName]:
	if view == VIEW_KEY:
		return inventory().ids_in(ItemDB.CATEGORY_KEY)
	var ids: Array[StringName] = []
	for iid in inventory().ids():  # already by kind
		if db().category_of(iid) != ItemDB.CATEGORY_KEY:
			ids.append(iid)
	match sort:
		SORT_NAME:
			ids.sort_custom(_by_name)
		SORT_COUNT:
			ids.sort_custom(_by_count)
	return ids


## Steps the sort through SORTS (wrapping). Returns the new sort.
func next_sort(step: int = 1) -> StringName:
	sort = SORTS[posmod(SORTS.find(sort) + step, SORTS.size())]
	return sort


## Steps the view through VIEWS (wrapping). Returns the new view.
func next_view(step: int = 1) -> StringName:
	view = VIEWS[posmod(VIEWS.find(view) + step, VIEWS.size())]
	return view


func view_label(of_view: StringName) -> String:
	return _tr(str(VIEW_KEYS.get(of_view, "")))


func sort_text() -> String:
	return _tr(SORT_LINE_KEY).format({"sort": _tr(str(SORT_KEYS.get(sort, "")))})


func rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if view == VIEW_KEY:
		for iid in item_ids():
			out.append(
				{"id": iid, "label": item_name(iid), "right": "", "enabled": true, "glyph": MenuGlyph.for_goods(iid)}
			)
		return out
	for iid in item_ids():
		(
			out
			. append(
				{
					"id": iid,
					"label": item_name(iid),
					"mp": category_name(iid),
					"right": count_text(iid),
					"right_role": &"text" if item_error(iid) == RESULT_OK else &"text_dim",
					"enabled": true,
					"glyph": MenuGlyph.for_goods(iid),
				}
			)
		)
	return out


func item_name(iid: StringName) -> String:
	var key := str(db().item(iid).get("name_key", ""))
	return _tr(key) if key != "" else String(iid)


func category_name(iid: StringName) -> String:
	return _tr(str(CATEGORY_KEYS.get(db().category_of(iid), "")))


func count_text(iid: StringName) -> String:
	return _tr(COUNT_KEY).format({"count": inventory().count(iid)})


## "Items · 4 held": the highlighted item's category and how many the bag holds.
func held_text(iid: StringName) -> String:
	return _tr(HELD_KEY).format({"category": category_name(iid), "count": inventory().count(iid)})


func desc(iid: StringName) -> String:
	return _tr(str(db().item(iid).get("desc_key", "")))


func empty_text() -> String:
	return _tr(KEY_EMPTY_KEY if view == VIEW_KEY else EMPTY_KEY)


# --- field use ------------------------------------------------------------------------------------


## The item's battle action when it may be used from the field menu, else null.
func field_action(iid: StringName) -> ItemBattleAction:
	if not bool(db().item(iid).get("field", false)):
		return null
	var act := ItemBattleAction.for_item(db(), iid)
	return act if act != null and act.targets_allies() else null


## Why `iid` can't be used from the bag at all, or RESULT_OK.
func item_error(iid: StringName) -> StringName:
	if inventory().count(iid) <= 0:
		return ERR_NONE_LEFT
	match db().category_of(iid):
		ItemDB.CATEGORY_KEY:
			return ERR_KEY
		ItemDB.CATEGORY_MATERIAL:
			return ERR_MATERIAL
		ItemDB.CATEGORY_FACET:
			return ERR_FACET
	return RESULT_OK if field_action(iid) != null else ERR_BATTLE_ONLY


## {text, ok}: how to use the highlighted item, or why it can't be used here.
## In the key view a key item is not refused but kept: its line says so, in the plain color.
func item_line(iid: StringName) -> Dictionary:
	if view == VIEW_KEY and db().category_of(iid) == ItemDB.CATEGORY_KEY:
		return {"text": _tr(KEY_NOTE_KEY), "ok": true}
	var err := item_error(iid)
	if err != RESULT_OK:
		return {"text": refusal_text(err, iid), "ok": false}
	return {"text": _tr(USE_HINT_KEY), "ok": true}


## True for an item that reaches every ally at once.
func is_all_allies(iid: StringName) -> bool:
	var act := field_action(iid)
	return act != null and act.target == ItemBattleAction.TARGET_ALL_ALLIES


func pick_title(iid: StringName) -> String:
	return _tr(PICK_ALL_TITLE_KEY if is_all_allies(iid) else PICK_TITLE_KEY).format({"item": item_name(iid)})


## The hero picker: each hero with HP and MP as they stand now. A refused hero stays choosable, so
## the preview line can say why; their numbers are dimmed.
func hero_rows(iid: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for cid in sheet.heroes:
		var c := sheet.combatant(cid)
		if c == null:
			continue
		var ok := hero_error(iid, cid) == RESULT_OK
		var hp := _tr(HP_KEY).format({"hp": c.hp, "max": c.max_hp})
		(
			out
			. append(
				{
					"id": cid,
					"label": sheet.hero_name(cid) + (_tr(FALLEN_TAG_KEY) if c.hp <= 0 else ""),
					"mp": hp,
					"right": _tr(MP_KEY).format({"mp": c.mp, "max": c.max_mp}),
					"right_role": &"text" if ok else &"text_dim",
					"enabled": true,
				}
			)
		)
	return out


## {hp, max_hp, mp, max_mp} of `cid` now (zeros for an unknown hero).
func vitals(cid: StringName) -> Dictionary:
	var c := sheet.combatant(cid)
	if c == null:
		return {"hp": 0, "max_hp": 0, "mp": 0, "max_mp": 0}
	return {"hp": c.hp, "max_hp": c.max_hp, "mp": c.mp, "max_mp": c.max_mp}


## Why `iid` would do nothing for (or would harm) `cid`, or RESULT_OK.
func hero_error(iid: StringName, cid: StringName) -> StringName:
	var err := item_error(iid)
	if err != RESULT_OK:
		return err
	var act := field_action(iid)
	var reach := _reach_error(act, sheet.combatant(cid))
	if reach != RESULT_OK:
		return reach
	var trial := _trial(act, cid)
	if int(trial["hp_after"]) < int(trial["hp_before"]):
		return ERR_WOULD_HURT
	if _changed(trial):
		return RESULT_OK
	return _why_nothing(act)


## The heroes a use of `iid` chosen on `cid` reaches: every hero it helps for an all_allies item,
## else `cid` alone when it helps them, else none.
func targets(iid: StringName, cid: StringName) -> Array[StringName]:
	var out: Array[StringName] = []
	if not is_all_allies(iid):
		if hero_error(iid, cid) == RESULT_OK:
			out.append(cid)
		return out
	for h in sheet.heroes:
		if hero_error(iid, h) == RESULT_OK:
			out.append(h)
	return out


## {text, ok}: what using `iid` on `cid` would do ("Rhen: HP 120 → 320"), or why not.
func preview(iid: StringName, cid: StringName) -> Dictionary:
	var reach := targets(iid, cid)
	if reach.is_empty():
		return {"text": _refusal_for(iid, cid), "ok": false}
	var parts: Array[String] = []
	for h in reach:
		parts.append(_change_text(h, _trial(field_action(iid), h)))
	return {"text": _tr(LIST_JOIN_KEY).join(parts), "ok": true}


## Uses one `iid` on `cid` (or on everyone it helps, for an all_allies item): consumes one, writes
## each target's new HP, MP and carried statuses to the saved vitals with their Swell kept. Returns
## {ok, text}: the receipt, or the refusal (nothing used).
func use(iid: StringName, cid: StringName) -> Dictionary:
	var reach := targets(iid, cid)
	if reach.is_empty():
		return {"text": _refusal_for(iid, cid), "ok": false}
	var act := field_action(iid)
	var parts: Array[String] = []
	for h in reach:
		var trial := _trial(act, h)
		_save(trial["combatant"] as BattleCombatant)
		parts.append(_change_text(h, trial))
	act.consume(inventory())
	return {
		"text": _tr(USED_KEY).format({"item": item_name(iid), "effects": _tr(LIST_JOIN_KEY).join(parts)}),
		"ok": true,
	}


## One refusal in words (REFUSAL_KEYS).
func refusal_text(err: StringName, iid: StringName, cid: StringName = &"") -> String:
	var key := str(REFUSAL_KEYS.get(err, ""))
	if key == "":
		return ""
	return _tr(key).format({"item": item_name(iid), "name": sheet.hero_name(cid) if cid != &"" else ""})


# --- internals ------------------------------------------------------------------------------------


func _refusal_for(iid: StringName, cid: StringName) -> String:
	if is_all_allies(iid) and item_error(iid) == RESULT_OK:
		return refusal_text(ERR_NO_ONE, iid)
	return refusal_text(hero_error(iid, cid), iid, cid)


## `act` resolved on a fresh copy of `cid` (nothing saved): {combatant, result, hp_before,
## hp_after, mp_before, mp_after, removed}.
func _trial(act: ItemBattleAction, cid: StringName) -> Dictionary:
	var c := sheet.combatant(cid)
	var hp_before := c.hp
	var mp_before := c.mp
	var result := act.resolve_on(c)
	return {
		"combatant": c,
		"result": result,
		"hp_before": hp_before,
		"hp_after": c.hp,
		"mp_before": mp_before,
		"mp_after": c.mp,
		"removed": result.get("statuses_removed", []),
	}


## Whether `act` reaches `c` at all by life state (ItemBattleAction.can_target), in words.
static func _reach_error(act: ItemBattleAction, c: BattleCombatant) -> StringName:
	if c == null:
		return ERR_UNKNOWN_HERO
	if act.can_target(c):
		return RESULT_OK
	if act.targets_fallen:
		return ERR_NOT_FALLEN
	return ERR_FALLEN if c.hp <= 0 else ERR_PETRIFIED


static func _changed(trial: Dictionary) -> bool:
	return (
		int(trial["hp_after"]) != int(trial["hp_before"])
		or int(trial["mp_after"]) != int(trial["mp_before"])
		or not (trial["removed"] as Array).is_empty()
	)


func _why_nothing(act: ItemBattleAction) -> StringName:
	var kinds: Array[StringName] = []
	for eff in act.effects:
		kinds.append(StringName(str(eff.get("type", ""))))
	if kinds.has(ItemBattleAction.EFFECT_HEAL_HP):
		return ERR_FULL_HP
	if kinds.has(ItemBattleAction.EFFECT_RESTORE_MP):
		return ERR_FULL_MP
	if kinds.has(ItemBattleAction.EFFECT_CURE):
		return ERR_NOTHING_TO_CURE
	return ERR_NO_EFFECT


## "Rhen: HP 120 → 320 · cures Poison".
func _change_text(cid: StringName, trial: Dictionary) -> String:
	var parts: Array[String] = []
	if int(trial["hp_after"]) != int(trial["hp_before"]):
		parts.append(_tr(PREVIEW_HP_KEY).format({"from": trial["hp_before"], "to": trial["hp_after"]}))
	if int(trial["mp_after"]) != int(trial["mp_before"]):
		parts.append(_tr(PREVIEW_MP_KEY).format({"from": trial["mp_before"], "to": trial["mp_after"]}))
	var names: Array[String] = []
	for sid: Variant in trial["removed"]:
		names.append(status_name(StringName(str(sid))))
	if not names.is_empty():
		parts.append(_tr(PREVIEW_CURE_KEY).format({"statuses": _tr(LIST_JOIN_KEY).join(names)}))
	return _tr(PREVIEW_KEY).format({"name": sheet.hero_name(cid), "changes": _tr(PREVIEW_JOIN_KEY).join(parts)})


func status_name(sid: StringName) -> String:
	var key := str((sheet.battle_db.statuses.get(sid, {}) as Dictionary).get("name_key", ""))
	return _tr(key) if key != "" else String(sid)


## Writes `c`'s HP, MP and carried statuses to the save, keeping its saved Swell gauge and mode.
func _save(c: BattleCombatant) -> void:
	var held: Array[StringName] = []
	for sid: Variant in c.statuses:
		held.append(StringName(str(sid)))
	var st := sheet.state
	# The saved mode is written back as it is: with no default given, an unset mode stays unset.
	st.record_vitals(c.id, c.hp, c.max_hp, c.mp, c.max_mp, held, carried, st.swell_of(c.id), st.swell_mode_of(c.id))


func _by_name(a: StringName, b: StringName) -> bool:
	var na := item_name(a).naturalnocasecmp_to(item_name(b))
	return na < 0 if na != 0 else db().sort_rank(a) < db().sort_rank(b)


func _by_count(a: StringName, b: StringName) -> bool:
	var ca := inventory().count(a)
	var cb := inventory().count(b)
	return ca > cb if ca != cb else db().sort_rank(a) < db().sort_rank(b)


static func _tr(key: String) -> String:
	return TranslationServer.translate(key) if key != "" else ""

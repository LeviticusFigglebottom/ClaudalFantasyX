class_name EquipMenuModel
extends RefCounted
## The words and choices of the Equip page (M2-MNU-02, SPEC §6.5), Node-free, over a PartySheet
## (docs/kb/tech/ui.md "Equip and Customize pages"). The view is EquipMenu. Rules stay where they
## are: EquipmentBag (wearing), EquipmentEffects (what gear does), Customize (crafting). Every
## string is a loc key from game/data/loc/menus_equip.csv, or an existing one (STAT_*, item,
## equipment and ability names).
##
## Rows are MenuPage dictionaries carrying what they stand for:
##   hero_rows()            {id: hero}
##   gear_rows(cid)         a slot row per equip slot {kind: KIND_SLOT, slot, uid} and, under it,
##                          one row per ability slot of the worn piece {kind: KIND_ABILITY, slot,
##                          uid, index, ability (&"" when empty)}
##   piece_rows(cid, slot)  the pieces `cid` can wear there (EquipmentBag.pieces_for) {kind:
##                          KIND_PIECE, uid}, then "Take it off" {kind: KIND_REMOVE} when worn
##   recipe_rows(uid, i)    Customize.candidates for that piece {kind: KIND_RECIPE, ability}
## Every row stays choosable, so the cursor can rest on a refused one and the line says why.
##
## Previews never touch the save: they equip (or craft) on a deep copy of the equipment and build
## the hero through a scratch PartySheet that shares the real one's state and Lattice, so the
## numbers are exactly PartySheet.combatant after the change (tests check that).

const KIND_SLOT := &"slot"
const KIND_ABILITY := &"ability"
const KIND_PIECE := &"piece"
const KIND_REMOVE := &"remove"
const KIND_RECIPE := &"recipe"
## "· Customize" under a spare piece with an empty slot (M2-MNU-09): opens RECIPES for it.
const KIND_CUSTOMIZE := &"customize"
const NO_PIECE := EquipmentBag.NO_PIECE
const RESULT_OK := EquipmentBag.RESULT_OK
## Preview rows, in this order: the two maxima, then the eight battle stats.
const STAT_HP := &"hp"
const STAT_MP := &"mp"
const STAT_KEYS := {
	&"hp": "EQUIP_MENU_STAT_HP",
	&"mp": "EQUIP_MENU_STAT_MP",
	&"strength": "STAT_STRENGTH",
	&"magic": "STAT_MAGIC",
	&"defense": "STAT_DEFENSE",
	&"magic_defense": "STAT_MAGIC_DEFENSE",
	&"agility": "STAT_AGILITY",
	&"accuracy": "STAT_ACCURACY",
	&"evasion": "STAT_EVASION",
	&"luck": "STAT_LUCK",
}
const SLOT_KEYS := {ItemDB.SLOT_WEAPON: "EQUIP_MENU_SLOT_WEAPON", ItemDB.SLOT_ARMOR: "EQUIP_MENU_SLOT_ARMOR"}
## EquipmentBag ERR_* -> the line that says it ({name}, {hero}, {slot} filled in).
const EQUIP_REFUSAL_KEYS := {
	EquipmentBag.ERR_UNKNOWN_PIECE: "EQUIP_MENU_ERR_UNKNOWN_PIECE",
	EquipmentBag.ERR_UNKNOWN_EQUIPMENT: "EQUIP_MENU_ERR_UNKNOWN_EQUIPMENT",
	EquipmentBag.ERR_WRONG_CHARACTER: "EQUIP_MENU_ERR_WRONG_CHARACTER_FMT",
	EquipmentBag.ERR_UNKNOWN_SLOT: "EQUIP_MENU_ERR_UNKNOWN_SLOT",
	EquipmentBag.ERR_WRONG_SLOT: "EQUIP_MENU_ERR_UNKNOWN_SLOT",
	EquipmentBag.ERR_SLOT_REQUIRED: "EQUIP_MENU_ERR_SLOT_REQUIRED_FMT",
	EquipmentBag.ERR_EQUIPPED: "EQUIP_MENU_ERR_EQUIPPED_FMT",
}
## Customize ERR_* -> the line that says it ({ability}, {piece}, {items} filled in).
const CRAFT_REFUSAL_KEYS := {
	Customize.ERR_UNKNOWN_PIECE: "EQUIP_MENU_ERR_UNKNOWN_PIECE",
	Customize.ERR_UNKNOWN_ABILITY: "EQUIP_MENU_CRAFT_ERR_UNKNOWN_ABILITY",
	Customize.ERR_NO_RECIPE: "EQUIP_MENU_CRAFT_ERR_NO_RECIPE_FMT",
	Customize.ERR_WRONG_SLOT_KIND: "EQUIP_MENU_CRAFT_ERR_WRONG_SLOT_FMT",
	Customize.ERR_ALREADY_HAS: "EQUIP_MENU_CRAFT_ERR_ALREADY_HAS_FMT",
	Customize.ERR_NO_EMPTY_SLOT: "EQUIP_MENU_CRAFT_ERR_NO_EMPTY_SLOT_FMT",
	Customize.ERR_SLOT_FILLED: "EQUIP_MENU_CRAFT_ERR_SLOT_FILLED_FMT",
	Customize.ERR_MISSING_ITEMS: "EQUIP_MENU_CRAFT_ERR_MISSING_FMT",
}
## How a list of names is joined (as EnemyPage.LIST_SEPARATOR).
const LIST_SEPARATOR := ", "

var sheet: PartySheet
var db: ItemDB
var bag: EquipmentBag
var inventory: Inventory
var customize: Customize
## Builds preview heroes: the real sheet's state and Lattice, a scratch EquipmentEffects.
var _scratch: PartySheet


## Opens over `with_sheet`. Every hero it shows who has no loadout yet gets their starting gear
## (EquipmentBag.grant_starting, idempotent: what loading a save does, PartyGoods.ensure_starting_gear).
func _init(with_sheet: PartySheet) -> void:
	sheet = with_sheet
	db = sheet.item_db
	bag = sheet.goods.equipment
	inventory = sheet.goods.inventory
	customize = Customize.new(db)
	for cid in sheet.heroes:
		bag.grant_starting(cid)
	_scratch = PartySheet.new(GameStateData.new(), [], sheet.battle_db, db)
	_scratch.state = sheet.state
	_scratch.lattice = sheet.lattice


func heroes() -> Array[StringName]:
	return sheet.heroes


func hero_name(cid: StringName) -> String:
	return sheet.hero_name(cid)


func hero_rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for cid in sheet.heroes:
		out.append({"id": cid, "label": hero_name(cid), "right": "", "enabled": true})
	return out


func gear_title(cid: StringName) -> String:
	return _tr("EQUIP_MENU_GEAR_TITLE_FMT").format({"hero": hero_name(cid)})


## Each equip slot with the piece worn there, and under it that piece's ability slots.
func gear_rows(cid: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for slot in db.equip_slots:
		var uid := worn(cid, slot)
		var row := {"id": StringName("slot:%s" % slot), "kind": KIND_SLOT, "slot": slot, "uid": uid}
		row["label"] = slot_name(slot)
		row["right"] = piece_name(uid) if uid != NO_PIECE else _tr("EQUIP_MENU_NOTHING_WORN")
		row["right_role"] = &"text" if uid != NO_PIECE else &"text_disabled"
		row["glyph"] = MenuGlyph.for_goods(bag.base_of(uid)) if uid != NO_PIECE else {}
		row["enabled"] = true
		out.append(row)
		if uid == NO_PIECE:
			continue
		var slots := bag.slots_of(uid)
		for i in slots.size():
			var aid := slots[i]
			(
				out
				. append(
					{
						"id": StringName("ability:%s:%d" % [slot, i]),
						"kind": KIND_ABILITY,
						"slot": slot,
						"uid": uid,
						"index": i,
						"ability": aid,
						"label": _tr("EQUIP_MENU_ABILITY_SLOT_FMT").format({"n": i + 1}),
						"right": ability_name(aid) if aid != &"" else _tr("EQUIP_MENU_EMPTY_SLOT"),
						"right_role": &"text" if aid != &"" else &"text_dim",
						"enabled": true,
					}
				)
			)
	return out


func pieces_title(cid: StringName, slot: StringName) -> String:
	return _tr("EQUIP_MENU_PIECES_TITLE_FMT").format({"hero": hero_name(cid), "slot": slot_name(slot)})


## The pieces `cid` can wear in `slot` (ascending uid), each marked when worn, then "Take it off"
## when something is worn there (refused, in words, for a required slot). Under each spare piece
## with an empty slot, a "· Customize" row (KIND_CUSTOMIZE, uid, index = its first empty slot):
## worn pieces are customized from their ability rows on GEAR (M2-MNU-09).
func piece_rows(cid: StringName, slot: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for uid in bag.pieces_for(cid, slot):
		var wearer := bag.wearer_of(uid)
		var mark := ""
		if wearer == cid:
			mark = _tr("EQUIP_MENU_WORN")
		elif wearer != &"":
			mark = _tr("EQUIP_MENU_WORN_BY_FMT").format({"hero": hero_name(wearer)})
		(
			out
			. append(
				{
					"id": StringName("piece:%d" % uid),
					"kind": KIND_PIECE,
					"uid": uid,
					"label": piece_name(uid),
					"glyph": MenuGlyph.for_goods(bag.base_of(uid)),
					"right": mark,
					"right_role": &"focus_gold" if wearer == cid else &"text_dim",
					"enabled": true,
				}
			)
		)
		if wearer == &"" and bag.first_empty_slot(uid) >= 0:
			out.append(customize_row(uid))
	if worn(cid, slot) != NO_PIECE:
		var ok := bag.unequip_error(cid, slot) == RESULT_OK
		(
			out
			. append(
				{
					"id": &"remove",
					"kind": KIND_REMOVE,
					"uid": NO_PIECE,
					"label": _tr("EQUIP_MENU_TAKE_OFF"),
					"right": "",
					"enabled": true,
					"refused": not ok,
				}
			)
		)
	return out


## The "· Customize" row for piece `uid` (its first empty slot), with how many slots are empty.
func customize_row(uid: int) -> Dictionary:
	return {
		"id": StringName("customize:%d" % uid),
		"kind": KIND_CUSTOMIZE,
		"uid": uid,
		"index": bag.first_empty_slot(uid),
		"label": _tr("EQUIP_MENU_CUSTOMIZE_ROW"),
		"right": _tr("EQUIP_MENU_EMPTY_COUNT_FMT").format({"n": bag.empty_slot_count(uid)}),
		"right_role": &"text_dim",
		"enabled": true,
	}


## What the "· Customize" row does, for the line under the pages.
func customize_desc(uid: int) -> String:
	return _tr("EQUIP_MENU_CUSTOMIZE_ROW_DESC_FMT").format({"piece": piece_name(uid)})


func recipes_title(uid: int) -> String:
	return _tr("EQUIP_MENU_CUSTOMIZE_TITLE_FMT").format({"piece": piece_name(uid)})


## What can be crafted into slot `index` of piece `uid` (Customize.candidates), each with whether
## the party holds the recipe ("Ready") or how many items it is short.
func recipe_rows(uid: int, _index: int = Customize.FIRST_EMPTY) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for aid in customize.candidates(bag, uid):
		var short := 0
		var gap := customize.shortfall(aid, inventory)
		for iid: StringName in gap:
			short += int(gap[iid])
		(
			out
			. append(
				{
					"id": aid,
					"kind": KIND_RECIPE,
					"ability": aid,
					"uid": uid,
					"label": ability_name(aid),
					"right":
					_tr("EQUIP_MENU_READY") if short == 0 else _tr("EQUIP_MENU_SHORT_FMT").format({"n": short}),
					"right_role": &"heal" if short == 0 else &"text_disabled",
					"enabled": true,
				}
			)
		)
	return out


# --- what a row says ---------------------------------------------------------------------------


## The line about a gear row: the worn piece's description, or what the ability does.
func gear_desc(row: Dictionary) -> String:
	match StringName(str(row.get("kind", ""))):
		KIND_SLOT:
			var uid := int(row.get("uid", NO_PIECE))
			if uid == NO_PIECE:
				return _tr("EQUIP_MENU_NOTHING_WORN_DESC_FMT").format({"slot": slot_name(row.get("slot", &""))})
			return piece_desc(uid)
		KIND_ABILITY:
			var aid := StringName(str(row.get("ability", "")))
			if aid == &"":
				return _tr("EQUIP_MENU_EMPTY_SLOT_DESC")
			return ability_desc(aid)
	return ""


## The status line for a gear row: why a filled ability slot can't be crafted over, else "".
func gear_line(row: Dictionary) -> Dictionary:
	if StringName(str(row.get("kind", ""))) != KIND_ABILITY or StringName(str(row.get("ability", ""))) == &"":
		return {}
	return {
		"text": craft_refusal(Customize.ERR_SLOT_FILLED, int(row["uid"]), StringName(str(row["ability"]))), "ok": true
	}


## {text, ok}: what wearing the piece row does, or why it can't be worn or taken off.
func piece_line(cid: StringName, slot: StringName, row: Dictionary) -> Dictionary:
	var uid := int(row.get("uid", NO_PIECE))
	if StringName(str(row.get("kind", ""))) == KIND_REMOVE:
		var err := bag.unequip_error(cid, slot)
		if err != RESULT_OK:
			return {"text": equip_refusal(err, cid, slot, NO_PIECE), "ok": false}
		return {
			"text": _tr("EQUIP_MENU_TAKE_OFF_LINE_FMT").format({"hero": hero_name(cid), "slot": slot_name(slot)}),
			"ok": true
		}
	var err := bag.equip_error(cid, uid)
	if err != RESULT_OK:
		return {"text": equip_refusal(err, cid, slot, uid), "ok": false}
	if bag.wearer_of(uid) == cid:
		return {"text": _tr("EQUIP_MENU_ALREADY_WORN_FMT").format({"hero": hero_name(cid)}), "ok": true}
	return {"text": "", "ok": true}


## {text, ok}: what crafting `aid` into slot `index` of `uid` costs, or why it can't happen.
func recipe_line(uid: int, index: int, aid: StringName) -> Dictionary:
	var err := customize.craft_error(bag, uid, aid, inventory, index)
	if err != Customize.RESULT_OK:
		return {"text": craft_refusal(err, uid, aid), "ok": false}
	return {
		"text": _tr("EQUIP_MENU_CRAFT_LINE_FMT").format({"ability": ability_name(aid), "piece": piece_name(uid)}),
		"ok": true,
	}


## One line per recipe item: how many it takes, how many are held, and the shortfall if any.
func recipe_parts(aid: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var gap := customize.shortfall(aid, inventory)
	for part in customize.cost(aid):
		var iid: StringName = part["item"]
		var short := int(gap.get(iid, 0))
		var args := {"name": item_name(iid), "count": int(part["count"]), "held": inventory.count(iid), "short": short}
		var key := "EQUIP_MENU_RECIPE_PART_FMT" if short == 0 else "EQUIP_MENU_RECIPE_PART_SHORT_FMT"
		out.append({"item": iid, "text": _tr(key).format(args), "short": short})
	return out


# --- acting --------------------------------------------------------------------------------------


## Wears the piece row (or takes the slot off). Returns {ok, text}: the receipt or the refusal.
func choose_piece(cid: StringName, slot: StringName, row: Dictionary) -> Dictionary:
	if StringName(str(row.get("kind", ""))) == KIND_REMOVE:
		var gone := worn(cid, slot)
		var err := bag.unequip(cid, slot)
		if err != RESULT_OK:
			return {"text": equip_refusal(err, cid, slot, NO_PIECE), "ok": false}
		return {
			"text": _tr("EQUIP_MENU_TOOK_OFF_FMT").format({"hero": hero_name(cid), "name": piece_name(gone)}),
			"ok": true
		}
	var uid := int(row.get("uid", NO_PIECE))
	var err := bag.equip(cid, uid)
	if err != RESULT_OK:
		return {"text": equip_refusal(err, cid, slot, uid), "ok": false}
	return {
		"text": _tr("EQUIP_MENU_EQUIPPED_FMT").format({"hero": hero_name(cid), "name": piece_name(uid)}), "ok": true
	}


## Crafts `aid` into slot `index` of `uid`, spending the recipe (Customize.craft). Permanent.
func craft(uid: int, index: int, aid: StringName) -> Dictionary:
	var err := customize.craft(bag, uid, aid, inventory, index)
	if err != Customize.RESULT_OK:
		return {"text": craft_refusal(err, uid, aid), "ok": false}
	return {
		"text": _tr("EQUIP_MENU_CRAFTED_FMT").format({"ability": ability_name(aid), "piece": piece_name(uid)}),
		"ok": true
	}


## The question asked before a craft (it cannot be undone).
func craft_confirm_text(uid: int, aid: StringName) -> String:
	return _tr("EQUIP_MENU_CRAFT_CONFIRM_FMT").format({"ability": ability_name(aid), "piece": piece_name(uid)})


# --- previews ------------------------------------------------------------------------------------


## `cid` as they stand now (PartySheet.combatant).
func current(cid: StringName) -> BattleCombatant:
	return sheet.combatant(cid)


## The preview of wearing piece `uid` in `slot` (NO_PIECE: taking the slot off). Nothing is saved.
## {stats: [{stat, label, now, next, delta}], gained: [ability ids], lost: [ability ids]}.
func preview_piece(cid: StringName, slot: StringName, uid: int) -> Dictionary:
	var copy := EquipmentBag.new(db, bag.data.duplicate(true))
	if uid == NO_PIECE:
		copy.unequip(cid, slot)
	else:
		copy.equip(cid, uid)
	return _preview(cid, copy)


## The preview of crafting `aid` into slot `index` of piece `uid` (only what the hero gains if
## the piece is worn, else no stat change). Nothing is saved or spent.
func preview_craft(cid: StringName, uid: int, index: int, aid: StringName) -> Dictionary:
	var copy := EquipmentBag.new(db, bag.data.duplicate(true))
	copy.set_slot(uid, index if index >= 0 else copy.first_empty_slot(uid), aid)
	var out := _preview(cid, copy)
	if bag.wearer_of(uid) != cid:
		out["gained"] = [aid] as Array[StringName]
	return out


## The stat table with no change (the hero now).
func preview_none(cid: StringName) -> Dictionary:
	return _preview(cid, bag)


func _preview(cid: StringName, copy: EquipmentBag) -> Dictionary:
	var now := sheet.combatant(cid)
	_scratch.effects = EquipmentEffects.new(db, copy)
	var next := _scratch.combatant(cid)
	var stats: Array[Dictionary] = []
	if now != null and next != null:
		for st: StringName in STAT_KEYS:
			var a := stat_of(now, st)
			var b := stat_of(next, st)
			stats.append({"stat": st, "label": _tr(str(STAT_KEYS[st])), "now": a, "next": b, "delta": b - a})
	var before := sheet.effects.abilities_for(cid)
	var after := _scratch.effects.abilities_for(cid)
	return {"stats": stats, "gained": _minus(after, before), "lost": _minus(before, after)}


## A combatant's value for a preview row (HP and MP rows are the maxima).
static func stat_of(c: BattleCombatant, stat: StringName) -> int:
	match stat:
		STAT_HP:
			return c.max_hp
		STAT_MP:
			return c.max_mp
	return int(c.get(stat))


## The signed delta in words ("+3", "−2", "" for none).
func delta_text(delta: int) -> String:
	if delta == 0:
		return ""
	var key := "EQUIP_MENU_DELTA_UP_FMT" if delta > 0 else "EQUIP_MENU_DELTA_DOWN_FMT"
	return _tr(key).format({"n": absi(delta)})


## "Gains: A, B" and "Loses: C" lines for a preview ("" when nothing changes).
func ability_change_text(preview: Dictionary) -> String:
	var lines: Array[String] = []
	var gained: Array = preview.get("gained", [])
	var lost: Array = preview.get("lost", [])
	if not gained.is_empty():
		lines.append(_tr("EQUIP_MENU_GAINS_FMT").format({"list": _names_of(gained)}))
	if not lost.is_empty():
		lines.append(_tr("EQUIP_MENU_LOSES_FMT").format({"list": _names_of(lost)}))
	return "\n".join(lines)


# --- names ---------------------------------------------------------------------------------------


## uid worn by `cid` in `slot`, or NO_PIECE (a stale uid reads as nothing worn).
func worn(cid: StringName, slot: StringName) -> int:
	var uid := bag.equipped(cid, slot)
	return uid if uid != NO_PIECE and bag.has_piece(uid) else NO_PIECE


func slot_name(slot: Variant) -> String:
	var key := str(SLOT_KEYS.get(StringName(str(slot)), ""))
	return _tr(key) if key != "" else str(slot)


func piece_name(uid: int) -> String:
	var base := bag.base_of(uid)
	var key := str(db.equipment_row(base).get("name_key", ""))
	return _tr(key) if key != "" else String(base)


func piece_desc(uid: int) -> String:
	return _tr(str(db.equipment_row(bag.base_of(uid)).get("desc_key", "")))


func ability_name(aid: StringName) -> String:
	var key := str(db.ability(aid).get("name_key", ""))
	return _tr(key) if key != "" else String(aid)


func ability_desc(aid: StringName) -> String:
	return _tr(str(db.ability(aid).get("desc_key", "")))


func item_name(iid: StringName) -> String:
	var key := str(db.item(iid).get("name_key", ""))
	return _tr(key) if key != "" else String(iid)


## One equip refusal in words (EQUIP_REFUSAL_KEYS).
func equip_refusal(err: StringName, cid: StringName, slot: StringName, uid: int) -> String:
	var key := str(EQUIP_REFUSAL_KEYS.get(err, ""))
	if key == "":
		return ""
	var wearer := bag.wearer_of(uid) if uid != NO_PIECE else &""
	var args := {"hero": hero_name(cid), "slot": slot_name(slot), "wearer": hero_name(wearer)}
	args["name"] = piece_name(uid) if uid != NO_PIECE else ""
	return _tr(key).format(args)


## One Customize refusal in words (CRAFT_REFUSAL_KEYS); a shortfall lists what is missing.
func craft_refusal(err: StringName, uid: int, aid: StringName) -> String:
	var key := str(CRAFT_REFUSAL_KEYS.get(err, ""))
	if key == "":
		return ""
	var missing: Array[String] = []
	var gap := customize.shortfall(aid, inventory)
	for iid: StringName in gap:
		missing.append(_tr("EQUIP_MENU_MISSING_PART_FMT").format({"n": int(gap[iid]), "name": item_name(iid)}))
	var args := {"ability": ability_name(aid), "piece": piece_name(uid), "items": LIST_SEPARATOR.join(missing)}
	return _tr(key).format(args)


func _names_of(ids: Array) -> String:
	var names: Array[String] = []
	for aid: Variant in ids:
		names.append(ability_name(StringName(str(aid))))
	return LIST_SEPARATOR.join(names)


## `a` without one copy of each entry of `b` (multisets: two Steady Arms count twice).
static func _minus(a: Array[StringName], b: Array[StringName]) -> Array[StringName]:
	var rest := b.duplicate()
	var out: Array[StringName] = []
	for x in a:
		var i := rest.find(x)
		if i >= 0:
			rest.remove_at(i)
		else:
			out.append(x)
	return out


static func _tr(key: String) -> String:
	return TranslationServer.translate(key) if key != "" else ""

class_name ItemDB
extends RefCounted
## Read-only item, equipment, ability, Customize and shop tables (SPEC §6.5, §6.11), indexed by
## id. Source files live in res://game/data/items/ and are checked by tools/validate_data.py.
## Tests build fixtures with from_tables(). See docs/kb/design/economy.md.

const DATA_DIR := "res://game/data/items"
const TABLES: Array[String] = ["items", "equipment", "abilities", "customize", "shops"]

const CATEGORY_CONSUMABLE := &"consumable"
const CATEGORY_MATERIAL := &"material"
const CATEGORY_FACET := &"facet"
const CATEGORY_KEY := &"key"
const SLOT_WEAPON := &"weapon"
const SLOT_ARMOR := &"armor"

## Item id -> row (items.json "items").
var items: Dictionary = {}
## Item ids in data order (the tiebreak for deterministic inventory listings).
var item_order: Array[StringName] = []
## Equipment id -> row; gear type id -> row; ability id -> row.
var equipment: Dictionary = {}
var equipment_order: Array[StringName] = []
var gear_types: Dictionary = {}
var abilities: Dictionary = {}
## Ability id -> Array of {"item": StringName, "count": int} (customize.json).
var recipes: Dictionary = {}
## Shop id -> row (shops.json "shops").
var shops: Dictionary = {}
## Character id -> {"weapon": equipment id, "armor": equipment id}.
var starting: Dictionary = {}

var stack_cap: int = 0
var key_item_cap: int = 0
var currency_cap: int = 0
var category_order: Array[StringName] = []
var max_slots: int = 0
var equip_slots: Array[StringName] = []
var required_slots: Array[StringName] = []
var sell_ratio_num: int = 0
var sell_ratio_den: int = 1
var min_sell_price: int = 0

## One line per table that was missing or failed to parse when the DB was loaded (load_dir).
## Such a table is read as empty, so the DB cannot describe what a save holds: see
## integrity_problem (M1-ARC-12).
var load_errors: Array[String] = []


static func load_default() -> ItemDB:
	return load_dir(DATA_DIR)


## Loads every table in TABLES from `dir`. A missing or unparseable table is read as empty, with a
## push_error and a line in load_errors. Tests point it at a folder with a broken table.
static func load_dir(dir: String) -> ItemDB:
	var raw: Dictionary = {}
	var errors: Array[String] = []
	for table in TABLES:
		var path := "%s/%s.json" % [dir, table]
		var parsed: Variant = null
		if FileAccess.file_exists(path):
			parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
		if typeof(parsed) != TYPE_DICTIONARY:
			errors.append("%s is missing or could not be parsed" % path)
			push_error("ItemDB: could not parse %s" % path)
			parsed = {}
		raw[table] = parsed
	var db := from_tables(raw)
	db.load_errors = errors
	return db


## Why this DB must not be used to judge saved equipment ("" when it can be): a table was missing
## or failed to parse (load_errors), or the equipment table has no equipment, gear types or equip
## slots. Every owned piece would then read as unknown, so SaveSystem neither repairs a loadout
## nor writes a save while this is non-empty (M1-ARC-12, QA review-sweep-H S1).
func integrity_problem() -> String:
	if not load_errors.is_empty():
		return "; ".join(load_errors)
	if equipment.is_empty() or gear_types.is_empty() or equip_slots.is_empty():
		return "the equipment table has no equipment, gear types or equip slots"
	return ""


## Builds a DB from {"items": items.json doc, "equipment": ..., "abilities": ..., "customize": ...,
## "shops": ...}. Missing tables are treated as empty.
static func from_tables(raw: Dictionary) -> ItemDB:
	var db := ItemDB.new()
	var it: Dictionary = raw.get("items", {})
	var rules: Dictionary = it.get("rules", {})
	db.stack_cap = int(rules.get("stack_cap", 0))
	db.key_item_cap = int(rules.get("key_item_cap", 0))
	db.currency_cap = int(rules.get("currency_cap", 0))
	db.category_order = _names(rules.get("category_order", []))
	for row: Variant in it.get("items", []):
		var d: Dictionary = row
		var iid := StringName(str(d["id"]))
		db.items[iid] = d
		db.item_order.append(iid)
	var eq: Dictionary = raw.get("equipment", {})
	var eq_rules: Dictionary = eq.get("rules", {})
	db.max_slots = int(eq_rules.get("max_slots", 0))
	db.equip_slots = _names(eq_rules.get("equip_slots", []))
	db.required_slots = _names(eq_rules.get("required_slots", []))
	db.gear_types = _index(eq.get("gear_types", []))
	for row: Variant in eq.get("equipment", []):
		var e: Dictionary = row
		var eid := StringName(str(e["id"]))
		db.equipment[eid] = e
		db.equipment_order.append(eid)
	var start: Dictionary = eq.get("starting", {})
	for cid: Variant in start:
		db.starting[StringName(str(cid))] = start[cid]
	db.abilities = _index((raw.get("abilities", {}) as Dictionary).get("abilities", []))
	for row: Variant in (raw.get("customize", {}) as Dictionary).get("recipes", []):
		var r: Dictionary = row
		var cost: Array[Dictionary] = []
		for part: Variant in r.get("items", []):
			var p: Dictionary = part
			cost.append({"item": StringName(str(p["item"])), "count": int(p["count"])})
		db.recipes[StringName(str(r["ability"]))] = cost
	var sh: Dictionary = raw.get("shops", {})
	var sh_rules: Dictionary = sh.get("rules", {})
	db.sell_ratio_num = int(sh_rules.get("sell_ratio_num", 0))
	db.sell_ratio_den = maxi(int(sh_rules.get("sell_ratio_den", 1)), 1)
	db.min_sell_price = int(sh_rules.get("min_sell_price", 0))
	db.shops = _index(sh.get("shops", []))
	return db


func item(item_id: StringName) -> Dictionary:
	return items.get(item_id, {})


func has_item(item_id: StringName) -> bool:
	return items.has(item_id)


func category_of(item_id: StringName) -> StringName:
	return StringName(str(item(item_id).get("category", "")))


func is_key_item(item_id: StringName) -> bool:
	return category_of(item_id) == CATEGORY_KEY


## Most of this item a party can carry: key items cap at key_item_cap, other items at their own
## "stack_cap" or the global stack_cap. 0 for an unknown id.
func cap_of(item_id: StringName) -> int:
	if not has_item(item_id):
		return 0
	if is_key_item(item_id):
		return key_item_cap
	return int(item(item_id).get("stack_cap", stack_cap))


## Buy price of an item or equipment piece; 0 if it has none (key items, unknown ids).
func price_of(goods_id: StringName) -> int:
	if items.has(goods_id):
		return int(item(goods_id).get("price", 0))
	return int((equipment.get(goods_id, {}) as Dictionary).get("price", 0))


## What a shop pays for one: floor(price × sell_ratio_num / sell_ratio_den), at least
## min_sell_price. 0 for anything that can't be sold (key items, unpriced, unknown).
func sell_price_of(goods_id: StringName) -> int:
	var price := price_of(goods_id)
	if price <= 0 or is_key_item(goods_id):
		return 0
	return maxi(price * sell_ratio_num / sell_ratio_den, min_sell_price)


func is_equipment(goods_id: StringName) -> bool:
	return equipment.has(goods_id)


func equipment_row(equip_id: StringName) -> Dictionary:
	return equipment.get(equip_id, {})


## The equip slot (&"weapon"/&"armor") of an equipment piece, via its gear type.
func slot_of(equip_id: StringName) -> StringName:
	var gt: Dictionary = gear_types.get(StringName(str(equipment_row(equip_id).get("type", ""))), {})
	return StringName(str(gt.get("slot", "")))


## The one character who can wear this piece, via its gear type.
func character_of(equip_id: StringName) -> StringName:
	var gt: Dictionary = gear_types.get(StringName(str(equipment_row(equip_id).get("type", ""))), {})
	return StringName(str(gt.get("character", "")))


func ability(ability_id: StringName) -> Dictionary:
	return abilities.get(ability_id, {})


func ability_category(ability_id: StringName) -> StringName:
	return StringName(str(ability(ability_id).get("category", "")))


## True if the ability may sit in a piece worn in `slot` (abilities.json "equip").
func ability_fits(ability_id: StringName, slot: StringName) -> bool:
	return _names(ability(ability_id).get("equip", [])).has(slot)


## Customize cost for an ability: [{"item", "count"}], or [] if it can't be crafted.
func recipe(ability_id: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	out.assign(recipes.get(ability_id, []))
	return out


## Sort rank of an item for listings: category position, then data order.
func sort_rank(item_id: StringName) -> Vector2i:
	var cat := category_order.find(category_of(item_id))
	if cat < 0:
		cat = category_order.size()
	return Vector2i(cat, item_order.find(item_id))


static func _index(rows: Array) -> Dictionary:
	var out: Dictionary = {}
	for row: Variant in rows:
		var d: Dictionary = row
		out[StringName(str(d["id"]))] = d
	return out


static func _names(list: Variant) -> Array[StringName]:
	var out: Array[StringName] = []
	if list is Array:
		for v: Variant in list:
			out.append(StringName(str(v)))
	return out

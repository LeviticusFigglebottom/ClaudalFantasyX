class_name EquipmentBag
extends RefCounted
## Owned equipment pieces and each character's loadout (SPEC §6.5). Every piece is an instance
## with its own ability slots, because Customize changes one piece and not its whole kind.
## Wraps GameStateData.equipment in place:
##   {"next_uid": int, "owned": {"<uid>": {"base": equipment id, "abilities": [id or ""]}},
##    "loadout": {"<character>": {"weapon": uid, "armor": uid}}}
## uids start at 1 and are never reused, so saves and listings stay deterministic.

const RESULT_OK := &"ok"
const ERR_UNKNOWN_PIECE := &"unknown_piece"
const ERR_UNKNOWN_EQUIPMENT := &"unknown_equipment"
const ERR_WRONG_CHARACTER := &"wrong_character"
const ERR_UNKNOWN_SLOT := &"unknown_slot"
const ERR_SLOT_REQUIRED := &"slot_required"
const ERR_EQUIPPED := &"piece_equipped"
const NO_PIECE := 0
const FIRST_UID := 1

var data: Dictionary
var db: ItemDB


func _init(item_db: ItemDB, backing: Dictionary = {}) -> void:
	db = item_db
	data = backing
	if not data.has("next_uid"):
		data["next_uid"] = FIRST_UID
	if not data.has("owned"):
		data["owned"] = {}
	if not data.has("loadout"):
		data["loadout"] = {}


## Creates a new piece of `equip_id` with its data-defined slots and pre-filled abilities.
## Returns its uid, or NO_PIECE for an unknown id.
func add_piece(equip_id: StringName) -> int:
	if not db.is_equipment(equip_id):
		push_error("EquipmentBag: unknown equipment '%s'" % equip_id)
		return NO_PIECE
	var row := db.equipment_row(equip_id)
	var slots: Array[String] = []
	var prefilled: Array = row.get("abilities", [])
	for i in int(row.get("slots", 0)):
		slots.append(str(prefilled[i]) if i < prefilled.size() else "")
	var uid := int(data["next_uid"])
	data["next_uid"] = uid + 1
	_owned()[str(uid)] = {"base": String(equip_id), "abilities": slots}
	return uid


## Removes an unequipped piece (selling, discarding). Returns RESULT_OK or an ERR_*.
func remove_piece(uid: int) -> StringName:
	if not has_piece(uid):
		return ERR_UNKNOWN_PIECE
	if wearer_of(uid) != &"":
		return ERR_EQUIPPED
	_owned().erase(str(uid))
	return RESULT_OK


func has_piece(uid: int) -> bool:
	return _owned().has(str(uid))


func base_of(uid: int) -> StringName:
	return StringName(str(_piece(uid).get("base", "")))


## The piece's slots in order; &"" marks an empty slot.
func slots_of(uid: int) -> Array[StringName]:
	var out: Array[StringName] = []
	for a: Variant in _piece(uid).get("abilities", []):
		out.append(StringName(str(a)))
	return out


## Filled abilities in slot order.
func abilities_of(uid: int) -> Array[StringName]:
	var out: Array[StringName] = []
	for a in slots_of(uid):
		if a != &"":
			out.append(a)
	return out


## Index of the first empty slot, or -1 if the piece is full (or unknown).
func first_empty_slot(uid: int) -> int:
	return slots_of(uid).find(&"")


func empty_slot_count(uid: int) -> int:
	return slots_of(uid).count(&"")


## Writes an ability into a slot. Customize validates first; this only checks the index.
func set_slot(uid: int, index: int, ability_id: StringName) -> bool:
	var slots: Array = _piece(uid).get("abilities", [])
	if index < 0 or index >= slots.size():
		return false
	slots[index] = String(ability_id)
	return true


## Every owned uid, ascending.
func uids() -> Array[int]:
	var out: Array[int] = []
	for k: Variant in _owned():
		out.append(int(str(k)))
	out.sort()
	return out


## Owned pieces `cid` could wear in `slot`, ascending uid.
func pieces_for(cid: StringName, slot: StringName) -> Array[int]:
	var out: Array[int] = []
	for uid in uids():
		var base := base_of(uid)
		if db.character_of(base) == cid and db.slot_of(base) == slot:
			out.append(uid)
	return out


## uid worn by `cid` in `slot`, or NO_PIECE.
func equipped(cid: StringName, slot: StringName) -> int:
	var lo: Dictionary = _loadout().get(String(cid), {})
	return int(lo.get(String(slot), NO_PIECE))


## Pieces `cid` wears, in the equip_slots order from equipment.json (weapon, then armor).
func equipped_uids(cid: StringName) -> Array[int]:
	var out: Array[int] = []
	for slot in db.equip_slots:
		var uid := equipped(cid, slot)
		if uid != NO_PIECE and has_piece(uid):
			out.append(uid)
	return out


## The character wearing this piece, or &"".
func wearer_of(uid: int) -> StringName:
	for cid: Variant in _loadout():
		var lo: Dictionary = _loadout()[cid]
		for slot: Variant in lo:
			if int(lo[slot]) == uid:
				return StringName(str(cid))
	return &""


func equip_error(cid: StringName, uid: int) -> StringName:
	if not has_piece(uid):
		return ERR_UNKNOWN_PIECE
	if db.character_of(base_of(uid)) != cid:
		return ERR_WRONG_CHARACTER
	if not db.equip_slots.has(db.slot_of(base_of(uid))):
		return ERR_UNKNOWN_SLOT
	return RESULT_OK


## Puts the piece in its slot for `cid`, replacing whatever was there.
func equip(cid: StringName, uid: int) -> StringName:
	var err := equip_error(cid, uid)
	if err != RESULT_OK:
		return err
	var key := String(cid)
	if not _loadout().has(key):
		_loadout()[key] = {}
	(_loadout()[key] as Dictionary)[String(db.slot_of(base_of(uid)))] = uid
	return RESULT_OK


func unequip_error(_cid: StringName, slot: StringName) -> StringName:
	if not db.equip_slots.has(slot):
		return ERR_UNKNOWN_SLOT
	if db.required_slots.has(slot):
		return ERR_SLOT_REQUIRED
	return RESULT_OK


## Empties a slot. Required slots (the weapon) can only be swapped, never emptied.
func unequip(cid: StringName, slot: StringName) -> StringName:
	var err := unequip_error(cid, slot)
	if err != RESULT_OK:
		return err
	var lo: Dictionary = _loadout().get(String(cid), {})
	lo.erase(String(slot))
	return RESULT_OK


## Gives a joining hero their starting gear (equipment.json "starting") and equips it, once.
## Returns false if they already have a loadout or the data has none for them.
func grant_starting(cid: StringName) -> bool:
	if _loadout().has(String(cid)) or not db.starting.has(cid):
		return false
	_loadout()[String(cid)] = {}
	var start: Dictionary = db.starting[cid]
	for slot in db.equip_slots:
		if start.has(String(slot)):
			var uid := add_piece(StringName(str(start[String(slot)])))
			if uid != NO_PIECE:
				equip(cid, uid)
	return true


func _owned() -> Dictionary:
	return data["owned"]


func _loadout() -> Dictionary:
	return data["loadout"]


func _piece(uid: int) -> Dictionary:
	return _owned().get(str(uid), {})

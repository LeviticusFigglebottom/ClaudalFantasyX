class_name StatusMenuModel
extends RefCounted
## The words and numbers of the party Status page (M2-MNU-03), Node-free, over a PartySheet. The
## view is StatusMenu. Loc keys: game/data/loc/menus_items.csv, plus the stat, hero, status, gear,
## ability, skill and Swell mode names that already exist.
##
## Every number is the one the next battle would use (PartySheet.combatant). Each stat is split so
## growth is visible (pillar 5): base (characters.json) + Lattice (LatticeProgress.apply_to) + gear
## (EquipmentEffects.apply_to), built the same way the sheet builds a hero, so the three parts
## always add up to the total.

## Battle stats in display order, with their names (strings.csv STAT_*).
const STATS: Array[StringName] = [
	&"strength", &"magic", &"defense", &"magic_defense", &"agility", &"accuracy", &"evasion", &"luck"
]
const STAT_KEYS := {
	&"max_hp": "STATUS_MENU_MAX_HP",
	&"max_mp": "STATUS_MENU_MAX_MP",
	&"strength": "STAT_STRENGTH",
	&"magic": "STAT_MAGIC",
	&"defense": "STAT_DEFENSE",
	&"magic_defense": "STAT_MAGIC_DEFENSE",
	&"agility": "STAT_AGILITY",
	&"accuracy": "STAT_ACCURACY",
	&"evasion": "STAT_EVASION",
	&"luck": "STAT_LUCK",
}
## Max HP and Max MP head the table: they grow on the Lattice and with gear too.
const VITAL_STATS: Array[StringName] = [&"max_hp", &"max_mp"]
const HP_KEY := "HUD_HP_FMT"
const MP_KEY := "MENUS_MP_FMT"
const LEVEL_KEY := "STATUS_MENU_LEVEL_FMT"
const FALLEN_KEY := "STATUS_MENU_FALLEN"
const SWELL_FMT_KEY := "STATUS_MENU_SWELL_FMT"
const NO_SWELL_KEY := "STATUS_MENU_NO_SWELL"
const NONE_KEY := "STATUS_MENU_NONE"
## A status's description key is its name_key with this suffix (menus.csv).
const DESC_SUFFIX := "_DESC"
const EMPTY_SLOT_KEY := "STATUS_MENU_EMPTY_SLOT"
const NO_ABILITIES_KEY := "STATUS_MENU_NO_ABILITIES"
const MOVEMENT_KEY := "STATUS_MENU_MOVEMENT_FMT"
const WOKEN_KEY := "STATUS_MENU_WOKEN_FMT"
const SKILLS_KEY := "STATUS_MENU_SKILLS_FMT"
const NO_LATTICE_KEY := "STATUS_MENU_NO_LATTICE"
const PLUS_KEY := "STATUS_MENU_PLUS_FMT"
const ZERO_KEY := "STATUS_MENU_ZERO"
const JOIN_KEY := "ITEMS_MENU_LIST_JOIN"
const SLOT_KEYS := {ItemDB.SLOT_WEAPON: "STATUS_MENU_WEAPON", ItemDB.SLOT_ARMOR: "STATUS_MENU_ARMOR"}

var sheet: PartySheet


func _init(with_sheet: PartySheet) -> void:
	sheet = with_sheet


func heroes() -> Array[StringName]:
	return sheet.heroes.duplicate()


## The hero list: name, and HP as it stands (dimmed for a fallen hero).
func hero_rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for cid in sheet.heroes:
		var c := sheet.combatant(cid)
		if c == null:
			continue
		(
			out
			. append(
				{
					"id": cid,
					"label": sheet.hero_name(cid),
					"right": _tr(FALLEN_KEY) if c.hp <= 0 else "",
					"right_role": &"danger",
					"enabled": true,
				}
			)
		)
	return out


## Everything the page shows for `cid` ({} for an unknown hero):
##   name, level_text, hp, max_hp, mp, max_mp, hp_text, mp_text, fallen,
##   stats: [{id, label, total, base, lattice, gear}] (VITAL_STATS then STATS),
##   gear: [{slot, slot_label, name, abilities}], swell: {has, points, max, mode, text},
##   lattice: {on_board, movement, woken, skills, lines: [String]}, statuses: [String].
func page(cid: StringName) -> Dictionary:
	var c := sheet.combatant(cid)
	if c == null:
		return {}
	return {
		"id": cid,
		"name": sheet.hero_name(cid),
		"level_text": _tr(LEVEL_KEY).format({"level": c.level}),
		"hp": c.hp,
		"max_hp": c.max_hp,
		"mp": c.mp,
		"max_mp": c.max_mp,
		"hp_text": _tr(HP_KEY).format({"hp": c.hp, "max": c.max_hp}),
		"mp_text": _tr(MP_KEY).format({"mp": c.mp, "max": c.max_mp}),
		"fallen": c.hp <= 0,
		"stats": stat_rows(cid),
		"gear": gear_rows(cid),
		"swell": swell_of(cid),
		"lattice": lattice_of(cid),
		"statuses": status_names(c),
		"status_descs": status_descs(c),
	}


## Each stat as total = base + Lattice + gear (VITAL_STATS, then STATS).
func stat_rows(cid: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var base := sheet.base_combatant(cid)
	if base == null:
		return out
	var with_lattice := sheet.base_combatant(cid)
	sheet.lattice.apply_to(with_lattice)
	var with_gear := sheet.base_combatant(cid)
	sheet.lattice.apply_to(with_gear)
	sheet.effects.apply_to(with_gear)
	var now := sheet.combatant(cid)
	for stat: StringName in VITAL_STATS + STATS:
		var b := int(base.get(stat))
		var lat := int(with_lattice.get(stat)) - b
		var gear := int(with_gear.get(stat)) - int(with_lattice.get(stat))
		(
			out
			. append(
				{
					"id": stat,
					"label": _tr(str(STAT_KEYS[stat])),
					"total": int(now.get(stat)),
					"base": b,
					"lattice": lat,
					"gear": gear,
				}
			)
		)
	return out


## "+12", "−3" or "—" for a growth column.
func growth_text(amount: int) -> String:
	if amount == 0:
		return _tr(ZERO_KEY)
	return _tr(PLUS_KEY).format({"amount": amount}) if amount > 0 else str(amount)


## Worn pieces in equip_slots order: {slot, slot_label, name, abilities (one line)}.
func gear_rows(cid: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var bag := sheet.goods.equipment
	for slot in sheet.item_db.equip_slots:
		var uid := bag.equipped(cid, slot)
		var row := {"slot": slot, "slot_label": _tr(str(SLOT_KEYS.get(slot, ""))), "name": "", "abilities": ""}
		if uid == EquipmentBag.NO_PIECE or not bag.has_piece(uid):
			row["name"] = _tr(EMPTY_SLOT_KEY)
		else:
			var key := str(sheet.item_db.equipment_row(bag.base_of(uid)).get("name_key", ""))
			row["name"] = _tr(key) if key != "" else String(bag.base_of(uid))
			var names: Array[String] = []
			for aid in bag.abilities_of(uid):
				var ak := str(sheet.item_db.ability(aid).get("name_key", ""))
				names.append(_tr(ak) if ak != "" else String(aid))
			row["abilities"] = _tr(JOIN_KEY).join(names) if not names.is_empty() else _tr(NO_ABILITIES_KEY)
		out.append(row)
	return out


## {has, points, max, mode, text}: the saved gauge and the fill mode in use (BattleSwellCarry).
func swell_of(cid: StringName) -> Dictionary:
	var rows := BattleSwellCarry.mode_rows(cid, sheet.state)
	var points := clampi(sheet.state.swell_of(cid), 0, Formulas.SWELL_MAX)
	if rows.is_empty():
		return {"has": false, "points": 0, "max": Formulas.SWELL_MAX, "mode": &"", "text": _tr(NO_SWELL_KEY)}
	var mode := StringName(str(rows[0].get("id", "")))
	var name_key := str(rows[0].get("name_key", ""))
	for r in rows:
		if bool(r.get("current", false)):
			mode = StringName(str(r.get("id", "")))
			name_key = str(r.get("name_key", ""))
	return {
		"has": true,
		"points": points,
		"max": Formulas.SWELL_MAX,
		"mode": mode,
		"text": _tr(SWELL_FMT_KEY).format({"mode": _tr(name_key), "points": points, "max": Formulas.SWELL_MAX}),
	}


## {on_board, movement, woken, skills, lines}: banked movement points, the stat and ability nodes
## this hero has woken (their start is not counted), and the skills learned on the Lattice.
func lattice_of(cid: StringName) -> Dictionary:
	var t := sheet.lattice.traveler(cid)
	if t == null:
		return {"on_board": false, "movement": 0, "woken": 0, "skills": [], "lines": [_tr(NO_LATTICE_KEY)]}
	var woken := 0
	for nid: StringName in t.activated:
		var n := sheet.lattice.board.lattice_node(nid)
		if n != null and n.is_activatable():
			woken += 1
	var skills: Array[String] = []
	for sid in sheet.lattice.learned_skills(cid):
		var key := str((sheet.battle_db.skills.get(sid, {}) as Dictionary).get("name_key", ""))
		skills.append(_tr(key) if key != "" else String(sid))
	var skill_text := _tr(JOIN_KEY).join(skills) if not skills.is_empty() else _tr(NONE_KEY)
	return {
		"on_board": true,
		"movement": t.movement_points,
		"woken": woken,
		"skills": skills,
		"lines":
		[
			_tr(MOVEMENT_KEY).format({"count": t.movement_points}),
			_tr(WOKEN_KEY).format({"count": woken}),
			_tr(SKILLS_KEY).format({"skills": skill_text}),
		],
	}


## What each carried status does, one line each (the status's name_key + DESC_SUFFIX; the Lead's Act I pass: a
## status the party carries out of a fight was named but never explained). [] when none is carried.
func status_descs(c: BattleCombatant) -> Array[String]:
	var out: Array[String] = []
	for sid: Variant in c.statuses:
		var key := str((sheet.battle_db.statuses.get(StringName(str(sid)), {}) as Dictionary).get("name_key", ""))
		if key != "" and _tr(key + DESC_SUFFIX) != key + DESC_SUFFIX:
			out.append("%s: %s" % [_tr(key), _tr(key + DESC_SUFFIX)])
	return out


## Carried status names (the saved ones a fight will start with); [None] when there are none.
func status_names(c: BattleCombatant) -> Array[String]:
	var out: Array[String] = []
	for sid: Variant in c.statuses:
		var key := str((sheet.battle_db.statuses.get(StringName(str(sid)), {}) as Dictionary).get("name_key", ""))
		out.append(_tr(key) if key != "" else str(sid))
	if out.is_empty():
		out.append(_tr(NONE_KEY))
	return out


static func _tr(key: String) -> String:
	return TranslationServer.translate(key) if key != "" else ""

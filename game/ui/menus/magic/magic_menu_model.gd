class_name MagicMenuModel
extends RefCounted
## The words and steps of the field Magic page (M3-UI-1251; the human's playtest FAST-TRACK 5, 2026-11-03), Node-free,
## over a PartySheet. A hero casts a field-usable spell (Mend and the like) on the party outside battle and pays its
## MP. What a spell does, who it may reach and what it costs are combat-systems' rules (FieldMagicRules, M3-CMB-1252):
## this page only asks them, shows the answer in words, and writes the result to the save as the Items page does
## (GameStateData.record_vitals, keeping each hero's Swell and only the carried statuses). The view is MagicMenu;
## words are loc keys (menus.csv MAGIC_MENU_*, plus the Items page's preview keys and the skill and hero names).
##
## Steps: a caster (every hero; one with no field spell is listed but says so), a spell (its MP cost on the right),
## then a hero (or every hero, for a spell that reaches all allies). A refused choice stays choosable, so the line
## under the page can say why (pillar 4).

const DATA_PATH := "res://game/data/ui/magic_menu.json"
const RESULT_OK := &""
const TARGET_ALL := ["all_allies", "all_other_allies"]
## The refusal ids the rules return (M3-CMB-1252) -> their loc keys ({spell}, {name}, {caster} filled in).
const REFUSAL_KEYS := {
	&"no_mp": "MAGIC_MENU_ERR_NO_MP_FMT",
	&"silenced": "MAGIC_MENU_ERR_SILENCED_FMT",
	&"caster_fallen": "MAGIC_MENU_ERR_CASTER_FALLEN_FMT",
	&"target_fallen": "MAGIC_MENU_ERR_FALLEN_FMT",
	&"not_fallen": "MAGIC_MENU_ERR_NOT_FALLEN_FMT",
	&"full_hp": "MAGIC_MENU_ERR_FULL_HP_FMT",
	&"nothing_to_cure": "MAGIC_MENU_ERR_NOTHING_TO_CURE_FMT",
	&"no_effect": "MAGIC_MENU_ERR_NO_EFFECT_FMT",
	&"no_one": "MAGIC_MENU_ERR_NO_ONE_FMT",
}
const ERR_NO_SPELLS := &"no_spells"
const ERR_NO_ONE := &"no_one"
const GENERIC_REFUSAL_KEY := "MAGIC_MENU_ERR_GENERIC_FMT"
const NO_SPELLS_KEY := "MAGIC_MENU_NO_SPELLS_FMT"
const COST_KEY := "MAGIC_MENU_COST_FMT"
const COUNT_KEY := "MAGIC_MENU_COUNT_FMT"
const COUNT_ONE_KEY := "MAGIC_MENU_COUNT_ONE"
const COUNT_NONE_KEY := "MAGIC_MENU_COUNT_NONE"
const CAST_HINT_KEY := "MAGIC_MENU_CAST_HINT"
const CASTER_HINT_KEY := "MAGIC_MENU_CASTER_HINT"
const PICK_TITLE_KEY := "MAGIC_MENU_PICK_TITLE_FMT"
const PICK_ALL_TITLE_KEY := "MAGIC_MENU_PICK_ALL_TITLE_FMT"
const CAST_KEY := "MAGIC_MENU_CAST_FMT"
const SPENT_KEY := "MAGIC_MENU_SPENT_FMT"
const REVIVED_KEY := "MAGIC_MENU_REVIVED"
const HP_KEY := "HUD_HP_FMT"
const MP_KEY := "MENUS_MP_FMT"
const FALLEN_TAG_KEY := "ITEMS_MENU_FALLEN_TAG"
const PREVIEW_KEY := "ITEMS_MENU_PREVIEW_FMT"
const PREVIEW_HP_KEY := "ITEMS_MENU_PREVIEW_HP_FMT"
const PREVIEW_MP_KEY := "ITEMS_MENU_PREVIEW_MP_FMT"
const PREVIEW_CURE_KEY := "ITEMS_MENU_PREVIEW_CURE_FMT"
const PREVIEW_JOIN_KEY := "ITEMS_MENU_PREVIEW_JOIN"
const LIST_JOIN_KEY := "ITEMS_MENU_LIST_JOIN"

var sheet: PartySheet
var rules: FieldMagicRules
## Statuses that outlast a battle (Game.carried_statuses()): the only ones a cast may save.
var carried: Array[StringName] = []


func _init(with_sheet: PartySheet, with_rules: FieldMagicRules, carried_statuses: Array[StringName] = []) -> void:
	sheet = with_sheet
	rules = with_rules
	carried = carried_statuses.duplicate()


## The live page: the sheet over Game.state, combat-systems' rules (null rules: no page) and the carried statuses.
static func from_sheet(with_sheet: PartySheet) -> MagicMenuModel:
	return MagicMenuModel.new(with_sheet, FieldMagicRules.live(), Game.carried_statuses())


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("MagicMenuModel: could not read %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary).get("magic_menu", {}) as Dictionary


## True when the rules exist (the field menu lists Magic only then).
func available() -> bool:
	return rules != null and rules.is_valid()


# --- casters --------------------------------------------------------------------------------------


## The caster's field-usable spells, in the rules' order.
func spells_of(caster: StringName) -> Array[StringName]:
	var out: Array[StringName] = []
	var c := sheet.combatant(caster)
	if c == null or not available():
		return out
	for sid: Variant in rules.usable.call(c):
		out.append(StringName(str(sid)))
	return out


## Every hero: name (fallen tagged), MP now, and how many field spells they know.
func caster_rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for cid in sheet.heroes:
		var c := sheet.combatant(cid)
		if c == null:
			continue
		var n := spells_of(cid).size()
		(
			out
			. append(
				{
					"id": cid,
					"label": sheet.hero_name(cid) + (_tr(FALLEN_TAG_KEY) if c.hp <= 0 else ""),
					"mp": _tr(MP_KEY).format({"mp": c.mp, "max": c.max_mp}),
					"right":
					_tr(COUNT_ONE_KEY if n == 1 else (COUNT_NONE_KEY if n == 0 else COUNT_KEY)).format({"count": n}),
					"right_role": &"text" if n > 0 else &"text_dim",
					"enabled": true,
				}
			)
		)
	return out


## {text, ok}: the caster line (how to go on, or why this hero has nothing to cast).
func caster_line(caster: StringName) -> Dictionary:
	if spells_of(caster).is_empty():
		return {"text": _tr(NO_SPELLS_KEY).format({"name": sheet.hero_name(caster)}), "ok": false}
	return {"text": _tr(CASTER_HINT_KEY), "ok": true}


# --- spells ---------------------------------------------------------------------------------------


func spell_name(sid: StringName) -> String:
	var key := str(_skill(sid).get("name_key", ""))
	return _tr(key) if key != "" else String(sid)


func spell_cost(sid: StringName) -> int:
	return int(_skill(sid).get("mp_cost", 0))


func is_all_allies(sid: StringName) -> bool:
	return TARGET_ALL.has(str(_skill(sid).get("target", "")))


## The caster's spells: name, MP cost (dimmed when it can't be cast now).
func spell_rows(caster: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for sid in spells_of(caster):
		(
			out
			. append(
				{
					"id": sid,
					"label": spell_name(sid),
					"right": _tr(COST_KEY).format({"mp": spell_cost(sid)}),
					"right_role": &"text" if spell_error(caster, sid) == RESULT_OK else &"text_dim",
					"enabled": true,
				}
			)
		)
	return out


## Why `caster` can't cast `sid` at all (the rules asked with no targets: MP, silence, a fallen caster), or OK.
func spell_error(caster: StringName, sid: StringName) -> StringName:
	var c := sheet.combatant(caster)
	if c == null or not spells_of(caster).has(sid):
		return ERR_NO_SPELLS
	return StringName(str(rules.refusal.call(c, sid, [] as Array[BattleCombatant])))


## {text, ok}: how to cast the highlighted spell, or why it can't be.
func spell_line(caster: StringName, sid: StringName) -> Dictionary:
	var err := spell_error(caster, sid)
	if err != RESULT_OK:
		return {"text": refusal_text(err, caster, sid), "ok": false}
	return {"text": _tr(CAST_HINT_KEY), "ok": true}


func pick_title(caster: StringName, sid: StringName) -> String:
	var key := PICK_ALL_TITLE_KEY if is_all_allies(sid) else PICK_TITLE_KEY
	return _tr(key).format({"spell": spell_name(sid), "caster": sheet.hero_name(caster)})


# --- targets --------------------------------------------------------------------------------------


## The hero picker: each hero with HP and MP as they stand; a refused hero stays choosable, dimmed.
func hero_rows(caster: StringName, sid: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for cid in sheet.heroes:
		var c := sheet.combatant(cid)
		if c == null:
			continue
		var ok := hero_error(caster, sid, cid) == RESULT_OK
		(
			out
			. append(
				{
					"id": cid,
					"label": sheet.hero_name(cid) + (_tr(FALLEN_TAG_KEY) if c.hp <= 0 else ""),
					"mp": _tr(HP_KEY).format({"hp": c.hp, "max": c.max_hp}),
					"right": _tr(MP_KEY).format({"mp": c.mp, "max": c.max_mp}),
					"right_role": &"text" if ok else &"text_dim",
					"enabled": true,
				}
			)
		)
	return out


## Why casting `sid` on `cid` would do nothing or may not be done, or OK.
func hero_error(caster: StringName, sid: StringName, cid: StringName) -> StringName:
	var err := spell_error(caster, sid)
	if err != RESULT_OK:
		return err
	var c := sheet.combatant(caster)
	var t := c if cid == caster else sheet.combatant(cid)
	if t == null:
		return &"no_effect"
	return StringName(str(rules.refusal.call(c, sid, [t] as Array[BattleCombatant])))


## The heroes a cast of `sid` chosen on `cid` reaches: every hero it may help for an all-allies spell, else `cid`.
func targets(caster: StringName, sid: StringName, cid: StringName) -> Array[StringName]:
	var out: Array[StringName] = []
	if not is_all_allies(sid):
		if hero_error(caster, sid, cid) == RESULT_OK:
			out.append(cid)
		return out
	for h in sheet.heroes:
		if hero_error(caster, sid, h) == RESULT_OK:
			out.append(h)
	return out


## {text, ok}: what the cast would do ("Asha: MP 60 → 56 · Rhen: HP 120 → 220"), or why not. Nothing is saved.
func preview(caster: StringName, sid: StringName, cid: StringName) -> Dictionary:
	var reach := targets(caster, sid, cid)
	if reach.is_empty():
		return {"text": _refusal_for(caster, sid, cid), "ok": false}
	return {"text": _change_text(_trial(caster, sid, reach)), "ok": true}


## Casts `sid` from `caster` on `cid` (or on everyone it helps): the rules apply it and spend the MP, and every
## changed hero is written to the save. Returns {ok, text}: the receipt, or the refusal (nothing spent).
func cast_on(caster: StringName, sid: StringName, cid: StringName) -> Dictionary:
	var reach := targets(caster, sid, cid)
	if reach.is_empty():
		return {"text": _refusal_for(caster, sid, cid), "ok": false}
	var trial := _trial(caster, sid, reach)
	if not bool((trial["result"] as Dictionary).get("ok", true)):
		return {"text": _refusal_for(caster, sid, cid), "ok": false}
	for c: BattleCombatant in trial["combatants"]:
		_save(c)
	return {
		"text":
		_tr(CAST_KEY).format(
			{"caster": sheet.hero_name(caster), "spell": spell_name(sid), "effects": _change_text(trial)}
		),
		"ok": true,
	}


## One refusal in words (REFUSAL_KEYS; an id the page does not know yet reads as the generic line).
func refusal_text(err: StringName, caster: StringName, sid: StringName, cid: StringName = &"") -> String:
	var words := {
		"spell": spell_name(sid),
		"caster": sheet.hero_name(caster),
		"name": sheet.hero_name(cid) if cid != &"" else sheet.hero_name(caster),
		"mp": spell_cost(sid),
	}
	if err == ERR_NO_SPELLS:
		return _tr(NO_SPELLS_KEY).format({"name": sheet.hero_name(caster)})
	return _tr(str(REFUSAL_KEYS.get(err, GENERIC_REFUSAL_KEY))).format(words)


# --- internals ------------------------------------------------------------------------------------


func _refusal_for(caster: StringName, sid: StringName, cid: StringName) -> String:
	var err := spell_error(caster, sid)
	if err == RESULT_OK and is_all_allies(sid):
		err = ERR_NO_ONE
	elif err == RESULT_OK:
		err = hero_error(caster, sid, cid)
	return refusal_text(err, caster, sid, cid)


## The cast on fresh copies (nothing saved): {combatants (caster first, then the targets, once each), before
## ({id: [hp, mp, statuses]}), result}.
func _trial(caster: StringName, sid: StringName, reach: Array[StringName]) -> Dictionary:
	var c := sheet.combatant(caster)
	var all: Array[BattleCombatant] = [c]
	var targets_c: Array[BattleCombatant] = []
	for h in reach:
		var t := c if h == caster else sheet.combatant(h)
		targets_c.append(t)
		if t != c:
			all.append(t)
	var before := {}
	for x in all:
		before[x.id] = [x.hp, x.mp, x.statuses.keys()]
	var result: Variant = rules.cast.call(c, sid, targets_c)
	return {"combatants": all, "before": before, "result": result if result is Dictionary else {}}


## "Asha: MP 60 → 56 · Rhen: HP 120 → 220, cures Poison", one part per hero that changed.
func _change_text(trial: Dictionary) -> String:
	var parts: Array[String] = []
	for c: BattleCombatant in trial["combatants"]:
		var was: Array = (trial["before"] as Dictionary)[c.id]
		var changes: Array[String] = []
		if int(was[0]) <= 0 and c.hp > 0:
			changes.append(_tr(REVIVED_KEY))
		if c.hp != int(was[0]):
			changes.append(_tr(PREVIEW_HP_KEY).format({"from": was[0], "to": c.hp}))
		if c.mp != int(was[1]):
			changes.append(_tr(PREVIEW_MP_KEY).format({"from": was[1], "to": c.mp}))
		var cured: Array[String] = []
		for sid: Variant in was[2]:
			if not c.statuses.has(sid):
				cured.append(_status_name(StringName(str(sid))))
		if not cured.is_empty():
			changes.append(_tr(PREVIEW_CURE_KEY).format({"statuses": _tr(LIST_JOIN_KEY).join(cured)}))
		if not changes.is_empty():
			var words := {"name": sheet.hero_name(c.id), "changes": _tr(PREVIEW_JOIN_KEY).join(changes)}
			parts.append(_tr(PREVIEW_KEY).format(words))
	return _tr(SPENT_KEY).join(parts)


func _status_name(sid: StringName) -> String:
	var key := str((sheet.battle_db.statuses.get(sid, {}) as Dictionary).get("name_key", ""))
	return _tr(key) if key != "" else String(sid)


func _skill(sid: StringName) -> Dictionary:
	return sheet.battle_db.skill(sid)


## Writes `c`'s HP, MP and carried statuses to the save, keeping its saved Swell gauge and mode.
func _save(c: BattleCombatant) -> void:
	var held: Array[StringName] = []
	for sid: Variant in c.statuses:
		held.append(StringName(str(sid)))
	var st := sheet.state
	st.record_vitals(c.id, c.hp, c.max_hp, c.mp, c.max_mp, held, carried, st.swell_of(c.id), st.swell_mode_of(c.id))


static func _tr(key: String) -> String:
	return TranslationServer.translate(key) if key != "" else ""

class_name EnemyPage
extends RefCounted
## The words of one foe's page (M2-UI-02, SPEC §6.1 and §6.11), shared by the battle Read panel
## (ReadPanel) and the bestiary menu (BestiaryMenu): name, level, HP and MP, the eight stats, the
## four affinity lists, delay immunity, statuses, lore and the defeat count. A model only: it
## turns a BattleRead.reveal() into display strings through loc keys, and EnemyPageView lays
## them out. Node-free, so tests read exactly what the screen shows.
##
## Page: {title, level, vitals, stats: [[label, value]], affinities: [{group, label, text}],
##        delay, statuses, lore, defeated, read}. A string that does not apply is "" (a bestiary
## page has no statuses, a Read in battle no defeat count), and the view leaves its row out.

## BattleRead's stat order, each with its label key (a literal tr() each, so the loc check sees it).
const STAT_KEYS := {
	"strength": "STAT_STRENGTH",
	"magic": "STAT_MAGIC",
	"defense": "STAT_DEFENSE",
	"magic_defense": "STAT_MAGIC_DEFENSE",
	"agility": "STAT_AGILITY",
	"accuracy": "STAT_ACCURACY",
	"evasion": "STAT_EVASION",
	"luck": "STAT_LUCK",
}
const AFFINITY_KEYS := {
	"weak": "HUD_READ_AFF_WEAK",
	"resist": "HUD_READ_AFF_RESIST",
	"immune": "HUD_READ_AFF_IMMUNE",
	"absorb": "HUD_READ_AFF_ABSORB",
}
const ELEMENT_KEY_PREFIX := "ELEMENT_"
const STATUS_KEY_PREFIX := "STATUS_"
const LIST_SEPARATOR := ", "
## M4-A2P-083: the Read's line for a foe's broken parts (BattleParts), each named by its charge skill.
const PARTS_BROKEN_FMT_KEY := "HUD_READ_PARTS_BROKEN_FMT"


## The page for a Read in battle: HP, MP and statuses as they stand. `statuses` is the battle's
## statuses table (BattleDB.statuses) for the status names.
func from_reveal(reveal: Dictionary, statuses: Dictionary = {}) -> Dictionary:
	var page := _common(reveal)
	page["vitals"] = (
		" · "
		. join(
			[
				tr("HUD_READ_HP_FMT").format({"hp": int(reveal.get("hp", 0)), "max": int(reveal.get("max_hp", 0))}),
				tr("HUD_READ_MP_FMT").format({"mp": int(reveal.get("mp", 0)), "max": int(reveal.get("max_mp", 0))}),
			]
		)
	)
	var names: PackedStringArray = []
	for sid: Variant in reveal.get("statuses", []):
		names.append(status_name(StringName(str(sid)), statuses))
	page["statuses"] = LIST_SEPARATOR.join(names) if not names.is_empty() else tr("HUD_READ_NONE")
	var parts: PackedStringArray = []
	for key: Variant in reveal.get("broken_parts", []):
		parts.append(tr(str(key)))
	page["parts"] = (
		tr(PARTS_BROKEN_FMT_KEY).format({"list": LIST_SEPARATOR.join(parts)}) if not parts.is_empty() else ""
	)
	return page


## The bestiary page of a foe the party has Read: its enemies.json row (`row`, id `enemy_id`) at
## full strength, with no statuses, and the defeat count.
func from_row(enemy_id: StringName, row: Dictionary, defeated: int) -> Dictionary:
	var c := BattleCombatant.from_dict(enemy_id, BattleCombatant.TEAM_ENEMY, row)
	var page := _common(BattleRead.reveal(c, row))
	page["vitals"] = " · ".join(
		[tr("BESTIARY_HP_FMT").format({"hp": c.max_hp}), tr("BESTIARY_MP_FMT").format({"mp": c.max_mp})]
	)
	page["defeated"] = defeated_text(defeated)
	return page


## The bestiary page of a foe defeated but never Read: its name and count only.
func name_only(row: Dictionary, defeated: int) -> Dictionary:
	var page := _blank()
	page["title"] = _name(str(row.get("name_key", "")), str(row.get("id", "")))
	page["defeated"] = defeated_text(defeated)
	page["lore"] = tr("BESTIARY_UNREAD")
	return page


func defeated_text(n: int) -> String:
	return tr("BESTIARY_DEFEATED_FMT").format({"n": n})


func element_name(element: StringName) -> String:
	var key := ELEMENT_KEY_PREFIX + String(element).to_upper()
	var t := tr(key)
	return t if t != key else String(element)


func status_name(sid: StringName, statuses: Dictionary = {}) -> String:
	var key := str((statuses.get(sid, {}) as Dictionary).get("name_key", STATUS_KEY_PREFIX + String(sid).to_upper()))
	var t := tr(key)
	return t if t != key else String(sid)


func _common(reveal: Dictionary) -> Dictionary:
	var page := _blank()
	page["read"] = true
	page["title"] = _name(str(reveal.get("name_key", "")), str(reveal.get("enemy_id", "")))
	page["level"] = tr("HUD_READ_LEVEL_FMT").format({"level": int(reveal.get("level", 1))})
	var stats: Dictionary = reveal.get("stats", {})
	var rows: Array = []
	for key: String in STAT_KEYS:
		rows.append([tr(STAT_KEYS[key]), str(int(stats.get(key, 0)))])
	page["stats"] = rows
	var groups: Dictionary = reveal.get("affinities", {})
	var aff: Array = []
	for group: String in AFFINITY_KEYS:
		var names: PackedStringArray = []
		for el: Variant in groups.get(group, []):
			names.append(element_name(StringName(str(el))))
		var text := LIST_SEPARATOR.join(names) if not names.is_empty() else tr("HUD_READ_NONE")
		aff.append({"group": group, "label": tr(AFFINITY_KEYS[group]), "text": text, "empty": names.is_empty()})
	page["affinities"] = aff
	page["delay"] = tr("HUD_READ_DELAY_IMMUNE") if bool(reveal.get("delay_immune", false)) else tr("HUD_READ_DELAY_OK")
	var lore_key := str(reveal.get("lore_key", ""))
	page["lore"] = tr(lore_key) if lore_key != "" else ""
	return page


func _blank() -> Dictionary:
	return {
		"title": "",
		"level": "",
		"vitals": "",
		"stats": [],
		"affinities": [],
		"delay": "",
		"statuses": "",
		"parts": "",
		"lore": "",
		"defeated": "",
		"read": false,
	}


func _name(key: String, fallback: String) -> String:
	return tr(key) if key != "" else fallback

class_name GameStateData
extends Resource
## All persistent, savable game state. Serialized by SaveSystem via to_dict()/from_dict().
##
## Save v4 (M1-ARC-06) adds party vitals, attuned shrines and the respawn point:
##   party_vitals     {"<character>": {"hp": int, "mp": int, "statuses": [status id]}}
##                    A member with no entry is at full HP and MP with no statuses. Inside an
##                    entry, a missing "hp" or "mp" also means full: a shrine heal cannot know
##                    the maximum (Lattice and gear raise it at battle setup), so it erases the
##                    values instead of writing them. "statuses" holds only the carried statuses
##                    (party_rest.json "carried_statuses"); battle-only statuses never persist.
##   attuned_shrines  shrine network ids in the order they were attuned (ShrineNetwork)
##   respawn          {"location_id", "spawn"}: where Continue puts the party (WorldReturn).
##                    An empty location means the registry's default; an empty spawn means
##                    the location's own spawn (game/data/world/locations.json).
##
## Save v5 (M1-CMB-03) adds the bestiary log:
##   bestiary         {"<enemy id>": {"read": bool, "defeated": whole number}} (Bestiary wraps it)
##
## Save v6 (M2-ARC-01) carries Swell (docs/kb/design/battle_ctb.md "Carried Swell"):
##   party_vitals     entries may also hold "swell" (gauge points, 0..Formulas.SWELL_MAX) and
##                    "swell_mode" (the hero's fill mode id). No "swell" means an empty gauge, and
##                    no "swell_mode" means swell.json's default mode. A shrine rest keeps both.
##   swell            {"unlocked": [mode id], "progress": {"<unlock rule id>": count}}: the modes
##                    unlocked through play and the counts towards the rest, party-wide
##                    (BattleSwell.to_saved / load_saved). Ids swell.json no longer lists are kept.

const KEY_HP := "hp"
const KEY_MP := "mp"
const KEY_STATUSES := "statuses"
const KEY_SWELL := "swell"
const KEY_SWELL_MODE := "swell_mode"

@export var flags: Dictionary = {}
@export var party_ids: Array[StringName] = []
@export var reserve_ids: Array[StringName] = []
@export var inventory: Dictionary = {}
@export var currency: int = 0
@export var play_time_sec: float = 0.0
@export var location_id: StringName = &""
@export var chapter: int = 0
## Lattice progress as plain data (LatticeProgress.to_dict()); rebuild it with
## LatticeProgress.from_dict(lattice, board, rules). Facets themselves live in `inventory`.
@export var lattice: Dictionary = {}
## Owned equipment pieces and loadouts as plain data (wrapped in place by EquipmentBag):
## {next_uid, owned: {"<uid>": {base, abilities[]}}, loadout: {character: {weapon, armor}}}.
## Items and Facets live in `inventory`, lume in `currency`.
@export var equipment: Dictionary = {}
## v4: per-member HP, MP and carried statuses (see the class comment).
@export var party_vitals: Dictionary = {}
## v4: ShrineNetwork ids the party has rested at, in attunement order.
@export var attuned_shrines: Array[StringName] = []
## v4: the respawn location id (LocationRegistry) and spawn marker name.
@export var respawn_location_id: StringName = &""
@export var respawn_spawn: StringName = &""
## v5: the bestiary log (Bestiary.new(bestiary) reads and writes it in place).
@export var bestiary: Dictionary = {}
## v6: the party's Swell record (see the class comment; BattleSwellCarry reads and writes it).
@export var swell: Dictionary = {}


func to_dict() -> Dictionary:
	return {
		"flags": flags.duplicate(true),
		"party_ids": party_ids.map(func(s: StringName) -> String: return String(s)),
		"reserve_ids": reserve_ids.map(func(s: StringName) -> String: return String(s)),
		"inventory": inventory.duplicate(true),
		"currency": currency,
		"play_time_sec": play_time_sec,
		"location_id": String(location_id),
		"chapter": chapter,
		"lattice": lattice.duplicate(true),
		"equipment": equipment.duplicate(true),
		"party_vitals": party_vitals.duplicate(true),
		"attuned_shrines": attuned_shrines.map(func(s: StringName) -> String: return String(s)),
		"respawn": {"location_id": String(respawn_location_id), "spawn": String(respawn_spawn)},
		"bestiary": bestiary.duplicate(true),
		"swell": swell.duplicate(true),
	}


static func from_dict(d: Dictionary) -> GameStateData:
	var s := GameStateData.new()
	s.flags = (d.get("flags", {}) as Dictionary).duplicate(true)
	for id: Variant in d.get("party_ids", []):
		s.party_ids.append(StringName(str(id)))
	for id: Variant in d.get("reserve_ids", []):
		s.reserve_ids.append(StringName(str(id)))
	s.inventory = (d.get("inventory", {}) as Dictionary).duplicate(true)
	for k: Variant in s.inventory:  # JSON loads counts as floats; the bag holds whole numbers
		s.inventory[k] = int(s.inventory[k])
	s.currency = int(d.get("currency", 0))
	s.play_time_sec = float(d.get("play_time_sec", 0.0))
	s.location_id = StringName(str(d.get("location_id", "")))
	s.chapter = int(d.get("chapter", 0))
	s.lattice = (d.get("lattice", {}) as Dictionary).duplicate(true)
	s.equipment = (d.get("equipment", {}) as Dictionary).duplicate(true)
	s.party_vitals = _clean_vitals(d.get("party_vitals", {}))
	for id: Variant in d.get("attuned_shrines", []):
		var sid := StringName(str(id))
		if not s.attuned_shrines.has(sid):
			s.attuned_shrines.append(sid)
	var rs: Variant = d.get("respawn", {})
	if typeof(rs) == TYPE_DICTIONARY:
		s.respawn_location_id = StringName(str((rs as Dictionary).get("location_id", "")))
		s.respawn_spawn = StringName(str((rs as Dictionary).get("spawn", "")))
	s.bestiary = Bestiary.from_saved(d.get("bestiary", {}))
	s.swell = _clean_swell(d.get("swell", {}))
	return s


# --- Party vitals (v4) -------------------------------------------------------------------------


## {hp?, mp?, statuses} for `cid` (a copy; {} when the member is at full with no statuses).
func vitals_of(cid: StringName) -> Dictionary:
	return (party_vitals.get(String(cid), {}) as Dictionary).duplicate(true)


## Carried statuses of `cid`, in stored order.
func statuses_of(cid: StringName) -> Array[StringName]:
	var out: Array[StringName] = []
	for sid: Variant in vitals_of(cid).get(KEY_STATUSES, []):
		out.append(StringName(str(sid)))
	return out


## Records `cid`'s state after a battle. HP and MP at their maximum are stored as "full" (no
## value), and only statuses in `carried` are kept. A member left at full with nothing carried
## has no entry at all, so saves stay small and the "no entry = full" rule holds. v6: a gauge
## above 0 is stored as `swell`, and a mode other than `default_mode` as `swell_mode`.
func record_vitals(
	cid: StringName,
	hp: int,
	max_hp: int,
	mp: int,
	max_mp: int,
	statuses: Array[StringName],
	carried: Array[StringName],
	swell_points: int = 0,
	swell_mode: StringName = &"",
	default_mode: StringName = &""
) -> void:
	var entry := {}
	if swell_points > 0:
		entry[KEY_SWELL] = swell_points
	if swell_mode != &"" and swell_mode != default_mode:
		entry[KEY_SWELL_MODE] = String(swell_mode)
	if hp < max_hp:
		entry[KEY_HP] = maxi(hp, 0)
	if mp < max_mp:
		entry[KEY_MP] = maxi(mp, 0)
	var kept: Array[String] = []
	for sid in statuses:
		if carried.has(sid) and not kept.has(String(sid)):
			kept.append(String(sid))
	if not kept.is_empty():
		entry[KEY_STATUSES] = kept
	if entry.is_empty():
		party_vitals.erase(String(cid))
	else:
		party_vitals[String(cid)] = entry


## A full rest (save shrine): every member's HP and MP become full and the statuses in `cures`
## are removed. Statuses not in `cures` stay, and so do Swell gauges and modes (v6: a rest is not
## a battle). Returns the ids whose entry changed, sorted.
func full_heal(cures: Array[StringName]) -> Array[StringName]:
	var changed: Array[StringName] = []
	for key: Variant in party_vitals.keys():
		var entry: Dictionary = party_vitals[key]
		var kept: Array[String] = []
		for sid: Variant in entry.get(KEY_STATUSES, []):
			if not cures.has(StringName(str(sid))):
				kept.append(str(sid))
		var before := entry.duplicate(true)
		entry.erase(KEY_HP)
		entry.erase(KEY_MP)
		entry.erase(KEY_STATUSES)
		if not kept.is_empty():
			entry[KEY_STATUSES] = kept
		if entry != before:
			changed.append(StringName(str(key)))
		if entry.is_empty():
			party_vitals.erase(key)
	changed.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	return changed


## Layers the stored vitals onto a freshly built party combatant. Run it LAST in the
## party_modifier chain, after the Lattice and gear have set max HP/MP: stored values are
## clamped to the new maximum. Carried statuses are added with `duration` before HP is set,
## because a KO'd combatant takes no statuses. A member without an entry is left untouched, so
## battles without saved vitals play exactly as before.
func apply_vitals_to(c: BattleCombatant, duration: int) -> void:
	var entry := vitals_of(c.id)
	if entry.is_empty():
		return
	for sid in statuses_of(c.id):
		c.add_status(sid, duration)
	if entry.has(KEY_HP):
		c.hp = clampi(int(entry[KEY_HP]), 0, c.max_hp)
		if c.hp == 0:
			c.statuses.clear()
	if entry.has(KEY_MP):
		c.mp = clampi(int(entry[KEY_MP]), 0, c.max_mp)
	if entry.has(KEY_SWELL):
		c.swell = clampi(int(entry[KEY_SWELL]), 0, Formulas.SWELL_MAX)
	if entry.has(KEY_SWELL_MODE):
		c.swell_mode = StringName(str(entry[KEY_SWELL_MODE]))


# --- Swell (v6) --------------------------------------------------------------------------------


## `cid`'s saved fill mode, or `default_mode` when none is saved.
func swell_mode_of(cid: StringName, default_mode: StringName = &"") -> StringName:
	var mode := str(vitals_of(cid).get(KEY_SWELL_MODE, ""))
	return StringName(mode) if mode != "" else default_mode


## `cid`'s saved gauge points (0 when none).
func swell_of(cid: StringName) -> int:
	return int(vitals_of(cid).get(KEY_SWELL, 0))


## Saves `cid`'s fill mode outside battle (a field menu), leaving the rest of its entry alone. The
## default mode is stored as no value. Callers check that the mode is choosable
## (BattleSwellCarry.set_mode).
func set_swell_mode(cid: StringName, mode: StringName, default_mode: StringName) -> void:
	var entry: Dictionary = party_vitals.get(String(cid), {})
	if mode == default_mode or mode == &"":
		entry.erase(KEY_SWELL_MODE)
	else:
		entry[KEY_SWELL_MODE] = String(mode)
	if entry.is_empty():
		party_vitals.erase(String(cid))
	else:
		party_vitals[String(cid)] = entry


## {unlocked: [String], progress: {String: int}} from a saved record (JSON counts are floats).
static func _clean_swell(raw: Variant) -> Dictionary:
	if typeof(raw) != TYPE_DICTIONARY:
		return {}
	var d := raw as Dictionary
	var out := {}
	if typeof(d.get("unlocked")) == TYPE_ARRAY:
		var ids: Array[String] = []
		for v: Variant in d["unlocked"]:
			ids.append(str(v))
		out["unlocked"] = ids
	if typeof(d.get("progress")) == TYPE_DICTIONARY:
		var counts := {}
		for k: Variant in d["progress"]:
			counts[str(k)] = int((d["progress"] as Dictionary)[k])
		out["progress"] = counts
	return out


## Keeps only well-formed entries (a hand-edited or damaged save must not crash battle setup).
static func _clean_vitals(raw: Variant) -> Dictionary:
	var out: Dictionary = {}
	if typeof(raw) != TYPE_DICTIONARY:
		return out
	for key: Variant in raw:
		var e: Variant = (raw as Dictionary)[key]
		if typeof(e) != TYPE_DICTIONARY:
			continue
		var entry := {}
		for k: String in [KEY_HP, KEY_MP]:
			var v: Variant = (e as Dictionary).get(k)
			if typeof(v) == TYPE_INT or typeof(v) == TYPE_FLOAT:
				entry[k] = maxi(int(v), 0)
		var points: Variant = (e as Dictionary).get(KEY_SWELL)
		if typeof(points) == TYPE_INT or typeof(points) == TYPE_FLOAT:
			if int(points) > 0:
				entry[KEY_SWELL] = int(points)
		var mode: Variant = (e as Dictionary).get(KEY_SWELL_MODE)
		if typeof(mode) == TYPE_STRING and str(mode) != "":
			entry[KEY_SWELL_MODE] = str(mode)
		var sts: Variant = (e as Dictionary).get(KEY_STATUSES, [])
		if typeof(sts) == TYPE_ARRAY and not (sts as Array).is_empty():
			var kept: Array[String] = []
			for sid: Variant in sts:
				kept.append(str(sid))
			entry[KEY_STATUSES] = kept
		if not entry.is_empty():
			out[str(key)] = entry
	return out

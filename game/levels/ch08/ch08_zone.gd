class_name Ch08Zone
extends Ch06Zone
## The Ch8 greybox zone root (M3-C08-02; act1_ch08.md; docs/kb/tech/chapter_flow.md "Ch8"): Corrow and
## Coilspire. Ch06Zone as it is (Ch01Zone's rest, give, hide_block / show_block; Ch04Zone's flag-driven
## "states"; the layout's "lights"; checkpoint(spawn)) plus three things Ch8 needs:
##   layout "start_hidden": [block ids]  Greybox blocks built hidden (with their collision), for the
##     states to show: the flood, the breach, the hoist, the storm wall.
##   layout "states_when": [{"when": {"set": [...], "unset": [...]}, "hide", "show", "place"}]  rows
##     like "states" but under a ZoneStory `when` (every flag must hold), applied after them on _ready
##     and in refresh_states(): Fenn in the beacon gallery only when he fed the beacon with Asha AND
##     Virel is bound; the storm's stand-ins only between two waves.
##   mend(source)  between the set piece's waves (act1_ch08.md §5a): every party member's carried HP
##     is raised to at least ch08_field.json mend.hp_pct of their battle maximum (the Stillguard line
##     rotates, and Ivo passes a water-skin). MP is left as it is. A `zone` step.

const CH08_FIELD_PATH := "res://game/data/flow/ch08_field.json"
const KEY_STATES_WHEN := "states_when"
const KEY_START_HIDDEN := "start_hidden"
const KEY_WHEN := "when"
const KEY_MEND := "mend"
const KEY_HP_PCT := "hp_pct"
const KEY_ENCOUNTER := "encounter"
const KEY_HP := "hp"
const PERCENT := 100.0

## ch08_field.json.
var ch08_field: Dictionary = {}
## The sources mend() was called with, in order (tests read it).
var mends: Array[String] = []


func build() -> void:
	if hint != null:
		return
	super()
	ch08_field = read_json(CH08_FIELD_PATH)
	for id: Variant in layout.get(KEY_START_HIDDEN, []):
		hide_block(str(id))


## Ch06Zone's states and lights, then the "states_when" rows.
func refresh_states() -> void:
	super()
	for r: Variant in layout.get(KEY_STATES_WHEN, []):
		var row: Dictionary = r
		if not ZoneStory.holds(row.get(KEY_WHEN, {})):
			continue
		for id: Variant in row.get("hide", []):
			hide_block(str(id))
		for id: Variant in row.get("show", []):
			show_block(str(id))
		var place: Dictionary = row.get(KEY_PLACE, {})
		for id: Variant in place:
			place_actor(str(id), str(place[id]))


## Raises each party member's carried HP to at least mend.hp_pct of the maximum a battle would give
## them (their Lattice and gear, built the way a live battle builds them). Returns the ids it raised.
func mend(source: String) -> Array[StringName]:
	mends.append(source)
	var cfg: Dictionary = ch08_field.get(KEY_MEND, {})
	var pct := float(cfg.get(KEY_HP_PCT, 0.0))
	var raised: Array[StringName] = []
	var ids: Array[StringName] = []
	ids.append_array(Game.state.party_ids)
	ids.append_array(Game.state.reserve_ids)
	if pct <= 0.0 or ids.is_empty():
		return raised
	var engine := BattleEngine.new()
	var plan := {
		BattleVitals.KEY_ACTIVE: Game.state.party_ids.duplicate(),
		BattleVitals.KEY_RESERVE: Game.state.reserve_ids.duplicate(),
		BattleVitals.KEY_ENCOUNTER: StringName(str(cfg.get(KEY_ENCOUNTER, ""))),
		BattleVitals.KEY_SEED: 0,
	}
	BattleVitals.setup(engine, BattleDB.load_default(), plan, BattleStage.lattice_for(ids, Game.state.lattice), true)
	for c in engine.party_active + engine.party_reserve:
		var floor_hp := ceili(float(c.max_hp) * pct / PERCENT)
		if c.hp >= floor_hp:
			continue
		var entry: Dictionary = Game.state.party_vitals.get(String(c.id), {})
		if floor_hp >= c.max_hp:
			entry.erase(KEY_HP)
		else:
			entry[KEY_HP] = floor_hp
		if entry.is_empty():
			Game.state.party_vitals.erase(String(c.id))
		else:
			Game.state.party_vitals[String(c.id)] = entry
		raised.append(c.id)
	return raised

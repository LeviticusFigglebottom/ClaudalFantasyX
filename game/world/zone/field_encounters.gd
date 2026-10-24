class_name FieldEncounters
extends Node
## Random field encounters for a greybox zone (M2-FP-25; docs/kb/tech/chapter_flow.md). The zone's
## layout "encounters" block:
##   table     [{"encounter": id, "weight": n}]  what can be met (encounters.json ids)
##   min_m     the least distance Rhen walks between two encounters
##   max_m     the most (each gap is drawn between them from the seeded rng)
##   when      {"set": [...], "unset": [...]}  encounters happen only while this holds
##   seed      the rng seed (a zone's encounters are the same on every run from the same state)
## Light Step and the like stretch every gap: the party's encounter_rate_pct (EquipmentEffects) is
## applied as gap * 100 / rate. A due encounter waits while the story is busy. When one fires it
## remembers where Rhen stood, and the battle returns to the zone's "Encounter" spawn there
## (GreyboxZone.place_at). Time passes only through walked(), so tests drive it exactly.

const RETURN_SPAWN := &"Encounter"
const FULL_RATE_PCT := 100.0

## Where the last encounter left Rhen, per location (the battle scene replaces the zone, so it is
## kept here for the return).
static var return_points: Dictionary = {}

var table: Array = []
var min_m := 0.0
var max_m := 0.0
var when: Dictionary = {}
var rate_pct := FULL_RATE_PCT
var rng := RandomNumberGenerator.new()
## Metres walked since the last encounter, and the gap to the next one.
var walked_m := 0.0
var next_m := 0.0
## Tests set this to record the encounter instead of starting the battle.
var on_encounter: Callable = Callable()

var _zone: GreyboxZone
var _last: Vector3
var _has_last := false


func setup(zone: GreyboxZone, block: Dictionary) -> void:
	_zone = zone
	table = block.get("table", [])
	min_m = float(block.get("min_m", 0.0))
	max_m = float(block.get("max_m", min_m))
	when = block.get("when", {})
	rng.seed = int(block.get("seed", 0)) + Game.state.chapter
	rate_pct = party_rate_pct()
	next_m = _draw()


## The party's encounter rate in percent (100 = normal; Light Step halves it).
static func party_rate_pct() -> float:
	var db := ItemDB.load_default()
	if db == null or Game.state.party_ids.is_empty():
		return FULL_RATE_PCT
	var goods := PartyGoods.from_state(db, Game.state)
	var fx := EquipmentEffects.new(db, goods.equipment)
	return float(maxi(fx.encounter_rate_pct(Game.state.party_ids), 1))


func _physics_process(_delta: float) -> void:
	if _zone == null or _zone.player == null:
		return
	var p := _zone.player.global_position
	if _has_last:
		walked(Vector2(p.x - _last.x, p.z - _last.z).length())
	_last = p
	_has_last = true


## Adds `metres` of walking; fires an encounter when the gap is reached and the story is free.
## Returns the encounter id that fired, or &"".
func walked(metres: float) -> StringName:
	if table.is_empty() or not ZoneStory.holds(when):
		return &""
	walked_m += metres
	if walked_m < next_m or not _zone.story.is_free():
		return &""
	var id := pick()
	walked_m = 0.0
	next_m = _draw()
	return_points[String(_zone.location_id)] = _zone.player.position
	if on_encounter.is_valid():
		on_encounter.call(id)
	else:
		_zone.story.random_battle(id, RETURN_SPAWN)
	return id


## A weighted pick from the table.
func pick() -> StringName:
	var total := 0
	for row: Dictionary in table:
		total += int(row.get("weight", 1))
	var roll := rng.randi_range(1, maxi(total, 1))
	for row: Dictionary in table:
		roll -= int(row.get("weight", 1))
		if roll <= 0:
			return StringName(str(row.get("encounter", "")))
	return StringName(str(table.back().get("encounter", "")))


func _draw() -> float:
	return rng.randf_range(min_m, max_m) * FULL_RATE_PCT / rate_pct

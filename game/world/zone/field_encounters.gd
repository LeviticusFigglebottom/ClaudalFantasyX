class_name FieldEncounters
extends Node
## Random field encounters for a greybox zone (M2-FP-25; docs/kb/tech/chapter_flow.md). The zone's
## layout "encounters" block:
##   table     [{"encounter": id, "weight": n}]  what can be met (encounters.json ids)
##   min_m     the least distance Rhen walks between two encounters
##   max_m     the most (each gap is drawn between them from the seeded rng)
##   when      {"set": [...], "unset": [...]}  encounters happen only while this holds
##   seed      the rng seed (a zone's encounters are the same on every run from the same state)
##   grace_m   metres after an encounter before the meter runs again (the walk back from a battle)
##   max_step_m  a frame's move longer than this is a teleport (a placement), never walking
## grace_m and max_step_m default to greybox_defaults.json "encounters".
## Light Step and the like stretch every gap: the party's encounter_rate_pct (EquipmentEffects) is
## applied as gap * 100 / rate. A zone root with encounter_rate_mult() (Ch1's lantern shutter) scales
## each metre walked by it, live. A due encounter waits while the story is busy. When one fires it
## remembers where Rhen stood, and the battle returns to the zone's "Encounter" spawn there
## (GreyboxZone.place_at). Time passes only through walked(), so tests drive it exactly.
## M2-MNU-08: gear changed in the field (the Equip page) reaches the gap in progress: the meter joins
## GROUP, and refresh_rate() rescales what is left of the gap by old rate / new rate (no new draw, so a run
## stays deterministic). With no joined party (the first playable), the field menu's heroes count.
## M2-FP-28 (the human's playtest: battles back to back): the meter (metres walked, the next gap, the
## grace left and the rng) is kept per location in `meters`, so the zone instanced again after the
## battle carries on instead of redrawing the same first gap; place_at re-anchors the walk, so the
## jump to the return spot never counts; and after each encounter `grace_m` must be walked first.

const RETURN_SPAWN := &"Encounter"
const FULL_RATE_PCT := 100.0
## The SceneTree group of live meters; the Equip page calls refresh_rate() on it when it closes.
const GROUP := &"field_encounters"

## Where the last encounter left Rhen, per location (the battle scene replaces the zone, so it is
## kept here for the return).
static var return_points: Dictionary = {}
## Each location's meter across the battle round trip and later visits: {walked_m, next_m, grace_m,
## rng_state}.
static var meters: Dictionary = {}

var table: Array = []
var min_m := 0.0
var max_m := 0.0
var when: Dictionary = {}
var rate_pct := FULL_RATE_PCT
var grace_after_m := 0.0
var max_step_m := 0.0
var rng := RandomNumberGenerator.new()
## Metres walked since the last encounter, and the gap to the next one.
var walked_m := 0.0
var next_m := 0.0
## Metres still to walk before the meter runs again (set to grace_after_m by each encounter).
var grace_m := 0.0
## Tests set this to record the encounter instead of starting the battle.
var on_encounter: Callable = Callable()

var _zone: GreyboxZone
var _last: Vector3
var _has_last := false


## Forgets every remembered meter and return point (a new game; tests).
static func reset() -> void:
	return_points.clear()
	meters.clear()


func setup(zone: GreyboxZone, block: Dictionary, defaults: Dictionary = {}) -> void:
	_zone = zone
	add_to_group(GROUP)
	if not EventBus.new_game_started.is_connected(reset):
		EventBus.new_game_started.connect(reset)  # a new game, or a loaded one, starts every meter afresh
		EventBus.game_loaded.connect(func(_slot: int) -> void: reset())
	table = block.get("table", [])
	min_m = float(block.get("min_m", 0.0))
	max_m = float(block.get("max_m", min_m))
	when = block.get("when", {})
	grace_after_m = float(block.get("grace_m", defaults.get("grace_m", 0.0)))
	max_step_m = float(block.get("max_step_m", defaults.get("max_step_m", 0.0)))
	rng.seed = int(block.get("seed", 0)) + Game.state.chapter
	rate_pct = party_rate_pct()
	var saved: Dictionary = meters.get(String(zone.location_id), {})
	if saved.is_empty():
		next_m = _draw()
		return
	walked_m = float(saved["walked_m"])
	next_m = float(saved["next_m"])
	grace_m = float(saved["grace_m"])
	rng.state = int(saved["rng_state"])
	# M2-MNU-08 with M2-FP-28: the kept gap was drawn at the rate of its time; gear changed since rescales it.
	rate_pct = float(saved.get("rate_pct", rate_pct))
	refresh_rate()


## Forgets where Rhen was, so the next frame's position starts the walk afresh (after a placement).
func reanchor() -> void:
	_has_last = false


func _exit_tree() -> void:
	remember()


## Keeps this location's meter for the zone's next instance.
func remember() -> void:
	if _zone != null:
		meters[String(_zone.location_id)] = {
			"walked_m": walked_m, "next_m": next_m, "grace_m": grace_m, "rng_state": rng.state, "rate_pct": rate_pct
		}


## The party's encounter rate in percent (100 = normal; Light Step halves it).
static func party_rate_pct() -> float:
	var db := ItemDB.load_default()
	var party := Game.state.party_ids if not Game.state.party_ids.is_empty() else FieldMenuModel.field_heroes()
	if db == null or party.is_empty():
		return FULL_RATE_PCT
	var goods := PartyGoods.from_state(db, Game.state)
	var fx := EquipmentEffects.new(db, goods.equipment)
	return float(maxi(fx.encounter_rate_pct(party), 1))


## Re-reads the party's rate (party_rate_pct, or `pct` when given) and rescales the rest of the gap in
## progress: at half the rate, what is left to walk doubles. Returns the new rate.
func refresh_rate(pct: float = -1.0) -> float:
	var new_rate := pct if pct > 0.0 else party_rate_pct()
	if not is_equal_approx(new_rate, rate_pct):
		next_m = walked_m + maxf(next_m - walked_m, 0.0) * rate_pct / new_rate
		rate_pct = new_rate
	return rate_pct


func _physics_process(_delta: float) -> void:
	if _zone == null or _zone.player == null:
		return
	var p := _zone.player.global_position
	if _has_last:
		var step := Vector2(p.x - _last.x, p.z - _last.z).length()
		if max_step_m <= 0.0 or step <= max_step_m:
			walked(step)
	_last = p
	_has_last = true


## Adds `metres` of walking; fires an encounter when the gap is reached and the story is free.
## Returns the encounter id that fired, or &"".
func walked(metres: float) -> StringName:
	if table.is_empty() or not ZoneStory.holds(when):
		return &""
	var m := metres * (float(_zone.call(&"encounter_rate_mult")) if _zone.has_method(&"encounter_rate_mult") else 1.0)
	var spent := minf(grace_m, m)
	grace_m -= spent
	walked_m += m - spent
	if walked_m < next_m or not _zone.story.is_free() or BattleRequest.opening():
		return &""  # M3-BPR-427: never while another battle is opening (the QA walk starts fights from outside)
	var id := pick()
	walked_m = 0.0
	next_m = _draw()
	grace_m = grace_after_m
	return_points[String(_zone.location_id)] = _zone.player.position
	remember()
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

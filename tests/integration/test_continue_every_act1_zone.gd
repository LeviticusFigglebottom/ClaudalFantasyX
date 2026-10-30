extends TestCase
## The Lead's save pass (2026-10-30, M4-A2P-1705): a save made in every Act I location continues there. For each
## playable Act I location (locations.json, the prologue to Ch9), a played state (party and reserve, story flags, the
## chapter, gear, money, the last shrine in an earlier zone) is autosaved at the chapter boundary, then Continue is
## chosen on the title (TitleSaveEntry.continue_game, as the title does): the state comes back as it was, and
## WorldReturn sends the party into that same location's scene at a spawn the location names. The shrine saves in
## every zone have their own round trip (test_qa_save_shrines); the autosave's mid-cutscene hold is
## test_autosave_deferred's.

const SAVE_DIR := "user://test_continue_every_act1_zone"
const ACT1_PREFIXES: Array[String] = [
	"prologue", "ch01", "ch02", "ch03", "ch04", "ch05", "ch06", "ch07", "ch08", "ch09"
]
const ACT2_PREFIXES: Array[String] = ["ch10", "ch11", "ch12", "ch13"]
const ACT1_PARTY: Array[StringName] = [&"rhen", &"asha"]
const ACT1_RESERVE: Array[StringName] = [&"toma"]
const ACT2_PARTY: Array[StringName] = [&"rhen", &"asha", &"pell"]
const ACT2_RESERVE: Array[StringName] = [&"toma", &"ysolde", &"liss", &"kerrid"]
const FAR_SHRINE := &"ch02/haluna"
## The state the played save sets (a load also fills an empty hero's starting gear, so "equipment" is not compared).
const CARRIED: Array[String] = [
	"chapter", "location_id", "party_ids", "reserve_ids", "flags", "inventory", "currency", "play_time_sec"
]


func test_every_act1_location_continues_where_it_was_saved() -> void:
	_sweep(ACT1_PREFIXES, ACT1_PARTY, ACT1_RESERVE, 12)


## The Lead's Act II pass (2026-10-30): the same in the mounted Ch10-Ch13, with the seven: three in the line, four in
## reserve, and Act II's story flags.
func test_every_act2_location_continues_where_it_was_saved() -> void:
	_sweep(ACT2_PREFIXES, ACT2_PARTY, ACT2_RESERVE, 10)


func _sweep(prefixes: Array[String], party: Array[StringName], reserve: Array[StringName], at_least: int) -> void:
	var saved := [SaveSystem.save_dir, SaveSystem.autosave_enabled, Game.state]
	SaveSystem.save_dir = SAVE_DIR
	SaveSystem.autosave_enabled = true
	var reg := LocationRegistry.load_default()
	var wr := WorldReturn.new()
	wr.registry = reg
	var checked := 0
	for loc in _locations(reg, prefixes):
		var state := _played_state(loc, party, reserve)
		Game.state = state
		var want := state.to_dict()
		assert_eq(SaveSystem.autosave(SaveSystem.REASON_CHAPTER), OK, "%s: the autosave is written" % loc)
		Game.state = GameStateData.new()
		assert_eq(TitleSaveEntry.continue_game(SaveSystem), OK, "%s: Continue loads it" % loc)
		var got := Game.state.to_dict()
		for key: String in CARRIED:
			assert_eq(got.get(key), want.get(key), "%s: %s comes back" % [loc, key])
		var to := wr.resolve(Game.state)
		assert_eq(str(to.get(LocationRegistry.KEY_SCENE, "")), reg.scene_of(loc), "%s: Continue enters its scene" % loc)
		var spawn := StringName(str(to.get(LocationRegistry.KEY_SPAWN, "")))
		assert_ne(spawn, &"", "%s: at a named spawn" % loc)
		checked += 1
	assert_true(checked >= at_least, "the locations were found (%d)" % checked)
	wr.free()
	_clear()
	SaveSystem.save_dir = saved[0]
	SaveSystem.autosave_enabled = saved[1]
	Game.state = saved[2]


static func _locations(reg: LocationRegistry, prefixes: Array[String]) -> Array[StringName]:
	var out: Array[StringName] = []
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://game/data/world/locations.json"))
	for row: Variant in (parsed as Dictionary).get("locations", []):
		var id := StringName(str((row as Dictionary).get("id", "")))
		if prefixes.has(String(id).get_slice("/", 0)) and reg.can_enter(id):
			out.append(id)
	return out


## A state from mid-journey in `loc`: its chapter, the party with Toma in reserve, a few story flags, gear and money,
## and the last shrine in another zone (the case a chapter autosave must not continue at).
static func _played_state(loc: StringName, party: Array[StringName], reserve: Array[StringName]) -> GameStateData:
	var s := GameStateData.new()
	var prefix := String(loc).get_slice("/", 0)
	s.chapter = prefix.trim_prefix("ch").to_int() if prefix.begins_with("ch") else 0
	s.location_id = loc
	s.respawn_location_id = FAR_SHRINE if loc != FAR_SHRINE else &"ch03/shell_shrine"
	s.party_ids = party.duplicate()
	s.reserve_ids = reserve.duplicate()
	s.flags = {"ch01_started": true, "ch01_wickfry_won": true, "ch02_met_asha": true, "tut_field_menu_seen": true}
	if s.chapter >= 10:
		s.flags.merge({"ch10_started": true, "ch11_nhoa_bound": true, "ch12_hesk_bound": true, "ch13_started": true})
	s.inventory = {"salt_tonic": 3, "quiet_tea": 1}
	s.currency = 321
	s.play_time_sec = 3600.0 + s.chapter
	return s


func _clear() -> void:
	var dir := DirAccess.open(SAVE_DIR)
	if dir == null:
		return
	for f in dir.get_files():
		DirAccess.remove_absolute(SAVE_DIR.path_join(f))
	DirAccess.remove_absolute(SAVE_DIR)

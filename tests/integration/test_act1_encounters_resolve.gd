extends TestCase
## act1_gpu_qa.md row 34 (act1-chapters): an Act I fight played on the battle sandbox's blank stage against its
## default foes (Lantern Eel, Reef Crab, Gull Harrier) instead of its own arena and enemies. Every Act I encounter
## (encounters.json ids ch01_ .. ch09_), started the way the field starts it (a pending BattleRequest, then the real
## field_battle.tscn's start), fights in the arena its row names and against exactly its row's enemies.

const FIELD_SCENE := "res://game/flow/field_battle.tscn"
const ENCOUNTERS_PATH := "res://game/data/battle/encounters.json"
const ACT1_ID := "^ch0[1-9]_"
## Act II (ADR 0205): its rows too, but four wait on their arenas (env-art-b; act2/chapters ch11.md, ch16.md).
const ACT2_ID := "^ch1[0-6]_"
const ACT2_NO_ARENA_YET: Array[String] = ["ch11_vey_rays", "ch11_vey_urchins", "ch16_rim_skates", "ch16_rim_crawlers"]
const LOCATION := &"ch06/brine_shoals"
const SPAWN := &"Entry"

var ctl: FieldBattle
var _saved_state: GameStateData


func _setup() -> void:
	_saved_state = Game.state
	Game.state = GameStateData.new()
	BattleRequest.clear()
	BattleRequest.change_scene = func(_path: String) -> void: pass


func _done() -> void:
	if ctl != null and is_instance_valid(ctl):
		# Freed at the frame's end, in the tree: an underwater arena's rig defers refresh_bounce_passes on it.
		ctl.queue_free()
	ctl = null
	BattleRequest.clear()
	BattleRequest.change_scene = Callable()
	Game.state = _saved_state


func _act1_rows(pattern: String = ACT1_ID) -> Array[Dictionary]:
	var re := RegEx.create_from_string(pattern)
	var out: Array[Dictionary] = []
	var parsed: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(ENCOUNTERS_PATH))
	for row: Dictionary in parsed["encounters"]:
		if re.search(str(row["id"])) != null:
			out.append(row)
	return out


func _start(encounter: StringName) -> void:
	BattleRequest.start(encounter, LOCATION, SPAWN, &"")
	ctl = (load(FIELD_SCENE) as PackedScene).instantiate() as FieldBattle
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.show_damage_numbers = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_sandbox()


func _base_ids(foes: Array) -> Array[String]:
	var out: Array[String] = []
	for c: BattleCombatant in foes:
		out.append(String(c.id).get_slice("#", 0))
	out.sort()
	return out


func test_every_act1_encounter_fights_in_its_arena_against_its_own_enemies() -> void:
	var rows := _act1_rows()
	assert_true(rows.size() >= 30, "Act I's encounters are read (%d)" % rows.size())
	for row in rows:
		var id := StringName(str(row["id"]))
		var arena := BattleArena.scene_of(str(row.get("arena", "")))
		assert_ne(arena, "", "%s names an arena in arenas.json, not the sandbox's stage" % id)
		assert_true(arena == "" or ResourceLoader.exists(arena), "%s: its arena scene exists (%s)" % [id, arena])
		_setup()
		_start(id)
		assert_eq(ctl.engine.encounter_id, id, "%s: the field battle plays the requested fight, not the sandbox's" % id)
		assert_eq(str(ctl.get_meta(BattleArena.META_ARENA, "")), arena, "%s: on its own arena" % id)
		var want: Array[String] = []
		for e: Variant in row.get("enemies", []):
			want.append(str(e))
		want.sort()
		assert_eq(_base_ids(ctl.engine.enemies), want, "%s: against its row's enemies only" % id)
		_done()


func test_every_act2_encounter_with_an_arena_fights_in_it_against_its_own_enemies() -> void:
	var rows := _act1_rows(ACT2_ID).filter(func(r: Dictionary) -> bool: return not ACT2_NO_ARENA_YET.has(str(r["id"])))
	assert_true(rows.size() >= 6, "Act II's rows are read (%d)" % rows.size())
	for row: Dictionary in rows:
		var id := StringName(str(row["id"]))
		var arena := BattleArena.scene_of(str(row.get("arena", "")))
		assert_ne(arena, "", "%s names an arena (or joins ACT2_NO_ARENA_YET with its request)" % id)
		_setup()
		_start(id)
		assert_eq(str(ctl.get_meta(BattleArena.META_ARENA, "")), arena, "%s: on its own arena" % id)
		var want: Array[String] = []
		for e: Variant in row.get("enemies", []):
			want.append(str(e))
		want.sort()
		assert_eq(_base_ids(ctl.engine.enemies), want, "%s: against its row's enemies only" % id)
		_done()

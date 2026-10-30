extends TestCase
## The Lead's 10-30 13:08 item: battle arenas carry their own ambience. A battle's arena (encounters.json `arena`) plays
## ambience.json `arenas` beds in place of the field's, and the field's come back when its listener leaves; a retry's
## new listener that already took the beds over keeps them; an arena with no row keeps the field's beds. Every Act II
## arena an encounter fights in has its beds, and every bed is a row.

const FIELD := &"fen_dusk"
const ARENA := &"arena_fen_roots"

var dir: AudioDirector


func before_each() -> void:
	dir = AudioDirector.new()
	_host().add_child(dir)
	dir.set_process(false)
	dir.zone = {"ambience": [String(FIELD)]}
	dir.set_ambience([FIELD] as Array[StringName], 0.0)


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _done() -> void:
	dir.stop_all_players()
	dir.free()


func _target(id: StringName) -> float:
	return (dir.beds[id] as FadeVoice).target if dir.beds.has(id) else 0.0


func test_the_arena_takes_over_and_gives_the_field_back() -> void:
	var a := RefCounted.new()
	dir.set_arena_ambience(a, AudioData.arena_beds(dir.ambience_data, "ossa_fen_roots"))
	assert_eq(_target(ARENA), 1.0, "the arena's bed comes in")
	assert_eq(_target(FIELD), 0.0, "the field's goes out")
	dir.release_arena_ambience(a)
	assert_eq(_target(FIELD), 1.0, "the field's comes back when the battle leaves")
	assert_eq(_target(ARENA), 0.0, "and the arena's goes")
	assert_true(dir.arena_owner == null, "nothing holds the beds")
	_done()


func test_a_retry_keeps_the_arena() -> void:
	var first := RefCounted.new()
	var retry := RefCounted.new()
	var ids := AudioData.arena_beds(dir.ambience_data, "ossa_fen_roots")
	dir.set_arena_ambience(first, ids)
	dir.set_arena_ambience(retry, ids)
	dir.release_arena_ambience(first)
	assert_eq(_target(ARENA), 1.0, "the old listener leaving does not take the retry's beds")
	dir.release_arena_ambience(retry)
	assert_eq(_target(FIELD), 1.0, "the retry's leaving gives the field back")
	_done()


func test_every_act2_arena_has_beds_and_every_bed_is_a_row() -> void:
	assert_true(
		AudioData.arena_beds(dir.ambience_data, "tideline_dawn").is_empty(), "an arena with no row keeps the field"
	)
	var scenes := BattleArena.data().get("scenes", {}) as Dictionary
	for arena: String in [
		"ossa_fen_roots",
		"lowlight_engine_hall",
		"keth_seep_terrace",
		"lacquer_court_steps",
		"ansedra_lagoon_escape",
		"bridal_barge_night",
		"drowned_choir_ring",
	]:
		assert_true(scenes.has(arena), "%s is an arena" % arena)
		var ids := AudioData.arena_beds(dir.ambience_data, arena)
		assert_false(ids.is_empty(), "%s has its beds" % arena)
		for id: StringName in ids:
			assert_true(dir.bed_table.has(String(id)), "%s is a bed row" % id)
	assert_true(float(dir.ambience_data.get("arena_fade_sec", -1.0)) >= 0.0, "a fade is set")
	_done()

extends TestCase
## M3-C01-1252 (the human's playtest FAST-TRACK, 11-03): the storm's fights used the normal backdrop and the uplifting
## battle theme. Every encounters.json row with `storm: true` fights on a storm arena (arenas.json `storm.arenas`: a
## scene with the storm sky, the rain and the vortex, an UndertowStorm named Undertow; or `storm.pending` while
## env-art-b builds its own scene) and plays a storm cue (music.json battle.storm_cues, never battle.default).

const MUSIC_PATH := "res://game/data/audio/music.json"
const TASKS_DIR := "res://docs/kb/tasks"
## The fights that happen while the Undertow is up (act1_ch01.md C1-13/C1-14, act1_ch08.md B10-B16,
## act2_ch16.md B09). A row here can't lose its flag quietly.
const STORM_FIGHTS: Array[StringName] = [
	&"ch01_scuttlers",
	&"ch01_hullgnaw",
	&"ch08_stair_hold_1",
	&"ch08_stair_hold_2",
	&"ch08_stair_hold_3",
	&"undertows_reach",
	&"ch16_storm_wakes",
]
## The storm's own node in a storm arena (the seawall arenas' Undertow: the wall, its rain and spray).
const UNDERTOW_NODE := ^"Undertow"


func _storm() -> Dictionary:
	return BattleArena.data().get("storm", {}) as Dictionary


func _music() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string(MUSIC_PATH)) as Dictionary


func _rows() -> Dictionary:
	return BattleDB.load_default().encounters


func _flagged() -> Array[StringName]:
	var out: Array[StringName] = []
	var rows := _rows()
	for key: Variant in rows:
		if bool((rows[key] as Dictionary).get("storm", false)):
			out.append(StringName(str(key)))
	return out


func test_every_storm_fight_is_flagged() -> void:
	var flagged := _flagged()
	for id in STORM_FIGHTS:
		assert_true(flagged.has(id), "%s is fought in the storm: encounters.json storm: true" % id)


func test_every_storm_fight_uses_a_storm_arena() -> void:
	var storm := _storm()
	var arenas := storm.get("arenas", []) as Array
	var pending := storm.get("pending", {}) as Dictionary
	var rows := _rows()
	for id in _flagged():
		var arena := str((rows[id] as Dictionary).get("arena", ""))
		assert_true(arenas.has(arena) or pending.has(arena), "%s fights on a storm arena, not '%s'" % [id, arena])
	# And the other way: nothing fought before or after the storm stands on a storm arena.
	for key: Variant in rows:
		var row := rows[key] as Dictionary
		var arena := str(row.get("arena", ""))
		if arenas.has(arena) or pending.has(arena):
			assert_true(bool(row.get("storm", false)), "%s is on storm arena %s: flag it storm" % [key, arena])


func test_every_storm_arena_shows_the_storm() -> void:
	var arenas := _storm().get("arenas", []) as Array
	assert_true(arenas.size() >= 3, "Ch8's three wall-head arenas at least")
	for a: Variant in arenas:
		var path := BattleArena.scene_of(str(a))
		assert_true(ResourceLoader.exists(path), "%s: %s exists" % [a, path])
		if not ResourceLoader.exists(path):
			continue
		var scene := (load(path) as PackedScene).instantiate()
		assert_true(
			scene.get_node_or_null(UNDERTOW_NODE) is UndertowStorm, "%s: the vortex (Undertow) stands in it" % a
		)
		scene.free()


func test_a_pending_storm_arena_has_its_request_and_a_fallback() -> void:
	var pending := _storm().get("pending", {}) as Dictionary
	for a: Variant in pending:
		var row := pending[a] as Dictionary
		var interim := str(row.get("interim", ""))
		assert_ne(BattleArena.scene_of(str(a)), "", "%s: a scenes row while it is pending" % a)
		assert_eq(
			BattleArena.scene_of(str(a)), BattleArena.scene_of(interim), "%s plays on %s meanwhile" % [a, interim]
		)
		assert_true(_task_exists(str(row.get("task", ""))), "%s: its request task %s is filed" % [a, row.get("task")])
		var own := BattleArenaRoot.path_for(StringName(str(a)))
		assert_false(
			ResourceLoader.exists(own), "%s's own scene has landed: point scenes at %s and move it to arenas" % [a, own]
		)


func test_every_storm_fight_plays_storm_music() -> void:
	var music := _music()
	var battle := music.get("battle", {}) as Dictionary
	var cues := battle.get("storm_cues", []) as Array
	var default_cue := str(battle.get("default", ""))
	assert_false(cues.has(default_cue), "the standard battle theme is never a storm cue")
	for id in _flagged():
		var cue := AudioData.battle_cue(music, id)
		assert_ne(String(cue), default_cue, "%s: not the uplifting standard theme" % id)
		assert_true(cues.has(String(cue)), "%s plays a storm cue, not %s" % [id, cue])
		var files := AudioData.cue_files(AudioData.cue(music, cue))
		assert_true(not files.is_empty(), "%s: cue %s has its files" % [id, cue])
		for f in files:
			assert_true(ResourceLoader.exists(f), "%s: %s exists" % [cue, f])


func _task_exists(task_id: String) -> bool:
	if task_id == "":
		return false
	var root := DirAccess.open(TASKS_DIR)
	if root == null:
		return false
	for m in root.get_directories():
		var d := DirAccess.open("%s/%s" % [TASKS_DIR, m])
		for f in d.get_files():
			if f.begins_with(task_id + "-"):
				return true
	return false

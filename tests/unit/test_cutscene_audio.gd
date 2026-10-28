extends TestCase
## M3-AUD-817: the slice's cutscene sound pass. CutsceneAudio plays cutscene_foley.json's rows on a sequencer's
## `@anim`, `@light` and `@vfx` cues at the actor, the light or the place, and stays silent through a skip; the
## director gives every actor a CutsceneStage can move its own FootstepAudio; the prologue plays its room tone. A
## stand-in sequencer (the real one's cue_played signature and is_skipping()) and a real CutsceneStage; sounds are
## recorded through the listener's player Callables, so nothing plays.

const PROLOGUE := "res://game/levels/prologue/prologue.tscn"
const DT := 1.0 / 60.0


class SeqStandIn:
	extends Node
	signal cue_played(cue: StringName, args: Array, kwargs: Dictionary)
	var skipping := false

	func is_skipping() -> bool:
		return skipping


var played: Array = []
var nodes: Array[Node] = []


func before_each() -> void:
	played = []
	nodes = []


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _add(n: Node, parent: Node = null) -> Node:
	(parent if parent != null else _host()).add_child(n)
	if parent == null:
		nodes.append(n)
	return n


func _done() -> void:
	for n in nodes:
		if is_instance_valid(n):
			n.free()
	nodes = []


func _audio() -> CutsceneAudio:
	var a := CutsceneAudio.new(AudioData.table(AudioData.CUTSCENE_FOLEY))
	a.player_at = func(id: StringName, at: Vector3) -> void: played.append([id, at])
	_add(a)
	return a


## A stage with actors ysolde (at (2, 0, 0)) and rhen, and the mark by_asha (at (0, 0, 4)).
func _stage() -> CutsceneStage:
	var stage := CutsceneStage.new()
	_add(stage)
	var actors := Node3D.new()
	actors.name = "Actors"
	stage.add_child(actors)
	for row: Array in [[&"ysolde", Vector3(2.0, 0.0, 0.0)], [&"rhen", Vector3(-2.0, 0.0, 0.0)]]:
		var a := Node3D.new()
		a.name = row[0]
		a.position = row[1]
		actors.add_child(a)
	var marks := Node3D.new()
	marks.name = "Marks"
	stage.add_child(marks)
	var m := Marker3D.new()
	m.name = "by_asha"
	m.position = Vector3(0.0, 0.0, 4.0)
	marks.add_child(m)
	return stage


func _ids() -> Array:
	return played.map(func(p: Array) -> String: return String(p[0]))


func test_every_row_exists() -> void:
	var rows := AudioData.sfx_rows()
	var d := AudioData.table(AudioData.CUTSCENE_FOLEY)
	var ids: Array = []
	for kind: String in ["anim", "vfx"]:
		ids.append_array((d.get(kind, {}) as Dictionary).values())
	for row: Dictionary in (d.get("light", {}) as Dictionary).values():
		ids.append_array(row.values())
	for id: String in ids:
		if id == "":
			continue
		assert_true(rows.has(id), "%s is an sfx row" % id)
		for f: String in (rows.get(id, {}) as Dictionary).get("files", []):
			assert_true(ResourceLoader.exists(f), "%s exists" % f)


func test_anim_cues_play_their_foley_at_the_actor() -> void:
	var a := _audio()
	_stage()
	var seq := _add(SeqStandIn.new()) as SeqStandIn
	a.watch(seq)
	a.watch(seq)
	seq.cue_played.emit(&"anim", [&"ysolde", &"vigil_book_shut"], {})
	assert_eq(_ids(), ["cs_book_shut"], "once, though watched twice")
	assert_true((played[0][1] as Vector3).is_equal_approx(Vector3(2.0, 1.1, 0.0)), "at Ysolde's hands")
	seq.cue_played.emit(&"anim", [&"rhen", &"look_at", &"asha"], {})
	seq.cue_played.emit(&"anim", [&"rhen", &"kneel_by_the_fire"], {})
	seq.cue_played.emit(&"anim", [&"rhen", &"laugh"], {})
	seq.cue_played.emit(&"anim", [&"rhen", &"some_new_clip"], {})
	seq.cue_played.emit(&"anim", [&"nobody", &"look_at"], {})
	assert_eq(_ids(), ["cs_book_shut", "cs_cloth_turn", "cs_cloth_kneel"], "a glob matches; '' and unknowns are silent")
	_done()


func test_a_lantern_catches_and_is_snuffed_only_when_lit() -> void:
	var a := _audio()
	var scene := _host()
	var light := OmniLight3D.new()
	light.name = "LanternLight"
	light.position = Vector3(1.0, 1.5, 0.0)
	light.light_energy = 0.0
	_add(light)
	var seq := _add(SeqStandIn.new()) as SeqStandIn
	a.watch(seq)
	assert_true(scene.find_child("LanternLight", true, false) == light, "the light is in the scene")
	seq.cue_played.emit(&"light", [&"LanternLight", &"off"], {})
	assert_eq(played, [], "already dark: nothing to put out (the prologue's first cue)")
	seq.cue_played.emit(&"light", [&"LanternLight", &"on", 1.4], {})
	assert_eq(_ids(), ["cs_lantern_catch"], "the burner catches")
	assert_true((played[0][1] as Vector3).is_equal_approx(light.global_position), "at the lantern")
	light.light_energy = 1.0
	seq.cue_played.emit(&"light", [&"LanternLight", &"off"], {})
	assert_eq(_ids(), ["cs_lantern_catch", "cs_lantern_snuff"])
	seq.cue_played.emit(&"light", [&"Sun", &"on"], {})
	assert_eq(played.size(), 2, "a light without a row is silent")
	_done()


func test_vfx_cues_play_at_their_place_and_a_skip_is_silent() -> void:
	var a := _audio()
	_stage()
	var seq := _add(SeqStandIn.new()) as SeqStandIn
	a.watch(seq)
	seq.cue_played.emit(&"vfx", [&"glimmer_lift"], {"at": "by_asha", "count": 12})
	assert_eq(_ids(), ["cs_glimmer_lift"])
	assert_true((played[0][1] as Vector3).is_equal_approx(Vector3(0.0, 0.0, 4.0)), "at the mark")
	seq.skipping = true
	seq.cue_played.emit(&"vfx", [&"glimmer_held"], {"at": "by_asha"})
	seq.cue_played.emit(&"anim", [&"ysolde", &"vigil_book_shut"], {})
	assert_eq(played.size(), 1, "nothing while the scene is skipped")
	_done()


func test_the_director_gives_the_cast_their_own_steps() -> void:
	var dir := AudioDirector.new()
	_add(dir)
	dir.setup(AudioData.table(AudioData.MIX), AudioData.table(AudioData.MUSIC), {"sfx": AudioData.sfx_rows()})
	dir.set_process(false)
	dir.footstep_data = (AudioData.table(AudioData.FOOTSTEPS) as Dictionary).duplicate(true)
	dir.zone_path = PROLOGUE
	var stage := _stage()
	dir.attach_cast(stage)
	var cast := stage.cast()
	assert_eq(cast.size(), 2, "both actors")
	for actor: Node3D in cast:
		assert_true(dir.listeners.has(actor) and dir.listeners[actor] is FootstepAudio, "%s steps" % actor.name)
	var steps: Array = []
	var l := dir.listeners[cast[0]] as FootstepAudio
	l.player = func(id: StringName, _at: Vector3, _opts: Dictionary) -> void: steps.append(id)
	for i in 180:  # Ysolde walks 3 m at 1 m/s
		cast[0].position.z += DT
		l.advance(DT)
	assert_true(
		steps.filter(func(id: StringName) -> bool: return String(id).begins_with("hero_step_")).size() >= 4,
		"a cutscene walk steps (%d)" % steps.size()
	)
	dir.attach_cast(stage)
	assert_eq(dir.get_children().filter(func(n: Node) -> bool: return n is FootstepAudio).size(), 2, "once each")
	_done()


func test_the_prologue_plays_its_room_tone() -> void:
	var dir := AudioDirector.new()
	_add(dir)
	dir.setup(
		AudioData.table(AudioData.MIX),
		AudioData.table(AudioData.MUSIC),
		{"sfx": AudioData.sfx_rows()},
		AudioData.table(AudioData.AMBIENCE)
	)
	dir.set_process(false)
	dir.flag_reader = func(_f: StringName) -> bool: return false
	dir.apply_zone(PROLOGUE)
	dir.flush_pending()
	assert_true(
		dir.beds.has(&"iskarra_dusk") and (dir.beds[&"iskarra_dusk"] as FadeVoice).target == 1.0,
		"Iskarra's dusk fades in"
	)
	var stream := (
		(dir.beds[&"iskarra_dusk"] as FadeVoice).player.stream as AudioStreamOggVorbis
		if dir.beds.has(&"iskarra_dusk")
		else null
	)
	assert_true(stream != null and stream.loop, "it loops")
	_done()


func test_a_lit_lamp_crackles_at_the_lamp_and_a_dark_one_is_silent() -> void:
	var a := _audio()
	var stage := _stage()
	var lamp := OmniLight3D.new()
	lamp.name = "LanternLight"
	lamp.position = Vector3(1.0, 1.2, 0.0)
	stage.get_node("Actors/rhen").add_child(lamp)
	var other := OmniLight3D.new()
	other.name = "KeyLight"
	stage.add_child(other)
	a.watch_lamps(stage)
	a.watch_lamps(stage)
	assert_eq(a.lamps.size(), 1, "only the named lamp, once")
	for i in int(20.0 / DT):
		a.advance(DT)
	var crackles := _ids().filter(func(id: String) -> bool: return id == "cs_lamp_crackle")
	assert_between(crackles.size(), 8, 34, "every 0.6-2.2 s over 20 s (%d)" % crackles.size())
	assert_eq(played.size(), crackles.size(), "nothing else")
	assert_true((played[0][1] as Vector3).is_equal_approx(lamp.global_position), "at the lamp")
	played.clear()
	lamp.light_energy = 0.0
	for i in int(5.0 / DT):
		a.advance(DT)
	assert_eq(played.size(), 0, "a dark lamp is silent")
	lamp.free()
	a.advance(DT)
	assert_eq(a.lamps.size(), 0, "a freed lamp is dropped")
	_done()


func test_the_prologue_stage_has_rhens_lamp() -> void:
	var zone := (load(PROLOGUE) as PackedScene).instantiate()
	_add(zone)
	var a := _audio()
	var stages := zone.find_children("*", "CutsceneStage", true, false)
	assert_true(stages.size() > 0, "the prologue has a cutscene stage")
	for s in stages:
		a.watch_lamps(s)
	assert_eq(a.lamps.size(), 1, "Rhen's lantern (LanternLight) is watched")
	_done()

extends TestCase
## M3-C09-02: Ch9 "The Ebbing", the end of Act I, end to end, headless, on the real chapter data
## (game/data/flow/chapters/ch09.json) and the greybox zone ch09/corrow_night: the strand's own entry
## (Ch8 isn't built) → B01 (the chapter becomes 9) → the barks and Toma → the raft's landing → the
## Ebbing (B03 the gilt line, three held movements, B06 the stair, B08 Pell) → the zone at dawn → B09
## the road out → B10 the Iskarra vigil → B11 the act card → the end card (Act II's stand-in). Instant
## sequencers; every hand-off is recorded through ZoneStory.hand_off.
## Also the chapter's watches (act1_ch09.md §0): every mote held, down and seaward, nothing lifting;
## the Ebbing's held input can't fail; Kerrid's cutaway is one shot, alone, with no mote or glow toward
## him; "Somebody's still below." with Asha off frame; Pell's first words; the side scene; the VO.

const ZONE := "res://game/levels/ch09/corrow_night/corrow_night.tscn"
const ZONE_ID := &"ch09/corrow_night"
const END_CARD := "res://game/flow/end_card.tscn"
const SAVE_DIR := "user://test_ch09_thread_saves"
const CH09_DLG := "res://game/data/dialogue/ch09"
const DIALOGUE_DIR := "res://game/data/dialogue"
const COMPILED := "res://game/data/dialogue/compiled/%s.json"
const DIALOGUE_CSV := "res://game/data/loc/dialogue.csv"
const SEQUENCER_JSON := "res://game/data/cutscene/sequencer.json"
const EBBING := "ch09_the_ebbing"
const ROAD := "ch09_the_road_out"
const STAIR_NODE := "ch09_the_stair"
const AFTER_STAIR_NODE := "ch09_ebb_letting_down"
## act1_ch09.md rule 6: Pell's first spoken words in the game.
const PELL_FIRST := "Beautiful. And pointing the wrong way."
## B10, the sheet's recommended line (Narrative's first choice).
const VIGIL_VO := "Seven of us walked out of Corrow that morning. I didn't count us then. I count us every night now."
const BELOW := &"ch09_road_004"
## The Ebbing's three movements (B04, B05, B07).
const MOVEMENTS := 3
## Chapter folders that come before Ch9 in the story: Pell says nothing in any of them.
const EARLIER_DIRS: Array[String] = ["prologue", "ch01", "ch02", "ch03", "ch04", "ch05", "ch06", "ch07", "ch08"]
## The no-fail drive: one frame, how long the player sits at a gate without holding, and a cap.
const TICK_SEC := 0.1
const IDLE_AT_GATE_SEC := 120.0
const MAX_TICKS := 20000
## Rhen's walk-in line at dawn: who forms the line on the road (D03), Kerrid last.
const LINE_WALKERS: Array[StringName] = [&"toma", &"pell", &"asha", &"ysolde", &"liss", &"rhen"]
const STAGING_WARNINGS: Array[String] = ["no shot", "no mark", "no actor", "cannot place", "no look_at"]

var saved_state: GameStateData
var saved_dir := ""
var zone: Ch09Zone
var story: ZoneStory
var hand_offs: Array[Array] = []
var lines: Array[StringName] = []
var overheard: Array[StringName] = []
## line id -> speaker id, for every line the main sequencer showed.
var speakers: Dictionary = {}
## Every @vfx cue played: [effect, kwargs].
var vfx: Array[Array] = []
var restore_at_line: Dictionary = {}
var warnings: Array[String] = []
var shot := &""
## At "Somebody's still below.": the shot and whether Asha was in it.
var below_shot := &""
var asha_in_below_frame := true


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	saved_dir = SaveSystem.save_dir
	SaveSystem.save_dir = SAVE_DIR
	hand_offs.clear()
	lines.clear()
	overheard.clear()
	speakers.clear()
	vfx.clear()
	restore_at_line.clear()
	warnings.clear()
	shot = &""
	below_shot = &""
	asha_in_below_frame = true


func test_ch9_plays_from_the_strand_to_the_end_card() -> void:
	var reg := LocationRegistry.load_default()
	assert_true(reg.is_playable(ZONE_ID), "the strand is reachable from its own location too")
	assert_eq(reg.spawn_of(ZONE_ID), &"Strand", "where Ch8 hands off")
	_strand()
	_the_ebbing()
	_dawn()
	_road_out_and_act_break()
	_check_staging()
	_done()


func test_shield_mate_side_scene_and_its_choice() -> void:
	for answer: int in [0, 1]:
		Game.state = GameStateData.new()
		for f: StringName in [&"ch09_started", &"ch08_met_ivo"]:
			Game.set_flag(f)
		lines.clear()
		_open()
		story.sequencer.auto_choice = answer
		assert_true(_trigger(&"toma").try_interact())
		assert_true(&"ch09_shield_001" in lines, "'I tied all of his.'")
		assert_true(&"ch09_shield_005" in lines, "'Another camp. Another year.' and nothing more of the shoals")
		assert_true(&"ch09_shield_006" in lines, "'Be level.'")
		assert_true(&"ch09_shield_012" in lines, "'I'll take him first.'")
		assert_true(bool(Game.get_flag(&"ch09_toma_knelt_with_ivo")))
		assert_eq(bool(Game.get_flag(&"ch09_rhen_answered_toma")), answer == 0, "'And still.' only if Rhen says it")
		assert_eq(&"ch09_shield_010" in lines, answer == 1, "Toma answers for the dead man himself")
		assert_false(&"ch09_toma_002" in lines, "no Kerrid question while the side scene is open")
		# Asked again, Toma has nothing more for Ivo: Rhen asks after Kerrid, and nobody looks for him.
		assert_true(_trigger(&"toma").try_interact())
		assert_eq(lines.back(), &"ch09_toma_002", "'Not since the stair.'")
		_close()
	_done()


func test_ch8_flags_pay_off() -> void:
	for f: StringName in [&"ch09_started", &"ch08_fed_the_beacon", &"ch08_hoist_cut_down"]:
		Game.set_flag(f)
	_open()
	assert_true(_trigger(&"npc_liss").try_interact(), "Liss on her cut rope")
	assert_eq(lines.back(), &"ch09_bark_liss_001", "'Thirty-one baskets.'")
	assert_true(_trigger(&"landing").on_touched())
	assert_true(&"ch09_wrong_way_014" in lines, "Fenn: 'Your mother danced for our drowned too.'")
	assert_false(&"ch09_wrong_way_015" in lines, "and not Hobb")
	_close()
	_done()


## Rule 1: every mote in Ch9 is held and drifts down and seaward; nothing rises, turns gold or is released.
func test_every_mote_is_held_down_and_seaward() -> void:
	var cues := 0
	for path in _dlg_files(CH09_DLG):
		for raw in FileAccess.get_file_as_string(path).split("\n"):
			var ln := raw.strip_edges()
			if not ln.begins_with("@vfx"):
				continue
			cues += 1
			assert_true(ln.begins_with("@vfx glimmer_held "), "%s: held motes only: %s" % [path.get_file(), ln])
			assert_true(ln.contains("drift=down_seaward"), "%s: drifting down and seaward: %s" % [path.get_file(), ln])
			assert_false(ln.contains("motion="), "%s: no spiral, nothing rising: %s" % [path.get_file(), ln])
	assert_true(cues > 0, "the chapter has its motes")
	var row: Dictionary = (_json(SEQUENCER_JSON).get("vfx", {}) as Dictionary).get("glimmer_held", {})
	var v: Array = row.get("velocity", [0, 0, 0])
	assert_true(float(v[1]) < 0.0, "the held placeholder sinks")
	assert_true(float(v[2]) > 0.0, "and drifts seaward (+Z, the harbour's south)")
	# No zone code lets the light go either.
	for f in DirAccess.get_files_at("res://game/levels/ch09"):
		if f.ends_with(".gd"):
			assert_false(FileAccess.get_file_as_string("res://game/levels/ch09".path_join(f)).contains("release("))
	_done()


## Rule 2 (ADR 0022 (f)): B06 is one shot, cut in and cut out; Kerrid alone on the stair; no mote turns
## toward him and nothing glows on him.
func test_kerrid_cutaway_is_one_shot_alone() -> void:
	var nodes: Dictionary = _json(COMPILED % EBBING).get("nodes", {})
	var stair: Array = (nodes.get(STAIR_NODE, {}) as Dictionary).get("ops", [])
	var shots: Array[String] = []
	var actors := {}
	for op: Dictionary in stair:
		assert_ne(str(op.get("op", "")), "line", "nobody speaks on the stair")
		if op.get("cue", "") == "camera":
			shots.append(str(op["args"][0]))
			assert_false((op.get("kwargs", {}) as Dictionary).has("blend"), "a cut in")
		elif op.get("cue", "") in ["anim", "mark", "face"]:
			actors[str(op["args"][0])] = true
	assert_eq(shots, ["N13"] as Array[String], "exactly one shot")
	assert_eq(actors.keys(), ["kerrid_stair"], "he is alone on the stair")
	var after: Array = (nodes.get(AFTER_STAIR_NODE, {}) as Dictionary).get("ops", [])
	for op: Dictionary in after:
		if op.get("cue", "") == "camera":
			assert_false((op.get("kwargs", {}) as Dictionary).has("blend"), "and a cut out")
			break
	# The motes over the wall-head start seaward of him and the held drift carries them further off.
	_open()
	var ks: Array[float] = [zone.stage.actor(&"kerrid_stair").position.z, zone.stage.mark(&"stair_climb").position.z]
	for op: Dictionary in stair:
		if op.get("cue", "") == "vfx":
			var at := str((op.get("kwargs", {}) as Dictionary).get("at", ""))
			assert_false(at.begins_with("kerrid"), "no mote is aimed at him")
			var m := zone.stage.mark(StringName(at))
			assert_true(m != null, "the motes are over the wall-head")
			if m != null:
				assert_true(m.position.z > ks.max(), "the river passes seaward, behind and beyond him")
	_close()
	# Nowhere in Ch9 does a mote or a glow go to him.
	for path in _dlg_files(CH09_DLG):
		for raw in FileAccess.get_file_as_string(path).split("\n"):
			var ln := raw.strip_edges()
			if ln.begins_with("@vfx"):
				assert_false(ln.contains("at=kerrid"), "%s: no @vfx at Kerrid: %s" % [path.get_file(), ln])
			assert_false(ln.begins_with("@anim kerrid") and ln.contains("glow"), "no rope-burn glow: %s" % ln)
	# And he is absent from the Ebbing and B08: no line from him.
	for n: Variant in nodes:
		for op: Dictionary in (nodes[n] as Dictionary).get("ops", []):
			assert_false(op.get("op", "") == "line" and op.get("speaker", "") == "kerrid", "Kerrid is absent (%s)" % n)
	_done()


## Rule 6: Pell's first spoken words in the game, exactly, and nothing from him in any earlier chapter.
func test_pell_first_words_are_the_mandated_line() -> void:
	for dir_name in EARLIER_DIRS:
		for path in _dlg_files(DIALOGUE_DIR.path_join(dir_name)):
			var scene := path.get_file().get_basename()
			for op: Dictionary in _ops(scene):
				assert_false(
					op.get("op", "") == "line" and op.get("speaker", "") == "pell", "Pell silent in %s" % scene
				)
	var first: Dictionary = {}
	for op: Dictionary in _ops(EBBING):
		if op.get("op", "") == "line" and op.get("speaker", "") == "pell":
			first = op
			break
	assert_eq(_text(str(first.get("key", ""))), PELL_FIRST, "Pell's first line is the mandated one")
	_done()


## B04-B07: the Ebbing's held input is a pause, never a fail. Played in real (driven) time: at each
## gate the dance waits for as long as the player waits; holding moves it on; letting go mid-way only
## pauses it; and the scene always reaches its end.
func test_the_ebbing_cannot_fail() -> void:
	Game.set_flag(&"ch09_started")
	_open()
	story.sequencer.instant = false
	story.sequencer.auto_advance = true
	story.sequencer.set_process(false)
	var gate := zone.hold_gate
	story.play_beat(&"ebbing")
	var ticks := 0
	var idled := 0
	var flip := false
	while story.sequencer.is_playing() and ticks < MAX_TICKS:
		ticks += 1
		zone.director.update(TICK_SEC)
		if not gate.gating:
			# Lines reveal on the box's own frames: in a driven test they are shown whole.
			if story.sequencer.overlay.box.is_revealing():
				story.sequencer.overlay.box.skip_reveal()
			story.sequencer.advance(TICK_SEC)
			continue
		if gate.held_sec <= 0.0 and idled < int(IDLE_AT_GATE_SEC / TICK_SEC):
			# Sitting at the gate without holding: nothing moves, nothing fails, nothing hands off.
			idled += 1
			assert_false(gate.tick(TICK_SEC, false))
			continue
		if idled >= int(IDLE_AT_GATE_SEC / TICK_SEC):
			assert_true(story.sequencer.is_playing(), "after two minutes unheld the dance still waits")
			assert_true(gate.gating)
			assert_false(bool(Game.get_flag(&"ch09_ebbing_danced")), "and nothing has moved on")
			assert_eq(hand_offs.size(), 0)
			idled = 0
		# Hold and let go in turns: the time held adds up and never resets.
		flip = not flip
		var before := gate.held_sec
		var gate_no := gate.gates
		var moved := gate.tick(TICK_SEC, flip)
		assert_eq(moved, flip, "the dance moves only while the staff is held")
		if gate.gates == gate_no and gate.gating:
			assert_true(gate.held_sec >= before, "letting go never takes progress away")
		elif not flip:
			fail("a gate closed while nothing was held")
	assert_true(ticks < MAX_TICKS, "the Ebbing reaches its end")
	assert_eq(gate.gates, MOVEMENTS, "three movements, three held inputs")
	assert_false(gate.gating, "no gate is left open")
	assert_true(story.sequencer.is_processing() == false, "the sequencer's processing is given back as it was")
	assert_true(bool(Game.get_flag(&"ch09_ebbing_danced")), "B07 always completes")
	assert_true(bool(Game.get_flag(&"ch09_pell_joined")), "and B08 follows")
	_close()
	_done()


func _strand() -> void:
	_open()
	story.begin()
	assert_eq(Game.state.chapter, 9, "B01 moves the story to chapter 9")
	assert_true(bool(Game.get_flag(&"ch09_started")))
	assert_eq(Game.state.party_ids, [&"rhen", &"asha", &"toma"] as Array[StringName])
	assert_eq(Game.state.reserve_ids, [&"kerrid", &"ysolde"] as Array[StringName])
	assert_false(&"pell" in Game.state.party_ids or &"pell" in Game.state.reserve_ids, "Pell has no battle row")
	assert_true(_at(&"Strand"))
	assert_true(SaveSystem.has_pending_autosave(), "the chapter autosave")
	SaveSystem.cancel_pending_autosave()
	assert_eq(lines.size(), 0, "B01 opens on the dead, without a word")
	assert_true(vfx.size() > 0, "the held motes hang over the low town and the strand")
	# act1_gpu_qa row 39 (the Lead, 10-30): on the night strand Asha and Toma follow Rhen; their stage bodies wait hidden
	# until a scene shows them (Toma's talk by the fire, the ebbing).
	var party := zone.player.get_node_or_null(NodePath(String(HeroFieldParty.NAME))) as HeroFieldParty
	for id: StringName in [&"asha", &"toma"]:
		assert_false(zone.stage.actor(id).visible, "%s's stage body is off on the strand" % id)
		assert_true(party == null or not party.staged(id), "%s follows Rhen on the strand" % id)

	assert_true(_trigger(&"npc_marra").try_interact())
	assert_true(&"ch09_bark_marra_003" in lines, "'Not while there's anyone below.'")
	assert_true(bool(Game.get_flag(&"ch09_heard_stair_clear")))
	assert_false(_trigger(&"npc_liss").is_available(), "Liss's bark needs Ch8's cut rope")
	assert_true(_trigger(&"hobb_overheard").on_touched())
	assert_true(&"ch09_bark_hobb_001" in overheard, "Hobb reads the names, overheard")
	assert_true(_trigger(&"stillguard_overheard").on_touched())
	assert_true(&"ch09_bark_stillguard_001" in overheard, "'a wider stair'")
	assert_true(_trigger(&"toma").try_interact())
	assert_eq(lines.back(), &"ch09_toma_002", "without Ch8's Ivo, Toma is asked after Kerrid: 'Not since the stair.'")
	assert_false(bool(Game.get_flag(&"ch09_toma_knelt_with_ivo")))
	assert_false(zone.stage.actor(&"toma").visible, "after the talk his body goes and he follows again")
	assert_false(_trigger(&"milestone").is_available(), "the road waits for dawn")


func _the_ebbing() -> void:
	var before := lines.size()
	assert_true(_trigger(&"landing").on_touched())
	var played := lines.slice(before)
	assert_true(&"ch09_gilt_001" in played, "Ysolde: 'They follow the light, not you. Let them.'")
	assert_eq(zone.hold_gate.gates, MOVEMENTS, "three movements, each a held input")
	assert_false(zone.hold_gate.gating)
	assert_true(bool(Game.get_flag(&"ch09_ebbing_danced")), "B07")
	assert_true(&"ch09_wrong_way_003" in played, "'They didn't want to go, Rhen.'")
	assert_true(bool(Game.get_flag(&"ch09_asha_said_they_hung_back")))
	var pell_lines: Array[StringName] = []
	for id in played:
		if speakers.get(id, &"") == &"pell":
			pell_lines.append(id)
	assert_eq(pell_lines.front() if not pell_lines.is_empty() else &"", &"ch09_wrong_way_004", "Pell speaks first here")
	assert_true(&"ch09_wrong_way_012" in played, "'...Walk behind me, then.'")
	assert_true(bool(Game.get_flag(&"ch09_pell_joined")))
	assert_true(&"ch09_wrong_way_015" in played, "without the beacon, Hobb tells Asha of the last Cantor")
	assert_false(&"kerrid" in speakers.values(), "Kerrid says nothing tonight")
	assert_eq(hand_offs.back(), [ZoneStory.KIND_GO, {"location": String(ZONE_ID), "spawn": "RoadGate"}], "dawn")
	assert_false(restore_at_line.get(played.back(), true), "the night hands off on black")
	for row: Array in vfx:
		assert_eq(row[0], &"glimmer_held", "held motes only")
		assert_eq(str((row[1] as Dictionary).get("drift", "")), "down_seaward", "every mote goes down and seaward")
	assert_false(_trigger(&"landing").is_available(), "the Ebbing is danced once")


func _dawn() -> void:
	_reopen(&"RoadGate")
	assert_eq(lines.size(), 0, "no scene at the gate")
	assert_true(_at(&"RoadGate"))
	assert_true(zone.stage.actor(&"kerrid").visible, "Kerrid is waiting at the milestone")
	assert_true(zone.stage.actor(&"kerrid").position.distance_to(zone.stage.mark(&"milestone").position) < 0.01)
	assert_false(zone.stage.actor(&"kerrid_stair").visible, "the stair is empty by day")
	# act1_gpu_qa row 39: the party walks the road with Rhen; their stage bodies hand over to the followers.
	var party := zone.player.get_node_or_null(NodePath(String(HeroFieldParty.NAME))) as HeroFieldParty
	for id: StringName in [&"asha", &"toma"]:
		assert_false(zone.stage.actor(id).visible, "%s's stage body is off: the follower walks with Rhen" % id)
		assert_true(party == null or not party.staged(id), "%s follows Rhen up the road" % id)
	assert_false(_trigger(&"toma").is_available(), "the strand's prompts are over")


func _road_out_and_act_break() -> void:
	assert_true(_trigger(&"milestone").on_touched())
	for id: StringName in [&"asha", &"toma"]:
		assert_true(zone.stage.actor(id).visible, "%s is staged again for the road scene" % id)
	assert_true(&"ch09_road_002" in lines, "'It was.'")
	assert_true(BELOW in lines, "'Somebody's still below.'")
	assert_eq(speakers.get(BELOW, &""), &"kerrid")
	assert_eq(below_shot, &"D02", "the line is Kerrid's single")
	assert_false(asha_in_below_frame, "Asha is off frame: 'below' never means her")
	assert_true(bool(Game.get_flag(&"ch09_pell_named")), "'Pell.'")
	assert_true(bool(Game.get_flag(&"ch09_kerrid_on_road")))
	# D03: Kerrid walks last, behind the whole line (the road heads east, +X).
	var kx := zone.stage.actor(&"kerrid").position.x
	for id in LINE_WALKERS:
		var a := zone.stage.actor(id)
		assert_true(a.position.x > kx, "%s walks ahead of Kerrid" % id)
	assert_eq(_text("DLG_CH09_VIGIL_001"), VIGIL_VO, "B10: the recommended VO")
	assert_true(&"ch09_vigil_001" in lines)
	assert_true(bool(Game.get_flag(&"ch09_act_one_complete")))
	# B11: the act card is a #card line (M2-FP-121): UI's ActCard on black, not a line in the box. Where the card
	# isn't supported yet it shows as the last line instead, and must still hand off on black.
	assert_true(lines.back() in [&"ch09_act_card_001", &"ch09_vigil_001"], "B11: the act card ends the scene")
	assert_eq(_text("DLG_CH09_ACT_CARD_001"), "Act II: The Truth")
	assert_eq(hand_offs.back(), [ZoneStory.KIND_SCENE, END_CARD], "the end card stands in for Ch10")
	if &"ch09_act_card_001" in lines:
		assert_false(restore_at_line.get(&"ch09_act_card_001", true), "it hands off on black")


func _open() -> void:
	zone = (load(ZONE) as PackedScene).instantiate() as Ch09Zone
	story = zone.story
	story.autostart = false
	_host().add_child(zone)
	zone.set_process(false)
	zone.hold_gate.set_process(false)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	zone.player.set_process_unhandled_input(false)
	zone.hint.instant = true
	story.active = true
	story.sequencer.instant = true
	story.overhear.instant = true
	story.sequencer.line_shown.connect(_on_line)
	story.overhear.line_shown.connect(func(s: DialogueStep) -> void: overheard.append(s.line_id))
	story.sequencer.cue_played.connect(_on_cue)
	story.hand_off = func(kind: StringName, target: Variant) -> void: hand_offs.append([kind, target])


func _on_line(s: DialogueStep) -> void:
	lines.append(s.line_id)
	speakers[s.line_id] = s.speaker
	restore_at_line[s.line_id] = story.sequencer.restore_fade
	if s.line_id == BELOW:
		below_shot = shot
		asha_in_below_frame = _in_frame(shot, zone.stage.actor(&"asha"))


func _on_cue(cue: StringName, args: Array, kwargs: Dictionary) -> void:
	if cue == &"camera" and not args.is_empty():
		shot = StringName(str(args[0]))
	elif cue == &"vfx" and not args.is_empty():
		vfx.append([StringName(str(args[0])), kwargs])


## True when `node` stands inside shot `id`'s view (its fov is vertical; the width is the project's).
func _in_frame(id: StringName, node: Node3D) -> bool:
	var s := zone.stage.shot(id)
	if s == null or node == null:
		return true
	var w := float(ProjectSettings.get_setting("display/window/size/viewport_width"))
	var h := float(ProjectSettings.get_setting("display/window/size/viewport_height"))
	var half_v := deg_to_rad(s.fov_deg * 0.5)
	var half_h := atan(tan(half_v) * w / h)
	var fwd := (s.look_at - s.position).normalized()
	var to := node.global_position - s.position
	var flat_fwd := Vector2(fwd.x, fwd.z).normalized()
	var flat_to := Vector2(to.x, to.z).normalized()
	return absf(flat_fwd.angle_to(flat_to)) <= half_h


## Opens the zone again where a hand-off left it (the router would), and runs its arrival.
func _reopen(spawn: StringName) -> void:
	_close()
	hand_offs.clear()
	lines.clear()
	_open()
	assert_true(zone.place_at(spawn, zone.spawn_yaw_deg(spawn)))
	story.begin()


func _close() -> void:
	if zone != null and is_instance_valid(zone):
		warnings.append_array(story.sequencer.warnings)
		_host().remove_child(zone)
		zone.free()
	zone = null


func _check_staging() -> void:
	for w in warnings:
		for needle in STAGING_WARNINGS:
			assert_false(w.contains(needle), "staged on this zone: %s" % w)


func _trigger(id: StringName) -> Interactable:
	for n in zone.find_children("*", "Interactable", true, false):
		if (n as Interactable).id == id:
			return n as Interactable
	fail("no trigger %s" % id)
	return Interactable.new()


func _at(spawn: StringName) -> bool:
	return zone.player.position.distance_to(zone.spawn_marker(spawn).position) < 0.01


## Every op of a compiled scene, node by node.
func _ops(scene: String) -> Array:
	var out: Array = []
	var nodes: Dictionary = _json(COMPILED % scene).get("nodes", {})
	for n: Variant in nodes:
		out.append_array((nodes[n] as Dictionary).get("ops", []))
	return out


## The English text of loc key `key` in dialogue.csv.
func _text(key: String) -> String:
	var f := FileAccess.open(DIALOGUE_CSV, FileAccess.READ)
	while f != null and not f.eof_reached():
		var row := f.get_csv_line()
		if row.size() > 1 and row[0] == key:
			return row[1]
	return ""


func _json(path: String) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return parsed if parsed is Dictionary else {}


func _dlg_files(dir: String) -> Array[String]:
	var out: Array[String] = []
	var d := DirAccess.open(dir)
	if d == null:
		return out
	for f in d.get_files():
		if f.ends_with(".dlg"):
			out.append(dir.path_join(f))
	for sub in d.get_directories():
		out.append_array(_dlg_files(dir.path_join(sub)))
	return out


func _done() -> void:
	_close()
	SaveSystem.cancel_pending_autosave()
	var dir := DirAccess.open(SAVE_DIR)
	if dir != null:
		for f in dir.get_files():
			DirAccess.remove_absolute(SAVE_DIR.path_join(f))
		DirAccess.remove_absolute(SAVE_DIR)
	SaveSystem.save_dir = saved_dir
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene

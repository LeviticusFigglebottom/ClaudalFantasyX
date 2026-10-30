extends TestCase
## M2-FP-14 on the real Haluna zone: B04 "Pila's Granddaughter" (Grandmother Osu at the causeway
## head, at the real wake-shell wall since M2-ENV-04, framed on H08 with an insert on the wall; it sets
## ch02_heard_pila, which B09's Teyo line reads), the B02 insert on Asha's packed bag, and H03, the
## lintel-gull look-at in the lane.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"
const PILA := &"ch02_pila_granddaughter"
const GULL := &"ch02_look_lintel_gull"

var zone: HalunaZone
var story: HalunaStory
var saved_state: GameStateData
var speakers: Array[StringName] = []
var lines: Array[StringName] = []
var shots: Array[StringName] = []


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	speakers.clear()
	lines.clear()
	shots.clear()
	zone = (load(ZONE) as PackedScene).instantiate() as HalunaZone
	story = zone.get_node("Story") as HalunaStory
	story.autostart = false
	_host().add_child(zone)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	zone.player.set_process_unhandled_input(false)
	story.active = true
	story.sequencer.instant = true
	story.sequencer.line_shown.connect(_on_line)
	story.sequencer.cue_played.connect(_on_cue)
	story.hand_off = func(_kind: StringName, _target: String) -> void: pass


func test_osu_waits_for_cutscene_a_then_tells_of_teyo_and_pila() -> void:
	var osu := _interactable(&"npc_osu")
	assert_true(osu != null, "Osu's prompt")
	assert_eq(osu.payload, {"dialogue": String(PILA)})
	assert_false(osu.is_available(), "not before Cutscene A")
	Game.set_flag(&"ch02_met_asha", true)
	# M4-A2P-115 A4: her causeway line waits for Neme's table (B02); she isn't there at dawn.
	assert_false(osu.is_available(), "not before Neme's table")
	Game.set_flag(&"ch02_ate_at_nemes", true)
	assert_true(osu.try_interact())
	assert_true(&"osu" in speakers and &"rhen" in speakers, "Osu and Rhen speak")
	assert_true(&"ch02_pila_granddaughter_005" in lines, "Teyo Marrin's shell")
	assert_true(&"ch02_pila_granddaughter_013" in lines, "to the end: 'To who?'")
	assert_eq(shots, [&"H08", &"H08_hand", &"H08"] as Array[StringName], "H08, the insert on her hand, H08")
	assert_true(bool(Game.get_flag(&"ch02_heard_pila")), "sets ch02_heard_pila")
	assert_false(story.busy)
	assert_true(zone.player.accepts_input, "free play again")
	_done()


func test_a_second_visit_is_one_short_line() -> void:
	Game.set_flag(&"ch02_met_asha", true)
	Game.set_flag(&"ch02_ate_at_nemes", true)
	Game.set_flag(&"ch02_heard_pila", true)
	assert_true(_interactable(&"npc_osu").try_interact())
	assert_eq(lines, [&"ch02_pila_granddaughter_015"] as Array[StringName])
	assert_eq(shots, [] as Array[StringName], "no camera for the short line")
	_done()


func test_b09_answers_with_teyo_once_osu_has_been_heard() -> void:
	Game.set_flag(&"ch02_met_asha", true)
	Game.set_flag(&"ch02_ate_at_nemes", true)
	assert_false(_reaches(&"ch03_the_first_verse", &"ch03_verse_034"), "no Teyo line before B04")
	_interactable(&"npc_osu").try_interact()
	assert_true(_reaches(&"ch03_the_first_verse", &"ch03_verse_034"), "B09's Teyo line after it")
	_done()


func test_osu_stands_on_dry_ground_clear_of_the_causeway_trigger() -> void:
	var body := zone.get_node("NPCs/Osu/Osu") as Node3D
	var p := body.global_position
	assert_true(zone.collision.covers(p.x, p.z), "inside the walk rect")
	var shore := zone.collision.shore_line[0]
	for s: Vector2 in zone.collision.shore_line:
		if absf(s.y - p.z) < absf(shore.y - p.z):
			shore = s
	var shore_x := shore.x
	assert_true(p.x < shore_x - 5.0, "landward of the sea wall (%.1f < %.1f)" % [p.x, shore_x])
	assert_between(p.y, zone.collision.ground_height(p.x, p.z) - 0.1, zone.collision.ground_height(p.x, p.z) + 0.1)
	var head := _interactable(&"causeway_head")
	var talk := _interactable(&"npc_osu")
	assert_false(head.contains_point(p), "Osu is outside the B05 trigger")
	assert_false(head.contains_point(talk.global_position), "and so is her prompt")
	# M2-ENV-04: the real wake-shell wall at the causeway head; Osu stands at its gap, H08 holds her
	# against it and the insert finds a shell on its face.
	var wall := _wake_wall_near(p)
	assert_true(wall != null, "a wake-shell wall at the causeway head")
	var face := wall.global_basis.z.normalized()  # the shell face looks along the piece's +Z
	var gap := wall.global_position + Vector3.UP * 1.45
	assert_between(Vector2(p.x, p.z).distance_to(Vector2(gap.x, gap.z)), 0.5, 1.0, "Osu stands at the gap")
	assert_true(face.dot((p - wall.global_position).normalized()) > 0.9, "in front of the shell face")
	var h08 := (zone.stage.get_node("Shots/H08") as CutsceneShotNode).shot
	var view := (h08.look_at - h08.position).normalized()
	assert_true(rad_to_deg(view.angle_to((gap - h08.position).normalized())) < h08.fov_deg * 0.5, "the wall in H08")
	var hand := (zone.stage.get_node("Shots/H08_hand") as CutsceneShotNode).shot
	var on_face := wall.global_transform.affine_inverse() * hand.look_at
	assert_between(on_face.y, 0.8, 1.6, "the insert at hand height on the wall")
	assert_between(Vector2(on_face.x, on_face.z).length(), 0.5, 1.5, "beside the gap, on the arc")
	_done()


func test_osu_and_the_bag_are_gone_at_night() -> void:
	var cfg := FirstPlayableConfig.section(FirstPlayableConfig.SECTION_HALUNA)
	zone.set_night(cfg.get("night", {}), cfg.get("night_hide", []))
	# Hidden and stopped, not freed (the VillagerLayer still holds them).
	for path: String in ["NPCs/Osu", "NPCs/Neme/Bag"]:
		var n := zone.get_node_or_null(path) as Node3D
		assert_true(n == null or (not n.is_visible_in_tree() and not n.can_process()), "%s is gone at night" % path)
	_done()


func test_nemes_table_cuts_to_the_bag_and_back() -> void:
	Game.set_flag(&"ch02_met_asha", true)
	Game.set_flag(&"ch02_tideline_won", true)
	story.begin()
	assert_eq(shots, [&"B02_bag", &"release"] as Array[StringName], "one insert, then the field camera")
	var bag := zone.get_node("NPCs/Neme/Bag") as Node3D
	var insert := (zone.stage.get_node("Shots/B02_bag") as CutsceneShotNode).shot
	var aim := (insert.look_at - insert.position).normalized()
	var to_bag := (bag.global_position - insert.position).normalized()
	assert_true(rad_to_deg(aim.angle_to(to_bag)) < 6.0, "the insert is on the bag")
	_done()


func test_the_lintel_gull_is_a_look_at_in_the_lane() -> void:
	var look := _interactable(&"look_lintel_gull")
	assert_true(look != null)
	assert_eq(look.prompt_key, "FIELD_PROMPT_LOOK")
	assert_eq(tr("FIELD_PROMPT_LOOK"), "Look")
	Game.set_flag(&"ch02_met_asha", true)
	assert_true(look.try_interact())
	assert_eq(shots, [&"H03"] as Array[StringName])
	assert_eq(lines, [&"ch02_look_lintel_gull_001"] as Array[StringName])
	var h03 := (zone.stage.get_node("Shots/H03") as CutsceneShotNode).shot
	var gull := _nearest_gull(h03.look_at)
	assert_true(gull != null and gull.global_position.distance_to(h03.look_at) < 1.0, "H03 is on a gull")
	_done()


func test_osu_is_a_speaker() -> void:
	var sp := DialogueSpeakers.load_default()
	assert_true(sp.has(&"osu"))
	assert_eq(tr("CHAR_OSU"), "Grandmother Osu")
	_done()


func _on_line(s: DialogueStep) -> void:
	speakers.append(s.speaker)
	lines.append(s.line_id)


func _on_cue(cue: StringName, args: Array, _kwargs: Dictionary) -> void:
	if cue == &"camera":
		shots.append(StringName(str(args[0])))


## True if `scene` reaches `line_id` with the game's flags, always taking the first option.
func _reaches(scene: StringName, line_id: StringName) -> bool:
	var runner := DialogueRunner.new(GameFlagAccess.new())
	runner.forward_events_to_bus = false
	runner.load_scene(scene)
	runner.start()
	for _i in 2000:
		var step := runner.next()
		if step.is_end():
			return false
		if step.line_id == line_id:
			return true
		if step.kind == DialogueStep.Kind.OPTIONS:
			runner.choose(0)
	return false


func _nearest_gull(at: Vector3) -> Node3D:
	var best: Node3D = null
	for n in zone.get_node("HalunaMood/Dresser").get_children():
		var g := n as Node3D
		if g != null and String(g.name).begins_with("lintel_gull"):
			if best == null or g.global_position.distance_to(at) < best.global_position.distance_to(at):
				best = g
	return best


## The dressed wake-shell wall nearest `p`, by its kind (its first mesh's name, as the collision builder
## reads it: Godot renames a duplicate sibling node, so the node name is no guide).
func _wake_wall_near(p: Vector3) -> Node3D:
	var best: Node3D = null
	for c in zone.get_node("HalunaMood/Dresser").get_children():
		var n := c as Node3D
		if n != null and HalunaCollision.piece_kind(n) == "wakeshell_wall":
			if best == null or n.global_position.distance_to(p) < best.global_position.distance_to(p):
				best = n
	return best


func _interactable(id: StringName) -> Interactable:
	for n in zone.find_children("*", "Interactable", true, false):
		if (n as Interactable).id == id:
			return n as Interactable
	return null


func _done() -> void:
	if zone != null:
		_host().remove_child(zone)
		zone.free()
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene

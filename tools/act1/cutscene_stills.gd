extends Node
## ADR 0041's playthrough stills (act1-chapters): walks each zone visit of a plan (tools/act1/cutscene_stills_plan.py) on
## one zone instance, running the flow's steps in order (set, zone calls, place, party, play), plays each cutscene in
## driven time and saves a still a moment after every camera cue, so the staging is viewed as the player meets it. Run it under the render wrapper (a scene, so the autoloads run):
##   STILLS_PLAN=<plan.json> STILLS_OUT=<dir> [STILLS_ONLY=<locations, comma-separated>] \
##     godot-render --path . res://tools/act1/cutscene_stills.tscn

const DT := 1.0 / 30.0
const SETTLE_SEC := 0.8  ## after a camera cue: blends, turns and walks under way
const RENDER_FRAMES := 4  ## real frames before a still, for shadows and the grade
const MAX_SEC := 240.0
const LINE_HOLD_SEC := 0.6
const PARTY: Array[StringName] = [&"rhen", &"asha", &"toma"]


func _ready() -> void:
	get_window().size = Vector2i(960, 540)
	_run.call_deferred()


func _run() -> void:
	var plan: Array = JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("STILLS_PLAN")))
	var out := OS.get_environment("STILLS_OUT")
	var only := OS.get_environment("STILLS_ONLY").split(",", false)
	DirAccess.make_dir_recursive_absolute(out)
	var n := 0
	for visit: Dictionary in plan:
		if not only.is_empty() and not only.has(str(visit["location"])):
			continue
		n = await _visit(visit, out, n)
	get_tree().quit()


## One zone visit: the first group's flags, the zone, then every group's flags and steps in order.
func _visit(visit: Dictionary, out: String, n: int) -> int:
	Game.state = GameStateData.new()
	Game.state.party_ids = PARTY.duplicate()
	var groups: Array = visit["groups"]
	for f: Variant in (groups[0] as Dictionary)["flags"]:
		Game.set_flag(StringName(str(f)))
	var zone := (load(str(visit["zone"])) as PackedScene).instantiate() as Node3D
	var story := zone.get(&"story") as ZoneStory if "story" in zone else null
	if story != null:
		story.autostart = false
	add_child(zone)
	for i in RENDER_FRAMES:
		await get_tree().process_frame
	for n2 in zone.find_children("*", "CharacterBody3D", true, false):
		if n2 is FieldController:
			(n2 as FieldController).set_physics_process(false)
			(n2 as FieldController).set_process_unhandled_input(false)
	var seq := CutsceneSequencer.new()  # one per visit (HeroFieldParty keeps the zone's sequencers)
	seq.instant = false
	seq.auto_advance = true
	seq.auto_advance_hold_sec = LINE_HOLD_SEC
	zone.add_child(seq)
	seq.set_process(false)
	for g: Dictionary in groups:
		for f: Variant in g["flags"]:
			Game.set_flag(StringName(str(f)))
		for step: Dictionary in g["steps"]:
			if step.has("set"):
				Game.set_flag(StringName(str(step["set"])))
			elif step.has("zone") and zone.has_method(StringName(str(step["zone"]))):
				zone.callv(StringName(str(step["zone"])), step.get("args", []))
			elif step.has("place") and zone.has_method(&"place_at"):
				zone.call(&"place_at", StringName(str(step["place"])))
			elif step.has("party"):
				var ids: Array[StringName] = []
				for id: Variant in (step["party"] as Dictionary).get("party", []):
					ids.append(StringName(str(id)))
				Game.state.party_ids = ids
			elif step.has("play"):
				n = await _play(zone, seq, StringName(str(step["play"])), out, n)
	zone.queue_free()
	await get_tree().process_frame
	return n


func _play(zone: Node3D, seq: CutsceneSequencer, scene_id: StringName, out: String, n: int) -> int:
	var stage := zone.get(&"stage") as CutsceneStage if "stage" in zone else null
	if stage == null:
		print("STILLS %s: no stage" % scene_id)
		return n
	var director := zone.get_node_or_null("CameraDirector") as FieldCameraDirector
	if director != null:
		director.auto_update = false  # driven: a camera blend advances with the sequence
	if OS.get_environment("STILLS_DEBUG") != "":
		for actor in stage.get_node("Actors").get_children():
			var a3 := actor as Node3D
			print(
				(
					"  ACTOR %s %s at %s"
					% [actor.name, a3.is_visible_in_tree(), a3.global_position.snapped(Vector3.ONE * 0.1)]
				)
			)
	var due: Array[Array] = []  # [frame to capture, shot name]
	var frame := [0]
	var on_cue := func(cue: StringName, args: Array, _kw: Dictionary) -> void:
		if cue == &"camera" and not args.is_empty():
			due.append([frame[0] + int(SETTLE_SEC / DT), str(args[0])])
	seq.cue_played.connect(on_cue)
	seq.play(scene_id, stage)
	var count := 0
	while seq.is_playing() and frame[0] * DT < MAX_SEC:
		if seq.overlay != null and seq.overlay.box.is_revealing():
			seq.overlay.box.skip_reveal()
		if director != null:
			director.update(DT)
		seq.advance(DT)
		frame[0] += 1
		while not due.is_empty() and frame[0] >= int(due[0][0]):
			var shot: String = due.pop_front()[1]
			for i in RENDER_FRAMES:
				await get_tree().process_frame
			var img := get_viewport().get_texture().get_image()
			img.save_png("%s/%03d_%s__%s.png" % [out, n, scene_id, shot])
			n += 1
			count += 1
	print("STILLS %s: %d stills, %.0f s%s" % [scene_id, count, frame[0] * DT, " (cap)" if seq.is_playing() else ""])
	seq.cue_played.disconnect(on_cue)
	if director != null:
		director.auto_update = true
	return n

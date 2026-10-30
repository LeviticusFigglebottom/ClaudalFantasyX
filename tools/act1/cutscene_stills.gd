extends Node
## ADR 0041's playthrough stills (act1-chapters): walks each zone visit of a plan
## (tools/act1/cutscene_stills_plan.py) on one zone instance, running the flow's steps in order (set, zone calls,
## place, party, play), plays each cutscene in driven time and saves a still a moment after every camera cue, so the
## staging is viewed as the player meets it (STILLS_EVERY adds one every s seconds: how a long hold plays). Run it
## under the render wrapper (a scene, so the autoloads run); STILLS_TIMING=1 saves none and runs headless, printing each
## scene's length and any TAIL (seconds held after its last step while walks and turns finish):
##   STILLS_PLAN=<plan.json> STILLS_OUT=<dir> [STILLS_ONLY=<locations, comma-separated>] [STILLS_EVERY=<s>] \
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
		n = (n / 1000 + 1) * 1000  # each visit's stills sort together
	get_tree().quit()


## One zone visit: its groups in order on one zone, as the story walks through them (actors stay where the last
## scene left them). An arrive row (the zone loading), or a group the story state contradicts (a flag it needs unset
## is set), gets a fresh zone with the story's flags so far (less the ones it needs unset), as a reload would.
func _visit(visit: Dictionary, out: String, n: int) -> int:
	var zone: Node3D = null
	var seq: CutsceneSequencer = null
	var opened := false
	for g: Dictionary in visit["groups"]:
		var stale := zone == null or bool(g.get("arrive", false))  # an arrive row is the zone loading
		for f: Variant in g.get("unset", []):
			stale = stale or Game.get_flag(StringName(str(f)))
		if stale:
			if zone != null:
				zone.queue_free()
				await get_tree().process_frame
			if not opened:  # the visit's start; later loads keep the story's flags so far (the plan is in story order)
				opened = true
				Game.state = GameStateData.new()
				Game.state.party_ids = PARTY.duplicate()
			for f: Variant in g.get("unset", []):
				Game.set_flag(StringName(str(f)), false)
			for f: Variant in g["flags"]:
				Game.set_flag(StringName(str(f)))
			zone = await _open(str(visit["zone"]))
			seq = CutsceneSequencer.new()  # one per zone (HeroFieldParty keeps the zone's sequencers)
			seq.instant = false
			seq.auto_advance = true
			seq.auto_advance_hold_sec = LINE_HOLD_SEC
			zone.add_child(seq)
			seq.set_process(false)
		for f: Variant in g["flags"]:
			Game.set_flag(StringName(str(f)))
		for step: Dictionary in g["steps"]:
			if step.has("set"):
				Game.set_flag(StringName(str(step["set"])))
			elif step.has("zone") and zone.has_method(StringName(str(step["zone"]))):
				zone.callv(StringName(str(step["zone"])), step.get("args", []))
			elif step.has("reload"):  # the flow's go to this same zone: a fresh load with the flags as they are
				zone.queue_free()
				await get_tree().process_frame
				zone = await _open(str(visit["zone"]))
				seq = CutsceneSequencer.new()
				seq.instant = false
				seq.auto_advance = true
				seq.auto_advance_hold_sec = LINE_HOLD_SEC
				zone.add_child(seq)
				seq.set_process(false)
				if str(step["reload"]) != "" and zone.has_method(&"place_at"):
					zone.call(&"place_at", StringName(str(step["reload"])))
			elif step.has("stand") and "player" in zone:
				var at: Array = step["stand"]
				(zone.get(&"player") as Node3D).global_position = Vector3(float(at[0]), float(at[1]), float(at[2]))
			elif step.has("place") and zone.has_method(&"place_at"):
				zone.call(&"place_at", StringName(str(step["place"])))
			elif step.has("party"):
				var ids: Array[StringName] = []
				var party: Variant = step["party"]  # {party, reserve} or a bare list
				for id: Variant in (party as Dictionary).get("party", []) if party is Dictionary else party:
					ids.append(StringName(str(id)))
				Game.state.party_ids = ids
			elif step.has("play"):
				n = await _play(zone, seq, StringName(str(step["play"])), out, n)
	if zone != null:
		zone.queue_free()
		await get_tree().process_frame
	return n


func _open(path: String) -> Node3D:
	var zone := (load(path) as PackedScene).instantiate() as Node3D
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
	return zone


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
	var shot_now := [""]
	var every := int(float(OS.get_environment("STILLS_EVERY")) / DT) if OS.get_environment("STILLS_EVERY") != "" else 0
	var timing_only := OS.get_environment("STILLS_TIMING") != ""  # no stills: the STILLS and TAIL lines only (headless)
	var dumped := [false]
	var script_end := [0.0]  # when the script's last step is done (its wait or fade run out); the rest is a tail
	var on_cue := func(cue: StringName, args: Array, _kw: Dictionary) -> void:
		var hold := 0.0
		if cue == &"wait" and not args.is_empty():
			hold = float(args[0])
		elif cue == &"fade" and args.size() > 1:
			hold = float(args[1])
		script_end[0] = frame[0] * DT + hold
		if cue == &"camera" and not args.is_empty():
			shot_now[0] = str(args[0])
			if not timing_only:
				due.append([frame[0] + int(SETTLE_SEC / DT), str(args[0])])
	var on_line := func(_step: DialogueStep) -> void: script_end[0] = frame[0] * DT + 1.5
	seq.cue_played.connect(on_cue)
	seq.line_shown.connect(on_line)
	seq.play(scene_id, stage)
	var count := 0
	while seq.is_playing() and frame[0] * DT < MAX_SEC:
		if seq.overlay != null and seq.overlay.box.is_revealing():
			seq.overlay.box.skip_reveal()
		if director != null:
			director.update(DT)
		seq.advance(DT)
		for card in seq.find_children("*", "", true, false):  # M2-FP-121's time cards step in _process: drive them
			if card.has_method(&"advance") and card.has_method(&"show_caption"):
				card.call(&"advance", DT)
		frame[0] += 1
		if timing_only and frame[0] * DT > float(script_end[0]) + 3.0 and frame[0] % 300 == 0:
			var live: Array[String] = []
			for key: StringName in seq.get(&"_motions"):
				var lm: Dictionary = seq.get(&"_motions")[key]
				live.append("%s %.0f/%.0f" % [key, float(lm["elapsed"]), float(lm["duration"])])
			print("  AWAIT %s %.0f s: %s %s" % [scene_id, frame[0] * DT, seq.get(&"_awaiting"), ", ".join(live)])
		if timing_only and not dumped[0] and frame[0] * DT > float(script_end[0]) + 0.5:
			dumped[0] = true  # what the sequencer still waits on once the script is done
			var motions: Dictionary = seq.get(&"_motions")
			for key: StringName in motions:
				var m: Dictionary = motions[key]
				if float(m["duration"]) - float(m["elapsed"]) > 1.0:
					print("  MOTION %s %s %.1f s left" % [scene_id, key, float(m["duration"]) - float(m["elapsed"])])
		if every > 0 and not timing_only and frame[0] % every == 0 and shot_now[0] != "":
			due.append([frame[0], "%s_t%03d" % [shot_now[0], roundi(frame[0] * DT)]])
		while not due.is_empty() and frame[0] >= int(due[0][0]):
			var shot: String = due.pop_front()[1]
			for i in RENDER_FRAMES:
				await get_tree().process_frame
			var img := get_viewport().get_texture().get_image()
			img.save_png("%s/%04d_%s__%s.png" % [out, n, scene_id, shot])
			if OS.get_environment("STILLS_DEBUG") != "":
				for actor in stage.get_node("Actors").get_children():
					if (actor as Node3D).is_visible_in_tree():
						print(
							(
								"  %04d %s at %s"
								% [n, actor.name, (actor as Node3D).global_position.snapped(Vector3.ONE * 0.1)]
							)
						)
			n += 1
			count += 1
	print("STILLS %s: %d stills, %.0f s%s" % [scene_id, count, frame[0] * DT, " (cap)" if seq.is_playing() else ""])
	var tail: float = frame[0] * DT - float(script_end[0])
	if tail > 1.0:  # the sequencer waiting on walks and turns after the script is done (a held frame)
		print("TAIL %s: %.1f s after its last step" % [scene_id, tail])
	seq.cue_played.disconnect(on_cue)
	seq.line_shown.disconnect(on_line)
	if director != null:
		director.auto_update = true
	return n

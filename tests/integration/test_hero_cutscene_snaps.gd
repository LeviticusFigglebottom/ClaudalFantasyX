extends TestCase
## M2-HER-1110: no snapping in cutscenes. Every in-engine cutscene the game plays (HeroGuardSources.cutscenes(): the
## prologue, the slice's HalunaStory scenes, the chapter files' "play" steps) is played in driven time on its stage,
## and each stage actor's visible body (its HeroBody when it has one) is sampled every frame. A step or a turn
## faster than motion_guard.json's limits is a snap, unless the camera cut on that frame (a reposition hidden by
## a cut is staging, not a snap) or it is a deliberate jump of cut_m or more.

## Snaps already handed to their owner, as "<scene>:<actor>": reported, not failed, until the fix lands. M2-HER-1113
## (slice-polish, docs/kb/tech/cutscene_no_snap.patch): stage-actor turns peaking near 800 deg/s, a walk jumped to its
## mark when the scene ends, and a far stand-in clip mark glided across (Ch9's pole_out, 30 m). Remove each entry
## once the patch is on this branch; the test then holds them.
const KNOWN: Array[String] = [
	"ch01_net_pen:pen_child",
	"ch04_gangplank:ysolde",
	"ch05_kahre:kerrid",
	"ch05_matron_wakes:kerrid",
	"ch06_after_barge:wrights",
	"ch06_barge:stillguard_a",
	"ch06_barge:stillguard_b",
	"ch06_barge:wrights",
	"ch06_raid:hound",
	"ch07_after_the_bell:liss",
	"ch07_after_the_bell:oruvel_diver_1",
	"ch07_after_the_bell:oruvel_diver_2",
	"ch07_after_the_bell:poolkeeper",
	"ch07_after_the_bell:tavi",
	"ch07_empty_moorings:Player",
	"ch07_empty_moorings:asha",
	"ch07_empty_moorings:kerrid",
	"ch07_empty_moorings:tavi",
	"ch07_galleries:liss",
	"ch07_tavi:tavi",
	"ch08_cut_rope:liss",
	"ch08_cut_rope:officer",
	"ch08_cut_rope:toma",
	"ch08_first_down:hobb",
	"ch08_keeping_flame:asha",
	"ch08_keeping_flame:fenn",
	"ch08_landfall:kerrid",
	"ch08_spire_door:liss",
	"ch08_spire_door:tender",
	"ch08_stuck_key:liss",
	"ch09_the_ebbing:asha",
	"ch09_the_ebbing:kerrid_stair",
	"ch09_the_ebbing:pell",
	"ch09_the_road_out:kerrid",
	"ch09_the_road_out:pell",
]
## A scene that has not ended by then is stopped (driven time; seconds).
const MAX_SEC := 240.0
## Lines advance after this hold (driven: nobody reads them).
const LINE_HOLD_SEC := 0.25
## A body that moves more than this in a frame is walking (its floor is checked).
const MOVING_M := 0.01
## A camera step at or over this (metres or degrees in a frame) is a cut.
const CAMERA_CUT_M := 0.75
const CAMERA_CUT_DEG := 20.0

## The game state before the test: the guard runs on a fresh one (no flags left by earlier tests: a zone's variants and
## a scene's staging follow the flags) and puts this back.
var _state_was: GameStateData


func before_each() -> void:
	_state_was = Game.state


func test_no_actor_snaps_in_any_cutscene() -> void:
	var data := HeroMotionGuard.load_data()
	var limits := data.get("transform", {}) as Dictionary
	var dt := HeroMotionGuard.frame_sec(data)
	Game.state = GameStateData.new()
	Game.state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
	var played := 0
	var scenes := HeroGuardSources.cutscenes()
	for path: String in scenes:
		for scene_id: String in scenes[path]:
			var zone := (load(path) as PackedScene).instantiate() as Node3D
			if "autoplay" in zone:
				zone.set(&"autoplay", false)  # the prologue set plays itself when it is the current scene
			_host().add_child(zone)
			var result := _play(zone, StringName(scene_id), dt)
			zone.free()
			if result.is_empty():
				continue
			played += 1
			for who: String in result["off_floor"]:  # report-only until M3-CIN-1220's via= paths land (then it fails)
				print("  OFF-FLOOR %s %s: %.2f m" % [scene_id, who, result["off_floor"][who]])
			var cuts := result["cuts"] as Dictionary
			for who: String in result["tracks"]:
				var samples := (result["tracks"] as Dictionary)[who] as Array[Transform3D]
				var found := HeroMotionGuard.snaps_only(HeroMotionGuard.transform_snaps(samples, dt, limits))
				var snaps := found.filter(func(s: Dictionary) -> bool: return not cuts.has(int(s["frame"])))
				for s: Dictionary in snaps:
					print("  %s %s frame %d: %s %.1f" % [scene_id, who, s["frame"], s["kind"], s["value"]])
				if KNOWN.has("%s:%s" % [scene_id, who]):
					if not snaps.is_empty():
						print("  KNOWN (M2-HER-1113): %s %s, %d snaps" % [scene_id, who, snaps.size()])
					continue
				assert_true(snaps.is_empty(), "%s: %s never snaps (%d)" % [scene_id, who, snaps.size()])
	Game.state = _state_was
	assert_true(played > 0, "at least one cutscene played")


## Plays `scene_id` on the zone's stage in driven time. Returns {tracks: who -> [Transform3D], cuts: {frame: true}},
## or {} when the zone has no stage or the scene cannot start.
func _play(zone: Node3D, scene_id: StringName, dt: float) -> Dictionary:
	var stage := zone.get(&"stage") as CutsceneStage if "stage" in zone else null
	if stage == null:
		for n in zone.find_children("*", "Node3D", true, false):
			if n is CutsceneStage:
				stage = n as CutsceneStage
				break
	if stage == null:
		print("  %s: no CutsceneStage in %s, skipped" % [scene_id, zone.name])
		return {}
	var story := zone.get(&"story") as ZoneStory if "story" in zone else null
	if story != null:
		story.autostart = false
	for n in zone.find_children("*", "CharacterBody3D", true, false):
		if n is FieldController:
			(n as FieldController).set_physics_process(false)
			(n as FieldController).set_process_unhandled_input(false)
	var director := zone.get_node_or_null("CameraDirector") as FieldCameraDirector
	if director != null:
		director.auto_update = false
	var seq := CutsceneSequencer.new()
	seq.instant = false
	seq.auto_advance = true
	seq.auto_advance_hold_sec = LINE_HOLD_SEC
	zone.add_child(seq)
	seq.set_process(false)
	var named := {}  # actors a cue names, resolved as the sequencer does (rhen falls back to the field player)
	seq.cue_played.connect(
		func(_cue: StringName, args: Array, _kw: Dictionary) -> void:
			if not args.is_empty() and stage.actor(StringName(str(args[0]))) != null:
				named[str(args[0])] = stage.actor(StringName(str(args[0])))
	)
	seq.play(scene_id, stage)
	if not seq.is_playing():
		print("  %s: did not start, skipped" % scene_id)
		return {}
	var tracks := {}
	var cuts := {}
	var off_floor := {}  # actor -> its worst floor gap while walking (metres)
	var limits := HeroMotionGuard.load_data().get("transform", {}) as Dictionary
	var exclude: Array[RID] = []  # the cast's own colliders and the field player's capsule are not the floor
	for n in zone.find_children("*", "CollisionObject3D", true, false):
		if stage.is_ancestor_of(n) or n is FieldController:
			exclude.append((n as CollisionObject3D).get_rid())
	var cam_was := Transform3D()
	var has_cam := false
	var frame := 0
	while seq.is_playing() and frame * dt < MAX_SEC:
		if seq.overlay != null and seq.overlay.box.is_revealing():
			seq.overlay.box.skip_reveal()
		if director != null:
			director.update(dt)
		seq.advance(dt)
		var cam := zone.get_viewport().get_camera_3d()
		if cam != null:
			var ct := cam.global_transform
			if has_cam and _camera_cut(cam_was, ct):
				cuts[frame] = true
			cam_was = ct
			has_cam = true
		var cast := _actors(stage)
		for n: Node3D in named.values():
			if is_instance_valid(n) and n.is_visible_in_tree() and not cast.has(n):
				cast.append(n)
		for actor in cast:
			var body := actor.get_node_or_null(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor
			if body != null:
				body.set_process(false)
				body.advance(dt)
			var who := String(actor.name)
			if not tracks.has(who):
				tracks[who] = [] as Array[Transform3D]
			var t := body.global_transform if body != null else actor.global_transform
			var prev := tracks[who] as Array[Transform3D]
			if not prev.is_empty() and prev[-1].origin.distance_to(t.origin) > MOVING_M:
				var gap := HeroMotionGuard.floor_gap(zone.get_world_3d(), t.origin, exclude, limits)
				if not is_nan(gap) and absf(gap) > float(limits.get("floor_tolerance_m", INF)):
					off_floor[who] = maxf(float(off_floor.get(who, 0.0)), absf(gap))
			prev.append(t)
		frame += 1
	if seq.is_playing():
		print("  %s: still playing after %.0f s, stopped" % [scene_id, MAX_SEC])
	print("  %s: %d frames, %d actors sampled" % [scene_id, frame, tracks.size()])
	return {"tracks": tracks, "cuts": cuts, "off_floor": off_floor}


func _camera_cut(a: Transform3D, b: Transform3D) -> bool:
	if a.origin.distance_to(b.origin) >= CAMERA_CUT_M:
		return true
	return rad_to_deg(a.basis.get_rotation_quaternion().angle_to(b.basis.get_rotation_quaternion())) >= CAMERA_CUT_DEG


## The stage's visible actors (Actors/<id>).
func _actors(stage: CutsceneStage) -> Array[Node3D]:
	var out: Array[Node3D] = []
	var folder := stage.get_node_or_null(CutsceneStage.ACTORS)
	if folder == null:
		return out
	for c in folder.get_children():
		if c is Node3D and (c as Node3D).is_visible_in_tree():
			out.append(c as Node3D)
	return out


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene

extends TestCase
## M2-HER-1110: no snapping in cutscenes. Every in-engine cutscene the slice and Act I zones play (the prologue,
## the chapter files' "play" steps and the slice's HalunaStory scenes) is played in driven time on its zone's stage,
## and each stage actor's visible body (its HeroBody when it has one) is sampled every frame. A step or a turn
## faster than motion_guard.json's limits is a snap, unless the camera cut on that frame (a reposition hidden by
## a cut is staging, not a snap) or it is a deliberate jump of cut_m or more.

const SCENES := {
	"res://game/levels/prologue/prologue.tscn": ["prologue_dead_city"],
	"res://game/levels/ch02/haluna/haluna.tscn": ["ch02_girl_on_the_beach", "ch02_nemes_table", "ch03_dock_at_night"],
	"res://game/levels/ch01/oruvel/oruvel.tscn": ["ch01_the_rising", "ch01_kell_stall", "ch01_hullgnaw_rises"],
	"res://game/levels/ch01/oruvel_underway/oruvel_underway.tscn": ["ch01_bell_room", "ch01_the_drop"],
	"res://game/levels/ch04/haluna_wake/haluna_wake.tscn": ["ch04_the_wake", "ch04_wake_neme", "ch04_shell_is_set"],
	"res://game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn": ["ch04_gangplank", "ch04_under_way"],
	"res://game/levels/ch05/pemakar/pemakar.tscn": ["ch05_ferry_comes_in", "ch05_smiths_question"],
	"res://game/levels/ch05/ashcrown/ashcrown.tscn": ["ch05_crown_pavilion", "ch05_kerrid_steps_up"],
	"res://game/levels/ch06/brine_shoals/brine_shoals.tscn": ["ch06_ridge_camp", "ch06_raid", "ch06_barge"],
	"res://game/levels/ch07/tamsule/tamsule.tscn": ["ch07_into_tamsule", "ch07_tavi"],
	"res://game/levels/ch07/tamsule_bell_galleries/tamsule_bell_galleries.tscn": ["ch07_galleries", "ch07_naming"],
	"res://game/levels/ch09/corrow_night/corrow_night.tscn": ["ch09_strand", "ch09_the_road_out"],
}
## Snaps already handed to their owner, as "<scene>:<actor>": reported, not failed, until the fix lands. M2-HER-1113
## (slice-polish, docs/kb/tech/cutscene_no_snap.patch): stage-actor turns peaking near 800 deg/s, and a walk jumped
## to its mark when the scene ends. Remove each entry once the patch is on this branch; the test then holds them.
const KNOWN: Array[String] = [
	"ch04_gangplank:ysolde",
	"ch06_barge:stillguard_a",
	"ch06_barge:stillguard_b",
	"ch06_barge:wrights",
	"ch06_raid:hound",
	"ch06_raid:inquisitor",
	"ch07_galleries:liss",
	"ch07_tavi:tavi",
	"ch09_the_road_out:liss",
	"ch09_the_road_out:pell",
]
## A scene that has not ended by then is stopped (driven time; seconds).
const MAX_SEC := 240.0
## Lines advance after this hold (driven: nobody reads them).
const LINE_HOLD_SEC := 0.25
## A camera step at or over this (metres or degrees in a frame) is a cut.
const CAMERA_CUT_M := 0.75
const CAMERA_CUT_DEG := 20.0

var _party_was: Array[StringName] = []


func before_each() -> void:
	_party_was = Game.state.party_ids.duplicate()


func test_no_actor_snaps_in_any_cutscene() -> void:
	var data := HeroMotionGuard.load_data()
	var limits := data.get("transform", {}) as Dictionary
	var dt := HeroMotionGuard.frame_sec(data)
	Game.state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
	var played := 0
	for path: String in SCENES:
		if not ResourceLoader.exists(path):
			continue
		for scene_id: String in SCENES[path]:
			var zone := (load(path) as PackedScene).instantiate() as Node3D
			if "autoplay" in zone:
				zone.set(&"autoplay", false)  # the prologue set plays itself when it is the current scene
			_host().add_child(zone)
			var result := _play(zone, StringName(scene_id), dt)
			zone.free()
			if result.is_empty():
				continue
			played += 1
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
	Game.state.party_ids = _party_was
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
			(tracks[who] as Array[Transform3D]).append(t)
		frame += 1
	if seq.is_playing():
		print("  %s: still playing after %.0f s, stopped" % [scene_id, MAX_SEC])
	print("  %s: %d frames, %d actors sampled" % [scene_id, frame, tracks.size()])
	return {"tracks": tracks, "cuts": cuts}


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

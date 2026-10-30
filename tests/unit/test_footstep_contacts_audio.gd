extends TestCase
## M3-AUD-802: FootstepAudio on the real heroes' foot contacts (game/data/audio/footsteps.json). Stand-in hero bodies
## built here, never the real classes (no class_name stubs): a body with a foot_contact signal fired by a method
## track, an AnimationTree laid out like HeroFieldActor's (idle/walk/run in a 1D blend space) whose clips carry
## M2-CHR-12's foot_l_down / foot_r_down markers, and a playing AnimationPlayer with markers. One step per contact,
## walk and run rows, the cloth and gear layers, the ground's surface (shallow water), the halt and turn scuffs, and
## the distance stepper when the body has no contacts. Sounds are recorded through the listener's player Callable,
## so nothing plays.

const HALUNA := "res://game/levels/ch02/haluna/haluna.tscn"
const DT := 1.0 / 60.0
const WALK_MPS := 1.0  # field_movement.json's walk (hero-integration ADR 0191)
const RUN_MPS := 3.6  # field_movement.json's run (hero-integration ADR 0191)
const WALK_LEN := 1.0
const RUN_LEN := 0.6
const MARKERS: Array[StringName] = [&"foot_l_down", &"foot_r_down"]
const BLEND := "parameters/loco/blend_position"
const RUN_POS := "parameters/loco/2/current_position"


class Walker:
	extends Node3D
	var on_ground := true

	func grounded() -> bool:
		return on_ground


class SignalBody:
	extends Node3D
	signal foot_contact(foot: StringName)
	var hero_id := &"asha"


## hero-integration's HeroFieldActor signature (M3-AUD-810): foot_contact(foot, run), the run flag from the live clip.
class GaitSignalBody:
	extends Node3D
	signal foot_contact(foot: StringName, run: bool)
	var hero_id := &"rhen"


class TreeBody:
	extends Node3D
	var hero_id := &"rhen"


var played: Array = []


func before_each() -> void:
	played = []


func _data() -> Dictionary:
	return (AudioData.table(AudioData.FOOTSTEPS) as Dictionary).duplicate(true)


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _listener(w: Node3D) -> FootstepAudio:
	var f := FootstepAudio.new(_data())
	f.player = func(id: StringName, at: Vector3, opts: Dictionary) -> void: played.append([id, at, opts])
	_host().add_child(f)
	f.attach(w, HALUNA)
	return f


func _rows(prefix: String) -> Array:
	return played.filter(func(p: Array) -> bool: return String(p[0]).begins_with(prefix))


## A 1 s walk and a 0.6 s run, each with a heel contact marker at 0 and at half the cycle (or none).
func _library(markers: bool = true) -> AnimationLibrary:
	var lib := AnimationLibrary.new()
	for row: Array in [[&"idle", 2.0, false], [&"walk", WALK_LEN, true], [&"run", RUN_LEN, true]]:
		var a := Animation.new()
		a.length = float(row[1])
		a.loop_mode = Animation.LOOP_LINEAR
		if markers and bool(row[2]):
			a.add_marker(MARKERS[0], 0.0)
			a.add_marker(MARKERS[1], a.length * 0.5)
		lib.add_animation(row[0] as StringName, a)
	return lib


## A walker carrying a HeroBody whose Model has an AnimationTree like HeroFieldActor's.
func _tree_walker(lib: AnimationLibrary) -> Array:
	var w := Walker.new()
	var body := TreeBody.new()
	body.name = "HeroBody"
	w.add_child(body)
	var model := Node3D.new()
	model.name = "Model"
	body.add_child(model)
	var bs := AnimationNodeBlendSpace1D.new()
	bs.max_space = 3.0
	for p: Array in [[&"idle", 0.0], [&"walk", 1.0], [&"run", 3.0]]:
		var n := AnimationNodeAnimation.new()
		n.animation = p[0] as StringName
		bs.add_blend_point(n, float(p[1]))
	# HeroFieldActor's layout: loco -> scale (TimeScale) -> mode (Transition) with an empty one-shot slot
	var bt := AnimationNodeBlendTree.new()
	bt.add_node(&"loco", bs)
	bt.add_node(&"scale", AnimationNodeTimeScale.new())
	bt.connect_node(&"scale", 0, &"loco")
	bt.add_node(&"act_a", AnimationNodeAnimation.new())
	var mode := AnimationNodeTransition.new()
	mode.input_count = 2
	mode.set_input_name(0, "scale")
	mode.set_input_name(1, "act_a")
	bt.add_node(&"mode", mode)
	bt.connect_node(&"mode", 0, &"scale")
	bt.connect_node(&"mode", 1, &"act_a")
	bt.connect_node(&"output", 0, &"mode")
	var tree := AnimationTree.new()
	tree.add_animation_library(&"", lib)
	tree.tree_root = bt
	tree.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	model.add_child(tree)
	_host().add_child(w)
	tree.active = true
	return [w, tree]


func _frames(f: FootstepAudio, w: Node3D, mps: float, sec: float, tick: Callable = Callable()) -> void:
	for i in int(round(sec / DT)):
		w.global_position += Vector3(mps * DT, 0.0, 0.0)
		if tick.is_valid():
			tick.call(DT)
		f.advance(DT)


## Marker crossings of a clip of `length` with contacts at 0 and length/2 between positions p0 and p0 + travel.
func _crossings(length: float, p0: float, travel: float) -> int:
	var half := length * 0.5
	return int(floor((p0 + travel) / half)) - int(floor(p0 / half))


func test_a_contact_signal_fired_by_a_method_track_is_one_step_each() -> void:
	var w := Walker.new()
	var body := SignalBody.new()
	body.name = "HeroBody"
	w.add_child(body)
	var ap := AnimationPlayer.new()
	body.add_child(ap)  # root_node ".." is the body
	var a := Animation.new()
	a.length = WALK_LEN
	a.loop_mode = Animation.LOOP_LINEAR
	var t := a.add_track(Animation.TYPE_METHOD)
	a.track_set_path(t, NodePath("."))
	for at: float in [0.25, 0.75]:
		a.track_insert_key(t, at, {"method": &"emit_signal", "args": [&"foot_contact", &"l"]})
	var lib := AnimationLibrary.new()
	lib.add_animation(&"walk", a)
	ap.add_animation_library(&"", lib)
	ap.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	ap.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_IMMEDIATE
	_host().add_child(w)
	var emitted := [0]
	body.foot_contact.connect(func(_foot: StringName) -> void: emitted[0] += 1)
	var f := _listener(w)
	f.advance(DT)
	assert_eq(f.contact_source, &"signal", "the body's foot_contact signal is the contact source")
	ap.play(&"walk")
	_frames(f, w, WALK_MPS, 2.0, func(dt: float) -> void: ap.advance(dt))
	assert_eq(int(emitted[0]), 4, "the method track fired four contacts in 2 s")
	var steps := _rows("hero_step_")
	assert_eq(steps.size(), int(emitted[0]), "one step per contact, none from distance")
	assert_eq(steps[0][0], &"hero_step_sand_walk", "Haluna's sand, walking")
	assert_eq(float((steps[0][2] as Dictionary)["volume_db"]), float(_data()["walk_db"]), "a walk at walk_db")
	assert_eq(_rows("hero_cloth_walk").size(), steps.size(), "cloth on every step")
	var every := int((_data()["foley"] as Dictionary)["gear_every"])
	assert_eq(_rows("hero_gear_shells").size(), steps.size() / every, "Asha's shells every %d steps" % every)
	assert_eq(_rows("hero_gear_lantern").size(), 0, "not Rhen's lantern")
	played.clear()
	_frames(f, w, RUN_MPS, 1.0, func(dt: float) -> void: ap.advance(dt))
	assert_true(_rows("hero_step_").size() > 0, "running still steps on contacts")
	assert_true(_rows("hero_step_").all(func(p: Array) -> bool: return p[0] == &"hero_step_sand_run"), "run rows")
	f.free()
	w.free()


func test_the_contact_signals_run_flag_sets_the_gait() -> void:
	var w := Walker.new()
	var body := GaitSignalBody.new()
	body.name = "HeroBody"
	w.add_child(body)
	_host().add_child(w)
	var f := _listener(w)
	f.advance(DT)
	assert_eq(f.contact_source, &"signal", "foot_contact(foot, run) is the contact source")
	_frames(f, w, WALK_MPS, 0.5)
	played.clear()
	body.foot_contact.emit(&"l", true)  # a run_start clip while the pace is still a walk's
	_frames(f, w, WALK_MPS, 0.3)
	body.foot_contact.emit(&"r", false)
	assert_eq(
		_rows("hero_step_").map(func(p: Array) -> StringName: return p[0]),
		[&"hero_step_sand_run", &"hero_step_sand_walk"],
		"the clip's gait, not the pace"
	)
	assert_eq(_rows("hero_gear_lantern").size() + _rows("hero_cloth_").size() > 0, true, "Rhen's foley follows")
	f.free()
	w.free()


func test_markers_on_a_locomotion_tree_step_on_the_dominant_clip() -> void:
	var lib := _library()
	var made := _tree_walker(lib)
	var w := made[0] as Walker
	var tree := made[1] as AnimationTree
	var f := _listener(w)
	f.advance(DT)
	assert_eq(f.contact_source, &"tree", "the AnimationTree's clip markers are the contact source")
	assert_eq(String(f.body.name), "HeroBody", "read from the walker's HeroBody")
	tree.set(BLEND, 1.0)
	_frames(f, w, WALK_MPS, 1.9, func(dt: float) -> void: tree.advance(dt))
	var steps := _rows("hero_step_")
	assert_eq(steps.size(), _crossings(WALK_LEN, 0.0, 1.9), "one step per walk contact (0.5, 1.0, 1.5 s)")
	assert_true(steps.all(func(p: Array) -> bool: return p[0] == &"hero_step_sand_walk"), "walk rows")
	assert_true(_rows("hero_gear_lantern").size() > 0, "Rhen's lantern (the body's hero_id)")
	played.clear()
	tree.set(BLEND, 3.0)
	tree.advance(0.0)
	f.advance(DT)
	played.clear()
	var p0 := float(tree.get(RUN_POS))
	_frames(f, w, RUN_MPS, 1.0, func(dt: float) -> void: tree.advance(dt))
	steps = _rows("hero_step_")
	assert_eq(steps.size(), _crossings(RUN_LEN, p0, 1.0), "one step per run contact")
	assert_true(steps.all(func(p: Array) -> bool: return p[0] == &"hero_step_sand_run"), "a run clip plays run rows")
	assert_eq(float((steps[0][2] as Dictionary)["volume_db"]), float(_data()["run_db"]), "a run at run_db")
	played.clear()
	tree.set(BLEND, 0.0)
	_frames(f, w, 0.0, 1.0, func(dt: float) -> void: tree.advance(dt))
	assert_eq(_rows("hero_step_").size(), 0, "idle has no contacts")
	f.free()
	w.free()


func test_a_playing_animation_player_with_markers_steps_on_them() -> void:
	var w := Walker.new()
	var ap := AnimationPlayer.new()
	w.add_child(ap)
	ap.add_animation_library(&"", _library())
	ap.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	_host().add_child(w)
	var f := _listener(w)
	f.advance(DT)
	assert_eq(f.contact_source, &"player", "no body, no tree: the walker's AnimationPlayer")
	ap.play(&"walk")
	ap.advance(0.0)
	_frames(f, w, WALK_MPS, 1.9, func(dt: float) -> void: ap.advance(dt))
	assert_eq(_rows("hero_step_").size(), 1 + _crossings(WALK_LEN, 0.0, 1.9), "the first frame's contact and 3 more")
	f.free()
	w.free()


func test_a_body_without_contacts_falls_back_to_distance_and_a_stalled_one_to_stall_m() -> void:
	var made := _tree_walker(_library(false))  # clips without markers (today's field clips)
	var w := made[0] as Walker
	var f := _listener(w)
	var d := _data()
	f.advance(DT)
	assert_eq(f.contact_source, &"", "no markers: the distance stepper")
	_frames(f, w, WALK_MPS, 10.0 / WALK_MPS)
	var stride := float(d["walk_step_m"])
	var want := 1 + int(floor((10.0 - stride * (1.0 - float(d["first_step"]))) / stride + 1e-6))
	assert_eq(_rows("hero_step_").size(), want, "a 10 m walk at walk_step_m strides")
	f.free()
	w.free()
	played.clear()
	var lib := _library()
	made = _tree_walker(lib)
	w = made[0] as Walker
	f = _listener(w)
	f.advance(DT)
	assert_eq(f.contact_source, &"tree", "markers exist")
	_frames(f, w, WALK_MPS, 10.0 / WALK_MPS)  # the tree is never advanced
	var stall := float((d["contacts"] as Dictionary)["stall_m"])
	# M3-AUD-812: one step at stall_m, then walk_step_m strides (hero-integration's clips without footfall markers)
	var first_at := stall - stride * float(d["first_step"])
	var stalled := 1 + int(floor((10.0 - first_at) / stride + 1e-6))
	assert_true(f.stalled, "it noticed the stall")
	assert_between(_rows("hero_step_").size(), stalled - 1, stalled + 1, "after the stall it walks at walk_step_m")
	f.free()
	w.free()


func test_the_ground_under_the_feet_picks_the_surface_shallow_water_first() -> void:
	var water := Area3D.new()
	water.add_to_group(&"audio_surface_water")
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(4.0, 2.0, 4.0)
	cs.shape = box
	water.add_child(cs)
	_host().add_child(water)
	water.global_position = Vector3(5.0, 0.0, 0.0)
	var dock := Node3D.new()  # M2-AUD-09's form: a footstep_surface group with a surface meta and a priority
	dock.add_to_group(&"footstep_surface")
	dock.set_meta(&"surface", "wood")
	dock.set_meta(&"surface_priority", 1.0)
	var cs2 := CollisionShape3D.new()
	var box2 := BoxShape3D.new()
	box2.size = Vector3(1.0, 2.0, 4.0)
	cs2.shape = box2
	dock.add_child(cs2)
	_host().add_child(dock)
	dock.global_position = Vector3(6.5, 0.0, 0.0)
	var w := Walker.new()
	_host().add_child(w)
	var f := _listener(w)
	f.advance(DT)
	_frames(f, w, WALK_MPS, 10.0 / WALK_MPS)
	for p: Array in _rows("hero_step_"):
		var x := (p[1] as Vector3).x
		var want := &"hero_step_sand_walk"
		if x >= 6.0 and x <= 7.0:
			want = &"hero_step_wood_walk"
		elif x >= 3.0 and x <= 7.0:
			want = &"hero_step_water_walk"
		assert_eq(p[0], want, "at x %.2f" % x)
	assert_true(_rows("hero_step_water_walk").size() >= 2, "wading through the water")
	assert_true(_rows("hero_step_wood_walk").size() >= 1, "the higher-priority dock inside it")
	assert_eq(FootstepAudio.surface_at(_data(), w.get_tree(), Vector3(5.0, 0.0, 0.0), &"sand"), &"water", "water")
	assert_eq(FootstepAudio.surface_at(_data(), w.get_tree(), Vector3(5.0, 3.0, 0.0), &"sand"), &"sand", "above it")
	f.free()
	w.free()
	water.free()
	dock.free()


func test_a_halt_scuffs_once_and_a_reversal_scuffs_a_turn() -> void:
	var w := Walker.new()
	_host().add_child(w)
	var f := _listener(w)
	f.advance(DT)
	_frames(f, w, WALK_MPS, 3.0 / WALK_MPS)
	assert_eq(_rows("hero_stop_").size(), 0, "no scuff while walking")
	_frames(f, w, 0.0, 0.5)
	assert_eq(_rows("hero_stop_").size(), 1, "one stop scuff when the hero halts")
	assert_eq(_rows("hero_stop_")[0][0], &"hero_stop_sand", "on the surface")
	played.clear()
	_frames(f, w, WALK_MPS, 0.3 / WALK_MPS)
	_frames(f, w, 0.0, 0.5)
	assert_eq(_rows("hero_stop_").size(), 0, "a shuffle shorter than stop.min_steps steps does not scuff")
	played.clear()
	_frames(f, w, WALK_MPS, 2.0 / WALK_MPS)
	_frames(f, w, -WALK_MPS, 2.0 / WALK_MPS)
	assert_eq(_rows("hero_turn_").size(), 1, "one turn scuff on a reversal")
	assert_eq(_rows("hero_turn_")[0][0], &"hero_turn_sand", "on the surface")
	assert_eq(f.turns, 1, "counted")
	f.free()
	w.free()


func test_every_row_footsteps_json_names_exists_and_loads() -> void:
	var d := _data()
	var rows := AudioData.sfx_rows()
	var ids: Array[String] = []
	for surf: String in d["surfaces"] as Dictionary:
		for kind: String in ["walk", "run", "stop", "turn"]:
			ids.append(String(FootstepAudio.row_for(d, StringName(surf), StringName(kind))))
	for key: String in ["cloth", "gear"]:
		for id: Variant in ((d["foley"] as Dictionary)[key] as Dictionary).values():
			ids.append(str(id))
	var surfaces := (d["surfaces"] as Dictionary).keys()
	for surf: String in ["sand", "stone", "wood", "water", "root", "snow", "slate"]:
		assert_true(surfaces.has(surf), "surface %s (Act I's four, Act II's root, snow and slate: ADR 0204 §11)" % surf)
	assert_eq(ids.size(), surfaces.size() * 4 + 5, "every surface x 4 kinds, 2 cloth and 3 gear rows")
	for id in ids:
		var row := rows.get(id, {}) as Dictionary
		assert_eq(str(row.get("bus", "")), "World", "%s plays on World" % id)
		for file: Variant in row.get("files", []):
			assert_true(ResourceLoader.exists(str(file)), "%s imports" % file)
	var steps := (rows.get("hero_step_water_walk", {}) as Dictionary).get("files", []) as Array
	assert_true(steps.size() >= 6, "six or more variants per surface and gait")

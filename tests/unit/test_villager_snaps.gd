extends TestCase
## M2-HER-1110 / item "villagers alive": no snapping on Haluna's villagers (creatures' FieldNpc and VillagerLayer,
## M3-CRE-610/613). The zone's villagers run their routines (routes, chats, work) while the player walks up to each
## one from behind its shoulder, talks and leaves; each actor's root is sampled every frame (HeroMotionGuard
## transform snaps), and every clip change a villager makes is checked for pops at FieldNpc's own cross-fades.
## Duck-typed: the villager layer is loaded by path, so this skips (with a note) until it reaches this branch.

const ZONE := "res://game/levels/ch02/haluna/haluna.tscn"
const ZONE_ID := &"ch02/haluna"
const LAYER_SCRIPT := "res://game/world/npc/villager_layer.gd"
const NPC_DATA := "res://game/data/world/npc/npc.json"
const ZONE_DATA := "res://game/data/world/npc/zones/ch02_haluna.json"
const ACTOR_PATH := "res://assets/characters/villagers/%s/%s_actor.tscn"
## Before the visits: the routines alone (seconds).
const WARM_SEC := 6.0
## Per villager: approach (stand at its shoulder), talk, then leave.
const NEAR_SEC := 1.5
const TALK_SEC := 2.0
const AWAY_SEC := 1.5
## Where the player stands for a visit: this far from the villager, this far round from its facing (a turn to make).
const VISIT_M := 1.3
const VISIT_TURN_DEG := 120.0
const AWAY_M := 12.0
## The clip changes a villager makes: [from, to, the npc.json blend key FieldNpc uses for `to`].
const CHANGES: Array[Array] = [
	[&"idle", &"talk", "talk_blend_sec"],
	[&"talk", &"idle", "idle_blend_sec"],
	[&"idle", &"walk", "walk_blend_sec"],
	[&"walk", &"idle", "idle_blend_sec"],
	[&"walk", &"talk", "talk_blend_sec"],
	[&"talk", &"walk", "walk_blend_sec"],
]

var _made: Array[Node] = []


func before_each() -> void:
	for n in _made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	_made.clear()


func test_no_villager_snaps_through_its_routine_and_a_visit() -> void:
	if not ResourceLoader.exists(LAYER_SCRIPT):
		print("  skipped: the villager layer (creatures' M3-CRE-613) is not on this branch yet")
		return
	var data := HeroMotionGuard.load_data()
	var limits := data.get("transform", {}) as Dictionary
	var dt := HeroMotionGuard.frame_sec(data)
	var zone := (load(ZONE) as PackedScene).instantiate() as Node3D
	_add(zone)
	var director := zone.get_node_or_null("CameraDirector") as FieldCameraDirector
	if director != null:
		director.auto_update = false
	var player := zone.get_node("Player") as FieldController
	player.set_physics_process(false)
	player.set_process_unhandled_input(false)
	var layer := (load(LAYER_SCRIPT) as GDScript).new() as Node3D
	layer.set("zone_id", ZONE_ID)
	layer.set("auto_build", false)
	zone.add_child(layer)
	var count := int(layer.call("build"))
	assert_true(count > 0, "Haluna has villagers")
	var villagers: Array = layer.get("villagers")
	var tracks := {}
	player.global_position = player.global_position + Vector3(AWAY_M * 4.0, 0.0, 0.0)
	_run(layer, villagers, tracks, WARM_SEC, dt)
	for v: Node3D in villagers:
		var facing := float(v.call("yaw"))
		var toward := Basis(Vector3.UP, facing + deg_to_rad(VISIT_TURN_DEG)) * Vector3.FORWARD
		player.global_position = v.global_position + toward * VISIT_M
		_run(layer, villagers, tracks, NEAR_SEC, dt)
		v.call("begin_talk", player)
		_run(layer, villagers, tracks, TALK_SEC, dt)
		v.call("end_talk")
		player.global_position = v.global_position + toward * AWAY_M
		_run(layer, villagers, tracks, AWAY_SEC, dt)
	for who: String in tracks:
		var samples := tracks[who] as Array[Transform3D]
		var rates := HeroMotionGuard.peak_rates(samples, dt, float(limits["cut_m"]))
		print("  %s: peak %.2f m/s, %.0f deg/s" % [who, rates["speed"], rates["turn"]])
		var snaps := HeroMotionGuard.snaps_only(HeroMotionGuard.transform_snaps(samples, dt, limits))
		for s in snaps:
			print("  %s frame %d: %s %.1f" % [who, s["frame"], s["kind"], s["value"]])
		assert_true(snaps.is_empty(), "%s never snaps (%d snaps)" % [who, snaps.size()])


func test_no_villager_clip_change_pops() -> void:
	var data := HeroMotionGuard.load_data()
	var limits := data.get("clips", {}) as Dictionary
	var dt := HeroMotionGuard.frame_sec(data)
	var npc := _json(NPC_DATA)
	var rows := npc.get("villagers", {}) as Dictionary
	var ids: Array[String] = []
	for id: String in rows:
		ids.append(id)
	for row: Variant in _json(ZONE_DATA).get("villagers", []):
		var zid := str((row as Dictionary).get("npc_id", "")) if row is Dictionary else ""
		if zid != "" and not ids.has(zid):
			ids.append(zid)
	var checked := 0
	for id: String in ids:
		var path := ACTOR_PATH % [id, id]
		if not ResourceLoader.exists(path):
			continue
		var actor := (load(path) as PackedScene).instantiate() as Node3D
		_add(actor)
		var p := HeroMotion.player_of(actor)
		var skel := HeroMotion.skeleton_of(actor)
		if p == null or skel == null:
			continue
		var tuning := (npc.get("defaults", {}) as Dictionary).merged(rows.get(id, {}) as Dictionary, true)
		for pair in CHANGES:
			var from: StringName = pair[0]
			var to: StringName = pair[1]
			if not (p.has_animation(from) and p.has_animation(to)):
				continue
			p.set_blend_time(from, to, float(tuning.get(pair[2], 0.0)))
			var r := HeroMotionGuard.clip_change(p, skel, from, to, limits, dt)
			print(
				(
					"  %s %s -> %s: blend %.2f s, peak %.3f m/frame, allowed %.3f%s"
					% [id, from, to, r["blend"], r["peak"], r["allowed"], "  POP" if r["pop"] else ""]
				)
			)
			assert_false(bool(r["cut"]), "%s %s -> %s cross-fades" % [id, from, to])
			assert_false(
				bool(r["pop"]), "%s %s -> %s: %.3f m/frame, over %.3f" % [id, from, to, r["peak"], r["allowed"]]
			)
			checked += 1
	if checked == 0:
		print("  skipped: no villager actors with clips on this branch yet")


## Ticks the layer (it ticks its villagers) for `sec`, sampling each villager's visible actor.
func _run(layer: Node, villagers: Array, tracks: Dictionary, sec: float, dt: float) -> void:
	for i in roundi(sec / dt):
		layer.call("tick", dt)
		for v: Node3D in villagers:
			var body := v.get("actor") as Node3D
			if body == null:
				continue
			var who := String(v.get("npc_id"))
			if not tracks.has(who):
				tracks[who] = [] as Array[Transform3D]
			(tracks[who] as Array[Transform3D]).append(body.global_transform)


static func _json(path: String) -> Dictionary:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	return parsed if parsed is Dictionary else {}


func _add(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	_made.append(n)

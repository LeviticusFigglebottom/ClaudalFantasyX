extends SceneTree
## The clip audit (creatures, 2026-10-29: the Lead's Act I final-quality audit). Samples every clip of every Act I
## regular foe's battle actor and every crowd body at 60 fps, headless, and reports per clip:
##   slip   the farthest a contact vertex (the skinned mesh's lowest) slides along the floor while it stays planted
##          (cm): foot sliding;
##   pop    the largest one-frame jump of any bone (cm), and its share of the actor's size: popping;
##   seam   a looping clip's largest bone gap between its last frame and its first (cm): a loop that hitches;
##   under  how far the lowest contact vertex dips under the floor (cm);
##   motion the largest any skin vertex (idle, hit; else bone) travels from its first-frame place (share of the
##          actor's size): an idle under STIFF_SHARE is stiff, a hit under HIT_SHARE doesn't read (nor one
##          reaching less than HIT_EARLY of its travel by HIT_PEAK_S);
##   float  where a KO ends: the whole skinned mesh's lowest point over the floor (cm), counting the battle hover the
##          creatures.json row raises it by (stand_in.hover), so a KO that leaves it in the air is caught;
## and per actor the reactions it lacks (hit, ko; a villager's idle, talk, walk).
## godot --headless --path . -s tools/creatures/clip_audit.gd [-- --json OUT] [-- id ...]
## (no ids: the roster below; an id may also name any creatures.json row,
## as Act II's foes). Flags (`!`) mark values past the thresholds; the clip names stay the data's.

const ENCOUNTERS := "res://game/data/battle/encounters.json"
const ENEMIES := "res://game/data/battle/enemies.json"
const CROWD := "res://game/data/world/npc/crowd.json"
const CREATURES := "res://game/data/creatures/creatures.json"
const CROWD_ACTOR := "res://assets/crowd/%s/%s_actor.tscn"
const ACT1 := "^ch0[1-9]_"
## The bosses are creatures-b's (M3-HER-1143); the rest of Act I's foes are this audit's.
const SKIP_IDS: Array[String] = ["cinder_matron", "spar_wraith", "stillguard_inquisitor"]
const FPS := 60.0
## Contact vertices: those under CONTACT_REST_M in the rest pose, at most CONTACT_MAX of them (evenly picked).
const CONTACT_REST_M := 0.15
const CONTACT_MAX := 600
## A bone is planted while it is within PLANT_M of its lowest point in the clip and that point is near the floor.
const FLOOR_M := 0.04
const PLANT_M := 0.012
const SLIP_FLAG_CM := 2.0
const POP_FLAG_SHARE := 0.08  # a one-frame jump past 8% of the actor's size
const SEAM_FLAG_CM := 1.0
const UNDER_FLAG_CM := 1.5
const STIFF_SHARE := 0.03  # an idle whose skin stays within 3% of the actor's size reads as a still frame
const HIT_SHARE := 0.06
const HIT_PEAK_S := 0.25
const HIT_EARLY := 0.7  # of its travel by HIT_PEAK_S
const FLOAT_FLAG_CM := 4.0
## KOs that go under on purpose: the hullgnaw slides back down into its breach (build_hullgnaw.ko_clip).
const KO_SUBMERGES: Array[String] = ["hullgnaw", "hull_rasp"]
const IDLE_CLIPS: Array[String] = ["idle", "idle_b"]
const MOTION_STRIDE := 7  # every 7th skinned vertex for the idle and hit motion
const HIT_CLIPS: Array[String] = ["hit", "hit_b"]
## Gaits played in place while the node moves (FieldNpc): their feet travel by design.
const IN_PLACE_GAITS: Array[String] = ["walk", "run"]
const FOE_CLIPS: Array[String] = ["idle", "attack", "hit", "ko"]
const NPC_CLIPS: Array[String] = ["idle", "talk", "walk"]

var rows: Array = []


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args := Array(OS.get_cmdline_user_args())
	var json_out := ""
	var i := args.find("--json")
	if i >= 0 and i + 1 < args.size():
		json_out = str(args[i + 1])
		args.remove_at(i + 1)
		args.remove_at(i)
	var roster := _roster()
	var ids: Array = args if not args.is_empty() else roster.keys()
	ids.sort()
	for id: String in ids:
		if not roster.has(id):
			# any creatures.json row by id (Act II's foes, a variant): its battle scene
			var row: Dictionary = (_creatures().get("creatures", {}) as Dictionary).get(id, {})
			if row.is_empty():
				print("%s: not in the roster or creatures.json" % id)
				continue
			roster[id] = {"scene": str(row.get("scene", "")), "kind": "foe"}
		_audit(id, str(roster[id]["scene"]), str(roster[id]["kind"]))
	if json_out != "":
		var f := FileAccess.open(json_out, FileAccess.WRITE)
		f.store_string(JSON.stringify(rows, "  "))
		f.close()
	quit()


func _creatures() -> Dictionary:
	var d: Variant = JSON.parse_string(FileAccess.get_file_as_string(CREATURES))
	return d if d is Dictionary else {}


## id -> {scene, kind}: Act I's regular foes (encounters ch01..ch09, their enemies.json `model`) and the crowd bodies.
func _roster() -> Dictionary:
	var out := {}
	var re := RegEx.create_from_string(ACT1)
	var enc: Variant = JSON.parse_string(FileAccess.get_file_as_string(ENCOUNTERS))
	var foes := {}
	for e: Dictionary in (enc as Dictionary).get("encounters", []):
		if re.search(str(e.get("id", ""))) != null:
			for f: Variant in e.get("enemies", []):
				foes[str(f)] = true
	var en: Variant = JSON.parse_string(FileAccess.get_file_as_string(ENEMIES))
	for r: Dictionary in (en as Dictionary).get("enemies", []):
		var id := str(r.get("id", ""))
		if foes.has(id) and not SKIP_IDS.has(id) and str(r.get("model", "")) != "":
			out[id] = {"scene": str(r["model"]), "kind": "foe"}
	var crowd: Variant = JSON.parse_string(FileAccess.get_file_as_string(CROWD))
	for body: String in ((crowd as Dictionary).get("bodies", {}) as Dictionary).keys():
		out[body] = {"scene": CROWD_ACTOR % [body, body], "kind": "npc"}
	return out


func _audit(id: String, scene_path: String, kind: String) -> void:
	var packed := load(scene_path) as PackedScene
	if packed == null:
		print("%s: cannot load %s" % [id, scene_path])
		return
	var actor := packed.instantiate() as Node3D
	if actor is CreatureActor:
		actor.set_script(null)  # sample the AnimationPlayer alone (no idle fidget switching clips under the sampler)
	root.add_child(actor)
	var players := actor.find_children("*", "AnimationPlayer", true, false)
	var skels := actor.find_children("*", "Skeleton3D", true, false)
	if players.is_empty() or skels.is_empty():
		print("%s: no AnimationPlayer or Skeleton3D" % id)
		actor.free()
		return
	var anim := players[0] as AnimationPlayer
	var skel := _animated_skeleton(anim, skels)
	var clips := Array(anim.get_animation_list()).filter(func(c: String) -> bool: return c != "RESET")
	var contacts := _contacts(actor)
	var samples := _samples(actor, MOTION_STRIDE)
	if not clips.is_empty():  # a player's first seek after load does not pose the skeleton: warm it up
		anim.play(StringName(str(clips[0])))
		anim.seek(0.0, true)
	var size := _size(actor)
	var missing: Array[String] = []
	for want: String in FOE_CLIPS if kind == "foe" else NPC_CLIPS:
		if not clips.has(want):
			missing.append(want)
	var line := (
		"%s (%s, %.2f m)%s" % [id, kind, size, ("  MISSING " + ", ".join(missing)) if not missing.is_empty() else ""]
	)
	print(line)
	for clip: String in clips:
		var r := _measure(anim, skel, StringName(clip), size, contacts, samples)
		if clip == "ko":
			r["float_cm"] = 100.0 * (_mesh_lowest(actor, skel) + _hover(scene_path))
			anim.seek(0.0, true)
			r["start_cm"] = 100.0 * (_mesh_lowest(actor, skel) + _hover(scene_path))
		r["id"] = id
		r["kind"] = kind
		r["clip"] = clip
		rows.append(r)
		var flags := ""
		flags += "!" if float(r["slip_cm"]) > SLIP_FLAG_CM and not IN_PLACE_GAITS.has(clip) else " "
		flags += "!" if float(r["pop_share"]) > POP_FLAG_SHARE else " "
		flags += "!" if float(r["seam_cm"]) > SEAM_FLAG_CM else " "
		flags += "!" if float(r["under_cm"]) > UNDER_FLAG_CM else " "
		var notes: Array[String] = []
		if IDLE_CLIPS.has(clip) and float(r["motion_share"]) < STIFF_SHARE:
			notes.append("STIFF")
		if HIT_CLIPS.has(clip) and (float(r["motion_share"]) < HIT_SHARE or float(r["early_share"]) < HIT_EARLY):
			notes.append("WEAK HIT")
		if r.has("float_cm") and float(r["float_cm"]) > FLOAT_FLAG_CM:
			notes.append("FLOATS %.0f cm" % r["float_cm"])
		# a KO sinks when it ends lower than it began (a sea creature already standing in the water is not sinking)
		var start_low := minf(float(r.get("start_cm", 0.0)), 0.0)
		if r.has("float_cm") and float(r["float_cm"]) < start_low - FLOAT_FLAG_CM and not KO_SUBMERGES.has(id):
			notes.append("SINKS %.0f cm" % (start_low - float(r["float_cm"])))
		r["notes"] = notes
		print(
			(
				"  %-14s %s slip %5.1f (%s)  pop %5.1f (%3.0f%%, %s)  seam %5.1f  under %4.1f  motion %4.1f%% @%.2fs %s"
				% [
					clip,
					flags,
					r["slip_cm"],
					r["slip_bone"],
					r["pop_cm"],
					100.0 * float(r["pop_share"]),
					r["pop_bone"],
					r["seam_cm"],
					r["under_cm"],
					100.0 * float(r["motion_share"]),
					r["peak_s"],
					" ".join(notes),
				]
			)
		)
	missing_rows(id, kind, missing)
	actor.free()


func missing_rows(id: String, kind: String, missing: Array[String]) -> void:
	for m in missing:
		rows.append({"id": id, "kind": kind, "clip": m, "missing": true})


## The whole skinned mesh's lowest point in the current pose (the clip held at its end by _measure's last seek).
func _mesh_lowest(actor: Node3D, skel: Skeleton3D) -> float:
	var low := INF
	for p in _skinned(skel, _samples(actor, 3)):
		low = minf(low, p.y)
	return low if low != INF else 0.0


## Every `stride`-th vertex of every skinned mesh, in _contacts' form (for the lowest point and the motion).
func _samples(actor: Node3D, stride: int) -> Array:
	var all: Array = []
	for mi: MeshInstance3D in actor.find_children("*", "MeshInstance3D", true, false):
		if mi.mesh == null or mi.skin == null:
			continue
		for s in mi.mesh.get_surface_count():
			var arr := mi.mesh.surface_get_arrays(s)
			var verts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
			if arr[Mesh.ARRAY_BONES] == null or verts.is_empty():
				continue
			var bones: PackedInt32Array = arr[Mesh.ARRAY_BONES]
			var weights: PackedFloat32Array = arr[Mesh.ARRAY_WEIGHTS]
			var per := bones.size() / verts.size()
			for v in range(0, verts.size(), stride):
				var bi: Array[int] = []
				var bw: Array[float] = []
				for k in per:
					bi.append(bones[v * per + k])
					bw.append(weights[v * per + k])
				all.append([mi, verts[v], bi, bw])
	return all


## The battle hover (m) the creatures.json row whose scene this is raises the actor by (0 when none).
func _hover(scene_path: String) -> float:
	for row: Variant in (_creatures().get("creatures", {}) as Dictionary).values():
		if row is Dictionary and str(row.get("scene", "")) == scene_path:
			return float(((row as Dictionary).get("stand_in", {}) as Dictionary).get("hover", 0.0))
	return 0.0


## The Skeleton3D the clips drive (a body can carry more than one): the first bone track's node, else the first found.
func _animated_skeleton(anim: AnimationPlayer, skels: Array) -> Skeleton3D:
	var base := anim.get_node_or_null(anim.root_node)
	for name: StringName in anim.get_animation_list():
		var a := anim.get_animation(name)
		for t in a.get_track_count():
			var path := a.track_get_path(t)
			var node := base.get_node_or_null(NodePath(String(path.get_concatenated_names()))) if base != null else null
			if node is Skeleton3D:
				return node as Skeleton3D
	return skels[0] as Skeleton3D


## The actor's rest size: the largest extent of its meshes' bounds (m).
func _size(actor: Node3D) -> float:
	var box := AABB()
	var first := true
	for m: MeshInstance3D in actor.find_children("*", "MeshInstance3D", true, false):
		var b := m.global_transform * m.get_aabb()
		box = b if first else box.merge(b)
		first = false
	return maxf(box.size.x, maxf(box.size.y, box.size.z))


## The skinned mesh's low vertices: [MeshInstance3D, rest positions, bone binds (4 per vertex), weights].
func _contacts(actor: Node3D) -> Array:
	var out: Array = []
	for mi: MeshInstance3D in actor.find_children("*", "MeshInstance3D", true, false):
		if mi.mesh == null or mi.skin == null:
			continue
		for s in mi.mesh.get_surface_count():
			var arr := mi.mesh.surface_get_arrays(s)
			var verts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
			var bones: PackedInt32Array = arr[Mesh.ARRAY_BONES] if arr[Mesh.ARRAY_BONES] != null else PackedInt32Array()
			var weights: PackedFloat32Array = (
				arr[Mesh.ARRAY_WEIGHTS] if arr[Mesh.ARRAY_WEIGHTS] != null else PackedFloat32Array()
			)
			if bones.is_empty() or verts.is_empty():
				continue
			var per := bones.size() / verts.size()
			var xf := mi.global_transform
			for v in verts.size():
				if (xf * verts[v]).y < CONTACT_REST_M:
					var bi: Array[int] = []
					var bw: Array[float] = []
					for k in per:
						bi.append(bones[v * per + k])
						bw.append(weights[v * per + k])
					out.append([mi, verts[v], bi, bw])
	if out.size() > CONTACT_MAX:
		var step := float(out.size()) / CONTACT_MAX
		var picked: Array = []
		for k in CONTACT_MAX:
			picked.append(out[int(k * step)])
		out = picked
	return out


## The contact vertices' world positions in the current pose (linear blend skinning, as the renderer does).
func _skinned(skel: Skeleton3D, contacts: Array) -> PackedVector3Array:
	var out := PackedVector3Array()
	var cache := {}
	for c: Array in contacts:
		var mi := c[0] as MeshInstance3D
		var skin := mi.skin
		var p := Vector3.ZERO
		for k in (c[2] as Array).size():
			var w := float(c[3][k])
			if w <= 0.0:
				continue
			var bind := int(c[2][k])
			var key := Vector2i(mi.get_instance_id() % 100000, bind)
			if not cache.has(key):
				var bone := skin.get_bind_bone(bind)
				if bone < 0:
					bone = skel.find_bone(skin.get_bind_name(bind))
				cache[key] = skel.global_transform * skel.get_bone_global_pose(bone) * skin.get_bind_pose(bind)
			p += w * ((cache[key] as Transform3D) * (c[1] as Vector3))
		out.append(p)
	return out


func _poses(anim: AnimationPlayer, skel: Skeleton3D, t: float) -> PackedVector3Array:
	anim.seek(t, true)
	var out := PackedVector3Array()
	var xf := skel.global_transform
	for b in skel.get_bone_count():
		out.append(xf * skel.get_bone_global_pose(b).origin)
	return out


func _measure(
	anim: AnimationPlayer, skel: Skeleton3D, clip: StringName, size: float, contacts: Array, samples: Array
) -> Dictionary:
	anim.speed_scale = 0.0  # held: only seek() moves it (pause() drops current_animation on some players)
	anim.play(clip, 0.0)
	var a := anim.get_animation(clip)
	var n := maxi(int(ceil(a.length * FPS)), 1)
	var frames: Array[PackedVector3Array] = []
	var touch: Array[PackedVector3Array] = []
	var skin: Array[PackedVector3Array] = []
	var judged := IDLE_CLIPS.has(String(clip)) or HIT_CLIPS.has(String(clip))
	for k in n + 1:
		frames.append(_poses(anim, skel, minf(k / FPS, a.length)))
		touch.append(_skinned(skel, contacts))
		if judged:
			skin.append(_skinned(skel, samples))
	var nb := skel.get_bone_count()
	var nc := contacts.size()
	var lowest := PackedFloat32Array()
	lowest.resize(nc)
	lowest.fill(INF)
	for f in touch:
		for c in nc:
			lowest[c] = minf(lowest[c], f[c].y)
	var slip := 0.0
	var slip_bone := ""
	for c in nc:
		if lowest[c] > FLOOR_M:
			continue
		var start := Vector2.INF
		for k in range(1, touch.size()):
			if touch[k][c].y <= lowest[c] + PLANT_M and touch[k - 1][c].y <= lowest[c] + PLANT_M:
				var here := Vector2(touch[k][c].x, touch[k][c].z)
				if start == Vector2.INF:
					start = Vector2(touch[k - 1][c].x, touch[k - 1][c].z)
				var away := here.distance_to(start)  # how far it has slid from where it planted
				if away > slip:
					slip = away
					slip_bone = "%s@%.2f,%.2f" % [(contacts[c][0] as MeshInstance3D).name, here.x, here.y]
			else:
				start = Vector2.INF
	var pop := 0.0
	var pop_bone := ""
	for k in range(1, frames.size()):
		for b in nb:
			var d := frames[k][b].distance_to(frames[k - 1][b])
			if d > pop:
				pop = d
				pop_bone = skel.get_bone_name(b)
	var seam := 0.0
	if a.loop_mode != Animation.LOOP_NONE:
		for b in nb:
			seam = maxf(seam, frames[-1][b].distance_to(frames[0][b]))
	var under := 0.0
	for c in nc:
		under = maxf(under, -lowest[c])
	var motion := 0.0  # the skin's largest travel from its first frame (bones' origins miss a leaf bone's turn)
	var peak_s := 0.0
	var early := 0.0  # the travel reached by HIT_PEAK_S: a hit reads when most of it comes at once
	var moving := skin if judged else frames
	for k in moving.size():
		for v in moving[k].size():
			var d := moving[k][v].distance_to(moving[0][v])
			if d > motion:
				motion = d
				peak_s = minf(k / FPS, a.length)
			if k / FPS <= HIT_PEAK_S:
				early = maxf(early, d)
	return {
		"slip_cm": 100.0 * slip,
		"slip_bone": slip_bone,
		"pop_cm": 100.0 * pop,
		"pop_share": pop / maxf(size, 0.01),
		"pop_bone": pop_bone,
		"seam_cm": 100.0 * seam,
		"under_cm": 100.0 * under,
		"motion_share": motion / maxf(size, 0.01),
		"peak_s": peak_s,
		"early_share": early / maxf(motion, 1e-6),
		"loop": a.loop_mode != Animation.LOOP_NONE,
		"length": a.length,
	}

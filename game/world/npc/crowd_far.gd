class_name CrowdFar
extends Node3D
## Distant crowds as flipbooks (M5-A3P-1809: Ch20 U04's remembered Reefball crowd needs 30+ held shapes, which is too
## many skinned actors). Each crowd body and clip in the data is posed once at load, `frames` times evenly through the
## clip, and each pose skinned on the CPU into a static mesh (bake). Each pose is one
## MultiMesh holding every person of that body and clip, all in one silhouette material (NpcSilhouette, the held
## shapes' `glow`), and each person shows in exactly one pose at a time: its own phase plus the clock at `fps`. So a
## crowd costs one draw call per body, clip and pose, has no skeletons and no AnimationPlayers, and casts no shadow.
## Deterministic: the phases come from the people's ids, the motion from the frame deltas only.
##
## Data (`data_path`, JSON): `glow` "#RRGGBB", `frames` (the poses per clip), `fps` (poses a second), and `people`:
## [{"id", "body": <crowd body id>, "clip": <its crowd library's clip>, "at": [x, y, z] or [x, y, z, yaw_deg]}].

const CROWD_ACTOR_PATH := "res://assets/crowd/%s/%s_actor.tscn"
## A person not on this pose: drawn at zero scale.
const HIDDEN := Transform3D(Vector3.ZERO, Vector3.ZERO, Vector3.ZERO, Vector3.ZERO)
## Hash salt for a person's phase (HeroIdleMicro.share).
const PHASE_SALT := "crowd_far"

@export_file("*.json") var data_path: String = ""
@export var auto_build := true

var data: Dictionary = {}
var frame_count := 0
var fps := 0.0
var clock := 0.0
## One per body and clip: {"body", "clip", "poses": Array[MultiMeshInstance3D], "places": Array[Transform3D],
## "phases": PackedFloat32Array, "shown": PackedInt32Array (the pose each person is on)}
var groups: Array[Dictionary] = []

var _built := false


func _ready() -> void:
	if auto_build:
		build()
	set_process(auto_build)


func _process(delta: float) -> void:
	step(delta)


## Bakes the poses and places the people (once); returns how many people it placed.
func build() -> int:
	if _built:
		return person_count()
	_built = true
	data = VillagerLayer.load_data(data_path)
	if data.is_empty():
		return 0
	frame_count = int(data["frames"])
	fps = float(data["fps"])
	var material := NpcSilhouette.material_for(Color(str(data["glow"])))
	var by_key: Dictionary = {}
	for row: Variant in data.get("people", []):
		if not row is Dictionary:
			continue
		var r := row as Dictionary
		var key := "%s/%s" % [r["body"], r["clip"]]
		if not by_key.has(key):
			by_key[key] = groups.size()
			groups.append(
				{
					"body": str(r["body"]),
					"clip": StringName(str(r["clip"])),
					"poses": [],
					"places": [],
					"phases": PackedFloat32Array(),
					"shown": PackedInt32Array()
				}
			)
		var g: Dictionary = groups[by_key[key]]
		(g["places"] as Array).append(_place(r["at"]))
		var phases: PackedFloat32Array = g["phases"]
		phases.append(HeroIdleMicro.share(StringName(str(r["id"])), PHASE_SALT))
		g["phases"] = phases
	for g in groups:
		var meshes := bake(str(g["body"]), g["clip"] as StringName, frame_count)
		var n := (g["places"] as Array).size()
		var shown := PackedInt32Array()
		shown.resize(n)
		shown.fill(-1)
		g["shown"] = shown
		for f in meshes.size():
			var mm := MultiMesh.new()
			mm.transform_format = MultiMesh.TRANSFORM_3D
			mm.mesh = meshes[f]
			mm.instance_count = n
			for i in n:
				mm.set_instance_transform(i, HIDDEN)
			var mmi := MultiMeshInstance3D.new()
			mmi.name = "%s_%s_%d" % [g["body"], g["clip"], f]
			mmi.multimesh = mm
			mmi.material_override = material
			mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			add_child(mmi)
			(g["poses"] as Array).append(mmi)
	_show_all()
	return person_count()


func person_count() -> int:
	var n := 0
	for g in groups:
		n += (g["places"] as Array).size()
	return n


## Draw calls (before shadow passes): one per pose MultiMesh.
func draw_calls() -> int:
	var n := 0
	for g in groups:
		n += (g["poses"] as Array).size()
	return n


## The pose person `i` of group `g` is on now.
func pose_of(g: Dictionary, i: int) -> int:
	var poses := (g["poses"] as Array).size()
	if poses == 0:
		return -1
	return posmod(int(floor(clock * fps + float((g["phases"] as PackedFloat32Array)[i]) * poses)), poses)


## One frame: each person whose pose changed moves to it.
func step(delta: float) -> void:
	clock += delta
	_show_all()


func _show_all() -> void:
	for g in groups:
		var poses: Array = g["poses"]
		var places: Array = g["places"]
		var shown: PackedInt32Array = g["shown"]
		for i in places.size():
			var f := pose_of(g, i)
			if f == shown[i]:
				continue
			if shown[i] >= 0:
				(poses[shown[i]] as MultiMeshInstance3D).multimesh.set_instance_transform(i, HIDDEN)
			(poses[f] as MultiMeshInstance3D).multimesh.set_instance_transform(i, places[i] as Transform3D)
			shown[i] = f
		g["shown"] = shown


static func _place(at: Variant) -> Transform3D:
	var a: Array = at
	var yaw := deg_to_rad(float(a[3])) if a.size() > 3 else 0.0
	return Transform3D(Basis(Vector3.UP, yaw), Vector3(float(a[0]), float(a[1]), float(a[2])))


## The crowd body's actor posed at `frames` even points through `clip`, each pose skinned on the CPU into one static
## mesh (every skinned mesh of the actor as a surface, in the actor's space, with no skin; the unskinned eyes are left
## out, inside the head of a silhouette). Skinned here rather than by
## MeshInstance3D.bake_mesh_from_current_skeleton_pose, which needs the renderer's skin registered (it isn't headless,
## so the tests couldn't run it). The actor is a hidden child while it poses and is freed after.
func bake(body: String, clip: StringName, frames: int) -> Array[ArrayMesh]:
	var out: Array[ArrayMesh] = []
	var packed := load(CROWD_ACTOR_PATH % [body, body]) as PackedScene
	if packed == null:
		push_error("CrowdFar: no crowd actor %s" % body)
		return out
	var actor := packed.instantiate() as Node3D
	actor.visible = false
	add_child(actor)
	var anim := HeroMotion.player_of(actor)
	if anim == null or not anim.has_animation(clip):
		push_error("CrowdFar: %s has no clip %s" % [body, clip])
		actor.free()
		return out
	var skinned: Array[MeshInstance3D] = []
	for node: Node in actor.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh != null and mi.skin != null and mi.get_node_or_null(mi.skeleton) is Skeleton3D:
			skinned.append(mi)
	var length := anim.get_animation(clip).length
	anim.play(clip)
	for f in frames:
		anim.seek(length * float(f) / float(frames), true)
		var mesh := ArrayMesh.new()
		for mi in skinned:
			var skel := mi.get_node(mi.skeleton) as Skeleton3D
			var mats := _bind_matrices(mi.skin, skel, _relative(skel, actor))
			for s in mi.mesh.get_surface_count():
				mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, _skinned(mi.mesh.surface_get_arrays(s), mats))
		out.append(mesh)
	actor.free()
	return out


## `node`'s transform in `top`'s space (the parents' local transforms, so it holds off the tree as well).
static func _relative(node: Node3D, top: Node3D) -> Transform3D:
	var xf := Transform3D.IDENTITY
	var n: Node = node
	while n != null and n != top:
		if n is Node3D:
			xf = (n as Node3D).transform * xf
		n = n.get_parent()
	return xf


## Per skin bind: the skeleton (in the actor's space) times the bone's posed global transform times its bind pose.
static func _bind_matrices(skin: Skin, skel: Skeleton3D, skel_xf: Transform3D) -> Array[Transform3D]:
	var mats: Array[Transform3D] = []
	for i in skin.get_bind_count():
		var bone := skin.get_bind_bone(i)
		if bone < 0:
			bone = skel.find_bone(skin.get_bind_name(i))
		var pose := skel.get_bone_global_pose(bone) if bone >= 0 else Transform3D.IDENTITY
		mats.append(skel_xf * pose * skin.get_bind_pose(i))
	return mats


## A surface's arrays skinned by `mats` (linear blend), with the skin dropped.
static func _skinned(arrays: Array, mats: Array[Transform3D]) -> Array:
	var v: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	var bones: PackedInt32Array = arrays[Mesh.ARRAY_BONES]
	var weights: PackedFloat32Array = arrays[Mesh.ARRAY_WEIGHTS]
	var has_n: bool = arrays[Mesh.ARRAY_NORMAL] != null
	var nrm: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL] if has_n else PackedVector3Array()
	var per := bones.size() / maxi(v.size(), 1)
	for k in v.size():
		var p := Vector3.ZERO
		var q := Vector3.ZERO
		for j in per:
			var w := weights[k * per + j]
			if w <= 0.0:
				continue
			var m := mats[bones[k * per + j]]
			p += (m * v[k]) * w
			if has_n:
				q += (m.basis * nrm[k]) * w
		v[k] = p
		if has_n:
			nrm[k] = q.normalized()
	arrays[Mesh.ARRAY_VERTEX] = v
	if has_n:
		arrays[Mesh.ARRAY_NORMAL] = nrm
	arrays[Mesh.ARRAY_TANGENT] = null
	arrays[Mesh.ARRAY_BONES] = null
	arrays[Mesh.ARRAY_WEIGHTS] = null
	return arrays

class_name CutsceneStaging
extends RefCounted
## M4-CIN-1304 (Act II staging, act2_tracks.md: cinematics owns `game/data/cutscene/ch1[0-6]/**`): a zone's cutscene
## shots and marks that are cinematics', not the chapter's field layout. `game/data/cutscene/<location id>.json`
## (e.g. ch10/reedhollow.json) holds {"shots": {id: {pos, look_at, fov}}, "marks": {id: [x, y, z, yaw]}} in the
## zone's frame, the layout's own format. Before a scene plays, every id the stage doesn't already have is added; an
## id the layout has stays the layout's (chapters' field shots and marks are never overridden), unless the file's
## "replace" list names it: a cutscene shot id the layout also uses for another frame, which the scripts mean as
## cinematics' (Ch10's R03 and R06: the chapter's plan named its shots before the scripts were written).

const DIR := "res://game/data/cutscene/%s.json"
## On a shot this file made (a replaced id is replaced once).
const META_STAGED := &"cutscene_staged"


## Adds the zone's staging to `stage` (once; later calls find every id there already). Returns the ids added.
static func apply(stage: CutsceneStage) -> Array[StringName]:
	var added: Array[StringName] = []
	var zone := stage.get_parent() if stage != null else null
	var loc := str(zone.get(&"location_id")) if zone != null and &"location_id" in zone else ""
	if loc == "" or not FileAccess.file_exists(DIR % loc):
		return added
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(DIR % loc))
	if typeof(data) != TYPE_DICTIONARY:
		push_warning("CutsceneStaging: %s is not a JSON object" % (DIR % loc))
		return added
	var replace: Array = (data as Dictionary).get("replace", [])
	var shots := _folder(stage, CutsceneStage.SHOTS, false)
	for id: String in (data as Dictionary).get("shots", {}).keys():
		var row: Dictionary = data["shots"][id]
		var sn := stage.shot_node(StringName(id))
		if sn != null and id in replace and sn.shot != null and not sn.shot.has_meta(META_STAGED):
			sn.shot = _shot(id, row)
			added.append(StringName(id))
		elif sn == null:
			sn = CutsceneShotNode.new()
			sn.name = id
			sn.shot = _shot(id, row)
			shots.add_child(sn)
			added.append(StringName(id))
	var marks := _folder(stage, CutsceneStage.MARKS, true)
	for id: String in (data as Dictionary).get("marks", {}).keys():
		if stage.mark(StringName(id)) == null:
			var p: Array = data["marks"][id]
			var m := Marker3D.new()
			m.name = id
			m.position = _vec3(p)
			m.rotation_degrees.y = float(p[3]) if p.size() > 3 else 0.0
			marks.add_child(m)
			added.append(StringName(id))
	return added


static func _shot(id: String, row: Dictionary) -> CameraShot:
	var shot := CameraShot.new()
	shot.id = StringName(id)
	shot.position = _vec3(row.get("pos", []))
	shot.look_at = _vec3(row.get("look_at", []))
	shot.fov_deg = float(row.get("fov", CameraShot.USE_DEFAULT))
	shot.set_meta(META_STAGED, true)
	return shot


static func _folder(stage: CutsceneStage, path: NodePath, spatial: bool) -> Node:
	var f := stage.get_node_or_null(path)
	if f == null:
		f = Node3D.new() if spatial else Node.new()
		f.name = String(path)
		stage.add_child(f)
	return f


static func _vec3(a: Array) -> Vector3:
	return Vector3(float(a[0]), float(a[1]), float(a[2])) if a.size() >= 3 else Vector3.ZERO

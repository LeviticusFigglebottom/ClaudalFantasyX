class_name CutsceneStage
extends Node3D
## Where a `.dlg` cutscene plays (M2-FP-01; docs/kb/tech/cutscenes.md). A zone adds one of these
## and the CutsceneSequencer resolves every cue id against it:
##   Shots/<ID>    CutsceneShotNode children, each holding a CameraShot. The id is `shot.id`, or the
##                 node name when that is empty (`@camera H05` finds Shots/H05).
##   Actors/<id>   one Node3D per speaker id, lowercase (`@anim asha ...` moves Actors/asha). The
##                 player stands in for `rhen` when there is no Actors/rhen.
##   Marks/<id>    Marker3D per scene mark: `@mark` targets, `@vfx at=` and `@sfx at=` places, and
##                 `@anim <actor> look_at <target>` targets (a mark or an actor).
## A missing id is a soft failure (the sequencer warns once and carries on), so a rough stage can
## play a finished script.

const SHOTS := ^"Shots"
const ACTORS := ^"Actors"
const MARKS := ^"Marks"
const PLAYER_ACTOR := &"rhen"

## The zone's FieldCameraDirector. Empty = the first FieldCameraDirector under the stage's parent.
@export var director_path: NodePath
## The zone's FieldController. Empty = the first node in group "player", or a sibling named Player.
@export var player_path: NodePath
## Placeholder staging until the rigs have clips: "<actor>/<clip>" -> mark id. When `@anim <actor>
## <clip>` plays a listed clip, the actor is placed on that mark and turned to its facing (-Z), so
## `@anim asha emerge_doorway` can put her in the doorway before there is an animation to walk her.
@export var clip_marks: Dictionary = {}


func director() -> FieldCameraDirector:
	var d := get_node_or_null(director_path) as FieldCameraDirector if director_path != NodePath() else null
	if d == null and get_parent() != null:
		d = _find_type(get_parent(), &"FieldCameraDirector") as FieldCameraDirector
	return d


func player() -> FieldController:
	var p := get_node_or_null(player_path) as FieldController if player_path != NodePath() else null
	if p == null and is_inside_tree():
		p = get_tree().get_first_node_in_group(&"player") as FieldController
	if p == null and get_parent() != null:
		p = get_parent().get_node_or_null(^"Player") as FieldController
	return p


## The authored CameraShot for `id`, or null.
func shot(id: StringName) -> CameraShot:
	var folder := get_node_or_null(SHOTS)
	if folder == null:
		return null
	for child in folder.get_children():
		var sn := child as CutsceneShotNode
		if sn != null and sn.shot != null and sn.shot_id() == id:
			return sn.shot
	return null


func shot_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	var folder := get_node_or_null(SHOTS)
	if folder != null:
		for child in folder.get_children():
			if child is CutsceneShotNode and (child as CutsceneShotNode).shot != null:
				out.append((child as CutsceneShotNode).shot_id())
	return out


## The actor node for a speaker id (lowercase), the player for `rhen` when no actor is authored.
func actor(id: StringName) -> Node3D:
	var a := get_node_or_null(NodePath("%s/%s" % [ACTORS, id])) as Node3D
	if a == null and id == PLAYER_ACTOR:
		a = player()
	return a


func mark(id: StringName) -> Node3D:
	return get_node_or_null(NodePath("%s/%s" % [MARKS, id])) as Node3D


## The mark a placeholder clip stands for (`clip_marks`), or null.
func clip_mark(actor_id: StringName, clip: StringName) -> Node3D:
	var key := "%s/%s" % [actor_id, clip]
	return mark(StringName(str(clip_marks[key]))) if clip_marks.has(key) else null


## A mark, else an actor:`@anim asha look_at rhen_lantern` and `at=asha` both resolve here.
func place(id: StringName) -> Node3D:
	var m := mark(id)
	return m if m != null else actor(id)


static func _find_type(root: Node, type_name: StringName) -> Node:
	for child in root.get_children():
		var s := child.get_script() as Script
		if s != null and s.get_global_name() == type_name:
			return child
		var found := _find_type(child, type_name)
		if found != null:
			return found
	return null

class_name CutsceneTrack
extends Node
## M4-CIN-1302 (act2_ch10.md B01 O02, "the camera does not stop with Pell"): `@camera <shot> track=<actor>` plays a
## copy of the shot that keeps its offset to a moving actor, so one authored frame becomes one continuous move (the
## layout's shots are fixed). Each frame the copy's position and look_at move by how far the actor has moved since
## the cue; the director evaluates a fixed shot from those every frame, so the move is as smooth as the actor's walk.
## The tracker ends itself once the director is on any other shot (the next @camera, a release, the scene's end).

const NODE_NAME := "CameraTrack"

## The copy the director is playing.
var shot: CameraShot
var actor: Node3D
var director: FieldCameraDirector

var _from: Vector3
var _pos: Vector3
var _look: Vector3


## The shot to play for `source` tracking `who`, with a tracker under `host` (replacing any earlier one). With no
## actor it is `source` itself and no tracker.
static func attach(host: Node, source: CameraShot, who: Node3D, dir: FieldCameraDirector) -> CameraShot:
	var old := host.get_node_or_null(NODE_NAME)
	if old != null:
		host.remove_child(old)
		old.queue_free()
	if who == null or source == null:
		return source
	var t := CutsceneTrack.new()
	t.name = NODE_NAME
	t.shot = source.duplicate() as CameraShot
	t.actor = who
	t.director = dir
	t._from = who.global_position
	t._pos = source.position
	t._look = source.look_at
	host.add_child(t)
	return t.shot


func _process(_delta: float) -> void:
	update()


## Moves the shot with the actor; frees the tracker once the director has left the shot. False when it has ended.
func update() -> bool:
	if not is_instance_valid(actor) or not is_instance_valid(director) or director.active_shot != shot:
		queue_free()
		return false
	var moved := actor.global_position - _from
	if director.rail_root != null:
		moved = director.rail_root.global_basis.inverse() * moved
	shot.position = _pos + moved
	shot.look_at = _look + moved
	return true

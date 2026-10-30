class_name CodexRecordSpot
extends RefCounted
## A codex record in the field (M3-UI-03, M3-NAR-01): an ordinary Interactable (INTERACT, "Examine") whose payload
## names the record, so CodexNotice marks `codex_<id>_found` and shows "Record added to the Codex". Once only: a
## record is found, not reread in the field (the codex keeps it).

const PROMPT_KEY := "FIELD_PROMPT_DEFAULT"


## The record `record_id` at `at`, reachable within `reach_m` (a sphere).
static func make(record_id: String, at: Vector3, reach_m: float) -> Interactable:
	var it := Interactable.new()
	it.name = "Record_%s" % record_id
	it.id = StringName(record_id)
	it.prompt_key = PROMPT_KEY
	it.once = true
	it.payload = {"record": record_id}
	it.position = at
	var ss := SphereShape3D.new()
	ss.radius = reach_m
	var shape := CollisionShape3D.new()
	shape.shape = ss
	it.add_child(shape)
	return it

class_name Ch04Zone
extends Ch01Zone
## A Ch4 greybox zone root (M3-C04-02; docs/kb/tech/chapter_flow.md "Ch4"). It reuses Ch01Zone's story
## calls as they are (rest, give, hide_block / show_block; Ch1's tutorial prompt table goes unused
## here, because Ch4's prompts are battle prompts) and adds the one thing Ch4's two zones need: a zone
## whose dressing follows the story flags, so it comes back right after a battle or a reload.
##   layout "states": [{"flag": f, "hide": [ids], "show": [ids], "place": {actor id: mark id}}]
##     Applied in order once the zone is ready, and again by refresh_states() (a `zone` step after a
##     scene that set a flag). Each row whose flag is set hides and shows its Greybox blocks or stage
##     actors (Ch01Zone.hide_block / show_block: a block's collision goes with it), and stands the
##     stage actors it places on those marks. Rhen is never one.
## Haluna's wake-night uses it for the windows going dark, Asha's shell in the wall, the village going
## home and the stranger at the wall; the ferry for the party crossing to the derelict and back, its
## sails, the wraith and the board. A battle reloads the zone, so this is what keeps it right.
## Kit collision (ADR 0200), for a zone dressed with env-art's kit on heights the flat greybox can't hold:
##   layout "collision_path": a JSON file whose "blocks" and "ramps" join the layout's own (generated
##     from the kit by tools/act1/, so the hand-written layout keeps only the story).
##   "ramps": [{"id", "from": [x, y, z], "to": [x, y, z], "width", "thick"?, "color"?}] a solid slab
##     whose top runs from `from` to `to` (a stair's flight: the controller has no step-up, so stairs
##     are ramps under 45 deg). Built under Greybox/<id> like a block, so hide_block works on it.

const KEY_STATES := "states"
const KEY_PLACE := "place"
const KEY_COLLISION := "collision_path"
const KEY_RAMPS := "ramps"
const KEY_BLOCKS := "blocks"
const RAMP_THICK_M := 0.4


func _ready() -> void:
	super()
	refresh_states()


## The layout's blocks plus its collision file's; then the ramps.
func _build_blocks() -> void:
	var extra: Dictionary = read_json(str(layout[KEY_COLLISION])) if layout.has(KEY_COLLISION) else {}
	for key: String in [KEY_BLOCKS, KEY_RAMPS]:
		if extra.has(key):
			var rows: Array = (layout.get(key, []) as Array).duplicate()
			rows.append_array(extra[key])
			layout[key] = rows
	super()
	var root := get_node(NodePath(String(GREYBOX)))
	for r: Dictionary in layout.get(KEY_RAMPS, []):
		root.add_child(ramp(r, str(r.get("color", setting("block_color")))))


## A ramp row as a solid slab (not added to the tree): a StaticBody3D named by its id, with a Mesh and
## a Shape like a block's, its top face running from "from" to "to".
static func ramp(r: Dictionary, color: String) -> StaticBody3D:
	var a := _vec3(r.get("from", [0, 0, 0]))
	var b := _vec3(r.get("to", [0, 0, 1]))
	var size := Vector3(float(r.get("width", 2.0)), float(r.get("thick", RAMP_THICK_M)), a.distance_to(b))
	var basis := Basis.looking_at(b - a, Vector3.UP)
	var body := StaticBody3D.new()
	body.name = str(r.get("id", "Ramp"))
	body.transform = Transform3D(basis, (a + b) * 0.5 - basis.y * size.y * 0.5)
	var mesh := BoxMesh.new()
	mesh.size = size
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color.html(color)
	mesh.material = mat
	var mi := MeshInstance3D.new()
	mi.name = "Mesh"
	mi.mesh = mesh
	body.add_child(mi)
	var shape := BoxShape3D.new()
	shape.size = size
	var cs := CollisionShape3D.new()
	cs.name = "Shape"
	cs.shape = shape
	body.add_child(cs)
	return body


## Applies every "states" row whose flag is set (see the class comment).
func refresh_states() -> void:
	for row: Dictionary in layout.get(KEY_STATES, []):
		if not bool(Game.get_flag(StringName(str(row.get("flag", ""))))):
			continue
		for id: Variant in row.get("hide", []):
			hide_block(str(id))
		for id: Variant in row.get("show", []):
			show_block(str(id))
		var place: Dictionary = row.get(KEY_PLACE, {})
		for id: Variant in place:
			place_actor(str(id), str(place[id]))


## Stands stage actor `id` on mark `mark_id` (its position and facing). False when either is missing.
func place_actor(id: String, mark_id: String) -> bool:
	var a := stage.actor(StringName(id))
	var m := stage.mark(StringName(mark_id))
	if a == null or m == null or a is FieldController:
		push_warning("Ch04Zone %s: cannot place '%s' on '%s'" % [location_id, id, mark_id])
		return false
	a.transform = m.transform  # Actors/ and Marks/ are sibling groups of the stage: one frame
	return true

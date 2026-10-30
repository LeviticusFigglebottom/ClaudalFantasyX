class_name PropAudio
extends RefCounted
## Cinematics' staged practicals that sound (prop_sfx.json; the Lead's 10-30 18:45 item). A prop whose scene is a
## `props` row gets a looping AudioStreamPlayer3D child when it enters the tree (the hearth in Quellan's inn); the
## loop goes with the prop. **Listens only**: it adds a player under the prop and never touches the prop otherwise.

const PLAYER := &"PropLoop"

## prop_sfx.json.
var data: Dictionary = {}


func _init(table: Dictionary = {}) -> void:
	data = table


## The row for `node` (its scene path), or {} when it has none.
func row_for(node: Node) -> Dictionary:
	if not node is Node3D or node.scene_file_path == "":
		return {}
	return (data.get("props", {}) as Dictionary).get(node.scene_file_path, {}) as Dictionary


func wants(node: Node) -> bool:
	return not row_for(node).is_empty()


## Starts `prop`'s loop (once).
func attach(prop: Node) -> AudioStreamPlayer3D:
	var row := row_for(prop)
	if row.is_empty() or not is_instance_valid(prop) or prop.has_node(NodePath(String(PLAYER))):
		return null
	var stream := load(str(row.get("file", ""))) as AudioStream
	if stream == null:
		return null
	var p := AudioStreamPlayer3D.new()
	p.name = PLAYER
	p.stream = stream
	p.bus = StringName(str(row.get("bus", "World")))
	p.volume_db = float(row.get("volume_db", 0.0))
	p.unit_size = float(row.get("unit_size_m", 3.0))
	p.position = Vector3(0.0, float(row.get("height_m", 0.0)), 0.0)
	prop.add_child(p)
	if p.is_inside_tree():
		p.play()
	return p

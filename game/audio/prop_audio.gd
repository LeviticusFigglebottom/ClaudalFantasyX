class_name PropAudio
extends RefCounted
## Cinematics' staged practicals that sound (prop_sfx.json; the Lead's 10-30 18:45 item). A prop whose scene is a
## `props` row gets a looping AudioStreamPlayer3D child when it enters the tree (the hearth in Quellan's inn); the
## loop goes with the prop. **Listens only**: it adds a player under the prop and never touches the prop otherwise.
## The `flames` row (the Lead's 10-30 21:05 item, env-art-b's ambient life): a zone's ZoneKitDressing gets a small loop
## on each warm `fire_lights` row that flickers (`flicker` >= min_flicker), once its lights are placed (`dressed`).
## The bound-teal lamps flicker too but aren't flames: a light whose colour is cooler than warm (blue over red) is
## left silent.
## A props row with `light` names an OmniLight3D in the prop (the Ch13 Archive's lamp): the loop's level follows that
## light's energy, so a scene's `@light <name> off` puts the flame's sound out with its light. step() reads it.

const PLAYER := &"PropLoop"
const FLAME_PLAYER := &"FlameLoop"
## ZoneKitDressing's own names: its light root, the layout key, a row's flicker share.
const FIRE_LIGHTS := &"FireLights"
const KEY_FIRE := "fire_lights"
const KEY_FLICKER := "flicker"
## Marks a dressing whose flames wait on its `dressed`.
const META_WAITING := &"audio_flames_waiting"
## A flame's start in its loop from its position (s per metre of x and of z), so a row never breathes in step.
const FLAME_PHASE := Vector2(7.3, 3.1)

## prop_sfx.json.
var data: Dictionary = {}
## Loops that follow a light: [player, light, the light's energy at attach, the player's volume_db].
var followers: Array[Array] = []


func _init(table: Dictionary = {}) -> void:
	data = table


## The row for `node` (its scene path), or {} when it has none.
func row_for(node: Node) -> Dictionary:
	if not node is Node3D or node.scene_file_path == "":
		return {}
	return (data.get("props", {}) as Dictionary).get(node.scene_file_path, {}) as Dictionary


func wants(node: Node) -> bool:
	return not row_for(node).is_empty() or (node is ZoneKitDressing and data.has("flames"))


## Starts `prop`'s loop (once); a zone's dressing gets its flames instead.
func attach(prop: Node) -> AudioStreamPlayer3D:
	if prop is ZoneKitDressing:
		attach_flames(prop as ZoneKitDressing)
		return null
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
	var light := prop.find_child(str(row.get("light", "")), true, false) as Light3D if row.has("light") else null
	if light != null and light.light_energy > 0.0:
		followers.append([p, light, light.light_energy, p.volume_db])
	return p


## Each frame (AudioDirector): a light-following loop sits at its light's share of the energy it started with, and
## stops when the light is out.
func step() -> void:
	var alive: Array[Array] = []
	for f: Array in followers:
		var p := f[0] as AudioStreamPlayer3D
		var light := f[1] as Light3D
		if not is_instance_valid(p) or not is_instance_valid(light):
			continue
		var share := clampf(light.light_energy / float(f[2]), 0.0, 1.0)
		if share <= 0.0:
			p.stop()
			continue
		p.volume_db = float(f[3]) + linear_to_db(share)
		alive.append(f)
	followers = alive


## Starts a loop under each warm flickering flame of `dressing` (once each), now if its lights are placed, else when it
## is dressed. Returns the players started.
func attach_flames(dressing: ZoneKitDressing) -> Array[AudioStreamPlayer3D]:
	var started: Array[AudioStreamPlayer3D] = []
	var row: Dictionary = data.get("flames", {})
	if row.is_empty() or not is_instance_valid(dressing):
		return started
	var root := dressing.get_node_or_null(NodePath(String(FIRE_LIGHTS)))
	if root == null:
		if not dressing.has_meta(META_WAITING):
			dressing.set_meta(META_WAITING, true)
			dressing.dressed.connect(_on_dressed.bind(dressing), CONNECT_ONE_SHOT)
		return started
	var stream := load(str(row.get("file", ""))) as AudioStream
	if stream == null:
		return started
	var rows: Array = dressing.layout.get(KEY_FIRE, [])
	var lights := root.get_children()
	for i in mini(rows.size(), lights.size()):
		var light := lights[i] as OmniLight3D
		var share := float((rows[i] as Dictionary).get(KEY_FLICKER, 0.0))
		if light == null or share < float(row.get("min_flicker", 0.0)) or not is_flame(light.light_color):
			continue
		if light.has_node(NodePath(String(FLAME_PLAYER))):
			continue
		var p := AudioStreamPlayer3D.new()
		p.name = FLAME_PLAYER
		p.stream = stream
		p.bus = StringName(str(row.get("bus", "World")))
		p.volume_db = float(row.get("volume_db", 0.0))
		p.unit_size = float(row.get("unit_size_m", 1.0))
		p.max_distance = float(row.get("max_distance_m", 0.0))
		light.add_child(p)
		if p.is_inside_tree():
			var at := light.position.x * FLAME_PHASE.x + light.position.z * FLAME_PHASE.y
			p.play(fposmod(at, stream.get_length()))
		started.append(p)
	return started


## A flame's light is warm: more red than blue (the zone's fire colour, never the bound teal).
static func is_flame(c: Color) -> bool:
	return c.r > c.b


func _on_dressed(dressing: ZoneKitDressing) -> void:
	dressing.remove_meta(META_WAITING)
	attach_flames(dressing)

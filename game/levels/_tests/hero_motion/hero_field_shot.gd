extends Node3D
## Screenshot rig for the field hero bodies (M2-HER-1101/1102, shots field_hero_rhen_walk and
## field_hero_party). Builds a lit greybox floor, a FieldController with the zone capsule stand-in (the
## hook swaps in Rhen) and a fixed camera, then walks the player a fixed number of fixed steps through
## the same calls the game makes (FieldController.step, HeroFieldParty.advance, HeroFieldActor.advance)
## and freezes everything, so the frame is the same on every run. `party` adds Asha and Toma on the
## trail (an arc); otherwise a grey capsule of the stand-in's size stands beside Rhen for scale.
## Numbers: game/levels/_tests/hero_motion/hero_field_shot.json.

const DATA_PATH := "res://game/levels/_tests/hero_motion/hero_field_shot.json"

@export var party := false

var player: FieldController


func _ready() -> void:
	var all: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	var d := (all as Dictionary).get("party" if party else "solo", {}) as Dictionary
	var common := (all as Dictionary).get("common", {}) as Dictionary
	_build_world(common)
	if party:
		Game.state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
	else:
		Game.state.party_ids = [&"rhen"] as Array[StringName]
	player = _make_player(common, "Player", _v3(d["start"]), deg_to_rad(float(d["start_yaw_deg"])))
	if not party:
		var ref := _capsule(common, "ScaleCapsule")
		ref.position += _v3(d["scale_capsule_at"])  # beside where the walk ends
		add_child(ref)
	_walk(d)
	# the camera frames where the walk ended (offsets from the leader's feet)
	var cam := Camera3D.new()
	cam.name = "ShotCamera"
	cam.fov = float(d["fov_deg"])
	add_child(cam)
	var at := player.global_position
	cam.look_at_from_position(at + _v3(d["camera_offset"]), at + _v3(d["look_offset"]))
	cam.current = true


## A FieldController with the greybox capsule (the hook swaps in the leader's body) at `at`, facing
## `yaw`, added under this node with its own physics and input off (the rig steps it).
func _make_player(common: Dictionary, node_name: String, at: Vector3, yaw: float) -> FieldController:
	var c := FieldController.new()
	c.name = node_name
	var shape := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = float(common["capsule_radius_m"])
	cap.height = float(common["capsule_height_m"])
	shape.shape = cap
	shape.position.y = cap.height * 0.5
	c.add_child(shape)
	c.add_child(_capsule(common, "StandIn"))
	c.position = at
	c.rotation.y = yaw
	add_child(c)
	c.set_physics_process(false)
	c.set_process_unhandled_input(false)
	return c


func _walk(d: Dictionary) -> void:
	var dt := 1.0 / float(d["fps"])
	var body := player.get_node(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor
	var group := player.get_node(NodePath(String(HeroFieldParty.NAME))) as HeroFieldParty
	group.set_physics_process(false)
	body.set_process(false)
	group.advance(dt)
	for leg: Dictionary in d["legs"]:
		var stick := Vector2(float(leg["stick"][0]), float(leg["stick"][1]))
		for i in int(leg["frames"]):
			player.input_override = stick.rotated(deg_to_rad(float(leg.get("curve_deg_per_frame", 0.0)) * i))
			player.walk_override = bool(leg.get("walk", false))
			player.step(dt)
			group.advance(dt)
			body.advance(dt)
			for f in group.followers:
				var fb := f.get_node(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor
				fb.set_process(false)
				fb.advance(dt)


func _build_world(c: Dictionary) -> void:
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color.html(str(c["sky"]))
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color.html(str(c["ambient"]))
	e.ambient_light_energy = float(c["ambient_energy"])
	e.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.environment = e
	add_child(env)
	var sun := DirectionalLight3D.new()
	sun.shadow_enabled = true
	sun.light_energy = float(c["sun_energy"])
	add_child(sun)
	sun.rotation_degrees = _v3(c["sun_rot_deg"])
	var floor_body := StaticBody3D.new()
	var fs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = _v3(c["floor_size"])
	fs.shape = box
	fs.position.y = -box.size.y * 0.5
	floor_body.add_child(fs)
	var fm := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = box.size
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color.html(str(c["floor_color"]))
	bm.material = mat
	fm.mesh = bm
	fm.position.y = -box.size.y * 0.5
	floor_body.add_child(fm)
	add_child(floor_body)


func _capsule(c: Dictionary, node_name: String) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.name = node_name
	var m := CapsuleMesh.new()
	m.radius = float(c["capsule_radius_m"])
	m.height = float(c["capsule_height_m"])
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color.html(str(c["capsule_color"]))
	m.material = mat
	mi.mesh = m
	mi.position.y = m.height * 0.5
	return mi


static func _v3(a: Variant) -> Vector3:
	var arr := a as Array
	return Vector3(float(arr[0]), float(arr[1]), float(arr[2]))

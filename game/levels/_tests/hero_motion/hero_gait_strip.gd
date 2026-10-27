extends "res://game/levels/_tests/hero_motion/hero_field_shot.gd"
## Screenshot rig for the field gait clips (M2-HER-1107, shot field_hero_gait_strip): Rhen on the field
## player, frozen at successive frames and stood side by side, one row each for a run start from rest, a
## run stop, and a turn in place. Each copy is its own FieldController driven through the same calls the
## game makes (FieldController.step, HeroFieldActor.advance) for its row's frame count, then its body is
## moved onto its slot in the row (yaw and pose kept), so one image shows the whole move. Without
## M2-CHR-12's clips the rows show the plain blend and eased spin. Numbers: hero_gait_strip.json.

const STRIP_PATH := "res://game/levels/_tests/hero_motion/hero_gait_strip.json"


func _ready() -> void:
	var all: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	var common := (all as Dictionary).get("common", {}) as Dictionary
	var d: Variant = JSON.parse_string(FileAccess.get_file_as_string(STRIP_PATH))
	var strip := d as Dictionary
	_build_world(common)
	Game.state.party_ids = [&"rhen"] as Array[StringName]
	var dt := 1.0 / float(strip["fps"])
	var spacing := float(strip["spacing_m"])
	var sim_gap := float(strip["sim_gap_m"])
	var rows: Array = strip["rows"]
	for r in rows.size():
		var row := rows[r] as Dictionary
		var counts: Array = row["frames"]
		for j in counts.size():
			var sim_at := Vector3(float(j) * sim_gap, 0.0, float(r) * sim_gap) + _v3(strip["sim_origin"])
			var c := _make_player(common, "Copy%d_%d" % [r, j], sim_at, deg_to_rad(float(strip["start_yaw_deg"])))
			var body := c.get_node(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor
			var group := c.get_node(NodePath(String(HeroFieldParty.NAME))) as HeroFieldParty
			group.set_physics_process(false)
			group.set_process(false)
			body.set_process(false)
			_play_row(c, body, row, int(counts[j]), dt, int(strip["rest_frames"]))
			var slot := Vector3(
				(float(j) - float(counts.size() - 1) * 0.5) * spacing, 0.0, -float(r) * float(strip["row_gap_m"])
			)
			body.global_position = slot
	var cam := Camera3D.new()
	cam.name = "ShotCamera"
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.size = float(strip["camera_size_m"])
	add_child(cam)
	cam.look_at_from_position(_v3(strip["camera_at"]), _v3(strip["look_at"]))
	cam.current = true


## Rest, then the row's move for `n` frames: `run_frames` of `stick` first for a stop row, `turn_deg` of
## facing change for a turn row.
func _play_row(c: FieldController, body: HeroFieldActor, row: Dictionary, n: int, dt: float, rest: int) -> void:
	var stick := _v2(row.get("stick", [0.0, 0.0]))
	for i in rest:
		_frame(c, body, Vector2.ZERO, dt)
	for i in int(row.get("run_frames", 0)):
		_frame(c, body, stick, dt)
	if row.has("turn_deg"):
		c.motor.facing_yaw = wrapf(c.motor.facing_yaw + deg_to_rad(float(row["turn_deg"])), -PI, PI)
		stick = Vector2.ZERO
	elif row.has("run_frames"):
		stick = Vector2.ZERO
	for i in n:
		_frame(c, body, stick, dt)


func _frame(c: FieldController, body: HeroFieldActor, stick: Vector2, dt: float) -> void:
	c.input_override = stick
	c.step(dt)
	body.advance(dt)


static func _v2(a: Variant) -> Vector2:
	var arr := a as Array
	return Vector2(float(arr[0]), float(arr[1]))

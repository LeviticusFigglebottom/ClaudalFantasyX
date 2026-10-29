extends TestCase
## M2-FP-120: CutsceneGrade puts a zone grade row (an Environment and its sun) on a stage's level and takes it off;
## `@vfx form=` stands a bound field's motes on a creature's outline (CutsceneVfx, glimmer_forms.json).

const GRADE := &"ch05_harbour_dusk"  # env-art's Ch5 row (assets/environments/zones/ch05/ch05_grades.json)

var level: Node3D
var stage: Node3D
var world_env: WorldEnvironment
var sun: DirectionalLight3D
var base_env: Environment


func before_each() -> void:
	level = Node3D.new()
	world_env = WorldEnvironment.new()
	base_env = Environment.new()
	world_env.environment = base_env
	level.add_child(world_env)
	sun = DirectionalLight3D.new()
	sun.name = "Sun"
	level.add_child(sun)
	stage = Node3D.new()
	level.add_child(stage)
	stage.owner = level
	sun.light_energy = 1.0


func after_each() -> void:
	level.free()


func test_a_grade_row_swaps_the_look_and_restore_puts_it_back() -> void:
	assert_true(CutsceneGrade.has_grade(GRADE), "the zones' grade tables are read")
	var g := CutsceneGrade.new()
	assert_true(g.apply(stage, GRADE))
	var row: Dictionary = CutsceneGrade.table()[GRADE]
	assert_true(world_env.environment != base_env, "a copy of the grade's Environment is on")
	assert_eq(world_env.environment.resource_path, "", "a copy, never the shared resource")
	assert_between(sun.light_energy, float(row["sun"]["energy"]) - 0.001, float(row["sun"]["energy"]) + 0.001)
	assert_between(
		sun.rotation_degrees.x, float(row["sun"]["pitch_deg"]) - 0.001, float(row["sun"]["pitch_deg"]) + 0.001
	)
	assert_eq(g.active, GRADE)
	g.restore()
	assert_eq(world_env.environment, base_env, "the level's own Environment is back")
	assert_between(sun.light_energy, 1.0 - 0.001, 1.0 + 0.001)
	assert_eq(g.active, &"")


func test_an_unbuilt_grade_changes_nothing() -> void:
	var g := CutsceneGrade.new()
	assert_false(g.apply(stage, &"no_such_grade"))
	assert_eq(world_env.environment, base_env)
	g.restore()
	assert_eq(world_env.environment, base_env)


func test_a_form_stands_one_mote_on_each_outline_point() -> void:
	var host := Node3D.new()
	level.add_child(host)
	var holder := Node.new()
	holder.add_user_signal("done")
	var done := Signal(holder, "done")
	var row := {"center_y_m": 0.0, "spread_m": 0.8}
	var field := CutsceneVfx.spawn(row, "glimmer_bound", {"form": "ilun"}, host, "Form", done)
	assert_true(field != null)
	var forms: Dictionary = GreyboxZone.read_json(CutsceneVfx.FORMS_PATH)["forms"]
	var points: Array = forms["ilun"]["points"]
	assert_eq(field.spawn_points.size(), points.size())
	assert_eq(field.fixed_count, points.size(), "one mote a point")
	assert_false(field.respawn, "held: nothing sheds or respawns")
	var body := field.get_node_or_null(^"Form") as Node3D
	assert_true(body != null, "the creature's own body stands in the field")
	var mesh := body.find_children("*", "MeshInstance3D", true, false)[0] as MeshInstance3D
	var mat := mesh.material_override as StandardMaterial3D
	assert_true(mat.emission.is_equal_approx(field.current_color()), "in the field's own bound colour")
	assert_true(mat.albedo_color.a < 1.0, "translucent")
	assert_true(
		CutsceneVfx.spawn(row, "glimmer_bound", {"form": "nobody"}, host, "None", done) == null, "an unknown form"
	)
	holder.free()

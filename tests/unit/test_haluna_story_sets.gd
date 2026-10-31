extends TestCase
## M3-ENV-709: HalunaDresser builds the layout's "story_sets" as hidden StorySet_<name> nodes that a chapter's zone
## shows by flag: Ch4's wake night (about 100 lamps, the feast, its warm lights) and the wake shells' states.

const LAYOUT := "res://game/levels/ch02/haluna/haluna_layout.json"
const MIN_WAKE_LAMPS := 100
const WAKE_LIGHTS := 14  # ten round the wall and the feast, four out along the dock (PC pass 7 row 24)


func _dresser() -> HalunaDresser:
	var dresser := HalunaDresser.new()
	dresser.layout = HalunaDresser._load_json(LAYOUT)
	dresser._place_story_sets(dresser.layout.get("story_sets", {}))
	return dresser


## Placed pieces of a kind: Godot renames clashing siblings, so count by the piece's own mesh inside each.
func _count(root: Node, piece: String) -> int:
	return root.get_children().filter(func(n: Node) -> bool: return n.find_child(piece, true, false) != null).size()


func test_the_wake_night_is_a_hidden_set_with_its_lamps_and_lights() -> void:
	var dresser := _dresser()
	var wake := dresser.story_set(&"ch04_wake")
	assert_true(wake != null, "the wake night set exists")
	if wake != null:
		assert_false(wake.visible, "hidden until Ch4 shows it")
		assert_true(_count(wake, "ground_lamp") >= MIN_WAKE_LAMPS, "about a hundred oil lamps")
		assert_true(_count(wake, "feast_mat") > 0, "the feast on the sand")
		var lights := wake.get_children().filter(func(n: Node) -> bool: return n is OmniLight3D)
		assert_eq(lights.size(), WAKE_LIGHTS, "its warm lights")
		for light: OmniLight3D in lights:
			assert_eq(light.light_volumetric_fog_energy, 0.0, "no fog banding (the fog-lamp rule)")
	assert_true(dresser.story_set(&"no_such_set") == null, "an unknown set is null")
	dresser.free()


func test_the_shell_states_override_the_shell_material() -> void:
	var dresser := _dresser()
	for pair: Array in [
		[&"ch04_shell_asha", "kit_wake_shell_inked"],
		[&"ch04_shell_imra_faded", "kit_wake_shell_faded"],
		[&"ch04_shell_imra_inked", "kit_wake_shell_inked"]
	]:
		var set_node := dresser.story_set(pair[0])
		assert_true(set_node != null, "%s exists" % pair[0])
		if set_node == null:
			continue
		var meshes := set_node.find_children("wake_shell_single", "MeshInstance3D", true, false)
		var shell := (meshes[0] if not meshes.is_empty() else null) as MeshInstance3D
		assert_true(shell != null, "%s holds a wake shell" % pair[0])
		if shell == null:
			continue
		var names: Array[String] = []
		for i in shell.mesh.get_surface_count():
			var mat := shell.get_surface_override_material(i)
			names.append(mat.resource_path.get_file().get_basename() if mat != null else "")
		assert_true(names.has(String(pair[1])), "%s wears %s" % [pair[0], pair[1]])
	dresser.free()

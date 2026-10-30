extends TestCase
## M4-A2P-054: Kerrid's rope-burn light is dark by default, lights per instance, lerps held -> lift, and his VFX sockets
## are there for M4-A2P-049's motes (KerridBurnGlow).

const MODEL := "res://assets/characters/kerrid/kerrid.glb"


func _burns(root: Node) -> MeshInstance3D:
	return root.find_children("Burns", "MeshInstance3D", true, false)[0] as MeshInstance3D


func test_dark_by_default_then_lit_per_instance() -> void:
	var a := (load(MODEL) as PackedScene).instantiate()
	var b := (load(MODEL) as PackedScene).instantiate()
	var base := _burns(a).get_active_material(0) as StandardMaterial3D
	assert_eq(base.emission_energy_multiplier, 0.0, "Ch5-Ch9: no light")
	var d := KerridBurnGlow.data()
	assert_eq(KerridBurnGlow.apply(a, float(d["ch15_peak"])), 1)
	var lit := _burns(a).get_active_material(0) as StandardMaterial3D
	var want := float(d["ch15_peak"]) * float(d["energy_per_unit"])
	assert_between(lit.emission_energy_multiplier, want - 1e-5, want + 1e-5)
	var other := _burns(b).get_active_material(0) as StandardMaterial3D
	assert_eq(other.emission_energy_multiplier, 0.0, "another Kerrid stays dark")
	assert_eq(KerridBurnGlow.apply(a, 2.0), 1)
	var top := float(d["energy_per_unit"])
	assert_between(lit.emission_energy_multiplier, top - 1e-5, top + 1e-5, "clamped to 1")
	a.free()
	b.free()


func test_lift_lerps_held_to_released_gold() -> void:
	var root := (load(MODEL) as PackedScene).instantiate()
	var d := KerridBurnGlow.data()
	KerridBurnGlow.apply(root, 0.5, 0.0)
	var mat := _burns(root).get_active_material(0) as StandardMaterial3D
	assert_true(mat.emission.is_equal_approx(Color(str(d["held"]))), "held cyan")
	KerridBurnGlow.apply(root, 0.5, 1.0)
	assert_true(mat.emission.is_equal_approx(Color(str(d["lift"]))), "released gold")
	root.free()


func test_sockets_on_both_forearms_and_palms() -> void:
	var root := (load(MODEL) as PackedScene).instantiate()
	var names: Array[String] = []
	for s: Node3D in KerridBurnGlow.sockets(root):
		names.append(String(s.name))
	# Godot's import writes the GLB's "VFX-palm.L" as "VFX-palm_L" (no "." in node names)
	assert_true(names.has("VFX-palm_L") and names.has("VFX-palm_R"), "a socket in each palm: %s" % [names])
	assert_eq(names.size(), 14, "six on each forearm and one in each palm")
	assert_eq(KerridBurnGlow.apply(Node3D.new(), 1.0), 0)
	root.free()

extends TestCase
## M3-CHR-506: Pell's name-shell has two states and only one shows (PellNameShell); his battle actor shows the blank.

const BATTLE := "res://game/characters/heroes/pell_battle.tscn"
const MODEL := "res://assets/characters/pell/pell.glb"


func _shells(root: Node) -> Dictionary:
	var out := {}
	for name: StringName in [PellNameShell.BLANK, PellNameShell.CARVED]:
		var found := root.find_children(String(name), "Node3D", true, false)
		out[name] = (found[0] as Node3D).visible if found.size() == 1 else null
	return out


func test_apply_shows_exactly_one_state() -> void:
	var root := (load(MODEL) as PackedScene).instantiate()
	assert_eq(PellNameShell.apply(root, false), 2)
	assert_eq(_shells(root), {PellNameShell.BLANK: true, PellNameShell.CARVED: false})
	assert_false(PellNameShell.is_carved(root))
	assert_eq(PellNameShell.apply(root, true), 2)
	assert_eq(_shells(root), {PellNameShell.BLANK: false, PellNameShell.CARVED: true})
	assert_true(PellNameShell.is_carved(root))
	root.free()


func test_apply_without_pell_finds_nothing() -> void:
	var root := Node3D.new()
	assert_eq(PellNameShell.apply(root, true), 0)
	assert_false(PellNameShell.is_carved(root))
	root.free()


func test_battle_actor_is_lod1_with_the_blank_shell() -> void:
	var root := (load(BATTLE) as PackedScene).instantiate()
	assert_eq(root.get_meta(&"hymn_battle_actor"), &"pell")
	assert_eq(_shells(root), {PellNameShell.BLANK: true, PellNameShell.CARVED: false})
	assert_eq(root.find_children("*", "Skeleton3D", true, false).size(), 1)
	root.free()

class_name BattleArenaLayout
extends RefCounted
## Reads the battle sandbox's slot layout and camera framing from its scene file (M2-ENV-11), without
## instancing it, so arena previews and tests always follow the battle scene: if Combat moves a slot
## or the camera, the arena checks move with it (docs/kb/tech/battle_arenas.md).

const SANDBOX_PATH := "res://game/battle/scene/battle_sandbox.tscn"
const PARTY_SLOTS := "Stage/PartySlots"
const ENEMY_SLOTS := "Stage/EnemySlots"
const CAMERA := "Stage/BattleCamera"


## {"party": Array[Transform3D], "enemy": Array[Transform3D], "enemy_slots": Transform3D (the EnemySlots node, for
## boss_seats), "camera": Transform3D, "fov": float}, in the battle root's space (parent transforms composed). Empty
## on a missing scene.
static func read(path: String = SANDBOX_PATH) -> Dictionary:
	var scene := load(path) as PackedScene
	if scene == null:
		push_error("BattleArenaLayout: cannot load %s" % path)
		return {}
	var state := scene.get_state()
	var local: Dictionary = {}  # node path -> local Transform3D
	var fov := 75.0
	for i in state.get_node_count():
		var p := _clean(String(state.get_node_path(i)))
		var xf := Transform3D.IDENTITY
		for k in state.get_node_property_count(i):
			var prop := state.get_node_property_name(i, k)
			if prop == &"transform":
				xf = state.get_node_property_value(i, k)
			elif prop == &"fov" and p == CAMERA:
				fov = float(state.get_node_property_value(i, k))
		local[p] = xf
	var party: Array[Transform3D] = []
	var enemy: Array[Transform3D] = []
	for p: String in local:
		if p.get_base_dir() == PARTY_SLOTS:
			party.append(_global(local, p))
		elif p.get_base_dir() == ENEMY_SLOTS:
			enemy.append(_global(local, p))
	return {
		"party": party,
		"enemy": enemy,
		"enemy_slots": _global(local, ENEMY_SLOTS),
		"camera": _global(local, CAMERA),
		"fov": fov,
	}


## Every slot's (x, z) on the floor, party first.
static func slot_points(layout: Dictionary) -> Array[Vector2]:
	var out: Array[Vector2] = []
	for key: String in ["party", "enemy"]:
		for xf: Transform3D in layout.get(key, []):
			out.append(Vector2(xf.origin.x, xf.origin.z))
	return out


static func _clean(p: String) -> String:
	return p.trim_prefix("./").trim_prefix(".")


static func _global(local: Dictionary, p: String) -> Transform3D:
	var xf: Transform3D = local.get(p, Transform3D.IDENTITY)
	var parent := p.get_base_dir()
	while parent != "":
		xf = (local.get(parent, Transform3D.IDENTITY) as Transform3D) * xf
		parent = parent.get_base_dir()
	return xf

extends TestCase
## M3-HER-1120: every Act I party member has a battle stand-in row of their own (battle_sandbox.json), so no hero
## falls back to the default primitive. Liss's row names hero-integration's battle wrapper; until that scene and
## her model reach this branch, FighterStandIn shows her capsule (a missing scene falls back to the primitive).
## Kerrid has no model anywhere yet (hero-integration's log), so his row is still to come.

const LISS_WRAPPER := "res://game/hero_motion/battle/liss_battle_actor.tscn"
const PENDING: Array[StringName] = [&"kerrid"]


func test_every_party_member_but_the_pending_has_a_stand_in_row() -> void:
	var rows: Dictionary = BattleStage.config().get("stand_ins", {})
	var heroes: Array = (
		JSON.parse_string(FileAccess.get_file_as_string("res://game/data/battle/characters.json"))["characters"]
	)
	for row: Variant in heroes:
		var id := StringName(str((row as Dictionary)["id"]))
		if PENDING.has(id):
			continue
		assert_true(rows.has(String(id)), "%s has a stand-in row" % id)


func test_liss_names_her_battle_wrapper_with_a_capsule_until_it_lands() -> void:
	var spec := BattleStage.stand_in_spec(&"liss")
	assert_eq(str(spec.get("scene", "")), LISS_WRAPPER)
	assert_eq(str(spec.get("shape", "")), "capsule", "her own capsule, not the default primitive")
	assert_eq(float(spec.get("yaw_deg", 0.0)), -90.0, "faces the foes like the other heroes")
	assert_eq(str(spec.get("tint", "")), "#7A8F6A", "her timeline tint")

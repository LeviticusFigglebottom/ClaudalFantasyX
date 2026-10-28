extends TestCase
## M3-CIN-01: sequencer.json "blink" takes a per-actor row. Sefir blinks once every 10-14 s (his tell,
## act1_npcs.md §1.6; his row also turns off the blink on an expression change); everyone else keeps the shared
## range. His pose table ships as a copy of Character's (game/levels/_tests is left out of a release).

const STEP := 0.05
const SOURCE := "res://game/levels/_tests/characters/sefir/sefir_face_poses.json"
const SHIPPED := "res://game/data/cutscene/sefir_face_poses.json"


## The first blink's time in seconds (INF if none by `limit`).
func _first_blink(actor_id: StringName, limit: float) -> float:
	var holder := Node3D.new()
	var face := CutsceneFace.new(holder)
	face.configure_blink(CutsceneSequencer.load_config().get("blink", {}), 7, actor_id)
	var t := 0.0
	while t < limit:
		face.advance(STEP)
		t += STEP
		if face.is_blinking():
			holder.free()
			return t
	holder.free()
	return INF


func test_sefir_blinks_slowly_and_everyone_else_as_before() -> void:
	var sefir := _first_blink(&"sefir", 15.0)
	assert_between(sefir, 10.0 - STEP, 14.0 + STEP, "Sefir's first blink comes after 10-14 s")
	assert_true(_first_blink(&"asha", 6.0) <= 5.0 + STEP, "Asha keeps the shared 2.2-5.0 s")


func test_his_shipped_pose_table_is_characters() -> void:
	assert_eq(FileAccess.get_file_as_string(SHIPPED), FileAccess.get_file_as_string(SOURCE), "the copy matches")
	var poses: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SHIPPED))
	assert_eq(float(poses["blend_in_s"]), 0.4, "his 0.40 s blend, the slowest in the cast")

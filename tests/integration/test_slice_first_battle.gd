extends TestCase
## M2-FP-105 (Pillar 4: the player always knows who acts next): on the M2 route the tideline is the first
## battle the player meets (Ch1's command and timeline tips come later, behind the Act I switch), so it
## opens on the timeline prompt and Rhen's first turn names the command flow.

const ENCOUNTER := &"ch02_tideline"


func test_the_first_battle_teaches_the_timeline_and_the_commands() -> void:
	var db := BattleDB.load_default()
	var enc: Dictionary = db.encounters.get(ENCOUNTER, {})
	assert_false(enc.is_empty(), "the tideline encounter exists")
	for key: String in ["prompt_key", "turn_prompt_key"]:
		var text_key := str(enc.get(key, ""))
		assert_ne(text_key, "", "%s is set" % key)
		assert_ne(tr(text_key), text_key, "%s is translated" % text_key)
	assert_eq(str(enc.get("turn_prompt_hero", "")), "rhen", "the commands tip waits for Rhen's first turn")

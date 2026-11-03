extends TestCase
## The Lead's 11-03 answer (act1-chapters' LEAD-ASK, Ch9 -> Ch10): Act I's end card returns to the title until
## sign-off; first_playable.json end_card.act2_playable (false) is the one-line switch that sends it on into Act II
## at Ossa Fen's FenEdge.

const LOCATIONS := "res://game/data/world/locations.json"


func _cfg() -> Dictionary:
	return FirstPlayableConfig.section(FirstPlayableConfig.SECTION_END_CARD)


func test_the_card_returns_to_the_title_until_sign_off() -> void:
	var cfg := _cfg()
	assert_false(bool(cfg.get("act2_playable", true)), "act2_playable ships false until Act I is signed off")
	assert_eq(EndCard.next_of(cfg), [&"", &""] as Array[StringName], "accept returns to the title")


func test_the_switch_sends_it_on_to_ossa_fen() -> void:
	var cfg := _cfg().duplicate()
	cfg["act2_playable"] = true
	var next := EndCard.next_of(cfg)
	assert_eq(next[0], &"ch10/ossa_fen", "Act II opens at Ossa Fen")
	assert_eq(next[1], &"FenEdge", "at the fen's edge")
	var rows: Array = (JSON.parse_string(FileAccess.get_file_as_string(LOCATIONS)) as Dictionary)["locations"]
	var found := rows.filter(func(r: Dictionary) -> bool: return str(r.get("id", "")) == String(next[0]))
	assert_eq(found.size(), 1, "ch10/ossa_fen is a location")
	if found.size() == 1:
		assert_true(ResourceLoader.exists(str(found[0]["scene"])), "its scene exists")

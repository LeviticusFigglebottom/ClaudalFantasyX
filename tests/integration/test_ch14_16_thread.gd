extends Act2GreyboxCase
## M4-C14-02 .. M4-C16-02: Ch14 "The Peace Wedding", Ch15 "Unlamped" and Ch16 "The Edge of the World" as greybox
## walks, headless, on the real chapter data (chapters/ch14.json .. ch16.json): the Lacquer Court's barge runs the
## escape to the open sea (Ch15), the barge's bow at dawn hands off to Hollowmere, its ship to the Pale Rim (Ch16),
## and the wade to the Drowned Choir. Each arrival sets its chapter. The story beats come with the beat sheets.

const COURT := "res://game/levels/ch13/ansedra_lacquer_court/ansedra_lacquer_court.tscn"
const SEA := "res://game/levels/ch15/open_sea/open_sea.tscn"
const HOLLOWMERE := "res://game/levels/ch17/hollowmere/hollowmere.tscn"
const RIM := "res://game/levels/ch16/pale_rim/pale_rim.tscn"
const CHOIR := "res://game/levels/ch16/drowned_choir/drowned_choir.tscn"


func test_the_wedding_court_to_the_choir() -> void:
	visit(COURT)
	assert_eq(Game.state.chapter, 14)
	go(&"barge", "ch15/open_sea", "Deck")
	visit(SEA)
	assert_eq(Game.state.chapter, 15)
	go(&"dawn", "ch17/hollowmere", "Dock")
	visit(HOLLOWMERE)
	assert_true(bool(Game.get_flag(&"ch15_reached_hollowmere")))
	go(&"ship", "ch16/pale_rim", "Rim")
	visit(RIM)
	assert_eq(Game.state.chapter, 16)
	go(&"to_choir", "ch16/drowned_choir", "Approach")
	visit(CHOIR)
	assert_true(bool(Game.get_flag(&"ch16_reached_choir")))
	after_visits()

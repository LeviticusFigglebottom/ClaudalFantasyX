extends TestCase
## M2-UI-28: TextFitProbe finds a label's box. A sibling panel that holds the whole label is its box, so text
## past that panel fails. A small panel laid over part of a wide label's row (the Lattice title bar's
## Whole board button, M3-MNU-04) is not the label's box, although it holds the label's centre.

var made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func test_text_past_its_sibling_panel_fails() -> void:
	var screen := _screen()
	_panel(screen, Rect2(100, 100, 120, 200))  # holds the label's centre; its text runs past the panel's foot
	_label(screen, Rect2(110, 110, 100, 40), "A line far too long for the little panel around it", true)
	var p := TextFitProbe.probe(screen, "probe")
	assert_eq(p.failures.size(), 1, p.report())


func test_a_small_panel_over_a_wide_title_s_centre_is_not_its_box() -> void:
	var screen := _screen()
	_panel(screen, Rect2(100, 100, 1000, 400))  # the page's frame
	_panel(screen, Rect2(560, 110, 200, 40))  # a button's frame in the title row
	_label(screen, Rect2(120, 110, 960, 40), "A title")  # left aligned: its text ends well before the button
	var p := TextFitProbe.probe(screen, "probe")
	assert_eq(p.failures.size(), 0, p.report())


func _screen() -> Control:
	var c := Control.new()
	c.size = TextFitProbe.reference_rect().size
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(c)
	made.append(c)
	return c


func _panel(screen: Control, r: Rect2) -> void:
	var p := Panel.new()
	p.position = r.position
	p.size = r.size
	screen.add_child(p)


## `wrap`: the label wraps, so long text grows it down (past a small panel's foot) instead of across.
func _label(screen: Control, r: Rect2, text: String, wrap: bool = false) -> Label:
	var l := Label.new()
	if wrap:
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.position = r.position
	l.size = r.size
	l.text = text
	screen.add_child(l)
	return l

class_name TitleReveal
extends RefCounted
## The title's opening reveal (the human's "parts look primitive" note: the title snapped on): the logo fades in,
## then the choices fade in while rising `rise_px` into place, then the help line, each after its own delay
## (title_menu.json "reveal", at the 1920 x 1080 reference). The menu takes input from the first frame; the
## reveal only draws. Reduced motion, or a title outside the tree, shows everything at once. The whole reveal ends
## before boot_title's settle frames do, so the capture grabs the title at rest.

var parts: Array[Dictionary] = []
var _tween: Tween
var _d: Dictionary = {}


## Plays the reveal over `root` (the title) for `logo`, `page` and `help`, from `d` (title_menu.json "reveal").
func play(root: Control, logo: Control, page: Control, help: Control, d: Dictionary) -> void:
	_d = d
	parts = [
		{"node": logo, "delay": "logo_delay_sec", "sec": "logo_sec", "rise": 0.0},
		{"node": page, "delay": "page_delay_sec", "sec": "page_sec", "rise": HudLayout.num(d, "rise_px")},
		{"node": help, "delay": "help_delay_sec", "sec": "help_sec", "rise": 0.0},
	]
	if UiSettings.shared().reduced_motion() or not root.is_inside_tree() or duration() <= 0.0:
		return
	_tween = root.create_tween().set_parallel(true)
	for p in parts:
		var node := p["node"] as Control
		if node == null:
			continue
		var rest_y := node.position.y
		node.modulate.a = 0.0
		node.position.y = rest_y + float(p["rise"])
		var sec := HudLayout.num(d, str(p["sec"]))
		var delay := HudLayout.num(d, str(p["delay"]))
		_tween.tween_property(node, "modulate:a", 1.0, sec).set_delay(delay).set_ease(Tween.EASE_OUT)
		_tween.tween_property(node, "position:y", rest_y, sec).set_delay(delay).set_trans(Tween.TRANS_CUBIC).set_ease(
			Tween.EASE_OUT
		)


## The whole reveal's length (the latest part's delay plus its fade).
func duration() -> float:
	var out := 0.0
	for p in parts:
		out = maxf(out, HudLayout.num(_d, str(p["delay"])) + HudLayout.num(_d, str(p["sec"])))
	return out


func is_playing() -> bool:
	return _tween != null and _tween.is_valid() and _tween.is_running()


## Ends the reveal at rest now (tests).
func finish() -> void:
	if is_playing():
		_tween.custom_step(duration() + 1.0)

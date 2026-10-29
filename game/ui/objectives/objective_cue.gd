class_name ObjectiveCue
extends Control
## The destination cue (M2-UI-19): where the objective points, in the field. When the target is on
## screen, a gold diamond ring (the map's objective shape) floats over it with the distance in
## words; when it is off screen or behind the camera, an arrow at the screen edge points the way.
## It hides near the target, while the line's gating hides it (cutscenes, menus), and when the
## Accessibility setting `objective_cue` is off. A view: the target comes from its ObjectiveHud.
## Numbers: game/data/ui/objective_hud.json "cue".

## The objective line it belongs to (zone, tracker, controller, gating).
var hud: ObjectiveHud
## The last placement (tests read it): {visible, on_screen, at, angle, words}.
var placement: Dictionary = {}

var _m: Dictionary = {}
var _label: Label


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_m = ObjectiveHud.load_data().get("cue", {}) as Dictionary
	_label = Label.new()
	_label.theme_type_variation = &"SmallLabel"
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_label.size = Vector2(HudLayout.num(_m, "label_width"), HudLayout.num(_m, "label_height"))
	_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# No backing plate: an outline (the theme's outline colour) keeps the words legible over any sky.
	_label.add_theme_constant_override(&"outline_size", int(HudLayout.num(_m, "label_outline_px")))
	add_child(_label)


func _process(_delta: float) -> void:
	refresh()


## Recomputes the cue from the live camera and player, and redraws.
func refresh() -> void:
	placement = {"visible": false}
	var cam := get_viewport().get_camera_3d() if is_inside_tree() else null
	if hud != null and cam != null and _enabled():
		var target := hud.target_position()
		if target != Vector3.INF:
			var from := hud.controller.global_position if hud.controller != null else cam.global_position
			target.y = from.y + HudLayout.num(_m, "marker_lift_m")
			placement = place(
				cam.is_position_behind(target), cam.unproject_position(target), get_viewport_rect().size, from, target
			)
	_label.visible = bool(placement.get("visible", false)) and bool(placement.get("on_screen", false))
	if _label.visible:
		_label.text = str(placement["words"])
		var at: Vector2 = placement["at"]
		_label.position = at + Vector2(-_label.size.x * 0.5, HudLayout.num(_m, "marker_px") * 1.4)
	queue_redraw()


## Where the cue goes for a target at screen point `screen` (`behind`: behind the camera) on a
## screen of `size`, the player at `from` and the target at `to` (world). Pure, for tests.
func place(behind: bool, screen: Vector2, size: Vector2, from: Vector3, to: Vector3) -> Dictionary:
	var dist := Vector2(to.x - from.x, to.z - from.z).length()
	if dist < HudLayout.num(_m, "hide_within_m"):
		return {"visible": false}
	var edge := HudLayout.num(_m, "edge_px")
	var inner := Rect2(Vector2(edge, edge), size - Vector2(edge, edge) * 2.0)
	var words := distance_words(dist)
	if not behind and inner.has_point(screen):
		return {"visible": true, "on_screen": true, "at": screen, "angle": 0.0, "words": words}
	var center := size * 0.5
	var dir := screen - center
	if behind:
		dir = -dir  # a point behind the camera projects mirrored
	if dir.length() < 0.001:
		dir = Vector2.DOWN
	var half := inner.size * 0.5
	var k := minf(half.x / maxf(absf(dir.x), 0.001), half.y / maxf(absf(dir.y), 0.001))
	return {"visible": true, "on_screen": false, "at": center + dir * k, "angle": dir.angle(), "words": words}


## "Near", "A short walk" or "Far" for `dist` metres.
func distance_words(dist: float) -> String:
	if dist < HudLayout.num(_m, "near_m"):
		return tr("OBJ_CUE_NEAR")
	if dist < HudLayout.num(_m, "walk_m"):
		return tr("OBJ_CUE_WALK")
	return tr("OBJ_CUE_FAR")


func _enabled() -> bool:
	return UiSettings.shared().objective_cue_enabled() and hud.allowed()


func _draw() -> void:
	if not bool(placement.get("visible", false)):
		return
	var at: Vector2 = placement["at"]
	var gold := get_theme_color(&"focus_gold", HymnThemeBuilder.PALETTE_TYPE)
	var focus := get_theme_color(&"focus", HymnThemeBuilder.PALETTE_TYPE)
	var shade := get_theme_color(&"outline", HymnThemeBuilder.PALETTE_TYPE)
	if bool(placement["on_screen"]):
		var r := HudLayout.num(_m, "marker_px")
		var ring := SwellRingView.diamond(at, r)
		ring.append(ring[0])
		draw_polyline(ring, shade, 5.0, true)
		draw_polyline(ring, gold, 2.0, true)
		draw_circle(at, r * 0.3, focus)
		return
	var a := HudLayout.num(_m, "arrow_px")
	var tri := SwellRingView.arrow(at, Vector2.from_angle(float(placement["angle"])), a)
	draw_colored_polygon(tri, shade)
	draw_colored_polygon(SwellRingView.arrow(at, Vector2.from_angle(float(placement["angle"])), a * 0.75), gold)

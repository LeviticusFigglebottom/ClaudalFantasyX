class_name UiFrame
extends RefCounted
## Layout at any window shape (M2-UI-29, docs/kb/tech/ui.md § Resolution and aspect). The project
## stretches canvas items with aspect "expand" from the 1920 x 1080 reference (project.godot), so
## a 16:10 window lays out in 1920 x 1200 and a 21:9 one in about 2560 x 1080. Every UI rect in
## game/data/ui/*.json is at that reference:
##   - a full-screen menu is one composition: centre(root) makes the root the reference frame,
##     centred on the screen, while its scrims and backdrops still cover the whole screen;
##   - a HUD piece keeps its margin to its own edge: HudLayout.place() reads a section's "pin";
##   - a one-line label keeps the larger text sizes up to its frame's width: fit_line().

## Set on a centred root: the children that cover the whole screen.
const META_COVERS := &"ui_frame_covers"
## The pass-through control a modal root gets under its content (clicks outside the frame).
const CATCHER_NAME := &"FrameCatcher"


## The reference size every layout file is drawn at (the project's base viewport).
static func reference_size() -> Vector2:
	return Vector2(
		float(ProjectSettings.get_setting("display/window/size/viewport_width")),
		float(ProjectSettings.get_setting("display/window/size/viewport_height"))
	)


## Makes `root` (a full-screen menu, already built) the reference frame, centred on the screen:
## children placed at reference coordinates land centred at any aspect, and children added later
## do too. Its children anchored to the full rect (scrims, backdrops) are stretched past the frame
## to the whole screen, now and on every window change. A root that takes the mouse gets a
## pass-through control under its content as large as the screen, so a click beside the frame
## still reaches the root (and nothing behind the menu) as it did before.
static func centre(root: Control) -> void:
	var half := reference_size() * 0.5
	for side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]:
		root.set_anchor(side, 0.5)
	root.offset_left = -half.x
	root.offset_top = -half.y
	root.offset_right = half.x
	root.offset_bottom = half.y
	root.grow_horizontal = Control.GROW_DIRECTION_BOTH
	root.grow_vertical = Control.GROW_DIRECTION_BOTH
	var covers: Array[Control] = []
	for c in root.get_children():
		if c is Control and _is_full_rect(c as Control):
			covers.append(c as Control)
	if root.mouse_filter != Control.MOUSE_FILTER_IGNORE and not root.has_node(NodePath(String(CATCHER_NAME))):
		var catcher := Control.new()
		catcher.name = CATCHER_NAME
		catcher.mouse_filter = Control.MOUSE_FILTER_PASS
		catcher.set_anchors_preset(Control.PRESET_FULL_RECT)
		root.add_child(catcher)
		root.move_child(catcher, 0)
		covers.append(catcher)
	root.set_meta(META_COVERS, covers)
	fit(root)
	if not root.is_inside_tree():
		return
	var vp := root.get_viewport()
	var refit := func() -> void:
		if is_instance_valid(root):
			fit(root)
	vp.size_changed.connect(refit)
	var stop := func() -> void:
		if is_instance_valid(vp) and vp.size_changed.is_connected(refit):
			vp.size_changed.disconnect(refit)
	root.tree_exiting.connect(stop, CONNECT_ONE_SHOT)


## Stretches a centred root's covers over the whole screen again (centre() calls it on every
## window change; call it after moving the root yourself).
static func fit(root: Control) -> void:
	if not root.is_inside_tree() or not root.has_meta(META_COVERS):
		return
	var view := root.get_viewport().get_visible_rect()
	var at := root.get_global_transform_with_canvas().origin
	for v: Variant in root.get_meta(META_COVERS) as Array:
		if not is_instance_valid(v):
			continue
		var c := v as Control
		c.offset_left = view.position.x - at.x
		c.offset_top = view.position.y - at.y
		c.offset_right = view.end.x - at.x - root.size.x
		c.offset_bottom = view.end.y - at.y - root.size.y


## Shrinks one line of text to `width` when the text size setting makes it longer than its frame:
## from the theme's (scaled) size down to no less than the base theme's size for its variation, so
## the 100 % layout, which fits by design, is the floor. Call it after every text change.
static func fit_line(l: Label, width: float) -> void:
	l.remove_theme_font_size_override(&"font_size")
	var fs := l.get_theme_font_size(&"font_size")
	var font := l.get_theme_font(&"font")
	var need := font.get_string_size(l.text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	if need > width and need > 0.0:
		var fitted := maxi(floori(float(fs) * width / need), base_font_size(l))
		if fitted < fs:
			l.add_theme_font_size_override(&"font_size", fitted)
	l.size.x = width


## The font size `l`'s variation has in the base Hymn theme (100 % text).
static func base_font_size(l: Label) -> int:
	var base := load(UiSettings.BASE_THEME_PATH) as Theme
	var kind := l.theme_type_variation if l.theme_type_variation != &"" else &"Label"
	if base.has_font_size(&"font_size", kind):
		return base.get_font_size(&"font_size", kind)
	return base.default_font_size


static func _is_full_rect(c: Control) -> bool:
	return (
		is_zero_approx(c.anchor_left)
		and is_zero_approx(c.anchor_top)
		and is_equal_approx(c.anchor_right, 1.0)
		and is_equal_approx(c.anchor_bottom, 1.0)
	)

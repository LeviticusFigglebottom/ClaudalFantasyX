class_name SubtitleStyle
extends RefCounted
## How the dialogue box's lines read (M2-UI-30; the Lead's subtitle item): the box follows
## UiSettings, so the text size reaches it. The speaker's name takes the HeaderLabel size and the
## line the BodyLabel size (or the sung variation's) from the scaled theme, in place of the box
## scene's fixed sizes. The name takes name_role (gold) and the line body_role (dialogue_assist.json
## "subtitles"; speaker_roles may give one speaker another role). Names are not colour-coded per
## hero: the palette has no four colours that stay apart for every colour vision. A backing in the panel_low role
## at the Accessibility "Subtitle backing" alpha sits behind the text, inside the box's panel.
## DialogueAssist applies it; nothing here writes the Architect's box scene.

const BACKING_NAME := &"SubtitleBacking"

var box: DialogueBox
var data: Dictionary = {}
var _backing: ColorRect
var _speaker: StringName = &"-"


func _init(with_box: DialogueBox, with_data: Dictionary) -> void:
	box = with_box
	data = with_data


## Follows the shared settings (text size, palette) and adds the backing.
func attach() -> void:
	UiSettings.shared().follow(box)
	var panel := box.get_node_or_null(^"Panel") as Control
	if panel != null and panel.get_node_or_null(NodePath(String(BACKING_NAME))) == null:
		_backing = ColorRect.new()
		_backing.name = BACKING_NAME
		_backing.mouse_filter = Control.MOUSE_FILTER_IGNORE
		panel.add_child(_backing)
		panel.move_child(_backing, 0)  # behind the text (a PanelContainer fills every child)
	apply()


## Re-applies the sizes, the name colour and the backing (on a setting change or a new speaker).
func apply() -> void:
	var name_label := box.get_node_or_null(^"%SpeakerName") as Label
	var body := box.get_node_or_null(^"%Body") as Label
	if name_label == null or body == null:
		return
	var names := StringName(str(data.get("name_variation", "")))
	var bodies := StringName(str(data.get("body_variation", "")))
	name_label.theme_type_variation = names  # the box never sets the name's variation; the line's is its own
	name_label.add_theme_font_size_override(&"font_size", box.get_theme_font_size(&"font_size", names))
	var body_type := body.theme_type_variation if body.theme_type_variation != &"" else bodies
	body.add_theme_font_size_override(&"font_size", box.get_theme_font_size(&"font_size", body_type))
	name_label.add_theme_color_override(&"font_color", speaker_color(current_speaker()))
	body.add_theme_color_override(&"font_color", _role(str(data.get("body_role", ""))))
	if _backing != null:
		var c := box.get_theme_color(StringName(str(data.get("backing_role", ""))), HymnThemeBuilder.PALETTE_TYPE)
		_backing.color = Color(c, UiSettings.shared().dialogue_backing_alpha())
		_backing.visible = _backing.color.a > 0.0


## The speaker of the line on show (&"" for narration).
func current_speaker() -> StringName:
	return StringName(str(box.get(&"_speaker")))


## The name colour for `speaker`: a speaker_roles entry, else name_role.
func speaker_color(speaker: StringName) -> Color:
	var roles := data.get("speaker_roles", {}) as Dictionary
	return _role(str(roles.get(String(speaker), data.get("name_role", ""))))


func _role(role: String) -> Color:
	return box.get_theme_color(StringName(role), HymnThemeBuilder.PALETTE_TYPE)


## Called every frame: a new speaker (or a new line's sung variation) restyles the box.
func poll() -> void:
	var s := current_speaker()
	var body := box.get_node_or_null(^"%Body") as Label
	var key := StringName("%s|%s" % [s, body.theme_type_variation if body != null else &""])
	if key != _speaker:
		_speaker = key
		apply()

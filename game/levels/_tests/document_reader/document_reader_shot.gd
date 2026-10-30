class_name DocumentReaderShot
extends Control
## Capture driver for the document reader shots (M4-A2P-080, tests/screenshots/shots.json), over the fixture records
## (reader_fixture.json), so a record's words never move a baseline. "three": three panes, one hand found (its gold
## lines and rules), a mark waiting in the first pane and the cursor in the second. "one": a found record read alone.

const FIXTURE := "res://game/levels/_tests/document_reader/reader_fixture.json"
const VIEWS := {
	&"three": {"record": &"fixture_three", "marks": [[0, 0], [1, 3], [0, 4]], "cursor": [1, 2]},
	&"one": {"record": &"fixture_one", "marks": [], "cursor": [0, 1]},
}

## Which view to stage: a VIEWS key.
@export var view: StringName = &"three"

var reader: DocumentReader


func _ready() -> void:
	var back := ColorRect.new()
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.color = get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	back.color.a = 1.0
	add_child(back)
	var v: Dictionary = VIEWS.get(view, VIEWS[&"three"])
	var row := DocumentReaderModel.row_of(v["record"], FIXTURE)
	var model := DocumentReaderModel.new(row, func(_f: StringName) -> void: pass)
	reader = (load(DocumentReader.SCENE_PATH) as PackedScene).instantiate() as DocumentReader
	reader.pause_tree = false
	reader.configure(model)
	add_child(reader)
	for m: Array in v["marks"]:
		reader.set_cursor(int(m[0]), int(m[1]))
		reader.mark()
	var c: Array = v["cursor"]
	reader.set_cursor(int(c[0]), int(c[1]))

class_name LedgerReaderShot
extends Control
## Capture driver for the ledger_reader shot (M5-A3P-1706, tests/screenshots/shots.json): Dace's ledger on its
## second written page (the torn sleeves, the Bastion, Oruvel, and the word sent to Rhen), written through the same
## sequencer signals the scene uses. Reduced motion, so the page is up at once and no fade is caught mid-way.

const ENTRIES: Array[StringName] = [
	&"DLG_CH17_LEDGER_PAGE_006", &"DLG_CH17_LEDGER_PAGE_007", &"DLG_CH17_LEDGER_PAGE_008", &"DLG_CH17_LEDGER_PAGE_016"
]

var reader: LedgerReader
var _seq: CutsceneSequencer


func _ready() -> void:
	var back := ColorRect.new()
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.color = get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	back.color.a = 1.0
	add_child(back)
	var settings := UiSettings.new()
	settings.set_value(UiSettings.REDUCED_MOTION, true)
	UiSettings.set_shared(settings)
	_seq = CutsceneSequencer.new()
	reader = LedgerReader.mount(self, _seq)
	_seq.line_shown.emit(_step("ch17_ledger_page_001", &"DLG_CH17_LEDGER_PAGE_001"))
	_seq.event_requested.emit(CutsceneHoldGate.EVENT_BEGIN, ["turn_page"])
	_seq.event_requested.emit(CutsceneHoldGate.EVENT_END, [])
	for key in ENTRIES:
		_seq.line_shown.emit(_step("ch17_ledger_page_" + String(key).right(3), key))


func _exit_tree() -> void:
	if is_instance_valid(_seq):
		_seq.free()


static func _step(line_id: String, key: StringName) -> DialogueStep:
	var s := DialogueStep.new()
	s.kind = DialogueStep.Kind.LINE
	s.line_id = StringName(line_id)
	s.text_key = key
	return s

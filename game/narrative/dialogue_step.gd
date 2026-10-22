class_name DialogueStep
extends RefCounted
## What DialogueRunner.next() hands back: a spoken line, a cue, a set of options, or the end.
## Text is never resolved here; the UI shows tr(text_key) (and tr(option.text_key)).

enum Kind { LINE, CUE, OPTIONS, END }

var kind: Kind = Kind.END
## Source line in the .dlg file, for debugging.
var src_line: int = 0

# LINE
var line_id: StringName = &""
var text_key: StringName = &""
## Speaker id from game/data/dialogue/speakers.json; empty for narration.
var speaker: StringName = &""
## Emotion tag from game/data/dialogue/emotions.json; empty means "no change" (neutral by default).
var emotion: StringName = &""
## Reserved for voice files (ADR 0004); always empty for now.
var voice: String = ""
var tags: PackedStringArray = PackedStringArray()

# CUE (numbers arrive as float, as JSON gives them)
var cue: StringName = &""
var args: Array = []
var kwargs: Dictionary = {}

# OPTIONS
var options: Array[DialogueOption] = []


func is_line() -> bool:
	return kind == Kind.LINE


func is_cue() -> bool:
	return kind == Kind.CUE


func is_options() -> bool:
	return kind == Kind.OPTIONS


func is_end() -> bool:
	return kind == Kind.END


static func make_end() -> DialogueStep:
	return DialogueStep.new()


static func from_line_op(op: Dictionary) -> DialogueStep:
	var s := DialogueStep.new()
	s.kind = Kind.LINE
	s.src_line = int(op.get("src", 0))
	s.line_id = StringName(str(op.get("id", "")))
	s.text_key = StringName(str(op.get("key", "")))
	s.speaker = StringName(str(op.get("speaker", "")))
	s.emotion = StringName(str(op.get("emotion", "")))
	s.voice = str(op.get("voice", ""))
	for t: Variant in op.get("tags", []):
		s.tags.append(str(t))
	return s


static func from_cue_op(op: Dictionary) -> DialogueStep:
	var s := DialogueStep.new()
	s.kind = Kind.CUE
	s.src_line = int(op.get("src", 0))
	s.cue = StringName(str(op.get("cue", "")))
	s.args = (op.get("args", []) as Array).duplicate(true)
	s.kwargs = (op.get("kwargs", {}) as Dictionary).duplicate(true)
	return s


static func from_options(src: int, available: Array[DialogueOption]) -> DialogueStep:
	var s := DialogueStep.new()
	s.kind = Kind.OPTIONS
	s.src_line = src
	s.options = available
	return s

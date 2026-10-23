class_name DialogueStep
extends RefCounted
## What DialogueRunner.next() hands back: a spoken line, a cue, a set of options, or the end.
## Text is never resolved here; the UI shows tr(text_key) (and tr(option.text_key)).

enum Kind { LINE, CUE, OPTIONS, END }

## Tag on a sung line: DialogueBox plays no blips and no lip-flap for it.
const TAG_SUNG := "sung"
## Tag on a do-not-translate line (its translator note is in compiled/translator_notes.tsv).
const TAG_NOTR := "notr"
## Reserved @music track id: fade the music bed out (cues.json "reserved").
const MUSIC_SILENCE := &"silence"

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
## Display-name override (`Asha as "The girl": ...`): show tr(name_key) instead of the speaker's
## name. Empty means use the speaker's own name_key from speakers.json.
var name_key: StringName = &""
## Voice identity of narration (`Narrator(rhen): ...`), a speakers.json id; empty for captions.
## Narration still shows no name; this picks the voice (and the blip pitch, if narration blips).
var narrator: StringName = &""
var tags: PackedStringArray = PackedStringArray()

# CUE (numbers arrive as float, as JSON gives them)
var cue: StringName = &""
var args: Array = []
var kwargs: Dictionary = {}
## For `@wait music=<marker>`: the music marker to hold for; empty for every other cue.
var wait_marker: StringName = &""

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


func is_sung() -> bool:
	return TAG_SUNG in tags


func is_do_not_translate() -> bool:
	return TAG_NOTR in tags


## True for `@wait music=<marker>` (see DialogueRunner.music_marker_reached).
func is_music_wait() -> bool:
	return kind == Kind.CUE and wait_marker != &""


## True for `@music silence`.
func is_music_silence() -> bool:
	return kind == Kind.CUE and cue == &"music" and not args.is_empty() and StringName(str(args[0])) == MUSIC_SILENCE


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
	s.name_key = StringName(str(op.get("name_key", "")))
	s.narrator = StringName(str(op.get("narrator", "")))
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
	if s.cue == &"wait" and s.kwargs.has("music"):
		s.wait_marker = StringName(str(s.kwargs["music"]))
	return s


static func from_options(src: int, available: Array[DialogueOption]) -> DialogueStep:
	var s := DialogueStep.new()
	s.kind = Kind.OPTIONS
	s.src_line = src
	s.options = available
	return s

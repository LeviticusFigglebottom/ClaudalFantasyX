class_name DialogueBacklog
extends RefCounted
## The session's dialogue backlog (M2-UI-25): every fully revealed line, as the speaker's shown
## name ("" for narration) and its text, oldest first, capped at `max_lines` (dialogue_assist.json).
## One shared log lives for the session; the title screen forgets it, so a loaded save never shows
## another run's lines. Tests build their own with DialogueBacklog.new(cap).

const KEY_SPEAKER := "speaker"
const KEY_TEXT := "text"

static var _shared: DialogueBacklog

var max_lines := 0

var _lines: Array[Dictionary] = []


func _init(cap: int = -1) -> void:
	max_lines = cap if cap >= 0 else int(DialogueAssist.load_data().get("max_lines", 0))


## The log every DialogueBox records into.
static func shared() -> DialogueBacklog:
	if _shared == null:
		_shared = DialogueBacklog.new()
	return _shared


## Empties the shared log (the title screen calls it).
static func forget() -> void:
	if _shared != null:
		_shared.clear()


## Adds one line; a line with no text is not kept. The oldest lines fall off past max_lines.
func record(speaker: String, text: String) -> void:
	if text.strip_edges().is_empty() or max_lines <= 0:
		return
	_lines.append({KEY_SPEAKER: speaker, KEY_TEXT: text})
	while _lines.size() > max_lines:
		_lines.pop_front()


## The kept lines, oldest first ({speaker, text}; a copy).
func lines() -> Array[Dictionary]:
	return _lines.duplicate(true)


func size() -> int:
	return _lines.size()


func is_empty() -> bool:
	return _lines.is_empty()


func clear() -> void:
	_lines.clear()

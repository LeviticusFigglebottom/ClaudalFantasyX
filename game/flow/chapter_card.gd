class_name ChapterCard
extends Node
## M3-CIN-1233 (the Lead, under ADR 0041/0042: Act I as played is one path): a chapter's title card between two
## chapters, B11 → Ch4 (the slice's dock at night ends here, no longer on the demo end card). UI's ActCard on black in
## its two-line shape, "Chapter 4" over the gold rule and "The Pilgrim's Wake" (first_playable.json chapter_card:
## label_key, title_key; the fade-in, hold and fade-out are act_card.json's). voice_key, when set, comes first as a
## caption alone on black: B12's voice-over, which closed the slice, now leads into Ch4. When the words have gone, the
## party travels on to next_location / next_spawn, and the black holds until the zone's own arrival fade lifts it.

const SCENE := "res://game/flow/chapter_card.tscn"

## How the hand-off travels: (location_id: StringName, spawn: StringName) -> void. Unset = FlowRouting.go_to.
var travel: Callable = Callable()
## True once the card has sent the party on (once).
var done := false
var card: ActCard
var _cfg: Dictionary = {}
var _titled := false


func _ready() -> void:
	_cfg = FirstPlayableConfig.section(FirstPlayableConfig.SECTION_CHAPTER_CARD)
	card = ActCard.open_in(self)
	var voice := str(_cfg.get("voice_key", ""))
	if voice != "":
		card.show_caption(voice)
		card.finished.connect(_show_title, CONNECT_ONE_SHOT)
	else:
		_show_title()


## True while the voice-over caption is up (before the chapter's title).
func voice_showing() -> bool:
	return card.is_showing() and card.act == 0 and not _titled


func _show_title() -> void:
	_titled = true
	card.show_titled(str(_cfg.get("label_key", "")), str(_cfg.get("title_key", "")))
	card.finished.connect(go_on, CONNECT_ONE_SHOT)


## Steps the card (tests; in play the card runs on its own _process).
func advance(delta: float) -> void:
	card.advance(delta)


## Sends the party on to the next chapter (once). Returns false when already done.
func go_on() -> bool:
	if done:
		return false
	done = true
	var loc := StringName(str(_cfg.get("next_location", "")))
	var spawn := StringName(str(_cfg.get("next_spawn", "")))
	if travel.is_valid():
		travel.call(loc, spawn)
	else:
		FlowRouting.go_to(loc, spawn)
	return true

class_name TutorialTips
extends RefCounted
## First-time tips (M2-UI-24), node-free: which tip a field event raises, in data order, once per
## save (a tip's seen flag is set when it is taken to show). Rows: game/data/ui/tutorial_tips.json.
## TipCard is the view. Tests build it with their own flag reader and writer and setting.

## The payload key a layout trigger names a save shrine by (Ch6-Ch8 place theirs so).
const SAVE_SHRINE_KEY := &"save_shrine"
const DATA_PATH := "res://game/data/ui/tutorial_tips.json"
const ON_FIELD_READY := &"field_ready"
const ON_NEAR := &"near"
const ON_FLAG := &"flag"
const TAG_SHRINE := &"shrine"

var data: Dictionary = {}
var tips: Array[Dictionary] = []
## Tips raised and waiting to show, oldest first.
var queue: Array[Dictionary] = []

var _is_set: Callable
var _mark: Callable
var _enabled: Callable


## `flag_check`: Callable(flag) -> bool (default Game.get_flag); `flag_mark`: Callable(flag) (default
## Game.set_flag); `enabled`: Callable() -> bool (default the Accessibility setting tutorial_tips).
func _init(flag_check: Callable = Callable(), flag_mark: Callable = Callable(), enabled: Callable = Callable()) -> void:
	_is_set = flag_check if flag_check.is_valid() else func(f: StringName) -> bool: return bool(Game.get_flag(f))
	_mark = flag_mark if flag_mark.is_valid() else func(f: StringName) -> void: Game.set_flag(f, true)
	_enabled = enabled if enabled.is_valid() else func() -> bool: return UiSettings.shared().tutorial_tips_enabled()
	data = load_data()
	for t: Variant in data.get("tips", []):
		tips.append(t as Dictionary)


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("tutorial_tips")) != TYPE_DICTIONARY:
		push_error("TutorialTips: could not read 'tutorial_tips' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["tutorial_tips"] as Dictionary


## The tags a "near" tip matches on `it`: its payload's keys, plus "shrine" for a save shrine.
static func tags_of(it: Interactable) -> Array[StringName]:
	var out: Array[StringName] = []
	if it == null:
		return out
	for k: Variant in it.payload.keys():
		out.append(StringName(str(k)))
	if it is SaveShrine or it.payload.has(SAVE_SHRINE_KEY):  # a layout trigger's shrine too (M4-A2P-1004 F8)
		out.append(TAG_SHRINE)
	return out


## The field took input in a scene. It also catches up a flag tip whose flag was set while no field listened (the
## first fight's victory flag is set in the battle scene; the field reloads after it: the Lead's first-hour pass,
## 2026-10-30, found the menu tip never came). Seen tips never come back, so this is still once.
func raise_field_ready() -> void:
	_raise(
		func(t: Dictionary) -> bool:
			if _on(t) == ON_FIELD_READY:
				return true
			return _on(t) == ON_FLAG and _whens(t).any(func(f: StringName) -> bool: return bool(_is_set.call(f)))
	)


## An interactable with `tags` came in reach.
func raise_near(tags: Array[StringName]) -> void:
	_raise(func(t: Dictionary) -> bool: return _on(t) == ON_NEAR and tags.has(StringName(str(t.get("tag", "")))))


## Story flag `flag` became `value`.
func raise_flag(flag: StringName, value: Variant) -> void:
	if not bool(value):
		return
	_raise(func(t: Dictionary) -> bool: return _on(t) == ON_FLAG and _whens(t).has(flag))


## Takes the next waiting tip to show and marks it seen ({} when none).
func take() -> Dictionary:
	if queue.is_empty():
		return {}
	var t: Dictionary = queue.pop_front()
	_mark.call(StringName(str(t.get("flag", ""))))
	return t


## True when `tip` has been seen in this save.
func seen(tip: Dictionary) -> bool:
	return bool(_is_set.call(StringName(str(tip.get("flag", "")))))


func _raise(matches: Callable) -> void:
	if not bool(_enabled.call()):
		return
	for t in tips:
		if not matches.call(t) or seen(t) or queue.has(t):
			continue
		var ready := true
		for f: Variant in t.get("requires", []):
			ready = ready and bool(_is_set.call(StringName(str(f))))
		var any: Array = t.get("requires_any", [])
		if not any.is_empty():
			ready = ready and any.any(func(f: Variant) -> bool: return bool(_is_set.call(StringName(str(f)))))
		if ready:
			queue.append(t)


## A flag tip's `when`: one flag, or a list of which any raises it (the Act I route and the slice's both teach).
static func _whens(t: Dictionary) -> Array[StringName]:
	var out: Array[StringName] = []
	var w: Variant = t.get("when", "")
	for f: Variant in w as Array if w is Array else [w]:
		out.append(StringName(str(f)))
	return out


## The actions tip `tip`'s body names as {action} (pressing one of them dismisses it: TipCard.dismiss).
static func actions_named(tip: Dictionary) -> Array[StringName]:
	var out: Array[StringName] = []
	var key := str(tip.get("body_key", ""))
	if key == "":
		return out
	var re := RegEx.create_from_string("\\{([a-z_]+)\\}")
	for m in re.search_all(TranslationServer.translate(key)):
		out.append(StringName(m.get_string(1)))
	return out


func _on(t: Dictionary) -> StringName:
	return StringName(str(t.get("on", "")))

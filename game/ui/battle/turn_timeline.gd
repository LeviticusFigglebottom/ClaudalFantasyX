class_name TurnTimeline
extends Control
## The always-visible turn order (SPEC §6.1, docs/kb/art/ui.md §6.1). Slot 0 is the fighter
## acting now; slots 1..15 come from BattleEngine.preview(). While a command is hovered, the
## preview's entries slide to their new slots, the actor's next turn shows as a ghost, and any
## chip the action shifts gets ▲/▼ (pillar 4). Pure view: it never touches combat state.

const MODE_PREVIEW := &"preview"
const MODE_TURN := &"turn"

## Turns shown, including the current one (CtbTimeline.PREVIEW_LENGTH).
var length := CtbTimeline.PREVIEW_LENGTH
## Last slots shown (for tests and the help line).
var slots: Array[Dictionary] = []

var _metrics: Dictionary = {}
## Combatant id -> {label: String, tint: Color}.
var _identity: Dictionary = {}
## Combatant id -> how many of its turns have passed (keeps chip keys stable across turns).
var _offsets: Dictionary = {}
## Slot key -> TimelineChip.
var _chips: Dictionary = {}
var _target_color := Color.WHITE
var _panel: Panel


func _ready() -> void:
	_metrics = HudLayout.section(&"timeline")
	HudLayout.place(self, _metrics)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	# Turns sliding in or out of the order stay inside the panel.
	clip_contents = true
	_panel = Panel.new()
	_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_panel)


func set_identity(cid: StringName, label: String, tint: Color) -> void:
	_identity[cid] = {"label": label, "tint": tint}


## Call once each time `cid` finishes a turn, before showing the new order.
func note_turn_taken(cid: StringName) -> void:
	_offsets[cid] = int(_offsets.get(cid, 0)) + 1


## Shows the order. `base` is engine.preview() (no candidate action). `preview` is
## engine.preview(skill, target, length - 1), or empty when nothing is hovered.
func show_turns(
	current_id: StringName,
	base: Array[TurnEntry],
	preview: Array[TurnEntry] = [],
	targets: Array[StringName] = [],
	target_color: Color = Color.WHITE,
	mode: StringName = MODE_PREVIEW
) -> void:
	_target_color = target_color
	var affected: Array[StringName] = [current_id]
	affected.append_array(targets)
	slots = build_slots(current_id, base, preview, _offsets, length, affected)
	for s in slots:
		s["targeted"] = targets.has(s["id"]) and not bool(s["is_current"])
	_sync_chips(mode)


## Pure layout of the timeline: one Dictionary per visible slot with
## {key, id, team, slot, skipped, ghost, moved, is_current}. Keys are "<id>#<turn index>", so a
## turn keeps its key while the preview moves it, and `moved` compares against `base`.
## With `affected` set, only those fighters get ▲/▼ (the actor and its targets): everyone else
## still slides, but arrows on every chip would bury the two that matter.
static func build_slots(
	current_id: StringName,
	base: Array[TurnEntry],
	preview: Array[TurnEntry],
	offsets: Dictionary,
	count: int,
	affected: Array[StringName] = []
) -> Array[Dictionary]:
	var base_keyed := _keyed(base, offsets, &"")
	var base_slot: Dictionary = {}
	for i in base_keyed.size():
		base_slot[base_keyed[i]["key"]] = i
	var out: Array[Dictionary] = []
	if preview.is_empty() or base.is_empty():
		for i in mini(base_keyed.size(), count):
			var s: Dictionary = base_keyed[i]
			s["slot"] = i
			s["moved"] = 0
			s["is_current"] = i == 0 and s["id"] == current_id
			out.append(s)
		return out
	var head: Dictionary = base_keyed[0]
	head["slot"] = 0
	head["moved"] = 0
	head["is_current"] = head["id"] == current_id
	out.append(head)
	var prev_keyed := _keyed(preview, offsets, current_id)
	for i in mini(prev_keyed.size(), count - 1):
		var s: Dictionary = prev_keyed[i]
		var slot := i + 1
		s["slot"] = slot
		s["is_current"] = false
		var before: int = base_slot.get(s["key"], count)
		var shows_arrow := affected.is_empty() or affected.has(s["id"])
		s["moved"] = signi(slot - before) if shows_arrow else 0
		out.append(s)
	return out


## Keys entries by occurrence. `skip_first_of` starts that id's count at 1 (the preview list
## leaves out the turn being taken right now).
static func _keyed(entries: Array[TurnEntry], offsets: Dictionary, skip_first_of: StringName) -> Array[Dictionary]:
	var seen: Dictionary = {}
	var out: Array[Dictionary] = []
	for e in entries:
		var k: int = int(seen.get(e.combatant_id, 1 if e.combatant_id == skip_first_of else 0))
		seen[e.combatant_id] = k + 1
		var key := "%s#%d" % [e.combatant_id, int(offsets.get(e.combatant_id, 0)) + k]
		out.append({"key": key, "id": e.combatant_id, "team": e.team, "skipped": e.skipped, "ghost": e.is_preview})
	return out


func slot_rect(slot: int) -> Rect2:
	var inset := HudLayout.num(_metrics, "inset")
	var w := size.x - inset * 2.0
	if slot == 0:
		return Rect2(inset, inset, w, HudLayout.num(_metrics, "slot0_height"))
	var y := inset + HudLayout.num(_metrics, "first_chip_offset") + (slot - 1) * HudLayout.num(_metrics, "chip_pitch")
	return Rect2(inset, y, w, HudLayout.num(_metrics, "chip_height"))


func chip_for_key(key: String) -> TimelineChip:
	return _chips.get(key) as TimelineChip


func _sync_chips(mode: StringName) -> void:
	var live: Dictionary = {}
	var dur := HudLayout.num(_metrics, "reorder_sec" if mode == MODE_TURN else "preview_in_sec")
	var stagger := HudLayout.num(_metrics, "stagger_sec") if mode == MODE_TURN else 0.0
	for s in slots:
		var key: String = s["key"]
		live[key] = true
		var chip := _chips.get(key) as TimelineChip
		var r := slot_rect(int(s["slot"]))
		var fresh := chip == null
		if fresh:
			chip = TimelineChip.new()
			chip.setup(_metrics)
			add_child(chip)
			_chips[key] = chip
			# A turn entering the bottom of the order rises in from one pitch below.
			var from_below := HudLayout.num(_metrics, "chip_pitch") if mode == MODE_TURN else 0.0
			chip.position = r.position + Vector2(0.0, from_below)
			chip.size = r.size
			chip.modulate.a = 0.0
		chip.target_color = _target_color
		chip.apply(s, _identity.get(s["id"], {}), bool(s["is_current"]))
		_move(chip, r, dur, stagger * int(s["slot"]), fresh, mode)
		if bool(s["is_current"]) and mode == MODE_TURN:
			_pulse(chip)
	for key: String in _chips.keys():
		if not live.has(key):
			_retire(_chips[key] as TimelineChip)
			_chips.erase(key)


func _move(chip: TimelineChip, r: Rect2, dur: float, delay: float, fresh: bool, mode: StringName) -> void:
	if chip.move_tween != null and chip.move_tween.is_valid():
		chip.move_tween.kill()
	if not is_inside_tree() or dur <= 0.0:
		chip.position = r.position
		chip.size = r.size
		chip.modulate.a = 1.0
		return
	var tw := chip.create_tween().set_parallel(true)
	chip.move_tween = tw
	var trans := Tween.TRANS_QUART if mode == MODE_TURN else Tween.TRANS_CUBIC
	var ease_type := Tween.EASE_IN_OUT if mode == MODE_TURN else Tween.EASE_OUT
	tw.tween_property(chip, "position", r.position, dur).set_trans(trans).set_ease(ease_type).set_delay(delay)
	tw.tween_property(chip, "size", r.size, dur).set_trans(trans).set_ease(ease_type).set_delay(delay)
	if fresh or chip.modulate.a < 1.0:
		tw.tween_property(chip, "modulate:a", 1.0, dur).set_delay(delay)


func _pulse(chip: TimelineChip) -> void:
	if not is_inside_tree():
		return
	var half := HudLayout.num(_metrics, "pulse_sec") * 0.5
	var big := HudLayout.num(_metrics, "pulse_scale")
	chip.pivot_offset = chip.size * 0.5
	var tw := chip.create_tween()
	tw.tween_property(chip, "scale", Vector2(big, big), half).set_ease(Tween.EASE_OUT)
	tw.tween_property(chip, "scale", Vector2.ONE, half).set_ease(Tween.EASE_IN)


func _retire(chip: TimelineChip) -> void:
	if chip.move_tween != null and chip.move_tween.is_valid():
		chip.move_tween.kill()
	if not is_inside_tree():
		chip.queue_free()
		return
	var tw := chip.create_tween()
	tw.tween_property(chip, "modulate:a", 0.0, HudLayout.num(_metrics, "preview_out_sec"))
	tw.tween_callback(chip.queue_free)

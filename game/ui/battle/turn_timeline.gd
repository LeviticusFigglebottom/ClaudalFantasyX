class_name TurnTimeline
extends Control
## The always-visible turn order (SPEC §6.1, docs/kb/art/ui.md §6.1). Slot 0 is the fighter
## acting now; slots 1..15 come from BattleEngine.preview(). While a command is hovered, the
## preview's entries slide to their new slots, the actor's next turn shows as a ghost, and any
## chip the action shifts gets ▲/▼ (pillar 4). A swap preview (BattleEngine.preview_swap) is a
## whole new order instead (`full_preview`), slot 0 included. Pure view: never touches combat state.

const MODE_PREVIEW := &"preview"
const MODE_TURN := &"turn"

## Turns shown, including the current one (CtbTimeline.PREVIEW_LENGTH).
var length := CtbTimeline.PREVIEW_LENGTH
## Last slots shown (for tests and the help line).
var slots: Array[Dictionary] = []
## Reduced motion (UiSettings): chips snap to their slot with a short cross-fade, no pulse.
var reduced_motion := false
var crossfade_sec := 0.0
var crossfade_from_alpha := 0.0
## Caption under the name on slot 0 ("Acting now", or why the fighter acts on its own).
var caption := ""
## Skill id -> label for turns already committed to a telegraphed skill (TurnEntry.intent, e.g. the
## Drownbell's toll): such a chip reads "<name> · <label>" in the danger color (M2-FP-06).
var intent_labels: Dictionary = {}

var _metrics: Dictionary = {}
## Combatant id -> {label: String, tint: Color}.
var _identity: Dictionary = {}
## Combatant id -> how many of its turns have passed (keeps chip keys stable across turns).
var _offsets: Dictionary = {}
## Slot key -> TimelineChip.
var _chips: Dictionary = {}
## Hidden chips built ahead of time (prebuild); a new turn takes one before making its own.
var _pool: Array[TimelineChip] = []
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


## M2-BPR-01: while an action's choreography plays, slot 0 is who acts next, not who is acting. Its caption
## reads `text`; "" puts the turn caption back.
func set_head_caption(text: String) -> void:
	if slots.is_empty():
		return
	var head: Dictionary = slots[0]
	head["caption"] = text if text != "" else caption
	var chip := chip_for_key(str(head["key"]))
	if chip != null:
		chip.apply(head, _identity.get(head["id"], {}), bool(head["is_current"]))


## Shows the order. `base` is engine.preview() (no candidate action). `preview` is
## engine.preview(skill, target, length - 1), or empty when nothing is hovered.
func show_turns(
	current_id: StringName,
	base: Array[TurnEntry],
	preview: Array[TurnEntry] = [],
	targets: Array[StringName] = [],
	target_color: Color = Color.WHITE,
	mode: StringName = MODE_PREVIEW,
	full_preview: bool = false
) -> void:
	_target_color = target_color
	var affected: Array[StringName] = [current_id]
	affected.append_array(targets)
	slots = build_slots(current_id, base, preview, _offsets, length, affected, full_preview)
	for s in slots:
		s["targeted"] = targets.has(s["id"]) and not bool(s["is_current"])
		s["caption"] = caption if bool(s["is_current"]) else ""
		s["intent_label"] = str(intent_labels.get(s.get("intent", &""), ""))
	_sync_chips(mode)


## Pure layout of the timeline: one Dictionary per visible slot with
## {key, id, team, slot, skipped, ghost, moved, is_current, doom}. Keys are "<id>#<turn index>",
## so a turn keeps its key while the preview moves it, and `moved` compares against `base`.
## With `affected` set, only those fighters get ▲/▼ (the actor and its targets): everyone else
## still slides, but arrows on every chip would bury the two that matter.
## `full_preview`: `preview` is a whole order from slot 0 (a swap preview, where the entrant may
## take the current turn). Turns that are not in `base` (the entrant's) get no arrow.
static func build_slots(
	current_id: StringName,
	base: Array[TurnEntry],
	preview: Array[TurnEntry],
	offsets: Dictionary,
	count: int,
	affected: Array[StringName] = [],
	full_preview: bool = false
) -> Array[Dictionary]:
	var base_keyed := _keyed(base, offsets, &"")
	var base_slot: Dictionary = {}
	for i in base_keyed.size():
		base_slot[base_keyed[i]["key"]] = i
	var out: Array[Dictionary] = []
	if full_preview and not preview.is_empty():
		var full := _keyed(preview, offsets, &"")
		for i in mini(full.size(), count):
			var f: Dictionary = full[i]
			f["slot"] = i
			f["is_current"] = i == 0
			var known := base_slot.has(f["key"])
			var arrow := known and (affected.is_empty() or affected.has(f["id"]))
			f["moved"] = signi(i - int(base_slot.get(f["key"], i))) if arrow else 0
			out.append(f)
		return out
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
		(
			out
			. append(
				{
					"key": key,
					"id": e.combatant_id,
					"team": e.team,
					"skipped": e.skipped,
					"ghost": e.is_preview,
					"doom": e.doom,
					"intent": e.intent,
				}
			)
		)
	return out


## Builds `count` hidden chips now, so a later show_turns() only fills them in. Entering the
## tree (theme propagation through each chip's labels) is most of a chip's cost, so a staged
## battle build spreads this over frames before the first order is shown (M1-UI-03).
func prebuild(count: int) -> void:
	for i in count:
		var chip := _new_chip()
		chip.visible = false
		_pool.append(chip)


func pooled_count() -> int:
	return _pool.size()


func _take_chip() -> TimelineChip:
	if _pool.is_empty():
		return _new_chip()
	var chip: TimelineChip = _pool.pop_front()
	chip.visible = true
	return chip


func _new_chip() -> TimelineChip:
	var chip := TimelineChip.new()
	chip.setup(_metrics)
	add_child(chip)
	return chip


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
			chip = _take_chip()
			_chips[key] = chip
			# A turn entering the bottom of the order rises in from one pitch below.
			var from_below := HudLayout.num(_metrics, "chip_pitch") if mode == MODE_TURN else 0.0
			chip.position = r.position + Vector2(0.0, from_below)
			chip.size = r.size
			chip.modulate.a = 0.0
		chip.target_color = _target_color
		chip.apply(s, _identity.get(s["id"], {}), bool(s["is_current"]))
		_move(chip, r, dur, stagger * int(s["slot"]), fresh, mode)
		if bool(s["is_current"]) and mode == MODE_TURN and not reduced_motion:
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
	if reduced_motion:
		_crossfade(chip, r, fresh)
		return
	var tw := chip.create_tween().set_parallel(true)
	chip.move_tween = tw
	var trans := Tween.TRANS_QUART if mode == MODE_TURN else Tween.TRANS_CUBIC
	var ease_type := Tween.EASE_IN_OUT if mode == MODE_TURN else Tween.EASE_OUT
	tw.tween_property(chip, "position", r.position, dur).set_trans(trans).set_ease(ease_type).set_delay(delay)
	tw.tween_property(chip, "size", r.size, dur).set_trans(trans).set_ease(ease_type).set_delay(delay)
	if fresh or chip.modulate.a < 1.0:
		tw.tween_property(chip, "modulate:a", 1.0, dur).set_delay(delay)


## Reduced motion: no slide. A chip that changes slot (or appears) snaps there and fades up.
func _crossfade(chip: TimelineChip, r: Rect2, fresh: bool) -> void:
	var moved := fresh or not chip.position.is_equal_approx(r.position) or not chip.size.is_equal_approx(r.size)
	chip.position = r.position
	chip.size = r.size
	chip.scale = Vector2.ONE
	if not moved or crossfade_sec <= 0.0:
		chip.modulate.a = 1.0
		return
	chip.modulate.a = 0.0 if fresh else minf(chip.modulate.a, crossfade_from_alpha)
	var tw := chip.create_tween()
	chip.move_tween = tw
	tw.tween_property(chip, "modulate:a", 1.0, crossfade_sec)


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
	var out_sec := crossfade_sec if reduced_motion else HudLayout.num(_metrics, "preview_out_sec")
	tw.tween_property(chip, "modulate:a", 0.0, out_sec)
	tw.tween_callback(chip.queue_free)

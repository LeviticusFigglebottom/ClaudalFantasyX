class_name Ch01Zone
extends GreyboxZone
## A Ch1 greybox zone root (M3-C01-02; docs/kb/tech/chapter_flow.md "Ch1"): a GreyboxZone with the
## few things Ch1's story steps call that the generic zone doesn't have. Every one is reached with a
## ZoneStory `zone` step ({"zone": method, "args": [...]}) and reads its numbers from data
## (game/data/flow/ch01_field.json, the layout, the chapter file):
##   begin_chapter(n)        Game.set_chapter(n): the chapter autosave (ADR 0018), at C1-01's card.
##   rest(source)            a full heal, no save: a bell-room (C1-03) or the breath before Hullgnaw.
##                           Emits EventBus.party_full_heal_requested(source), as a shrine or inn does.
##   give(items, lume)       adds {item id: count} to the bag (a negative count takes it away) and
##                           lume to the purse: a cut prop, the old tin, the gauge-wheel's sale.
##   prompt(id)              a one-time tutorial prompt (ch01_field.json prompts): its scene plays on
##                           `hint` unless its seen-flag is set, then the flag is set.
##   hide_block(id) / show_block(id)  a Greybox block (or a stage actor) gone or back, its collision
##                           with it: a bridge that breaks, a hull that drifts clear.
## The layout may also set "fog": {color, density} on the zone's environment (the Underway's murk).

const FIELD_PATH := "res://game/data/flow/ch01_field.json"
const KEY_PROMPTS := "prompts"
const KEY_HOLD := "hold_sec"

## The tutorial prompt sequencer: advances by itself and never holds the player (tests: instant).
var hint: CutsceneSequencer
## ch01_field.json.
var field: Dictionary = {}
## Full heals requested so far (tests read it).
var rests := 0


func build() -> void:
	if hint != null:
		return
	super()
	field = read_json(FIELD_PATH)
	_build_fog()
	hint = CutsceneSequencer.new()
	hint.name = "Hint"
	hint.hold_player = false
	hint.auto_advance = true
	hint.auto_advance_hold_sec = float((field.get(KEY_PROMPTS, {}) as Dictionary).get(KEY_HOLD, 0.0))
	add_child(hint)


func begin_chapter(chapter: int) -> void:
	Game.set_chapter(chapter)


func rest(source: String) -> void:
	rests += 1
	EventBus.party_full_heal_requested.emit(StringName(source))


## Adds every {item id: count} (negative: removes up to that many) and earns `lume`.
func give(items: Dictionary, lume: int = 0) -> void:
	var goods := PartyGoods.from_state(ItemDB.load_default(), Game.state)
	for id: Variant in items:
		var n := int(items[id])
		if n > 0:
			goods.inventory.add(StringName(str(id)), n)
		elif n < 0:
			goods.inventory.remove(StringName(str(id)), mini(-n, goods.inventory.count(StringName(str(id)))))
	goods.wallet.earn(lume)


## Plays prompt `id` once (its seen-flag). Returns true when it played.
func prompt(id: String) -> bool:
	var row: Dictionary = (field.get(KEY_PROMPTS, {}) as Dictionary).get(id, {})
	var flag := StringName(str(row.get("flag", "")))
	if row.is_empty() or flag == &"" or bool(Game.get_flag(flag)):
		return false
	Game.set_flag(flag)
	if hint.is_playing():
		return true  # the flag is spent; one prompt at a time
	hint.play(StringName(str(row.get("scene", ""))), stage)
	return true


func hide_block(id: String) -> void:
	_set_block(id, false)


func show_block(id: String) -> void:
	_set_block(id, true)


## True when Greybox/<id> (or the stage actor `id`) is shown.
func block_shown(id: String) -> bool:
	var n := _block(id)
	return n != null and n.visible


func _set_block(id: String, shown: bool) -> void:
	var n := _block(id)
	if n == null:
		push_warning("Ch01Zone %s: no block or actor '%s'" % [location_id, id])
		return
	n.visible = shown
	var shape := n.get_node_or_null(^"Shape") as CollisionShape3D
	if shape != null:
		shape.disabled = not shown


func _block(id: String) -> Node3D:
	var n := get_node_or_null(NodePath("%s/%s" % [GREYBOX, id])) as Node3D
	if n == null and stage != null:
		n = stage.actor(StringName(id))
	return n


func _build_fog() -> void:
	var f: Dictionary = layout.get("fog", {})
	var we := get_node_or_null(^"WorldEnvironment") as WorldEnvironment
	if f.is_empty() or we == null:
		return
	we.environment.fog_enabled = true
	we.environment.fog_light_color = Color.html(str(f.get("color", "#000000")))
	we.environment.fog_density = float(f.get("density", 0.0))

class_name Ch08CoilspireZone
extends Ch08Zone
## Coilspire, `ch08/coilspire` (M3-C08-02; act1_ch08.md B03-B07): the headland path, the keeper's hut,
## the spire's four tiers and the crown with its beacon gallery. A Ch08Zone that is the view of
## CoilspireTrial (the rules; ch08_field.json "trial"). Layout triggers carry {"flue": key id}; they
## answer only while the trial's begun_flag is set, the flame isn't at the crown and the story is free.
## The view:
##   - turns Greybox/Key_<key> by trial.key_turn_deg while it is open, and back when it shuts;
##   - lights a tier (shows Greybox/Flame_<tier>, hides Greybox/Gate_<tier>) and writes the climb to
##     the numeric tiers_flag, so a battle's reload or a load builds the trial where it was;
##   - at the top sets crown_flag and refreshes the states (the crown door opens);
##   - the side flue's niche: sets niche_flag and hides Greybox/NicheSeal;
##   - the seized key: when the seized_hero is with the party (active or reserve) it plays the story's
##     seized_beat (Liss frees the key and finds the mark), then turns the key; otherwise nothing;
##   - plays hint_scene on the hint sequencer once a tier after hint_sec idle.

const KEY_TRIAL := "trial"
const KEY_FLUE := "flue"
const KEY_TURN_DEG := "key_turn_deg"
const KEY_BLOCK := "Key_%s"
const FLAME_BLOCK := "Flame_%s"
const GATE_BLOCK := "Gate_%s"
const SEAL_BLOCK := "NicheSeal"

var trial: CoilspireTrial
## The last turn's outcome (tests read it).
var last_outcome: StringName = &""


func build() -> void:
	if trial != null:
		return
	super()
	trial = CoilspireTrial.new(ch08_field.get(KEY_TRIAL, {}))
	trial.turned.connect(_on_turned)
	trial.coughed.connect(_on_coughed)
	trial.lit.connect(_on_lit)
	trial.niche_opened.connect(_on_niche)
	trial.hint_due.connect(_on_hint)


func _ready() -> void:
	super()
	FieldEvents.connect_interacted(_on_interacted)
	trial.restore(
		int(Game.get_flag(_flag("tiers_flag"), 0)),
		bool(Game.get_flag(_flag("niche_flag"))),
		bool(Game.get_flag(_flag("seized_flag")))
	)
	for i in trial.tier_count():
		if i < trial.tier:
			_show_lit(i)
		elif _block(FLAME_BLOCK % trial.tier_id(i)) != null:
			hide_block(FLAME_BLOCK % trial.tier_id(i))
	if trial.niche_open:
		hide_block(SEAL_BLOCK)


func _exit_tree() -> void:
	if EventBus.is_connected(FieldEvents.INTERACTED, _on_interacted):
		EventBus.disconnect(FieldEvents.INTERACTED, _on_interacted)


func _physics_process(delta: float) -> void:
	if live():
		trial.advance(delta)


## True while the flue-keys answer (see the class comment).
func live() -> bool:
	return bool(Game.get_flag(_flag("begun_flag"))) and not trial.is_done() and story != null and story.is_free()


## Turns flue-key `key` (what an interaction does). Returns true when the trial took it.
func act(key: String) -> bool:
	if not live():
		return false
	var k := StringName(key)
	if trial.is_seized(k):
		if not _wright_with_party():
			return false
		_free_seized(k)
		return true
	last_outcome = trial.turn(k)
	return last_outcome != CoilspireTrial.OUT_NONE


func _free_seized(key: StringName) -> void:
	await story.play_beat(StringName(str(trial.data.get("seized_beat", ""))))
	if bool(Game.get_flag(_flag("seized_flag"))):
		trial.freed = true
		last_outcome = trial.turn(key)


func _wright_with_party() -> bool:
	var hero := StringName(str(trial.data.get("seized_hero", "")))
	return Game.state.party_ids.has(hero) or Game.state.reserve_ids.has(hero)


func _on_interacted(_id: StringName, _kind: StringName, payload: Dictionary) -> void:
	if payload.has(KEY_FLUE):
		act(str(payload[KEY_FLUE]))


func _on_turned(key: StringName, is_open: bool) -> void:
	var n := _block(KEY_BLOCK % key)
	if n != null:
		n.rotation_degrees.y = float(trial.data.get(KEY_TURN_DEG, 0.0)) if is_open else 0.0


func _on_coughed(tier: int) -> void:
	for k in trial.keys_of(tier):
		_on_turned(k, false)


func _on_lit(tier: int) -> void:
	_on_coughed(tier)  # every key on the lit tier goes back to shut
	Game.set_flag(_flag("tiers_flag"), trial.tier)
	_show_lit(tier)
	if trial.is_done():
		Game.set_flag(_flag("crown_flag"))
		refresh_states()


func _on_niche() -> void:
	Game.set_flag(_flag("niche_flag"))
	hide_block(SEAL_BLOCK)
	give({"sailmakers_needle": 1})  # M3-UI-204 (ADR 0040): the tier-2 niche gives the needle


func _on_hint() -> void:
	if hint != null and not hint.is_playing():
		hint.play(StringName(str(trial.data.get("hint_scene", ""))), stage)


func _show_lit(tier: int) -> void:
	var id := String(trial.tier_id(tier))
	if _block(FLAME_BLOCK % id) != null:
		show_block(FLAME_BLOCK % id)
	if _block(GATE_BLOCK % id) != null:
		hide_block(GATE_BLOCK % id)


func _flag(key: String) -> StringName:
	return StringName(str(trial.data.get(key, "")))

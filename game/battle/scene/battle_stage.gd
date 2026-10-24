class_name BattleStage
extends Node3D
## The 3D half of the battle sandbox: places FighterStandIns on the slot markers, shows ground
## rings, and projects fighters to screen space for the HUD. Reads engine state, never writes.
## KO'd fighters sink and fade; petrified ones turn to stone where they stand. shake() nudges the
## camera on heavy hits (the controller skips it under reduced motion).

const CONFIG_PATH := "res://game/data/ui/battle_sandbox.json"

static var _config: Dictionary = {}

## Camera shakes started (tests read it).
var shakes_started := 0
## The choreography sequencer for the current engine (BattleChoreo.attached sets it; M2-BPR-01).
var choreo: BattleChoreo

var _party_slots: Array[Marker3D] = []
var _enemy_slots: Array[Marker3D] = []
## Combatant id -> FighterStandIn.
var _fighters: Dictionary = {}
## Enemy combatant id -> the enemy slot index it stands on.
var _enemy_slot_of: Dictionary = {}
var _shake_tween: Tween

@onready var camera: Camera3D = %BattleCamera
@onready var _fighter_root: Node3D = %Fighters


static func config() -> Dictionary:
	if _config.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(CONFIG_PATH))
		if typeof(parsed) != TYPE_DICTIONARY:
			push_error("BattleStage: could not read %s" % CONFIG_PATH)
			return {}
		_config = (parsed as Dictionary).get("battle_sandbox", {}) as Dictionary
	return _config


## Lattice progress for fighters `ids` on the sandbox board: `saved` (GameStateData.lattice) when
## it holds any, otherwise a fresh start. Every id gets a traveler. A save is restored onto the
## board it names (M1-ARC-14), so a configured board change never re-homes saved travelers.
static func lattice_for(ids: Array[StringName], saved: Dictionary = {}) -> LatticeProgress:
	var configured := StringName(str(config().get("board", LatticeBoard.DEFAULT_BOARD)))
	var board := LatticeProgress.board_for(saved, configured)
	var rules := LatticeRules.load_file()
	var p := (
		LatticeProgress.from_dict(saved, board, rules) if not saved.is_empty() else LatticeProgress.new(board, rules)
	)
	for cid in ids:
		p.add_character(cid)
	return p


## Stand-in spec for a combatant id ("reef_crab#1" uses the "reef_crab" row), defaults merged.
static func stand_in_spec(cid: StringName) -> Dictionary:
	var cfg := config()
	var base := String(cid).get_slice("#", 0)
	var row: Dictionary = (cfg.get("stand_ins", {}) as Dictionary).get(base, {})
	return (cfg.get("stand_in_defaults", {}) as Dictionary).merged(row, true)


func _ready() -> void:
	for n in %PartySlots.get_children():
		_party_slots.append(n as Marker3D)
	for n in %EnemySlots.get_children():
		_enemy_slots.append(n as Marker3D)


func spawn(engine: BattleEngine) -> void:
	for f: FighterStandIn in _fighters.values():
		f.queue_free()
	_fighters.clear()
	for i in engine.party_active.size():
		_place(engine.party_active[i].id, _party_slots[i])
	_enemy_slot_of.clear()
	for i in engine.enemies.size():
		_seat_enemy(engine.enemies[i].id, mini(i, _enemy_slots.size() - 1))


## Seats an enemy that joined mid-battle (BossMechanics spawns and summons) in the first enemy
## slot nobody standing holds; a fallen fighter's stand-in there gives way. If every slot is
## held, it shares the last one.
func add_enemy(c: BattleCombatant, engine: BattleEngine) -> void:
	var held: Dictionary = {}
	for e in engine.enemies:
		if e != c and e.is_alive() and _enemy_slot_of.has(e.id):
			held[int(_enemy_slot_of[e.id])] = true
	var slot := _enemy_slots.size() - 1
	for i in _enemy_slots.size():
		if not held.has(i):
			slot = i
			break
	for cid: StringName in _enemy_slot_of.keys():
		if int(_enemy_slot_of[cid]) == slot and not held.has(slot) and _fighters.has(cid):
			(_fighters[cid] as FighterStandIn).queue_free()
			_fighters.erase(cid)
			_enemy_slot_of.erase(cid)
	_seat_enemy(c.id, slot)


func _seat_enemy(cid: StringName, slot: int) -> void:
	_place(cid, _enemy_slots[slot])
	_enemy_slot_of[cid] = slot


## Re-seats the active party after a swap (slot i shows party_active[i]) or a Vowbound's call or
## departure (M2-UI-05): every party stand-in no longer on the field steps off, and a called
## Vowbound stands alone on battle_sandbox.json's vowbound_slot.
func sync_party(engine: BattleEngine) -> void:
	var on_field := BattleIds.of(engine.party_active)
	for cid: StringName in _fighters.keys():
		if not _enemy_slot_of.has(cid) and not on_field.has(cid):
			var f := _fighters[cid] as FighterStandIn
			_fighters.erase(cid)
			if choreo != null:
				choreo.leave(cid, f)  # M2-BPR-04: a call's step-off or a Vowbound's exit plays out
			else:
				f.queue_free()
	var out := engine.vowbound.is_out()
	for i in engine.party_active.size():
		var cid := engine.party_active[i].id
		if not _fighters.has(cid):
			var slot := clampi(int(config().get("vowbound_slot", i)), 0, _party_slots.size() - 1) if out else i
			_place(cid, _party_slots[slot])
			if choreo != null:
				choreo.enter(cid)


func refresh_ko(engine: BattleEngine) -> void:
	var cfg := config()
	var stone: Dictionary = cfg.get("stone", {})
	for c in engine.party_active + engine.enemies:
		var f := stand_in(c.id)
		if f == null or (choreo != null and choreo.holds_ko(c.id)):
			continue  # BattleChoreo shows this KO on its collapse beat
		f.set_stone(
			c.is_petrified(), Color.html(str(stone.get("color", "#FFFFFF"))), float(stone.get("roughness", 1.0))
		)
		var ko := c.hp <= 0
		f.set_ko(ko, float(cfg.get("ko_sink_m", 0.0)), float(cfg.get("ko_alpha", 1.0)))
		if choreo != null:
			choreo.on_ko_state(c.id, ko)


## How long the result panel waits after the battle ends: `base`, or longer for the victory pose or the escape.
func outro_hold(base: float) -> float:
	return choreo.outro.hold(base) if choreo != null and choreo.outro != null else base


## How long the controller holds after an action: `base`, or longer while the choreography plays.
func hold_after(base: float) -> float:
	return choreo.hold_after(base) if choreo != null else base


## A short, decaying side-to-side camera nudge (deterministic: no randomness).
func shake() -> void:
	if camera == null or not is_inside_tree():
		return
	var cfg: Dictionary = config().get("shake", {})
	var amp := float(cfg.get("amplitude_m", 0.0))
	var steps := maxi(int(cfg.get("steps", 1)), 1)
	var step_sec := float(cfg.get("sec", 0.0)) / steps
	if amp <= 0.0 or step_sec <= 0.0:
		return
	shakes_started += 1
	if _shake_tween != null and _shake_tween.is_valid():
		_shake_tween.kill()
	_shake_tween = create_tween()
	for i in steps:
		var side := 1.0 if i % 2 == 0 else -1.0
		var fade := 1.0 - float(i) / steps
		_shake_tween.tween_property(camera, "h_offset", amp * side * fade, step_sec)
	_shake_tween.tween_property(camera, "h_offset", 0.0, step_sec)


func stand_in(cid: StringName) -> FighterStandIn:
	return _fighters.get(cid) as FighterStandIn


func has_fighter(cid: StringName) -> bool:
	return _fighters.has(cid)


## Screen position (canvas coordinates) just above the fighter's head.
func screen_pos(cid: StringName, extra_m: float = 0.0) -> Vector2:
	var f := stand_in(cid)
	if f == null or camera == null:
		return Vector2.ZERO
	return camera.unproject_position(f.head_position(extra_m))


func set_rings(ids: Array[StringName], hostile: Array[bool], ally_color: Color, foe_color: Color) -> void:
	for cid: StringName in _fighters:
		var i := ids.find(cid)
		var f := _fighters[cid] as FighterStandIn
		if i < 0:
			f.set_ring(FighterStandIn.RING_NONE, ally_color)
		elif hostile[i]:
			f.set_ring(FighterStandIn.RING_FOE, foe_color)
		else:
			f.set_ring(FighterStandIn.RING_ALLY, ally_color)


func clear_rings() -> void:
	for f: FighterStandIn in _fighters.values():
		f.set_ring(FighterStandIn.RING_NONE, Color.WHITE)


func ringed_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for cid: StringName in _fighters:
		if (_fighters[cid] as FighterStandIn).ring_mode_visible():
			out.append(cid)
	return out


func _place(cid: StringName, slot: Marker3D) -> void:
	var f := FighterStandIn.new()
	_fighter_root.add_child(f)
	f.setup(cid, stand_in_spec(cid), config().get("ring", {}) as Dictionary)
	f.global_transform = slot.global_transform
	_fighters[cid] = f

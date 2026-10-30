class_name BattleStage
extends Node3D
## The 3D half of the battle sandbox: places FighterStandIns on the slot markers, shows ground
## rings, and projects fighters to screen space for the HUD. Reads engine state, never writes.
## KO'd fighters sink and fade; petrified ones turn to stone where they stand. shake() nudges the
## camera on heavy hits (the controller skips it under reduced motion).

const CONFIG_PATH := "res://game/data/ui/battle_sandbox.json"
const SETTING_SHAKE := &"screen_shake"  # M3-BPR-401: accessibility.json
const WITHDRAWN_META := &"hymn_withdrawn"  # M3-BPR-406: the retreat started
const WITHDRAW_TWEEN_META := &"hymn_withdraw_tween"  # its tween, so a freeze-frame can hold it mid-way

static var _config: Dictionary = {}

## Camera shakes started (tests read it).
var shakes_started := 0
## The choreography sequencer for the current engine (BattleChoreo.attached sets it; M2-BPR-01). Setting it
## hooks the part cues to its contact beat (M3-C05-07).
var choreo: BattleChoreo:
	set(value):
		choreo = value
		part_cues = BattlePartCues.attach(self, value, part_cues)
## Model parts shown and hidden by battle events (the Cinder Matron's Crust; M3-C05-07).
var part_cues: BattlePartCues

var _party_slots: Array[Marker3D] = []
var _enemy_slots: Array[Marker3D] = []
## Combatant id -> FighterStandIn.
var _fighters: Dictionary = {}
## Enemy combatant id -> the enemy slot index it stands on.
var _enemy_slot_of: Dictionary = {}
var _shake_tween: Tween
## Plays the actors' body clips from the engine's signals (M2-CRE-03).
var _motion: BattleActorMotion

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


## Stand-in spec for a combatant id ("reef_crab#1" uses the "reef_crab" row), defaults merged. An enemy with
## an enemies.json `model` also gets its creature actor `scene` and creatures.json overrides (M2-CRE-03).
static func stand_in_spec(cid: StringName) -> Dictionary:
	var cfg := config()
	var base := String(cid).get_slice("#", 0)
	var row: Dictionary = (cfg.get("stand_ins", {}) as Dictionary).get(base, {})
	var spec := (cfg.get("stand_in_defaults", {}) as Dictionary).merged(row, true)
	var model := CreatureModels.stand_in_overrides(base)
	return spec.merged(model if not model.is_empty() else vowbound_model(base), true)


## A Vowbound's own creature model (M3-BPR-417): a creatures.json row keyed by the Vowbound's id with `vowbound` true
## and a `scene` replaces the capsule, with that row's stand_in keys. The same rule as the creatures track's
## CreatureModels.vowbound_creature (M3-CRE-638); once that reaches this branch it answers first and this stopgap can
## go. {} for anyone else or a row with no scene (the capsule stays).
static func vowbound_model(base: String) -> Dictionary:
	var rows := CreatureActor.data().get("creatures", {}) as Dictionary
	var own := rows.get(base, {}) as Dictionary
	if not bool(own.get("vowbound", false)) or str(own.get("scene", "")) == "":
		return {}
	var is_vowbound := false
	for v: Dictionary in BattleVowbound.load_config():
		is_vowbound = is_vowbound or str(v.get("id", "")) == base
	if not is_vowbound:
		return {}
	var row := CreatureActor.row_for(StringName(base))
	var out := (row.get("stand_in", {}) as Dictionary).duplicate()
	out["scene"] = str(row["scene"])
	return out


func _ready() -> void:
	for n in %PartySlots.get_children():
		_party_slots.append(n as Marker3D)
	for n in %EnemySlots.get_children():
		_enemy_slots.append(n as Marker3D)


func spawn(engine: BattleEngine) -> void:
	_motion = BattleActorMotion.attach(self, engine, _motion)
	for f: FighterStandIn in _fighters.values():
		f.queue_free()
	_fighters.clear()
	for i in engine.party_active.size():
		_place(engine.party_active[i].id, _party_slots[i])
	_enemy_slot_of.clear()
	var seats := _seat_order(engine.enemies)
	for i in engine.enemies.size():
		_seat_enemy(engine.enemies[i].id, seats[i])
	_seat_lone_boss(engine)
	if is_inside_tree():  # M3-BPR-403: the opening line-up keeps the real models' footprints apart
		var data := BattleChoreo.load_data()
		var axis := camera.global_basis.x if camera != null else Vector3.RIGHT  # sideways on screen
		BattleLineup.apply(_side(engine.party_active), data, axis)
		BattleLineup.apply(_side(engine.enemies), data, axis)


## Each opening foe's slot. The encounter sweep (10-30): on the causeway the 2.9 m Lantern Eel, first in the list, took
## the slot nearest the camera and hid the Gull Harrier behind it until it struck. With choreo.json
## spacing.tall_to_back, the tallest foes (stand-in height plus hover) take the slots farthest from the camera; foes of
## equal height keep their own slots. Otherwise slot i, the last shared.
func _seat_order(foes: Array[BattleCombatant]) -> Array[int]:
	var n := foes.size()
	var out: Array[int] = []
	for i in n:
		out.append(mini(i, _enemy_slots.size() - 1))
	var sp := BattleChoreo.load_data().get("spacing", {}) as Dictionary
	if not bool(sp.get("tall_to_back", false)) or camera == null or n < 2 or n > _enemy_slots.size():
		return out
	var slots: Array[int] = []
	for i in n:
		slots.append(i)
	var eye := camera.global_position
	slots.sort_custom(
		func(a: int, b: int) -> bool:
			var da := _enemy_slots[a].global_position.distance_to(eye)
			var db := _enemy_slots[b].global_position.distance_to(eye)
			return da > db if not is_equal_approx(da, db) else a < b
	)
	var order: Array[int] = []
	for i in n:
		order.append(i)
	var top := func(c: BattleCombatant) -> float:
		var spec := stand_in_spec(c.id)
		return float(spec.get("height", 0.0)) + float(spec.get("hover", 0.0))
	var dist := func(i: int) -> float: return _enemy_slots[out[i]].global_position.distance_to(eye)
	order.sort_custom(
		func(a: int, b: int) -> bool:
			var ta: float = top.call(foes[a])
			var tb: float = top.call(foes[b])
			if not is_equal_approx(ta, tb):
				return ta > tb
			return float(dist.call(a)) > float(dist.call(b))  # equal heights keep their own slots
	)
	for k in n:
		out[order[k]] = slots[k]
	return out


func _side(cs: Array[BattleCombatant]) -> Array:
	var out: Array = []
	for c in cs:
		if _fighters.has(c.id):
			out.append(_fighters[c.id])
	return out


## Seats an enemy that joined mid-battle (BossMechanics spawns and summons) in the first enemy
## slot nobody standing holds; a fallen fighter's stand-in there gives way. If every slot is
## held, it shares the last one. It walks onto its mark (choreo.json enter).
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
	if choreo != null:
		choreo.enter(c.id)  # M3-BPR-411: a summoned foe walks onto its mark, not just appears


## M3-CRB-011: a lone boss with a battle_sandbox.json `boss_seats` mark stands there (EnemySlots space), not on Slot0,
## so the default camera sees all of it. Only when it is the only foe at spawn; its slot bookkeeping is unchanged.
func _seat_lone_boss(engine: BattleEngine) -> void:
	if engine.enemies.size() != 1 or _enemy_slots.is_empty() or not is_inside_tree():
		return
	var cid := engine.enemies[0].id
	var seat: Variant = (config().get("boss_seats", {}) as Dictionary).get(String(cid).get_slice("#", 0))
	var f := _fighters.get(cid) as FighterStandIn
	if not (seat is Array and (seat as Array).size() == 3) or f == null:
		return
	var v := seat as Array
	f.global_position = (_enemy_slots[0].get_parent() as Node3D).to_global(
		Vector3(float(v[0]), float(v[1]), float(v[2]))
	)


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
		if c.withdrawn:  # M3-BPR-406: it leaves the field, not felled: it backs away and is gone, no collapse
			_withdraw(f)
			continue
		var ko := c.hp <= 0 or c.yielded  # a foe that yielded or ran has left the fight
		var alpha := float(cfg.get("ko_alpha", 1.0))
		if engine.enemies.has(c):  # a fallen foe fades out and is hidden (M2-BPR-11); the party stays to be revived
			alpha = float(cfg.get("foe_ko_alpha", alpha))
		f.set_ko(ko, float(cfg.get("ko_sink_m", 0.0)), alpha)
		if choreo != null:
			choreo.on_ko_state(c.id, ko)


## A withdrawn foe (ADR 0100: Pell's Storm-Call, a set piece's end) backs away from the party by choreo.json
## withdraw.back_m over withdraw.sec, then is hidden. Reduced motion or instant pacing hide it at once. Once only.
func _withdraw(f: FighterStandIn) -> void:
	if f.has_meta(WITHDRAWN_META):
		return
	f.set_meta(WITHDRAWN_META, true)
	var cfg := BattleChoreo.load_data().get("withdraw", {}) as Dictionary
	var sec := float(cfg.get("sec", 0.0)) / maxf(battle_speed(), 0.01)
	if choreo == null or choreo.reduced_motion or not choreo.animating() or sec <= 0.0 or not is_inside_tree():
		f.visible = false
		return
	var away := -choreo.facing(f.combatant_id) * float(cfg.get("back_m", 0.0))
	var tw := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	tw.tween_property(f, "position", f.position + away, sec)
	tw.tween_callback(f.hide)
	f.set_meta(WITHDRAW_TWEEN_META, tw)


## How long the result panel waits after the battle ends: `base`, or longer for the victory pose or the escape.
func outro_hold(base: float) -> float:
	return choreo.outro.hold(base) if choreo != null and choreo.outro != null else base


## How long the controller holds after an action: `base`, or longer while the choreography plays.
func hold_after(base: float) -> float:
	return choreo.hold_after(base) if choreo != null else base


## The battle presentation speed every battle view plays at: the choreography's (BattleChoreo.speed, M2-BPR-03,
## read from UiSettings.battle_speed), or `fallback` before the sequencer is attached.
func battle_speed(fallback: float = 1.0) -> float:
	return choreo.speed if choreo != null else fallback


## A short, decaying side-to-side camera nudge (deterministic: no randomness). `speed` is the
## battle presentation speed (UiSettings.battle_speed, M2-UI-23); `scale` sizes it (BattleImpact: by the blow).
func shake(speed: float = 1.0, scale: float = 1.0) -> void:
	if camera == null or not is_inside_tree():
		return
	var cfg: Dictionary = config().get("shake", {})
	var amp := float(cfg.get("amplitude_m", 0.0)) * scale * shake_setting()
	var steps := maxi(int(cfg.get("steps", 1)), 1)
	var step_sec := float(cfg.get("sec", 0.0)) / steps
	if amp <= 0.0 or step_sec <= 0.0:
		return
	shakes_started += 1
	if _shake_tween != null and _shake_tween.is_valid():
		_shake_tween.kill()
	_shake_tween = create_tween().set_speed_scale(speed)
	for i in steps:
		var side := 1.0 if i % 2 == 0 else -1.0
		var fade := 1.0 - float(i) / steps
		_shake_tween.tween_property(camera, "h_offset", amp * side * fade, step_sec)
	_shake_tween.tween_property(camera, "h_offset", 0.0, step_sec)


## The player's screen-shake scale (M3-BPR-401): the screen_shake setting (1 full, 0.5 half, 0 off), and none under
## reduced motion, whose help text promises no shake. 1 without settings (tests, tools).
static func shake_setting() -> float:
	var settings := UiSettings.shared()
	if settings == null:
		return 1.0
	if settings.reduced_motion():
		return 0.0
	return float(settings.get_value(SETTING_SHAKE)) if settings.settings().has(SETTING_SHAKE) else 1.0


## Jumps every creature's phase change to its end (CreatureActor.settle; M2-CRE-08), and every entrance in progress
## onto its mark (a summoned foe's walk, M3-BPR-416), for captures.
func settle_actors() -> void:
	for cid: StringName in _fighters.keys():
		var f := _fighters[cid] as FighterStandIn
		if f.creature() != null:
			f.creature().settle()
		if choreo != null:
			choreo.skip_entering(cid)


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

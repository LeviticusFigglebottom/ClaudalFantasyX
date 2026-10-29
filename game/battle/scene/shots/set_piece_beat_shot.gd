extends Node
## Screenshot fixture (M3-BPR-406): a Ch8 set piece's stage beat frozen on the battle sandbox (the parent), live wave
## data on the wall-head arena. `beat`:
## - "intercept": a Tide Crawler's Grip the Stair lands on Toma, who covers the stair (intercepted_by), at contact.
## - "counter": Rhen's counter stance answers a crawler's claw; frozen as his riposte lands on it.
## - "withdraw": a crawler withdraws (Storm-Call, the wave's end): it backs away, held half-way.
## The actions are built as the engine reports them (ActionResult) and played by the real choreography, forced on and
## frozen; the boss intro and floats are off. shots.json battle_ch08_intercept / _counter / _withdraw.

const BEAT_INTERCEPT := &"intercept"
const BEAT_COUNTER := &"counter"
const BEAT_WITHDRAW := &"withdraw"
const CRAWLER := "tide_crawler"

@export var encounter: StringName = &"ch08_stair_hold_1"
@export var party: Array[StringName] = [&"rhen", &"asha", &"toma"]
@export var beat: StringName = BEAT_INTERCEPT
@export var rng_seed := 20261027
## Seconds after the beat's moment (contact; the riposte's landing) the frame holds.
@export var offset_sec := 0.04
## How far through the withdrawal the frame holds (0..1).
@export var withdraw_t := 0.5

var _started := false


func _ready() -> void:
	_start.call_deferred()


func _start() -> void:
	if _started:
		return
	_started = true
	var ctl := get_parent() as BattleController
	ctl.set_meta(BattleBossIntro.META_PLAYED, String(encounter))
	ctl.pacing_scale = 0.0
	ctl.show_damage_numbers = false
	ctl.hud.apply_settings(UiSettings.new())
	ctl.start_battle(party, [], encounter, rng_seed)
	ctl.pacing_scale = 1.0
	var choreo := ctl.stage.choreo
	choreo.force_play = true
	choreo.live = false
	choreo.speed = 1.0
	choreo.reduced_motion = false
	choreo.skip = false
	var foe := _crawler(ctl)
	if beat == BEAT_WITHDRAW:
		foe.withdraw()
		ctl.stage.refresh_ko(ctl.engine)
		var f := ctl.stage.stand_in(foe.id)
		var tw := f.get_meta(BattleStage.WITHDRAW_TWEEN_META) as Tween
		tw.custom_step(float(choreo.data["withdraw"]["sec"]) * withdraw_t)
		tw.set_speed_scale(0.0)
		return
	choreo.frozen = true
	ctl.engine.action_resolved.emit(result(beat, foe.id))
	choreo.seek(moment(choreo.current(), beat) + offset_sec)


## The first crawler on the field.
static func _crawler(ctl: BattleController) -> BattleCombatant:
	for e in ctl.engine.enemies:
		if String(e.id).get_slice("#", 0) == CRAWLER:
			return e
	return ctl.engine.enemies[0]


## The action as the engine reports it: Toma takes the crawler's grip for the stair, or Rhen's riposte answers its
## claw (ADR 0100's intercepted_by and counter_by).
static func result(which: StringName, foe_id: StringName) -> ActionResult:
	var r := ActionResult.new()
	r.actor_id = foe_id
	if which == BEAT_INTERCEPT:
		r.skill_id = &"grip_blow"
		r.intercepted_by = &"toma"
		r.hits = [{"target_id": &"toma", "hit": true, "crit": false, "amount": 24, "statuses_added": []}]
	else:
		r.skill_id = &"tide_claw"
		r.hits = [
			{"target_id": &"rhen", "hit": true, "crit": false, "amount": 18, "statuses_added": []},
			{
				"target_id": foe_id,
				"hit": true,
				"crit": false,
				"amount": 15,
				"statuses_added": [],
				"counter_by": &"rhen"
			},
		]
	return r


## The beat's moment in `plan`: the contact, or the riposte's landing on the attacker.
static func moment(plan: Dictionary, which: StringName) -> float:
	if which == BEAT_COUNTER:
		for re: Dictionary in plan.get("reactions", []):
			if str(re.get("counter_by", "")) != "":
				return float(re["at"])
	return float(plan.get("contact", 0.0))

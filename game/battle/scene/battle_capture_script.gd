class_name BattleCaptureScript
extends RefCounted
## The capture scripts (tests/screenshots/shots.json): each plays a started fixture
## deterministically to its capture state through the controller's public player actions and
## simulated ui_* input, exactly as a player would. Moved out of BattleController (M1-UI-04)
## unchanged; BattleController.run_script() loads the fixture and calls play().

## The Swell ring shot freezes this long before the second flare's peak, the ring closing in.
const RING_SHOT_BEFORE_PEAK_SEC := 0.2
## M2-UI-02 / M2-UI-01 capture states (their fixtures share the id; see shots.json).
const SCRIPT_READ_PANEL := &"read_panel"
const SCRIPT_OPENING_BANNER := &"opening_banner"
const SCRIPT_SWELL_MODES := &"swell_modes"
## M2-UI-05: Asha's Call row highlighted (the call's preview), and Ilun out with Dismiss highlighted.
const SCRIPT_VOWBOUND_CALL := &"vowbound_call"
const SCRIPT_VOWBOUND_OUT := &"vowbound_out"
const VOWBOUND_ID := &"ilun"
const CALLER_ID := &"asha"
## M2-BPR-06: mid-action freeze-frames. Each plays one action with the choreography forced on, frozen at a beat
## (plus an offset in seconds): [actor, skill, target base id ("" = default target), beat, offset].
const CHOREO_PREFIX := "choreo_"
const CHOREO_FREEZES := {
	&"choreo_melee": [&"rhen", &"attack", &"gull_harrier", &"contact", -0.04],
	&"choreo_hit": [&"rhen", &"undertow_cut", &"reef_crab", &"contact", 0.14],
	&"choreo_cast": [&"ysolde", &"ember", &"lantern_eel", &"contact", -0.05],
	&"choreo_support": [&"asha", &"mend", &"rhen", &"contact", -0.05],
	&"choreo_read": [&"ysolde", &"read", &"lantern_eel", &"contact", -0.05],
	&"choreo_ko": [&"rhen", &"attack", &"gull_harrier", &"ko_at", 0.3],
	# M2-BPR-04: Lamp Dive mid-plunge (half way from the leap's top to the contact); a Swell technique unleashes.
	&"choreo_lamp_dive": [&"rhen", &"lamp_dive", &"gull_harrier", &"contact", -0.085],
}
const CHOREO_SWAP := &"choreo_swap"
## The walk-in is frozen at this share of its time.
const SWAP_FREEZE_SHARE := 0.5
## M2-BPR-04: the Drownbell's Toll, frozen this long after its contact: the age BattleBossVfx's shockwave ring
## (started on the contact, in real time) has when the shot is taken (shots.json settle_frames 45 at 60 fps), so
## the party's recoil and the ring agree.
const CHOREO_TOLL := &"choreo_toll"
const TOLL_BELL := &"drownbell"
const TOLL_FREEZE_AFTER_CONTACT_SEC := 0.75
## M2-BPR-04: Ilun rising at his slot after Asha's call, frozen at this share of the rise.
const CHOREO_VOWBOUND_RISE := &"choreo_vowbound_rise"
const RISE_FREEZE_SHARE := 0.5
## A Swell technique in a freeze-frame skips its input with this result (Rhen's three-flare ring).
const SWELL_FREEZE_GRADES: Array[StringName] = [
	SwellInput.GRADE_PERFECT, SwellInput.GRADE_GOOD, SwellInput.GRADE_PERFECT
]


## Plays `ctl`'s already-started fixture `sid` (a BattleController.SCRIPT_* id) to its state.
static func play(ctl: BattleController, sid: StringName) -> void:
	match sid:
		BattleController.SCRIPT_PLAYER_PREVIEW:
			_to_turn_of(ctl, &"rhen")
			ctl.hud.commands.select(BattleMenus.ROW_SKILLS)  # past the Swell row (M2-UI-01)
			_press(ctl, &"ui_accept")
			ctl.hud.commands.select(&"undertow_cut")
			_press(ctl, &"ui_accept")
			ctl.aim_at(&"gull_harrier")
		BattleController.SCRIPT_SWAP_MENU:
			_to_turn_of(ctl, &"rhen")
			ctl.hud.commands.select(BattleMenus.ROW_SWAP)
			_press(ctl, &"ui_accept")
		BattleController.SCRIPT_VICTORY:
			_play_to_victory(ctl)
		BattleController.SCRIPT_DEFEAT:
			_play_naive(ctl)
		BattleController.SCRIPT_STATUSES:
			# Ysolde is provoked by the reflecting Lantern Eel: Ember must go at it and bounces
			# onto Rhen (Doom, Zombie, Regen turned to harm); Asha stands as stone.
			_to_turn_of(ctl, &"ysolde")
			_press(ctl, &"ui_down")
			_press(ctl, &"ui_accept")
			ctl.hud.commands.select(&"ember")
			_press(ctl, &"ui_accept")
		BattleController.SCRIPT_SWELL_RING:
			# Rhen opens with a full gauge: Swell, Lamp Dive on the Gull Harrier, the first flare
			# struck perfectly, then the input frozen with the second ring closing on the lamp.
			_to_turn_of(ctl, &"rhen")
			ctl.hud.commands.select(BattleMenus.ROW_SWELL)
			_press(ctl, &"ui_accept")
			_press(ctl, &"ui_accept")
			ctl.aim_at(&"gull_harrier")
			_press(ctl, &"ui_accept")
			var ring := ctl.swell_input()
			ctl.tick(ring.time_to_peak())
			_press(ctl, &"ui_accept")
			ctl.tick(ring.time_to_peak() - RING_SHOT_BEFORE_PEAK_SEC)
			ctl.swell_input_live = false
		SCRIPT_READ_PANEL:
			# Ysolde opens and Reads the reflecting Lantern Eel: the Read panel holds the battle.
			_to_turn_of(ctl, &"ysolde")
			ctl.hud.commands.select(BattleMenus.ROW_SKILLS)
			_press(ctl, &"ui_accept")
			ctl.hud.commands.select(&"read")
			_press(ctl, &"ui_accept")
			ctl.aim_at(&"lantern_eel")
			_press(ctl, &"ui_accept")
		SCRIPT_OPENING_BANNER:
			pass  # the fixture's ambush plays the foes' turns and shows the banner by itself
		SCRIPT_SWELL_MODES:
			# Rhen's gauge is part full: the Swell page lists Lamp Dive (greyed) and the fill modes.
			_to_turn_of(ctl, &"rhen")
			ctl.hud.commands.select(BattleMenus.ROW_SWELL)
			_press(ctl, &"ui_accept")
			ctl.hud.commands.select(StringName(BattleMenus.ROW_SWELL_MODE_PREFIX + "wake"))
		SCRIPT_VOWBOUND_CALL:
			# Asha's turn with Ilun bound: the Call row shows the order with Ilun in the party's place.
			_to_turn_of(ctl, CALLER_ID)
			ctl.hud.commands.select(StringName(BattleMenus.ROW_CALL_PREFIX + String(VOWBOUND_ID)))
		SCRIPT_VOWBOUND_OUT:
			# Asha calls Ilun, who strikes once and takes the foes' turns; on his next turn Dismiss
			# shows the party's return, Asha after her call delay.
			_to_turn_of(ctl, CALLER_ID)
			ctl.vow.call_vowbound(VOWBOUND_ID)
			ctl.act(BattleMenus.ATTACK_SKILL, [ctl.default_targets(BattleMenus.ATTACK_SKILL)[0].id])
			_to_turn_of(ctl, VOWBOUND_ID)
			ctl.hud.commands.select(BattleMenus.ROW_DISMISS)
		CHOREO_SWAP:
			_to_turn_of(ctl, &"rhen")
			var choreo := _force_choreo(ctl)
			ctl.swap_members(CALLER_ID, &"toma")
			var sec := float((choreo.data.get("enter", {}) as Dictionary).get("sec", 0.0))
			choreo.advance(sec * SWAP_FREEZE_SHARE / choreo.speed)
		CHOREO_TOLL:
			_freeze_toll(ctl)
		CHOREO_VOWBOUND_RISE:
			# Asha calls Ilun: the party has stepped off and Ilun is half way up out of the water at his slot.
			_to_turn_of(ctl, CALLER_ID)
			var choreo := _force_choreo(ctl)
			ctl.vow.call_vowbound(VOWBOUND_ID)
			var rise := choreo.entering(VOWBOUND_ID)
			var spec := rise.get("spec", {}) as Dictionary
			choreo.advance(
				(-float(rise.get("t", 0.0)) + float(spec.get("sec", 0.0)) * RISE_FREEZE_SHARE) / choreo.speed
			)
		_:
			if CHOREO_FREEZES.has(sid):
				_freeze_action(ctl, CHOREO_FREEZES[sid] as Array)


## Forces the choreography on for a capture, with its clock held (BattleChoreo.force_play, frozen).
static func _force_choreo(ctl: BattleController) -> BattleChoreo:
	var choreo := ctl.stage.choreo
	choreo.force_play = true
	choreo.live = false
	choreo.speed = 1.0
	choreo.reduced_motion = false
	choreo.skip = false
	return choreo


## Plays `spec` ([actor, skill, target base id, beat, offset]) and freezes it at its beat + offset.
static func _freeze_action(ctl: BattleController, spec: Array) -> void:
	_to_turn_of(ctl, StringName(spec[0]))
	var choreo := _force_choreo(ctl)
	choreo.frozen = true
	var skill := StringName(spec[1])
	var target := ctl.default_targets(skill)[0].id
	for c in ctl.engine.party_active + ctl.engine.enemies:
		if String(c.id).get_slice("#", 0) == String(spec[2]) and c.is_alive():
			target = c.id
	if ctl.swell.is_technique(ctl.engine.current, skill):
		ctl.unleash(skill, [target], {BattleSwell.RESULT_GRADES: SWELL_FREEZE_GRADES})  # its input skipped
	else:
		ctl.act(skill, [target])
	choreo.seek(float(choreo.current().get(String(spec[3]), 0.0)) + float(spec[4]))


## The party (none of them quick enough to strike the rim) attacks until the Drownbell's Toll fires; the
## choreography is forced on for that one action, frozen just after its contact.
static func _freeze_toll(ctl: BattleController) -> void:
	var engine := ctl.engine
	var choreo := ctl.stage.choreo
	var arm := func(actor: BattleCombatant) -> void:
		if String(actor.id).get_slice("#", 0) == String(TOLL_BELL) and actor.is_charging() and actor.charge_left <= 1:
			_force_choreo(ctl).frozen = true
	engine.turn_started.connect(arm)
	var guard := 0
	while engine.outcome == &"" and not choreo.frozen and guard < CtbTimeline.PREVIEW_LENGTH:
		guard += 1
		if engine.is_party_turn():
			ctl.act(BattleMenus.ATTACK_SKILL, [ctl.default_targets(BattleMenus.ATTACK_SKILL)[0].id])
	engine.turn_started.disconnect(arm)
	if choreo.playing():
		choreo.seek(float(choreo.current()["contact"]) + TOLL_FREEZE_AFTER_CONTACT_SEC)


## Plays (party: Attack the first living foe) until it is `cid`'s turn.
static func _to_turn_of(ctl: BattleController, cid: StringName) -> void:
	var engine := ctl.engine
	var guard := 0
	while engine.outcome == &"" and ctl.current_actor_id() != cid and guard < CtbTimeline.PREVIEW_LENGTH:
		guard += 1
		if engine.is_party_turn():
			ctl.act(BattleMenus.ATTACK_SKILL, [ctl.default_targets(BattleMenus.ATTACK_SKILL)[0].id])


## The sandbox's "elegant answer" policy: bring Toma in for Asha, then hit the weakest foe.
static func _play_to_victory(ctl: BattleController) -> void:
	var engine := ctl.engine
	var guard := 0
	while engine.outcome == &"" and guard < CtbTimeline.PREVIEW_LENGTH * CtbTimeline.PREVIEW_LENGTH:
		guard += 1
		if not engine.is_party_turn():
			break
		if engine.find(&"asha") in engine.party_active and engine.find(&"toma") in engine.party_reserve:
			ctl.swap_members(&"asha", &"toma")
			continue
		var weakest := engine.living_foes_of(engine.current)[0]
		for f in engine.living_foes_of(engine.current):
			if f.hp < weakest.hp:
				weakest = f
		ctl.act(BattleMenus.ATTACK_SKILL, [weakest.id])


## Attack the first living foe until the fight ends.
static func _play_naive(ctl: BattleController) -> void:
	var engine := ctl.engine
	var guard := 0
	while engine.outcome == &"" and guard < CtbTimeline.PREVIEW_LENGTH * CtbTimeline.PREVIEW_LENGTH:
		guard += 1
		if not engine.is_party_turn():
			break
		ctl.act(BattleMenus.ATTACK_SKILL, [engine.living_foes_of(engine.current)[0].id])


static func _press(ctl: BattleController, action: StringName) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	ctl.handle_input(ev)

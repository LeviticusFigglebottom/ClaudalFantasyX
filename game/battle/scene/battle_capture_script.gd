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

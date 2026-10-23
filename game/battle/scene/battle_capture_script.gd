class_name BattleCaptureScript
extends RefCounted
## The capture scripts (tests/screenshots/shots.json): each plays a started fixture
## deterministically to its capture state through the controller's public player actions and
## simulated ui_* input, exactly as a player would. Moved out of BattleController (M1-UI-04)
## unchanged; BattleController.run_script() loads the fixture and calls play().


## Plays `ctl`'s already-started fixture `sid` (a BattleController.SCRIPT_* id) to its state.
static func play(ctl: BattleController, sid: StringName) -> void:
	match sid:
		BattleController.SCRIPT_PLAYER_PREVIEW:
			_to_turn_of(ctl, &"rhen")
			_press(ctl, &"ui_down")
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

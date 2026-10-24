class_name SwellModeRows
extends RefCounted
## Choosing a hero's Swell fill mode on the battle Swell page (M2-UI-01, SPEC §6.2). The page lists
## the techniques, then one row per unlocked mode (BattleMenus.swell_mode_rows). This is the glue
## BattleController's menu handlers call through one-line hooks, so the controller (at its line
## cap) gains no flow of its own:
##   - highlight(): a mode row shows what fills the gauge in that mode and that the choice is
##     free, and the timeline shows the order unchanged (no ghost: choosing costs no time);
##   - pick(): a mode row sets the mode (BattleSwell.set_mode, the engine's own rule) and redraws
##     the page (and the root row's mode name) in place; any other row goes on to `otherwise`
##     (the technique's target pick).
## Pillar 4: the cost ("No time") is on the row, the help line says it, and the timeline agrees.
## The mode lasts for this battle until M2-ARC-01 carries it between battles and saves.


## Handles the highlight of a fill-mode row on the Swell page. True when it did.
static func highlight(ctl: BattleController, row: Dictionary) -> bool:
	var mode := mode_of(ctl, row)
	if mode == &"":
		return false
	_show_unchanged_order(ctl)
	ctl.hud.set_help(ctl.menus.swell_mode_help(ctl.swell, ctl.engine.current, mode))
	return true


## Chooses `row`: a fill-mode row sets the actor's mode (no time passes, the turn stays theirs);
## any other row calls `otherwise`.
static func pick(ctl: BattleController, row: Dictionary, otherwise: Callable) -> void:
	var mode := mode_of(ctl, row)
	if mode == &"":
		otherwise.call()
		return
	var actor := ctl.engine.current
	if actor.swell_mode != mode and ctl.swell.set_mode(actor, mode):
		ctl.hud.commands.refresh_top(ctl.menus.swell_rows(ctl.engine, ctl.swell))
		ctl.hud.commands.refresh_root(ctl.menus.root_rows(ctl.engine, ctl.items, ctl.swell))
		_show_unchanged_order(ctl)
		ctl.hud.set_help(ctl.menus.swell_mode_set_text(ctl.swell, actor))
		return
	ctl.hud.set_help(ctl.menus.swell_mode_help(ctl.swell, actor, mode))


## The mode a Swell-page row chooses (&"" for any other row, or off the Swell page, or when it is
## not the party's turn).
static func mode_of(ctl: BattleController, row: Dictionary) -> StringName:
	if ctl == null or ctl.engine == null or ctl.swell == null:
		return &""
	if ctl.state != BattleController.STATE_SWELL or not ctl.engine.is_party_turn():
		return &""
	return StringName(str(row.get(BattleMenus.KEY_SWELL_MODE, "")))


static func _show_unchanged_order(ctl: BattleController) -> void:
	var tl := ctl.hud.timeline
	tl.caption = ctl.menus.turn_caption(&"")
	var color := ctl.hud.get_theme_color(&"focus", HymnThemeBuilder.PALETTE_TYPE)
	tl.show_turns(ctl.current_actor_id(), ctl.engine.preview(), [], [], color, TurnTimeline.MODE_PREVIEW)


## A fill mode unlocked through play (BattleSwell.mode_unlocked, connected with `ctl` bound) floats
## "{mode} unlocked" over the field in the swell color (M2-UI-03, pillar 5: growth you can see).
## Floats follow show_damage_numbers, so captures stay still.
static func announce(mode: StringName, ctl: BattleController) -> void:
	if not ctl.show_damage_numbers:
		return
	var text := unlocked_text(ctl, mode)
	var at: Array = HudLayout.section(&"swell_ring").get("unlock_at", [0, 0])
	ctl.hud.pop_info(text, Vector2(float(at[0]), float(at[1])), &"swell")


## "{mode} unlocked" for `mode`, in words.
static func unlocked_text(ctl: BattleController, mode: StringName) -> String:
	return ctl.tr("HUD_SWELL_MODE_UNLOCKED_FMT").format({"mode": ctl.menus.swell_mode_name(ctl.swell, mode)})

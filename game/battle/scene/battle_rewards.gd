class_name BattleRewards
extends RefCounted
## The result panel's victory rows and the Lattice award behind them. Moved out of
## BattleController (M1-CMB-04) unchanged, to keep the controller under the file-length cap.


## XP from engine.xp_awards() becomes Lattice movement points (formulas.md, Progression). Fills
## `ctl.last_awards` and, for a live battle, writes the Lattice back to Game.state.
func award_victory(ctl: BattleController) -> Array[Dictionary]:
	var engine := ctl.engine
	var progress := ctl.progress
	var awards := engine.xp_awards()
	var rows: Array[Dictionary] = []
	for c in engine.party_active + engine.party_reserve:
		if not c.participated:
			continue
		var label := ctl.menus.display_name(c)
		if not awards.has(c.id):
			rows.append({"label": label, "xp_text": "", "moves_text": tr("HUD_RESULT_FELL"), "fell": true})
			continue
		var xp := int(awards[c.id])
		var moves := -1
		if progress != null and progress.traveler(c.id) != null:
			moves = progress.award_battle(c.id, xp)
		ctl.last_awards[c.id] = {"xp": xp, "moves": moves}
		var moves_text := tr("HUD_RESULT_MOVES_FMT").format({"n": moves}) if moves >= 0 else tr("HUD_RESULT_NO_LATTICE")
		rows.append({"label": label, "xp_text": tr("HUD_RESULT_XP_FMT").format({"xp": xp}), "moves_text": moves_text})
	if ctl.persist_progress and progress != null and ctl.fixture == null:
		Game.state.lattice = progress.to_dict()
	return rows

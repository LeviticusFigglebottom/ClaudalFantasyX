class_name BattleChoreoPlan
extends RefCounted
## The choreography's plan, as pure data (M2-BPR-01; moved out of BattleChoreo under the lint cap, no behaviour
## change): which style an action plays, and its beat times, reactions and KOs. BattleChoreo's plan_for(), style()
## and style_id_for() call these with its data and engine; tests call either.


## The style an action plays: item_style for an item, else style_by_skill, style_by_target, style_by_kind.
static func style_id_for(data: Dictionary, engine: BattleEngine, result: ActionResult) -> String:
	if result.item_id != &"":
		return str(data.get("item_style", BattleChoreo.FALLBACK_STYLE))
	var sid := String(result.skill_id)
	var by_skill := data.get("style_by_skill", {}) as Dictionary
	if by_skill.has(sid):
		return str(by_skill[sid])
	var row: Dictionary = engine.db.skill(result.skill_id) if engine != null else {}
	var by_target := data.get("style_by_target", {}) as Dictionary
	if by_target.has(str(row.get("target", ""))):
		return str(by_target[str(row["target"])])
	return str((data.get("style_by_kind", {}) as Dictionary).get(str(row.get("kind", "")), BattleChoreo.FALLBACK_STYLE))


static func style(data: Dictionary, id: String) -> Dictionary:
	var styles := data.get("styles", {}) as Dictionary
	return styles.get(id, styles.get(BattleChoreo.FALLBACK_STYLE, {})) as Dictionary


## What an action plays, with no nodes: {style, actor, targets, reactions [{target, kind}], kos, and the beat
## times approach_end, contact, strike_end, recover_end, return_end, ko_at, total}. {} for a failed action.
static func plan_for(data: Dictionary, engine: BattleEngine, result: ActionResult) -> Dictionary:
	if result == null or not result.ok:
		return {}
	var sid := style_id_for(data, engine, result)
	var st := style(data, sid)
	var a := float(st.get("approach_sec", 0.0))
	var s := float(st.get("strike_sec", 0.0))
	var c := a + s * float(st.get("contact_at", 1.0))
	var rec := a + s + float(st.get("recover_sec", 0.0))
	var ret := rec + float(st.get("return_sec", 0.0))
	var targets: Array[StringName] = []
	var reactions: Array[Dictionary] = []
	var kos: Array[StringName] = []
	var stagger := float(st.get("stagger_sec", 0.0))
	for hit: Dictionary in result.hits:
		var tid := StringName(str(hit.get("target_id", "")))
		if not targets.has(tid):
			targets.append(tid)
		if tid == result.actor_id:
			continue
		var amount := int(hit.get("amount", 0))
		var kind := (
			BattleChoreo.REACT_MISS
			if not bool(hit.get("hit", true))
			else (BattleChoreo.REACT_DAMAGE if amount > 0 else "")
		)
		if kind == "" and amount < 0:
			kind = BattleChoreo.REACT_HEAL
		if kind != "":
			reactions.append({"target": tid, "kind": kind, "at": c + stagger * reactions.size()})
		var t := engine.find(tid) if engine != null else null
		if amount > 0 and t != null and t.hp <= 0 and not kos.has(tid):
			kos.append(tid)
	var plan := {
		"style": sid,
		"shot": str(st.get("shot", "")),
		"actor": result.actor_id,
		"targets": targets,
		"reactions": reactions,
		"kos": kos,
		"approach_end": a,
		"contact": c,
		"strike_end": a + s,
		"recover_end": rec,
		"return_end": ret,
	}
	retime(data, plan)
	return plan


## Sets a plan's ko_at (a felled target collapses after its own reaction starts) and total from its reactions'
## start times (`at`: the contact, staggered by stagger_sec, or delayed by a wave's travel).
static func retime(data: Dictionary, plan: Dictionary) -> void:
	var reaction := data.get("reaction", {}) as Dictionary
	var kos: Array = plan["kos"]
	var react_end := float(plan["contact"])
	var ko_from := react_end
	for r: Dictionary in plan["reactions"]:
		var at := float(r["at"])
		react_end = maxf(react_end, at + float((reaction.get(r["kind"], {}) as Dictionary).get("sec", 0.0)))
		if kos.has(r["target"]):
			ko_from = maxf(ko_from, at)
	var ko := data.get("ko", {}) as Dictionary
	plan["ko_at"] = ko_from + float(ko.get("delay_sec", 0.0))
	var total := maxf(float(plan["return_end"]), react_end)
	if not kos.is_empty():
		total = maxf(total, float(plan["ko_at"]) + float(ko.get("collapse_sec", 0.0)))
	plan["total"] = total

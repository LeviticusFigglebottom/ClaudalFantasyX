extends SceneTree
## Command-line entry for the balancing simulator. tools/balance/sim.py runs it:
##   godot --headless --path . -s res://game/battle/sim/sim_main.gd -- \
##       --encounter=sandbox_reef --active=rhen,asha --reserve=toma,ysolde \
##       --policies=naive,role_answer --seeds=1000 [--first-seed=1] [--out=/abs/path.json]
## Prints one line "SIM_RESULT <json>" per policy (aggregate plus per-seed runs) and, with
## --out, writes all of them as a JSON array. Exit code 1 on bad arguments.

const PREFIX := "SIM_RESULT "


func _initialize() -> void:
	var args := _parse(OS.get_cmdline_user_args())
	var encounter := StringName(str(args.get("encounter", "")))
	var active := _ids(str(args.get("active", "")))
	var reserve := _ids(str(args.get("reserve", "")))
	var policies := _ids(str(args.get("policies", ",".join(BattleSim.POLICY_NAMES))))
	var seeds := int(args.get("seeds", "0"))
	var first := int(args.get("first-seed", "1"))
	var sim := BattleSim.new()
	if not sim.db.encounters.has(encounter) or active.is_empty() or seeds <= 0:
		printerr("sim_main: need --encounter=<known id> --active=a,b --seeds=N (got %s)" % str(args))
		quit(1)
		return
	var results: Array = []
	for p in policies:
		var policy := sim.make_policy(p)
		if policy == null:
			quit(1)
			return
		var runs: Array[Dictionary] = []
		for s in range(first, first + seeds):
			runs.append(sim.run_one(encounter, active, reserve, policy, s))
		var agg := BattleSim.summarize(runs)
		agg["encounter"] = String(encounter)
		agg["policy"] = String(p)
		agg["first_seed"] = first
		agg["runs"] = runs
		results.append(agg)
		print(PREFIX + JSON.stringify(agg))
	if args.has("out"):
		var f := FileAccess.open(str(args["out"]), FileAccess.WRITE)
		if f == null:
			printerr("sim_main: cannot write %s" % args["out"])
			quit(1)
			return
		f.store_string(JSON.stringify(results))
		f.close()
	quit(0)


static func _parse(argv: PackedStringArray) -> Dictionary:
	var out: Dictionary = {}
	for a in argv:
		if a.begins_with("--") and a.contains("="):
			out[a.substr(2, a.find("=") - 2)] = a.substr(a.find("=") + 1)
	return out


static func _ids(csv: String) -> Array[StringName]:
	var out: Array[StringName] = []
	for part in csv.split(",", false):
		out.append(StringName(part.strip_edges()))
	return out

extends SceneTree
## Command-line wrapper for the balancing simulator; tools/balance/sim.py runs it:
##   godot --headless --path . -s res://tools/balance/sim_main.gd -- \
##       --encounter=sandbox_reef --active=rhen,asha --reserve=toma,ysolde \
##       --policies=naive,role_answer --seeds=1000 [--first-seed=1] [--out=/abs/path.json]
## Prints one line "SIM_RESULT <json>" per policy and, with --out, writes them all as a JSON
## array. Exit code 1 on bad arguments. All logic lives in BattleSim (run_cli, parse_args),
## which the test suite covers; this file only does process I/O (docs/kb/qa/coverage.md).

const PREFIX := "SIM_RESULT "


func _initialize() -> void:
	var args := BattleSim.parse_args(OS.get_cmdline_user_args())
	var res := BattleSim.new().run_cli(args)
	if not res["ok"]:
		printerr("sim_main: %s" % res["error"])
		quit(1)
		return
	for r: Variant in res["results"]:
		print(PREFIX + JSON.stringify(r))
	if args.has("out"):
		var f := FileAccess.open(str(args["out"]), FileAccess.WRITE)
		if f == null:
			printerr("sim_main: cannot write %s" % args["out"])
			quit(1)
			return
		f.store_string(JSON.stringify(res["results"]))
		f.close()
	quit(0)

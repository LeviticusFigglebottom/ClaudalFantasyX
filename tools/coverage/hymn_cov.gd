@tool
class_name HymnCov
extends Node
## Coverage probe recorder (M1-QA-03, ADR 0013). Never part of the game: tools/coverage/run_coverage.py
## copies it into a temporary instrumented project, registers it as the `HymnCovSink` autoload, and
## rewrites game/battle and game/progression scripts so each statement calls h() or t() first.
## On exit the hit probe ids are written as JSON to the file named by $HYMN_COV_OUT.

const OUT_ENV := "HYMN_COV_OUT"

static var _hits: Dictionary = {}


## Marks a statement probe as executed.
static func h(probe: int) -> void:
	_hits[probe] = true


## Marks a condition or iterable probe as executed; always true so `t() and (cond)` equals `cond`.
static func t(probe: int) -> bool:
	_hits[probe] = true
	return true


## Writes the sorted probe ids to $HYMN_COV_OUT. Returns false if the variable is unset or unwritable.
static func dump() -> bool:
	var path := OS.get_environment(OUT_ENV)
	if path.is_empty():
		return false
	var ids: Array = _hits.keys()
	ids.sort()
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		push_error("HymnCov: cannot write %s" % path)
		return false
	f.store_string(JSON.stringify({"hits": ids}))
	f.close()
	return true


func _exit_tree() -> void:
	dump()

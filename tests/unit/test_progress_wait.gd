extends TestCase
## M2-ARC-08: ProgressWait, the wait that gives up on a stall, not after a fixed time (BootCard and the router's
## reveal hold). Pure: driven frame by frame with injected frame times.

const STALL_MS := 1000.0
const CAP_MS := 5000.0
const FRAME_MS := 250.0


func test_progress_keeps_it_waiting_until_the_cap() -> void:
	var w := ProgressWait.new(STALL_MS, CAP_MS)
	var frames := int(CAP_MS / FRAME_MS)
	for i in frames - 1:
		assert_eq(w.step(FRAME_MS, i + 1), ProgressWait.Verdict.WAITING, "frame %d: progressing" % i)
	assert_eq(w.step(FRAME_MS, frames), ProgressWait.Verdict.CAPPED, "the safety cap, progress or not")
	assert_eq(w.waited_ms, CAP_MS)


func test_no_progress_for_the_stall_time_is_a_stall() -> void:
	var w := ProgressWait.new(STALL_MS, CAP_MS)
	assert_eq(w.step(FRAME_MS, 1), ProgressWait.Verdict.WAITING)
	for i in int(STALL_MS / FRAME_MS) - 1:
		assert_eq(w.step(FRAME_MS, 1), ProgressWait.Verdict.WAITING, "frame %d: not yet a stall" % i)
	assert_eq(w.step(FRAME_MS, 1), ProgressWait.Verdict.STALLED)
	assert_eq(w.stalled_ms, STALL_MS)


func test_progress_resets_the_stall_and_a_long_frame_with_progress_is_not_one() -> void:
	var w := ProgressWait.new(STALL_MS, CAP_MS)
	w.step(STALL_MS - 1.0, 0)
	assert_eq(w.step(FRAME_MS, 1), ProgressWait.Verdict.WAITING, "progress just in time")
	assert_eq(w.stalled_ms, 0.0)
	assert_eq(w.step(STALL_MS * 2.0, 2), ProgressWait.Verdict.WAITING, "a long frame that ended in progress")
	assert_eq(w.step(FRAME_MS, 1), ProgressWait.Verdict.WAITING, "any change of the count is progress")


func test_work_that_never_reports_progress_stalls_like_the_old_cap() -> void:
	var w := ProgressWait.new(STALL_MS, CAP_MS)
	assert_eq(w.step(STALL_MS, 0), ProgressWait.Verdict.STALLED, "a count that stays 0")


func test_values_from_data_and_verdict_names() -> void:
	var s := ProgressWait.load_settings()
	var w := ProgressWait.from_settings()
	assert_eq(w.stall_ms, float(s["stall_timeout_ms"]))
	assert_eq(w.max_ms, float(s["max_wait_ms"]))
	assert_true(w.stall_ms > 0.0 and w.max_ms > w.stall_ms)
	assert_eq(ProgressWait.verdict_name(ProgressWait.Verdict.STALLED), "stalled")
	assert_eq(ProgressWait.verdict_name(ProgressWait.Verdict.CAPPED), "capped")

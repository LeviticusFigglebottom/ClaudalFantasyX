# Audio work in progress at the account handover (2026-10-25)

## M3-AUD-805: Act II sketches II (Ch13–Ch16)
The worktree agent was cut off by the usage limit after rendering, before any checks ran.
- **Sources on claude/audio:** `assets_src/music/{ansedra, lamp_archive, peace_wedding, unlamped, pale_rim,
  drowned_choir}.py`. They are not wired into render_all's JOBS, so nothing renders or ships them yet.
- **The wiring the agent had written:** `M3-AUD-805-wiring.patch` (render_all JOBS and M2_CUES, the music.json cue
  rows, LOOPING_CUES, PROVENANCE rows, listening notes). It was made against claude/audio at 6c4cfdcd. Apply it
  with `git apply --3way docs/kb/audio/wip/M3-AUD-805-wiring.patch`; PROVENANCE and render_all may need a union
  merge by hand.
- **To finish:**
  1. Apply the patch.
  2. Run `python3 tools/audio/render_all.py --only <cue>` for each of the six.
  3. Run `godot --headless --path . --import` with your own XDG_DATA_HOME.
  4. Check each cue with `--determinism`, then run validate_data, the loudness test (−16 ±0.5 LUFS, TP ≤ −1) and
     Godot `--filter=audio_loops`.
  5. Commit the PROVENANCE rows in their own commit, and set docs/kb/tasks/M3/M3-AUD-805-act2-sketches-b.md to
     review.
  The agent's renders came to 3.38 MiB. With M3-AUD-804's sketches and the foley, shipped audio is 47.1 MiB, so the
  total stays under ADR 0170's 56 MiB.

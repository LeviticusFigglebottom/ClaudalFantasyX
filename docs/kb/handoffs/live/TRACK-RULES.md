# Track rules for the new account (2026-10-25)

Every track session reads this file. The Lead owns it.

## COMMON RULES (every track)
- **Project:** "Hymn of the Undertow", an original cinematic CTB RPG in Godot 4.6.3. The repo LeviticusFigglebottom/ClaudalFantasyX is your only memory. The **Lead** is cloud session `session_018aiGwGLGkxsnMnu8VfCu1m`.
- **Integration branch:** `claude/undertow-lead-handoff-ze8rrn`. It replaces `-423ixt`: wherever a doc says -423ixt, read -ze8rrn. Push ONLY your own track branch. Never push to `main`, the integration branch, or another track's branch.
- **Read first:**
  1. CLAUDE.md (binding);
  2. `docs/kb/handoffs/live/CONSOLIDATED.md` on the integration branch (§4 process rules, §7 gotchas);
  3. your live log's "STATE AT HANDOVER (2026-10-25)" section on your branch;
  4. docs/kb/STATUS.md, your role's KB folder, and `python3 tools/taskboard.py --role <role>`.
- **Setup:** `pip install -r tools/requirements.txt`, `python3 tools/dev/fetch_godot.py`, `python3 tools/dev/fetch_render_deps.py`, plus `tools/dev/fetch_blender.py` if you build Blender assets. Then run `godot --headless --path . --import` after every merge.
- **Start:** `git fetch origin`, then merge `origin/claude/undertow-lead-handoff-ze8rrn` into your branch (merge commits, no rebase or force-push), re-import, and run your scoped tests.
- **Guardrails:**
  - the pillars;
  - no Final Fantasy or Square Enix names, terms, music, UI or spell-tier echoes (tools/banned_terms.txt);
  - no AI-generated art or audio, no asset packs;
  - every asset reproducible from assets_src/ or tools/, with a PROVENANCE row;
  - original music only;
  - typed GDScript, no magic numbers outside data, every string through loc keys;
  - the battle core stays headless and deterministic.
- **Gates (no waiting):**
  - Per item, scoped checks only: gdlint, gdformat, validate_data, taskboard --check, dlgc --check, the Godot tests filtered to your area, Blender verify for the jobs you changed, and `HYMN_SHOTS=` only for shots you can affect. VIEW every shot you change.
  - Run long checks in the background and keep working meanwhile. Never run the whole screenshot manifest.
  - The Lead runs full gates on the PC runner.
- **Reporting:**
  - After each finished item, or a small batch, commit (imperative, with the task id), push, and append a line to your live log `docs/kb/handoffs/live/<track>.md` under a new section "NEW ACCOUNT (from 2026-10-25)": `MERGE-READY @ <sha>: <items>; checks run; checks skipped`.
  - send_message to the Lead may be refused. The live log is the channel, and the Lead polls it every 20 minutes.
  - Mark human playtest fixes `FAST-TRACK` so the Lead cherry-picks them at once.
- **Merging:**
  - When the Lead announces a merge, merge the integration branch in again.
  - Shared append-only files (strings.csv, flags.tres, PROVENANCE.md, validate_data.py, ownership.md, accessibility.json): resolve with `python3 tools/dev/merge_union.py <file>`, then check for duplicate loc keys (`cut -d, -f1 game/data/loc/strings.csv | sort | uniq -d`) and keep the newer text.
  - Claim paths in ownership.md before editing scenes or assets. Never edit another track's claimed files; request it via a task (`request-from:`) or send_message that track.
- **Shell safety:** never kill processes by pattern. Give every run a unique `HYMN_LOG_DIR` and `XDG_DATA_HOME` under your scratch dir.
- **NEVER IDLE:**
  - Never end a turn while queue items remain.
  - If you're blocked on another track or on a human verdict, log it and take the next item. Human reviews never block work.
  - When your queue empties, take adjacent work or M3 work from the task board (your role), log it, and continue.
  - If you hit a usage limit, write your exact next step to your live log first.
  - Write a per-session handoff (CLAUDE.md §7) whenever you stop.

## RENDERING GOES TO THE PC (human directive, 2026-10-27)
**No cloud session captures screenshots any more.** Don't run `capture.sh`, `ci_local.sh` with shots, or `HYMN_SHOTS` captures. Portrait or other Godot renders, and look-dev frames, go to the PC too. Headless Godot tests are fine. Blender asset builds and verify stay in the cloud, because they're asset builds, not renders.

The protocol:
1. **Request.** Push your branch. Then append one line to your live log, under a heading `### Render requests`:
   `RENDER-REQUEST @ <sha>: <comma-separated shot ids>; why: <one line>`.
   Any shot id in `tests/screenshots/shots.json` works. For a new shot, add it to shots.json in that commit.
2. **The PC renders.** It polls every `origin/claude/*` live log for unanswered requests and renders them on lavapipe in WSL2 (pixel parity with the baselines), one request at a time and never during a benchmark. It pushes `<id>_out.png`, `<id>_diff.png` and `compare.txt` to a new branch `gpu/render-<track>-<sha7>` under `docs/kb/qa/renders/<track>-<sha7>/`. Then it appends `RENDERED @ <sha>: gpu/render-<track>-<sha7>; <n> pass, <m> drift` to `pc-gpu.md`. The Lead relays this to you.
3. **You view and approve.**
   - `git fetch origin gpu/render-<track>-<sha7>` and VIEW every out and diff PNG.
   - To approve, copy the out PNGs into `tests/screenshots/baselines/`, with baselines.json metadata `{"adapter": "llvmpipe (LLVM 22.1.8, 256 bits)", "godot": "4.6.3-stable (debian4.6.3+ds-2)", "rendering_driver": "vulkan", "rendering_method": "forward_plus"}`. Never use "?".
   - Commit `<task>: re-approve <ids> after viewing (PC render gpu/render-<track>-<sha7>)`.
4. **Don't wait.** Keep working on the next item while the render is queued.

Batch requests: one line per push, covering every shot your recent items can affect.
- **Portrait renders:** post `RENDER-REQUEST @ <sha>: portraits:<id>[,portraits:<id>...]; tool: tools/portraits/render.sh --only <id>`. The PC runs render.sh and pushes the PNGs on the same kind of branch. Shot ids must exist in `tests/screenshots/shots.json` at the requested sha; anything else is skipped.
- **PC import crashes:** if Godot's import aborts, the PC retries it up to 3 times on a fresh `.godot` and never publishes black captures.

## WHILE THE PC IS PAUSED (from 2026-10-27 ~21:30, the human's instruction)
- The PC (`pc-gpu`) is paused until the human says to resume.
- **The Lead's cloud container serves render requests instead.** The protocol is unchanged: post the same `RENDER-REQUEST @ <sha>: <ids>` lines in your live log.
- Results go to `lead/gate-render-<track>-<sha7>` (not `gpu/...`), and their RENDERED lines go in `lead-cloud.md`.
- Cloud lavapipe matches the baselines; it is just slower (4 CPUs, one job at a time). **Keep requests small:** list only the shots you changed.
- **Still never capture in your own session.**

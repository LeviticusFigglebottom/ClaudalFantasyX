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

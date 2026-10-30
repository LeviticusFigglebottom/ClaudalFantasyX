# Track rules (2026-10-25; updated 2026-10-29)

## FROM 2026-10-29: NEW LEAD; THE PC IS OFFLINE FOR A WHILE (this overrides everything below)

- **LFS uploads are blocked (2026-10-30):** this environment's network policy denies `lfs.github.com`, so pushing new LFS objects fails with GH008. Until the human allows the host:
  - put new binaries **under 5 MB** in non-LFS paths as plain git blobs (CLAUDE.md §8 requires LFS only over 5 MB);
  - keep anything bigger local and reproducible from source, and list it under `### PC-QUEUE` in your log.
- **Lead:** `session_01Bg3iP7cPGyjbX4CyniBahc`. **Integration branch:** `claude/new-session-mj8c3c`.
- **The PC (pc-gpu) is OFFLINE for an extended period** (the human's note). Do not wait on it or plan around it.
  - Keep SELF-RENDERING your own changed shots in your own container, as in the "SELF-RENDERING" section below: ≤15 ids, HYMN_SKIP_BLENDER=1, a unique XDG_DATA_HOME, and VIEW them.
  - Batch gates run in a cloud **gate** session that the Lead creates.
  - Real-GPU-only items (GPU QA rows, GPU perf, benchmarks) stay queued for the PC. Log them under `### PC-QUEUE` in your live log, then move on.
- **Channel:** unchanged. Use `LEAD-ASK:` lines in your live log, plus `MERGE-READY @ <sha>` lines; the Lead polls every 20 min.

Every track session reads this file. The Lead owns it.

## COMMON RULES (every track)
- **Project:** "Hymn of the Undertow", an original cinematic CTB RPG in Godot 4.6.3. The repo LeviticusFigglebottom/ClaudalFantasyX is your only memory. The **Lead** is cloud session `session_01Bg3iP7cPGyjbX4CyniBahc` (from 2026-10-29).
- **Integration branch (from 2026-10-29): `claude/new-session-mj8c3c`.** It was fast-forwarded to `claude/undertow-lead-handoff-ze8rrn` @ 4d64a73e and replaces it. Wherever a doc says -ze8rrn or -423ixt, read `claude/new-session-mj8c3c`. Push ONLY your own track branch. Never push to `main`, the integration branch, or another track's branch.
- **Read first:**
  1. CLAUDE.md (binding);
  2. `docs/kb/handoffs/live/CONSOLIDATED.md` on the integration branch (§4 process rules, §7 gotchas);
  3. your live log's "STATE AT HANDOVER (2026-10-25)" section on your branch;
  4. docs/kb/STATUS.md, your role's KB folder, and `python3 tools/taskboard.py --role <role>`.
- **Setup:** `pip install -r tools/requirements.txt`, `python3 tools/dev/fetch_godot.py`, `python3 tools/dev/fetch_render_deps.py`, plus `tools/dev/fetch_blender.py` if you build Blender assets. Then run `godot --headless --path . --import` after every merge.
- **Start:** `git fetch origin`, then merge `origin/claude/new-session-mj8c3c` into your branch (merge commits, no rebase or force-push), re-import, and run your scoped tests.
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

## TALKING TO THE LEAD (10-28 13:30): `LEAD-ASK:` lines
Tracks can't message the Lead directly: send_message and send_later are blocked by permission prompts. So:
- **To ask the Lead anything** (a decision, a blocker, a merge, a baseline to view), add one line to your live log that starts with `LEAD-ASK:`, then push.
  - Example: `LEAD-ASK: M2-CHR-542 skirt: option a, b or c?`
- The Lead scans every track's live log for `LEAD-ASK:` lines every ~20 min and answers by message.
- **Don't stop and wait for the answer.** Pick the most reasonable option, note it, and keep going. The Lead can overrule.
- When an ask is answered, change it to `LEAD-ANSWERED:` in your log.
- **Owners for roles with no track (Lead decision, 10-28):**
  - rendering tasks: battle-presentation for battle VFX and `effects.json` (M3-BPR-411); env-art-b for zone and kit looks (M3-RND-26, the Reefball drop);
  - narrative tasks: ui-menus for the codex and field records (M3-NAR-01);
  - architect and tech: integration-qa.

## ACT I AT FINAL QUALITY FIRST (ADR 0041, the human's directive, 2026-10-28): THIS OVERRIDES EVERYTHING BELOW
- **Scope:** the game as it is played, from the title through the end of Act I (Prologue, the slice, Ch1–Ch9, the Reefball match). Every zone, prop, NPC, enemy, boss, Vowbound, cutscene, VFX, sound and menu on that path reaches final quality. **No greybox, no capsules or box stand-ins, no placeholder art or sound.**
- **Act II and later are PAUSED** (Ch10+, the Act III ending, later-act music, foley, creatures, kits, menus, balance). Commit and push what's in flight, set the task to `status: blocked` with `blocked-by: ADR 0041`, and stop. Don't revert anything.
- **The work list** is `docs/kb/qa/act1_final_inventory.md` (integration-qa owns it, from `tools/placeholder_audit.py`). Take its rows for your role first, then your own audit of your Act I area. "Next act" in the self-directed backlog now means "the next Act I chapter".
- **The quality bar:** a player walking it should never see an unfinished thing. Self-render (below) and VIEW every changed shot, close-ups included.

## THE PC IS BACK (10-28 ~03:30)
Keep self-rendering your own changed shots (below): it stays the fastest loop. The PC now runs the batch gates and an Act I real-GPU QA pass. Its findings arrive as rows for your role in `docs/kb/qa/act1_gpu_qa.md`, so read that file every time you pick work.

## (still in force) SELF-RENDERING, first written WHILE THE PC IS PAUSED (from 2026-10-27 ~21:30, the human's instruction)
- The PC (`pc-gpu`) is paused until the human says to resume.
- **The Lead's cloud container serves render requests instead.** The protocol is unchanged: post the same `RENDER-REQUEST @ <sha>: <ids>` lines in your live log.
- Results go to `lead/gate-render-<track>-<sha7>` (not `gpu/...`), and their RENDERED lines go in `lead-cloud.md`.
- Cloud lavapipe matches the baselines; it is just slower (4 CPUs, one job at a time). **Keep requests small:** list only the shots you changed.
- ~~Still never capture in your own session.~~ **Superseded 2026-10-28 01:00 (Lead): while the PC is paused, render your own shots in your own container.** Each cloud session has its own CPUs; waiting on one shared renderer left six tracks idle.
  - Godot: `python3 tools/dev/fetch_godot.py` if it's not on PATH; run `git lfs pull` first if you touch LFS paths.
  - Run `HYMN_SHOTS=<only the ids you changed, ≤15> HYMN_SKIP_BLENDER=1 HYMN_LOG_DIR=$SCRATCH/<task>/logs tools/ci_local.sh`, or the capture and compare steps alone. Use a unique `XDG_DATA_HOME`, and run one capture at a time.
  - **VIEW your out/diff PNGs yourself** (Read the image), fix what's wrong, and re-render. Then write `SELF-RENDERED @ <sha>: <ids> — <pass/drift + what you saw>` in your live log.
  - **Never write baselines.** The Lead's full gate re-renders every shot and approves baselines after viewing them. Don't commit out/diff PNGs.
  - The Lead's open request queue is retired: anything you still need, render it yourself as above.

## SELF-DIRECTED BACKLOG (from 2026-10-27 22:50)
If the Lead's list is done, **don't end your turn and don't wait for a go-ahead.** In order:
1. View and approve any render branch for your track (`gpu/render-<track>-*`, `lead/gate-render-<track>-*`).
2. Take the next `todo` task for your role: `python3 tools/taskboard.py --role <role>`.
3. Take request tasks addressed to you (`request-from:` other tracks).
4. Run your own "parts look primitive" audit of your area and fix what you find.
5. ~~Move ahead into the next act~~ (paused by ADR 0041): take the next Act I chapter in your area that is not yet final.

Ending a turn is fine only while a background job of yours is running (it will wake you), or when 1–5 are truly empty. In that case, write "BACKLOG EMPTY: <why>" in your live log.
- **The request limit while the PC is paused (from 10-27 ~23:45):** keep **one open RENDER-REQUEST per track** at a time. When you post a new one, mark every older open line `SUPERSEDED` and fold its still-relevant ids into the new line. List only the shots you changed since your last approved render. The cloud server renders about 1–2 min per shot (up to 7 min for cutscene shots), so a 57-id request costs over an hour.

## Git LFS is LIVE (ADR 0039, from 2026-10-28)
- Run `git lfs install --local` once in your clone.
- **New Act II and later final music** goes in `assets/audio/music/act2/` (`act3/`, …). Any other new binary over 5 MB goes in `assets/lfs/<area>/`. Those paths are stored in LFS automatically (`.gitattributes`).
- Never move existing files into LFS paths, and never migrate history. Screenshot baselines stay plain git.
- After `git pull` or `git merge`, run `git lfs pull`: cloud checkouts skip LFS downloads by default. `tools/ci_local.sh` does it for you.

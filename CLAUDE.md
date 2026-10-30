# CLAUDE.md — Operating Rules for Every Agent

Project: **Hymn of the Undertow**, an original, cinematic, turn-based RPG in Godot 4.
The full brief is [`SPEC.md`](SPEC.md). Only the Lead edits it, and every change needs an ADR plus a version note at the bottom.

## 0. Before you start any session

1. Read [`docs/kb/STATUS.md`](docs/kb/STATUS.md): the current milestone, risks, and blockers.
2. Read your role's KB folder (`docs/kb/<story|art|audio|design|tech|qa>/`) and the **latest handoff** for your role in `docs/kb/handoffs/`.
3. Run `python3 tools/taskboard.py --role <role>` and pick or claim a task (§4 below).
4. Check [`docs/kb/ownership.md`](docs/kb/ownership.md) before you touch any scene or asset path.

## 1. Pillars (higher wins a conflict) — SPEC §1

1. **Sincerity**: no meta jokes, and humor never undercuts sorrow.
2. **Beauty in decline**: gorgeous *and* doomed.
3. **The pilgrimage**: a linear journey that opens late.
4. **Tactical clarity**: the player always knows who acts next and what an action costs.
5. **Growth you can see**: spatial, visible progression.
6. **The cost of ending a cycle**: breaking it is right, but nobody keeps everything.

## 2. Guardrails (non-negotiable) — SPEC §2

- **No Square Enix / Final Fantasy names, terms, music, text, or pixel-copied UI.** The banned list is [`tools/banned_terms.txt`](tools/banned_terms.txt), and CI greps for it. If you notice a near-miss term, add it there.
- **No reference images in the repo.** Describe references in words only, in `docs/kb/art/references.md`.
- **No pre-made asset packs.** CC0 and public-domain meshes, textures, and audio are off-limits too. Only OFL fonts and permissively licensed code-only addons are allowed. The one exception is the MPFB2/MakeHuman CC0 *data*, which ADR 0021 vendors under `assets_src/third_party/mpfb2/` as a heavily modified base topology per the human's SPEC §16 Q2 answer. Its GPL code is never vendored.
- **No AI image or audio generation** (SPEC §16 Q5) unless the human approves it.
- **Every asset is reproducible from source** in `assets_src/` or `tools/`, and has a row in [`assets/PROVENANCE.md`](assets/PROVENANCE.md). CI fails on a missing row.
- Original music only. Evoke a style; never imitate a melody.

## 3. Coding standards — SPEC §5.4

- Godot **4.6.3-stable** (ADR 0001), Forward+, typed GDScript everywhere: `class_name`, typed vars, typed arrays, and return types.
- `snake_case.gd` files, `PascalCase` classes. **No magic numbers outside data files.** `game/battle/formulas.gd` is the one exception, because its constants *are* the formulas.
- Data-driven: game tables are JSON under `game/data/` (ADR 0007), and flags are declared in `game/data/flags.tres`. Read and write flags only through `Game.get_flag(&"name")` / `Game.set_flag(&"name")` so the validator can see them.
- Every player-facing string goes through a localization key (`*_key` fields, `tr("KEY")`, and `#line:` tags in `.dlg`).
- **The battle engine must stay headless and deterministic**: no scene or Node dependencies in `game/battle/` core classes, and all randomness goes through the engine's seeded `rng`.
- Every system ships with tests in `tests/unit` or `tests/integration` (ADR 0006). Coverage in `game/battle/` and `game/progression/` may not drop.
- Formulas: edit `docs/kb/design/formulas.md`, `game/battle/formulas.gd`, and `tests/unit/test_formulas.gd` **together** in one commit.
- Formatting and linting: `gdformat -l 120 game tests` and `gdlint game tests` (config in `gdlintrc`).

### Local checks before you push

`tools/ci_local.sh` runs every CI gate and **is the merge gate while GitHub Actions isn't running** (ADR 0008). In a worktree, set `HYMN_SHOTS=<comma-separated ids>` to the screenshots your change can affect (your own shots, plus any scene or shader you touched); the Lead runs the full manifest on merge. Rendering every shot from every agent at once overloads the shared CPU. If there's no Godot on PATH, run `python3 tools/dev/fetch_godot.py` first. The individual steps:

```bash
pip install -r tools/requirements.txt
python3 tools/validate_data.py
python3 tools/run_tool_tests.py -j 4      # the tools suite in parallel, 2–3 min (plain unittest discover also works)
python3 tools/taskboard.py --check
gdlint game tests && gdformat -l 120 --check game tests
# With Godot 4.6.3 on PATH as `godot`:
godot --headless --path . --import
godot --headless --path . res://tests/run_tests.tscn       # add -- --filter=battle to narrow
```

### Fast batches (human directive, 2026-10-30; ADR 0205)
A batch gate blocks only on data, taskboard, lint/format, the tools suite, the Godot tests for the touched areas, the boot smoke and the shots the batch can affect. The full suite, Blender and the full manifest run non-blocking after the merge; their reds become FAST-TRACKs. The hitch bar is ≤ 2 s hidden. Act II starts per track once it has no open Act I row.

### Gate scope: run what your change can break (human directive, 2026-10-23)

Long checks that block work should run only when they can catch something. They are not a ritual.
- **Docs, story or task-board only:** `validate_data`, `taskboard --check`, `dlgc --check`, plus `unittest` only if you touched `tools/`. No Godot run.
- **Code:** lint, format and data checks, plus the Godot tests filtered to your area (`-- --filter=<area>`). Run the coverage step only if you touched `game/battle/` or `game/progression/`.
- **Screenshots:** only the shots your change can affect (`HYMN_SHOTS`). Never the whole manifest from a worktree.
- **Blender:** the rebuild step runs only for jobs your branch touched. Set `HYMN_SKIP_BLENDER=1` when you touched no Blender source.
- **Full `tools/ci_local.sh` with every shot:** the Lead runs it on the integration branch after a batch of code or render merges, not after every docs merge.
- If a check can't catch anything in your diff, skip it and say so in your report. Skipping a check that *could* catch something is not allowed.

## 4. Claiming work — SPEC §13.3

- Tasks are files: `docs/kb/tasks/<milestone>/<id>-<slug>.md` (see `docs/kb/tasks/README.md`).
- To claim one, set `status: doing` and `owner_session: <your session or worktree name>`, commit that change alone, and **push it to the integration branch** (`main`, or the Lead's session branch while one is active) **before starting**. A claim that exists only in your worktree is invisible to everyone else. If two claims race, the one that reached the integration branch first wins, and the other agent picks a different task.
- Agents launched by the Lead in a worktree may leave the claim to the Lead (the Lead records it); they still update their own task file's status and notes.
- When the work is ready, set `status: review` and name the reviewer role (SPEC §12.3 pairs). The reviewer appends to the task's **Review log**. Only then does it move to `done`.
- To ask another role for something, create a task with `role: <target>`, `status: todo`, and `request-from: <your role>`.
- Urgent blockers go in the **Blockers** section of `STATUS.md`.

## 5. Scene and asset ownership — SPEC §5.3

- Claim path globs in `docs/kb/ownership.md` before you edit `.tscn` or `.tres` files or assets.
- Never edit another role's claimed scene. Open a request task instead.
- Prefer small, single-purpose scenes instanced into level scenes.
- **Shared files** that many roles touch (`game/data/loc/*.csv`, `game/data/flags.tres`, `assets/PROVENANCE.md`, `tools/banned_terms.txt`, `tools/validate_data.py`, `docs/kb/design/formulas.md`, `docs/kb/glossary.md`) are **append-only for non-owners**: add your rows or sections at the end of the relevant block, never reorder or reformat others' lines, and keep each edit in its own small commit so merges stay trivial. Prefer a new per-domain file (such as `game/data/loc/dialogue.csv` or `tools/tests/test_<area>.py`) over growing a shared one.

## 6. Decisions — SPEC §13.4

Any choice that affects more than one role, or that departs from the spec, gets an ADR in `docs/kb/decisions/NNNN-slug.md` (template: `0000-template.md`). ADRs are append-only. To overturn one, write a new ADR that supersedes it.

## 7. Handoffs — SPEC §13.5

Every session ends with `docs/kb/handoffs/<YYYY-MM-DD>-<role>-<n>.md` covering what was done, what's in progress, **the exact next step**, known issues, and the files touched. The template is in `docs/kb/handoffs/README.md`.

### 7a. Live handoff logs (human directive, 2026-10-23)

The project will move to another account with new environments on the same repo. At any moment, a fresh Lead must be able to resume from the repo alone.
- **`docs/kb/handoffs/live/CONSOLIDATED.md`** is the single entry point. The Lead keeps it current after every merge batch. It covers the state of every environment and branch, what's in flight, the exact next steps, open human questions, and gotchas.
- **`docs/kb/handoffs/live/<environment>.md`** has one file per environment (`lead-cloud.md`, `pc-gpu.md`, `first-playable.md` and so on). Each environment updates its own file on its own branch after every finished item: what's done, what's in progress, the exact next step, and any un-pushed state. Never edit another environment's file; the Lead merges them.
- A per-session handoff (§7) is still written at the end of each task.

## 8. Branches and merging

- `main` is always green. Work on a branch per role or task (`<role>/<task-id>-slug`, or the session branch you were given), ideally in a **git worktree** when streams run in parallel.
- Merge to `main` at least daily, and only behind passing CI. Prefer merge commits on shared branches. Never rewrite history someone else depends on.
- Commit messages are imperative and reference the task id, e.g. `M1-CMB-01: add swap preview`.
- Never commit generated `.godot/` caches, large binaries over 5 MB as plain blobs (Git LFS is approved for new large binaries by path, ADR 0039; screenshot baselines stay plain git; never migrate history), or any copyrighted reference material.

## 8a. Shared machine etiquette (parallel agents)
- **Never kill processes by pattern** (`pkill -f capture.tscn`, `killall godot` and the like). Other agents run the same commands in their own worktrees. Kill only PIDs you started, for example by remembering `$!` or by checking `/proc/<pid>/cwd` is your worktree.
- **Scratch files:** put them in a subfolder named after your worktree or task, such as `$SCRATCH/<task-id>/`, and always set a unique `HYMN_LOG_DIR` for `ci_local.sh` runs. Parallel agents share the scratchpad, and shared paths have mixed up gate logs.
- Use `HYMN_SHOTS` for screenshot gates in a worktree (see §3). Godot's `user://` is isolated per `ci_local.sh` run (`XDG_DATA_HOME`); if you run Godot outside it, set your own `XDG_DATA_HOME`.

## 9. Asking the human

Only for the items in SPEC §16 or for an irreversible choice. Everything else: decide, write an ADR, and keep going.

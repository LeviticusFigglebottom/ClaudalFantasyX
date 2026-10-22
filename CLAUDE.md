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
- **No pre-made asset packs.** CC0 and public-domain meshes, textures, and audio are off-limits too. Only OFL fonts and permissively licensed code-only addons are allowed.
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

`tools/ci_local.sh` runs every CI gate and **is the merge gate while GitHub Actions isn't running** (ADR 0008). If there's no Godot on PATH, run `python3 tools/dev/fetch_godot.py` first. The individual steps:

```bash
pip install -r tools/requirements.txt
python3 tools/validate_data.py
python3 -m unittest discover -s tools/tests
python3 tools/taskboard.py --check
gdlint game tests && gdformat -l 120 --check game tests
# With Godot 4.6.3 on PATH as `godot`:
godot --headless --path . --import
godot --headless --path . res://tests/run_tests.tscn       # add -- --filter=battle to narrow
```

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

## 8. Branches and merging

- `main` is always green. Work on a branch per role or task (`<role>/<task-id>-slug`, or the session branch you were given), ideally in a **git worktree** when streams run in parallel.
- Merge to `main` at least daily, and only behind passing CI. Prefer merge commits on shared branches. Never rewrite history someone else depends on.
- Commit messages are imperative and reference the task id, e.g. `M1-CMB-01: add swap preview`.
- Never commit generated `.godot/` caches, large binaries over 5 MB (Git LFS is deferred, ADR 0005), or any copyrighted reference material.

## 9. Asking the human

Only for the items in SPEC §16 or for an irreversible choice. Everything else: decide, write an ADR, and keep going.

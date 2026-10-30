#!/usr/bin/env python3
"""File-based task board (SPEC §13.3).

Tasks live in docs/kb/tasks/<milestone>/<id>-<slug>.md with YAML-ish frontmatter:
  id, title, role, status (todo|doing|review|done|blocked), owner_session, depends_on,
  milestone, and optionally request-from.

Usage:
  python3 tools/taskboard.py            # board summary grouped by status
  python3 tools/taskboard.py --check    # exit 1 on malformed tasks, unknown dependencies or a duplicate id
  python3 tools/taskboard.py --role combat
Stale rule: a 'doing' task whose file has had no commit for more than 48h is flagged STALE.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS = ROOT / "docs" / "kb" / "tasks"
STATUSES = ["doing", "review", "blocked", "todo", "done"]
REQUIRED = ["id", "title", "role", "status", "owner_session", "depends_on", "milestone"]
ROLES = {"lead", "architect", "combat", "progression", "narrative", "cinematics", "rendering",
         "character", "environment", "ui", "audio", "qa"}
STALE_SEC = 48 * 3600


def parse(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing frontmatter")
    end = text.find("\n---", 4)
    if end < 0:
        raise ValueError("unterminated frontmatter")
    meta: dict[str, object] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, _, val = line.partition(":")
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            meta[key.strip()] = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
        else:
            meta[key.strip()] = val.strip("'\"")
    meta["_path"] = path
    return meta


def last_commit_ts(path: Path) -> float | None:
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%ct", "--", str(path)], cwd=ROOT,
                             capture_output=True, text=True, check=False).stdout.strip()
        return float(out) if out else None
    except OSError:
        return None


def load_all() -> tuple[list[dict[str, object]], list[str]]:
    tasks, problems = [], []
    for p in sorted(TASKS.rglob("*.md")):
        if p.name.upper() == "README.MD":
            continue
        try:
            t = parse(p)
        except ValueError as e:
            problems.append(f"{p.relative_to(ROOT)}: {e}")
            continue
        missing = [k for k in REQUIRED if k not in t]
        if missing:
            problems.append(f"{p.relative_to(ROOT)}: missing {missing}")
        rel = p.relative_to(ROOT)
        if t.get("status") not in STATUSES:
            problems.append(f"{rel}: bad status '{t.get('status')}'")
        if t.get("role") not in ROLES:
            problems.append(f"{rel}: unknown role '{t.get('role')}' (one of {sorted(ROLES)})")
        if not p.name.startswith(f"{t.get('id')}-"):
            problems.append(f"{rel}: filename must start with its id '{t.get('id')}-'")
        if t.get("status") in ("doing", "review") and not t.get("owner_session"):
            problems.append(f"{rel}: status '{t.get('status')}' needs an owner_session")
        if t.get("status") == "done":
            body = p.read_text(encoding="utf-8")
            log = body.split("## Review log", 1)[1] if "## Review log" in body else ""
            if not any(line.strip().startswith("-") for line in log.splitlines()):
                problems.append(f"{rel}: 'done' requires a Review log entry (SPEC §11.6)")
        tasks.append(t)
    problems += duplicate_ids(tasks)
    ids = {t.get("id") for t in tasks}
    for t in tasks:
        for dep in t.get("depends_on") or []:
            if dep not in ids:
                problems.append(f"{t['id']}: depends on unknown task '{dep}'")
    return tasks, problems


def duplicate_ids(tasks: list[dict[str, object]]) -> list[str]:
    """One problem per id that two or more task files carry (a claim, a dependency or a review would hit either)."""
    files: dict[str, list[str]] = {}
    for t in tasks:
        path = t.get("_path")
        rel = str(path.relative_to(ROOT)) if isinstance(path, Path) and path.is_relative_to(ROOT) else str(path)
        files.setdefault(str(t.get("id")), []).append(rel)
    return [f"{tid}: duplicate id in {len(fs)} files: {', '.join(sorted(fs))}"
            for tid, fs in sorted(files.items()) if len(fs) > 1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--role")
    ap.add_argument("--milestone")
    args = ap.parse_args()
    tasks, problems = load_all()
    if args.role:
        tasks = [t for t in tasks if t.get("role") == args.role]
    if args.milestone:
        tasks = [t for t in tasks if t.get("milestone") == args.milestone]
    done_ids = {t["id"] for t in tasks if t.get("status") == "done"}
    now = time.time()
    for status in STATUSES:
        group = [t for t in tasks if t.get("status") == status]
        if not group:
            continue
        print(f"\n== {status.upper()} ({len(group)})")
        for t in group:
            note = ""
            deps = [d for d in (t.get("depends_on") or []) if d not in done_ids]
            if status == "todo" and deps:
                note += f"  [waits on {', '.join(deps)}]"
            if status == "doing":
                ts = last_commit_ts(t["_path"])  # type: ignore[arg-type]
                if ts is not None and now - ts > STALE_SEC:
                    note += f"  STALE ({int((now - ts) / 3600)}h)"
            owner = t.get("owner_session") or "-"
            print(f"  {t['id']:<10} {t.get('role', '?'):<12} {owner:<14} {t.get('title')}{note}")
    total = len(tasks)
    done = len([t for t in tasks if t.get("status") == "done"])
    print(f"\n{done}/{total} done")
    for p in problems:
        print(f"PROBLEM {p}")
    return 1 if (args.check and problems) else 0


if __name__ == "__main__":
    sys.exit(main())

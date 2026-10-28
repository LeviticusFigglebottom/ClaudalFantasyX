#!/usr/bin/env python3
"""Integration QA's trial merge (the Lead, 2026-10-28): catch two tracks editing the same thing before the batch merge.

In a throwaway worktree (never pushed), start from the integration branch and merge every track head into it in
turn. For each merge that conflicts, the report names the files and, for each file, the tracks already merged that
changed it since the integration branch (the other side of the clash). The merge is then resolved so the next track
can go in:
- the append-only shared files by union (tools/dev/merge_union.py);
- anything else keeps the side already merged ("ours"), which the report notes, so the tree stays approximate.
Prints the report as Markdown; `--out` writes it to a file too; the worktree's path is printed for further checks
(the placeholder audit). Nothing is committed to any real branch.

  python3 tools/dev/trial_merge.py [--dir SCRATCH/trial] [--out report.md] [--keep]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INTEGRATION = "claude/undertow-lead-handoff-ze8rrn"
TRACKS = [
    "env-art",
    "env-art-b",
    "creatures",
    "creatures-b",
    "characters",
    "ui",
    "battle-presentation",
    "act1-chapters",
    "m2-slice",
    "audio",
    "hero-integration",
]
IDENT = ["-c", "user.name=trial-merge", "-c", "user.email=trial-merge@localhost"]


def git(*args: str, cwd: Path = ROOT, check: bool = True) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args), r.stderr.strip()))
    return r.stdout


def blob(ref: str, file: str, wt: Path) -> str:
    """The file's blob at `ref` ("" when the file isn't there)."""
    r = subprocess.run(["git", "rev-parse", "-q", "--verify", "%s:%s" % (ref, file)], cwd=wt, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def other_sides(file: str, track: str, merged: list[str], wt: Path) -> list[list[str]]:
    """The versions of `file` already merged that clash with `track`'s: the merged tracks grouped by the blob they
    hold, leaving out those that still have the integration branch's version or the same as `track`'s. Tracks that
    merged each other's work share a group."""
    base = blob("origin/%s" % INTEGRATION, file, wt)
    mine = blob("origin/claude/%s" % track, file, wt)
    groups: dict[str, list[str]] = {}
    for m in merged:
        b = blob("origin/claude/%s" % m, file, wt)
        if b != base and b != mine:
            groups.setdefault(b, []).append(m)
    return list(groups.values())


def merge_all(wt: Path, tracks: list[str]) -> list[dict]:
    results: list[dict] = []
    merged: list[str] = []
    for t in tracks:
        ref = "origin/claude/%s" % t
        head = git("rev-parse", "--short=8", ref, cwd=wt).strip()
        new = git("rev-list", "--count", "HEAD..%s" % ref, cwd=wt).strip()
        r = subprocess.run(["git", *IDENT, "merge", "--no-edit", "-q", ref], cwd=wt, capture_output=True, text=True)
        row = {"track": t, "head": head, "new": int(new or 0), "conflicts": [], "union": [], "kept_ours": []}
        if r.returncode != 0:
            files = [f for f in git("diff", "--name-only", "--diff-filter=U", cwd=wt).split() if f]
            for f in files:
                row["conflicts"].append({"file": f, "with": other_sides(f, t, merged, wt)})
            subprocess.run([sys.executable, str(wt / "tools/dev/merge_union.py")], cwd=wt, capture_output=True, text=True)
            left = [f for f in git("diff", "--name-only", "--diff-filter=U", cwd=wt).split() if f]
            row["union"] = sorted(set(files) - set(left))
            for f in left:
                if subprocess.run(["git", "checkout", "--ours", "--", f], cwd=wt, capture_output=True).returncode != 0:
                    git("rm", "-q", "--", f, cwd=wt, check=False)  # deleted on our side
                git("add", "--", f, cwd=wt, check=False)
            row["kept_ours"] = left
            git(*IDENT, "commit", "-q", "--no-edit", cwd=wt)
        merged.append(t)
        results.append(row)
    return results


def report(base: str, results: list[dict]) -> str:
    lines = ["TRIAL MERGE @ integration %s: %s" % (base, ", ".join("%s %s" % (r["track"], r["head"]) for r in results))]
    clashes = [r for r in results if r["conflicts"]]
    if not clashes:
        lines.append("- No conflicts: every track head merges cleanly onto the integration branch and onto each other.")
    for r in clashes:
        real = [c for c in r["conflicts"] if c["file"] not in r["union"]]
        lines.append(
            "- **%s** (%s): %d conflicted file(s); %d resolved by union (append-only files)%s"
            % (r["track"], r["head"], len(r["conflicts"]), len(r["union"]), ":" if real else ".")
        )
        for c in real:
            sides = " vs ".join("+".join(g) for g in c["with"]) or "the merged tree"
            lines.append("  - `%s`: %s vs %s (the trial keeps the merged side)" % (c["file"], r["track"], sides))
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", help="where to put the throwaway worktree (default: a temp dir)")
    ap.add_argument("--out", help="also write the report here")
    ap.add_argument("--keep", action="store_true", help="keep the worktree (to run the placeholder audit in it)")
    ap.add_argument("--tracks", nargs="*", default=TRACKS)
    args = ap.parse_args(argv)
    git("fetch", "-q", "origin", INTEGRATION, *["claude/%s" % t for t in args.tracks])
    wt = Path(args.dir) if args.dir else Path(tempfile.mkdtemp(prefix="trial_merge_")) / "wt"
    if wt.exists():
        git("worktree", "remove", "--force", str(wt), check=False)
    git("worktree", "add", "-q", "--detach", str(wt), "origin/%s" % INTEGRATION)
    base = git("rev-parse", "--short=8", "HEAD", cwd=wt).strip()
    try:
        text = report(base, merge_all(wt, args.tracks))
    finally:
        if not args.keep:
            git("worktree", "remove", "--force", str(wt), check=False)
    print(text, end="")
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    if args.keep:
        print("worktree: %s" % wt)
    return 0


if __name__ == "__main__":
    sys.exit(main())

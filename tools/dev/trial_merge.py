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
INTEGRATION = "claude/new-session-mj8c3c"  # the Lead's integration branch (TRACK-RULES.md); --integration overrides
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
BASE = ""  # the tree the tracks merge onto: the integration branch, plus --prefold refs (set in main)
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
    base = blob(BASE or "origin/%s" % INTEGRATION, file, wt)
    mine = blob("origin/claude/%s" % track, file, wt)
    groups: dict[str, list[str]] = {}
    for m in merged:
        b = blob("origin/claude/%s" % m, file, wt)
        if b != base and b != mine:
            groups.setdefault(b, []).append(m)
    return list(groups.values())


def prefold(wt: Path, refs: list[str]) -> list[str]:
    """Merges each ref (a batch the Lead hasn't landed yet, e.g. lead/gate-big16) onto the worktree before the
    tracks, so the trial shows what the next batch will meet. Returns the files a prefold clashed on (kept ours)."""
    clashed: list[str] = []
    for ref in refs:
        cmd = ["git", *IDENT, "merge", "--no-edit", "-q", "origin/%s" % ref]
        r = subprocess.run(cmd, cwd=wt, capture_output=True, text=True)
        if r.returncode != 0:
            subprocess.run([sys.executable, str(ROOT / "tools/dev/merge_union.py")], cwd=wt, capture_output=True, text=True)
            for f in [f for f in git("diff", "--name-only", "--diff-filter=U", cwd=wt).split() if f]:
                clashed.append("%s (%s)" % (f, ref))
                git("checkout", "--theirs", "--", f, cwd=wt, check=False)
                git("add", "--", f, cwd=wt, check=False)
            git(*IDENT, "commit", "-q", "--no-edit", cwd=wt)
    return clashed


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
            subprocess.run([sys.executable, str(ROOT / "tools/dev/merge_union.py")], cwd=wt, capture_output=True, text=True)
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


def report(base: str, results: list[dict], folded: list[str] | None = None, clashed: list[str] | None = None) -> str:
    on = "integration %s" % base + "".join(" + %s" % f for f in folded or [])
    lines = ["TRIAL MERGE @ %s: %s" % (on, ", ".join("%s %s" % (r["track"], r["head"]) for r in results))]
    for c in clashed or []:
        lines.append("- prefold clash (the trial keeps the prefold's side): `%s`" % c)
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


def set_integration(branch: str) -> None:
    global INTEGRATION
    INTEGRATION = branch


def set_base(ref: str) -> None:
    global BASE
    BASE = ref


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", help="where to put the throwaway worktree (default: a temp dir)")
    ap.add_argument("--out", help="also write the report here")
    ap.add_argument("--keep", action="store_true", help="keep the worktree (to run the placeholder audit in it)")
    ap.add_argument("--tracks", nargs="*", default=TRACKS)
    ap.add_argument("--integration", default=INTEGRATION, help="the branch to merge onto (default: %(default)s)")
    ap.add_argument("--prefold", nargs="*", default=[], help="refs merged first, e.g. a batch not yet on integration")
    args = ap.parse_args(argv)
    set_integration(args.integration)
    git("fetch", "-q", "origin", INTEGRATION, *args.prefold, *["claude/%s" % t for t in args.tracks])
    wt = Path(args.dir) if args.dir else Path(tempfile.mkdtemp(prefix="trial_merge_")) / "wt"
    if wt.exists():
        git("worktree", "remove", "--force", str(wt), check=False)
    git("worktree", "add", "-q", "--detach", str(wt), "origin/%s" % INTEGRATION)
    base = git("rev-parse", "--short=8", "HEAD", cwd=wt).strip()
    try:
        clashed = prefold(wt, args.prefold)
        set_base(git("rev-parse", "HEAD", cwd=wt).strip())
        folded = ["%s %s" % (f, git("rev-parse", "--short=8", "origin/%s" % f, cwd=wt).strip()) for f in args.prefold]
        text = report(base, merge_all(wt, args.tracks), folded, clashed)
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

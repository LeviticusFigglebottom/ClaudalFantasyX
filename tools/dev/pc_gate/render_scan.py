"""List unanswered RENDER-REQUEST lines in every origin/claude/* live log (TRACK-RULES "RENDERING GOES TO THE PC").

A request is answered when pc-gpu.md (on any origin/gpu/* branch, or the local file given) has `RENDERED @ <sha>`.
Run in the Windows clone after `git fetch origin`. Prints: track sha ids why (oldest commit first).
"""
import re
import subprocess
import sys

REPO = sys.argv[1] if len(sys.argv) > 1 else "."
REQ = re.compile(r"RENDER-REQUEST @ ([0-9a-f]{7,40})\s*:\s*([^;]+?)(?:;\s*why:\s*(.*))?$")
DONE = re.compile(r"RENDERED @ ([0-9a-f]{7,40})")


def git(*a: str) -> str:
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, encoding="utf-8").stdout


def refs(prefix: str) -> list[str]:
    return git("for-each-ref", "--format=%(refname:short)", f"refs/remotes/origin/{prefix}").split()


done: set[str] = set()
for r in refs("gpu/"):
    done.update(m.group(1)[:7] for m in DONE.finditer(git("show", f"{r}:docs/kb/handoffs/live/pc-gpu.md")))
for extra in sys.argv[2:]:
    done.update(m.group(1)[:7] for m in DONE.finditer(open(extra, encoding="utf-8").read()))

seen: set[tuple[str, str]] = set()
for r in refs("claude/"):
    track = r.split("/", 2)[-1]
    for path in git("ls-tree", "--name-only", f"{r}:docs/kb/handoffs/live/").split():
        if not path.endswith(".md"):
            continue
        for line in git("show", f"{r}:docs/kb/handoffs/live/{path}").splitlines():
            m = REQ.search(line.strip().strip("`"))
            if not m or m.group(1)[:7] in done or (track, m.group(1)[:7]) in seen:
                continue
            seen.add((track, m.group(1)[:7]))
            ts = git("show", "-s", "--format=%ct", m.group(1)).strip() or "?"
            print(ts, track, m.group(1), m.group(2).strip().replace(" ", ""), "|", (m.group(3) or "").strip())

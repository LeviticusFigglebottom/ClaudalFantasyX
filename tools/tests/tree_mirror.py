"""A scratch copy of the repo for tests that run tools/validate_data.py on a tree they edit (M2-NIT-06).

`game/` (about 9 MB) is copied for real, so a test may rewrite any file in it in place. `assets/` (about 200 MB)
is mirrored as real directories holding symlinks to the repo's files: a test may add or delete files there, but
must never write into an existing one (that would write through the link into the repo). Directories are never
symlinked, because Path.rglob does not descend into a linked directory and the validator would quietly see less.

The copy lives in RAM (/dev/shm) when the machine has it: on the shared disk, deleting the ~2,600 entries after
each test took about five seconds, more than the validator run itself. HYMN_TEST_TMP overrides the location.
Each call makes its own unique directory, so tests and parallel runs never share a path."""
import os
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COPIED = ("game", "tools/banned_terms.txt", "docs/kb/glossary.md")
LINKED = ("assets",)


def scratch_root() -> str | None:
    """Where scratch trees go: HYMN_TEST_TMP, else /dev/shm when it is a writable directory, else the default."""
    env = os.environ.get("HYMN_TEST_TMP")
    if env:
        return env
    shm = "/dev/shm"
    return shm if os.path.isdir(shm) and os.access(shm, os.W_OK | os.X_OK) else None


def make_scratch(prefix: str) -> Path:
    return Path(tempfile.mkdtemp(prefix=prefix, dir=scratch_root()))


def mirror_repo(dst: Path, root: Path = ROOT) -> Path:
    for rel in COPIED + LINKED:
        src, out = root / rel, dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, out, ignore=shutil.ignore_patterns(".godot"),
                            copy_function=os.symlink if rel in LINKED else shutil.copy2)
        elif src.exists():
            shutil.copy(src, out)
    return dst


def scratch_repo(prefix: str) -> Path:
    """A fresh, unique mirror of the repo (see the module docstring); the caller removes it with shutil.rmtree."""
    return mirror_repo(make_scratch(prefix))

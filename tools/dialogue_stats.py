#!/usr/bin/env python3
"""Dialogue word counts against the SPEC §3.6 budget (40–60k words, hard ceiling 80k).

Compiles every .dlg with tools/dlgc.py (nothing is written) and reports:
  * words per scene, split into spoken lines, narration (no speaker), and player options
  * words per speaker across all scenes
  * the total, and a projection to the full game from the slice's share of it

The projection: the vertical slice is about `--slice-minutes` of a main story of about
`--game-hours` (SPEC §10.1: 25–35 h). If the game kept the slice's dialogue density, it would
need total / share words. The slice's fair share of the budget is 40k–60k × share.

Words are runs of letters and digits (apostrophes and hyphens inside a word don't split it).
Scenes under game/data/dialogue/test/ are fixtures and are skipped unless --include-tests.
A line over the voice guide's ~25-word limit is listed as a warning (dlgc warns too), unless it is
tagged #long. Narration with a voice identity (`Narrator(rhen): ...`) counts as "(narration: rhen)".

Usage: python3 tools/dialogue_stats.py [--slice-minutes 40] [--game-hours 30] [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dlgc  # noqa: E402

BUDGET_MIN = 40_000
BUDGET_MAX = 60_000
BUDGET_CEILING = 80_000
LINE_WORD_LIMIT = dlgc.LINE_WORD_LIMIT  # docs/kb/story/voice_guide.md: "about 25 words or fewer"
NARRATION = "(narration)"
OPTIONS = "(player options)"
FIXTURE_DIR = dlgc.TEST_DIR.as_posix() + "/"


def count_words(text: str) -> int:
    return dlgc.count_words(text)


def who_of(op: dict) -> str:
    """The word-count bucket for a line op: its speaker, or narration (with its voice identity)."""
    if op["speaker"]:
        return op["speaker"]
    return f"(narration: {op['narrator']})" if op.get("narrator") else NARRATION


def collect(root: Path, include_tests: bool = False) -> dict:
    """Returns {"scenes": {scene: {...}}, "speakers": {...}, "total": n, "long_lines": [...]}."""
    result = dlgc.compile_project(root)
    if result.errors:
        raise SystemExit("dlgc errors:\n" + "\n".join(result.errors))
    text_by_key = dict(result.loc_rows)
    scenes: dict[str, dict] = {}
    speakers: dict[str, int] = defaultdict(int)
    long_lines: list[tuple[str, str, int]] = []
    for rel, raw in sorted(result.outputs.items()):
        if not rel.endswith(".json"):
            continue
        scene = json.loads(raw)
        if not include_tests and scene["source"].startswith(FIXTURE_DIR):
            continue
        row = {"source": scene["source"], "spoken": 0, "narration": 0, "options": 0, "lines": 0,
               "speakers": defaultdict(int)}
        for node in scene["nodes"].values():
            for op in node["ops"]:
                if op["op"] == "line":
                    n = count_words(text_by_key[op["key"]])
                    who = who_of(op)
                    row["narration" if not op["speaker"] else "spoken"] += n
                    row["lines"] += 1
                    row["speakers"][who] += n
                    speakers[who] += n
                    if n > LINE_WORD_LIMIT and dlgc.TAG_LONG not in op.get("tags", []):
                        long_lines.append((scene["scene"], op["id"], n))
                elif op["op"] == "options":
                    for choice in op["choices"]:
                        n = count_words(text_by_key[choice["key"]])
                        row["options"] += n
                        row["lines"] += 1
                        row["speakers"][OPTIONS] += n
                        speakers[OPTIONS] += n
        row["words"] = row["spoken"] + row["narration"] + row["options"]
        row["speakers"] = dict(row["speakers"])
        scenes[scene["scene"]] = row
    total = sum(s["words"] for s in scenes.values())
    return {"scenes": scenes, "speakers": dict(speakers), "total": total, "long_lines": long_lines}


def projection(total: int, slice_minutes: float, game_hours: float) -> dict:
    share = slice_minutes / (game_hours * 60.0)
    return {
        "slice_minutes": slice_minutes,
        "game_hours": game_hours,
        "share": share,
        "slice_budget_min": round(BUDGET_MIN * share),
        "slice_budget_max": round(BUDGET_MAX * share),
        "projected_game_words": round(total / share) if share > 0 else 0,
    }


def render(stats: dict, proj: dict) -> str:
    out: list[str] = []
    out.append(f"{'scene':34} {'lines':>5} {'spoken':>7} {'narr':>5} {'opts':>5} {'words':>6}")
    for name, s in stats["scenes"].items():
        out.append(f"{name:34} {s['lines']:5d} {s['spoken']:7d} {s['narration']:5d} {s['options']:5d} "
                   f"{s['words']:6d}")
    out.append("")
    out.append(f"{'speaker':34} {'words':>6} {'share':>6}")
    total = stats["total"] or 1
    for who, n in sorted(stats["speakers"].items(), key=lambda kv: (-kv[1], kv[0])):
        out.append(f"{who:34} {n:6d} {100.0 * n / total:5.1f}%")
    out.append("")
    out.append(f"TOTAL {stats['total']} words in {len(stats['scenes'])} scene(s)")
    out.append(f"Budget (SPEC §3.6): {BUDGET_MIN:,}–{BUDGET_MAX:,} words, ceiling {BUDGET_CEILING:,}.")
    out.append(f"Slice share: {proj['slice_minutes']:g} min of a {proj['game_hours']:g} h main story = "
               f"{100.0 * proj['share']:.2f}% -> the slice's share of the budget is "
               f"{proj['slice_budget_min']:,}–{proj['slice_budget_max']:,} words.")
    out.append(f"At this density the full game would run about {proj['projected_game_words']:,} words.")
    for scene, line_id, n in stats["long_lines"]:
        out.append(f"WARN {scene}/{line_id}: {n} words (voice guide: about {LINE_WORD_LIMIT} or fewer)")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--slice-minutes", type=float, default=40.0, help="vertical slice length (SPEC: 30–45)")
    ap.add_argument("--game-hours", type=float, default=30.0, help="main story length (SPEC §10.1: 25–35)")
    ap.add_argument("--include-tests", action="store_true", help="count test fixture scenes too")
    ap.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = ap.parse_args(argv)
    if args.slice_minutes <= 0 or args.game_hours <= 0:
        ap.error("--slice-minutes and --game-hours must be positive")
    stats = collect(args.root, args.include_tests)
    proj = projection(stats["total"], args.slice_minutes, args.game_hours)
    if args.json:
        stats["long_lines"] = [list(t) for t in stats["long_lines"]]
        print(json.dumps({"stats": stats, "projection": proj}, indent=1, ensure_ascii=False))
    else:
        print(render(stats, proj))
    return 0


if __name__ == "__main__":
    sys.exit(main())

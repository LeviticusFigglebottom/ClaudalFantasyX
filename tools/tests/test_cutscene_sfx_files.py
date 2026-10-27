"""Every `@sfx <id>` a cutscene names has its file (M3-AUD-818), and every `@music <id>` a cue (M3-AUD-823). The CutsceneSequencer plays
`<sequencer.json sfx_dir><id>.ogg` and only warns "no sound" when it is missing, so a cue with no file is silent and
nothing fails. This test fails instead, naming the cue and its .dlg. Audio's sources are assets_src/sfx/act1_cutscene_sfx.py
and the older battle_sfx.py (drownbell_toll). Run: python3 -m unittest discover -s tools/tests"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SFX_CUE = re.compile(r"^\s*@sfx\s+(\S+)", re.M)
MUSIC_CUE = re.compile(r"^\s*@music\s+(\S+)", re.M)
SILENCE = "silence"
# Cues the scripts name that audio has not delivered yet (M3-AUD-819..822 are composing them). The list may only
# shrink: a cue that lands must leave it, and a new script id must get a cue or join it on purpose.
MUSIC_TODO = {
    "corrow_night", "dawn_road", "going_under", "hush_second_verse", "kerrid_stair", "lanternfall",
    "liss_theme", "raid", "rhen_current_hum", "shoals_dusk",
    "undertow_rising",
}


def sfx_dir() -> Path:
    cfg = json.loads((ROOT / "game/data/cutscene/sequencer.json").read_text(encoding="utf-8"))
    return ROOT / str(cfg["sfx_dir"]).removeprefix("res://")


def _scripts() -> list[Path]:
    return [d for d in sorted((ROOT / "game/data/dialogue").rglob("*.dlg")) if not d.name.startswith("test_")]


def music_ids() -> set[str]:
    """Every @music id a script names, but the reserved silence."""
    return {m.group(1) for d in _scripts() for m in MUSIC_CUE.finditer(d.read_text(encoding="utf-8"))} - {SILENCE}


def known_music() -> set[str]:
    cues = json.loads((ROOT / "game/data/audio/music.json").read_text(encoding="utf-8"))["cues"]
    seq = json.loads((ROOT / "game/data/cutscene/sequencer.json").read_text(encoding="utf-8"))
    return set(cues) | set(seq.get("music_stand_ins", {}))


def missing() -> list[str]:
    out = []
    base = sfx_dir()
    for dlg in sorted((ROOT / "game/data/dialogue").rglob("*.dlg")):
        if dlg.name.startswith("test_"):
            continue  # the parser's fixtures name made-up cues on purpose
        for m in SFX_CUE.finditer(dlg.read_text(encoding="utf-8")):
            if not (base / f"{m.group(1)}.ogg").is_file():
                out.append(f"{dlg.relative_to(ROOT)}: @sfx {m.group(1)}")
    return out


class CutsceneSfxFilesTest(unittest.TestCase):
    def test_every_sfx_cue_has_a_file(self) -> None:
        self.assertEqual(missing(), [], "render it (tools/audio/render_all.py) or ask audio for it")

    def test_every_music_cue_resolves_or_is_on_the_todo_list(self) -> None:
        unknown = sorted(music_ids() - known_music() - MUSIC_TODO)
        self.assertEqual(unknown, [], "a script names a cue nobody is making: add it to music.json, or to MUSIC_TODO")

    def test_the_todo_list_only_holds_missing_cues(self) -> None:
        done = sorted(MUSIC_TODO & known_music())
        self.assertEqual(done, [], "these cues exist now: take them off MUSIC_TODO")

    def test_the_act1_source_renders_into_the_sequencers_folder(self) -> None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("act1_cutscene_sfx", ROOT / "assets_src/sfx/act1_cutscene_sfx.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(Path(mod.OUT_DIR).resolve(), sfx_dir().resolve())
        names = [n for n, _, _ in mod.CUES]
        self.assertEqual(len(names), len(set(names)), "each cue once")


if __name__ == "__main__":
    unittest.main()

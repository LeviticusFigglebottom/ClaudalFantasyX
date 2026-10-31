"""Every `@sfx <id>` a cutscene names has its file (M3-AUD-818), and every `@music <id>` a cue (M3-AUD-823) that the
sequencer can play (M3-AUD-833). The CutsceneSequencer plays
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
# Cues the scripts name that audio has not delivered yet. Empty since M3-AUD-819..822 landed; a new script id must
# get a cue, or join this set on purpose while one is being made (it may only shrink). Act II's two people-boss and
# memory gaps were on it until audio delivered them (big21, big22).
# M5-A3P-1002/1005/1008/1012/1016 (act2-plan's audio requests): Act III's script cues still being made.
MUSIC_TODO: set[str] = {"engine_down", "haluna_lifting", "kite_first_lamp", "memory_ansedra", "memory_coilspire",
    "memory_lanternfall", "memory_lowlight", "memory_oruvel", "memory_tidecup", "thank_you", "the_cage", "the_choice",
    "the_eye", "undertow_descent"}
# The same for `@sfx`: Act II script cues audio is making (M4-A2P-107). Empty since big22 delivered all eleven.
# M5-A3P-1002/1005/1008/1012/1016: Act III's script sfx still being made.
SFX_TODO: set[str] = {"clutch_hum", "engine_hum_stops", "hull_meets_water", "kite_engine_strains", "kite_engines_stop",
    "kite_settles", "kite_touches_floor", "match_struck", "names_murmured", "pell_farewell_tide", "rope_creak",
    "rope_slips", "sails_fill", "sea_flat_lap", "shell_into_water", "velamir_lullaby_hum", "wind_in_sails"}


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
            if m.group(1) not in SFX_TODO and not (base / f"{m.group(1)}.ogg").is_file():
                out.append(f"{dlg.relative_to(ROOT)}: @sfx {m.group(1)}")
    return out


class CutsceneSfxFilesTest(unittest.TestCase):
    def test_every_sfx_cue_has_a_file(self) -> None:
        self.assertEqual(missing(), [], "render it (tools/audio/render_all.py) or ask audio for it")

    def test_every_music_cue_resolves_or_is_on_the_todo_list(self) -> None:
        unknown = sorted(music_ids() - known_music() - MUSIC_TODO)
        self.assertEqual(unknown, [], "a script names a cue nobody is making: add it to music.json, or to MUSIC_TODO")

    def test_every_music_cue_plays_as_the_sequencer_finds_it(self) -> None:
        """M3-AUD-833: the sequencer plays <music_dir><id>.ogg or its stand-in's file and never reads music.json, so an
        alias row or a cue made of stems is silent in a cutscene unless music_stand_ins names a file for it."""
        seq = json.loads((ROOT / "game/data/cutscene/sequencer.json").read_text(encoding="utf-8"))
        base = ROOT / str(seq["music_dir"]).removeprefix("res://")
        stand_ins = seq.get("music_stand_ins", {})
        silent = sorted(i for i in music_ids() - MUSIC_TODO
                        if not any(n and (base / f"{n}.ogg").is_file() for n in (i, stand_ins.get(i, ""))))
        self.assertEqual(silent, [], "add a music_stand_ins row naming the cue's file (a stem cue: its first stem)")

    def test_the_todo_list_only_holds_missing_cues(self) -> None:
        done = sorted(MUSIC_TODO & known_music())
        self.assertEqual(done, [], "these cues exist now: take them off MUSIC_TODO")

    def test_the_sfx_todo_list_only_holds_missing_cues_that_a_script_names(self) -> None:
        named = {m.group(1) for d in _scripts() for m in SFX_CUE.finditer(d.read_text(encoding="utf-8"))}
        self.assertEqual(sorted(SFX_TODO - named), [], "no script names these any more: take them off SFX_TODO")
        done = sorted(i for i in SFX_TODO if (sfx_dir() / f"{i}.ogg").is_file())
        self.assertEqual(done, [], "these cues have files now: take them off SFX_TODO")

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

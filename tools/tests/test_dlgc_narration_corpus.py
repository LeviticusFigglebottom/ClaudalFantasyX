"""M1-NAR-07: realistic narration must compile with no near-miss error (and, for prose, no warning).

Rhen narrates the whole game, so colon-led prose is common. Every line here is plain narration as a
writer would type it (no `\\:`, no `#narration`). A heuristic change that rejects or warns on any of
them is a false positive. Run: python3 -m unittest discover -s tools/tests
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import dlgc  # noqa: E402

# The first ten are the review-sweep-C lines (M1-NAR-06 Review log), seven of which used to fail.
CORPUS = [
    "The bell rang three times: once for the drowned, once for the living, once for her.",
    "Mother used to say it plainly: the sea keeps what it is given.",
    "At 6:20 the tide turned.",
    "Three things I kept from Corrow: a lamp, a knife, and her name.",
    "I remember what she told me: don't look back at the harbour.",
    "Asha's answer: nothing.",
    "Ratio 3:1, salt to oil, the way the old keepers mixed it.",
    "When I was small, my father said: the lamps remember us.",
    "No. Not like that: like this.",
    "[The rest of the page is water-stained.]",
    "Asha laughed: once, then never again that winter.",
    "Toma said only this: lie still, and let the water pass.",
    "Then she said: go home.",
    "Rain as cold as iron: that was the first night.",
    "Mother said: run.",
    "We had one rule on the raft: nobody sleeps alone.",
    "By 11:45 the lamps were out, all but hers.",
    "Kerrid's voice came through the hull: low, patient, wrong.",
    "Here is what the Order took from us: our names, our dead, our songs.",
    "The ledger read: twelve hulls, nine families, one bell.",
    "It was always the same question: who rings the bell when the ringer drowns?",
    "Pell kept count on his fingers: four days of water, maybe five.",
    "Sefir had a word for it: stillness.",
    "Nobody told me the truth about the Hollow: it was never empty.",
    "Psalm 4:2 was carved over the door, half worn away.",
    "Liss had two moods that spring: furious and asleep.",
    "The keepers had a saying for it: light the lamp, then leave.",
    "Years later, I understood: she had been saying goodbye.",
    "Only one thing mattered that morning: the boat.",
    "Ysolde wrote a single line in the margin: forgive him.",
    "A rope, a lamp, a name: that was all I carried.",
    "The tide charts were clear: 3:1 against us by dusk.",
    "Asha [the girl from the beach] was already gone.",
    "Rain [or something like it] fell all night.",
    "[Static.] The radio hissed, then nothing.",
    "The harbour at 4:10, grey and empty: I will never forget it.",
    "I asked her why. She shrugged: because.",
    "Every child in Corrow learns the count: one bell, two bells, the long silence.",
    # review-sweep-D narration probes (M1-NAR-07 Review log).
    "I knew it then: she was never coming back.",
    "I had one job that winter: keep the lamp lit.",
    "I counted them twice: eleven, then ten.",
    "My hands remembered before I did: knot, pull, tie off.",
    "Chapter 2: The Raft",
    "Corrow Harbour, Dawn",
    "Asha and Toma: the only two who stayed.",
    "Asha and I: that was all that was left of us.",
    "Not Asha: me.",
    "Only Kerrid: he alone understood.",
    "Ansedra, the Drowned City: we reached it on the ninth day.",
    "Low tide, the eastern reef: nothing moved.",
    "What I said next: I don't remember.",
    "I said the only thing I could: sorry.",
    "Toma's rule was simple: never trust still water.",
    "Kerrid's ship: the Patience, black-hulled, unlit.",
    "North of Corrow: only the reef, and past it nothing.",
    "The Long Dark, Year 412: the lamps went out.",
    "\"Run,\" she said: and I ran.",
    "Even now: I hear it.",
    "Sefir and Pell: brothers in everything but blood.",
    "I Remember Corrow: that was the song.",
]

# Captions and headings: name-shaped, but no speaker in them. They compile as narration with one WARN
# that gives the `\:` / `#narration` escape (review-sweep-D, Lead decision). Never an error.
# (`Asha Vell: ...` from the same probe set names a speaker, so it is an error: see test_dlgc.py.)
CAPTIONS = [
    "Chapter Two: The Raft",
    "Part One: Ashfall",
    "Day Three: the reef.",
    "The Hollow: three days later.",
    "Corrow Harbour: dawn.",
    "Eleven Bells: that is what they called the hour.",
    "Interlude: Ysolde",
    "The Order of Lamps: what they wanted was simple.",
]


class NarrationCorpusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        d = self.tmp / "game" / "data" / "dialogue"
        d.mkdir(parents=True)
        (self.tmp / "game" / "data" / "loc").mkdir(parents=True)
        for name in ("speakers.json", "emotions.json", "cues.json", "events.json"):
            shutil.copy(ROOT / "game" / "data" / "dialogue" / name, d / name)
        # The real display names, so the near-miss checks see what they see in the repo.
        shutil.copy(ROOT / "game" / "data" / "loc" / "strings.csv", self.tmp / "game" / "data" / "loc" / "strings.csv")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def compile_one(self, text: str) -> dlgc.CompileResult:
        p = self.tmp / "game" / "data" / "dialogue" / "ch99" / "t_corpus.dlg"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"title: t_corpus\n---\n{text} #line:t_corpus_001\n===\n", encoding="utf-8")
        return dlgc.compile_project(self.tmp)

    def test_corpus_is_large_enough(self) -> None:
        self.assertGreaterEqual(len(CORPUS), 30)
        self.assertEqual(len(set(CORPUS)), len(CORPUS))

    def test_every_line_is_plain_narration(self) -> None:
        for text in CORPUS:
            with self.subTest(text=text):
                res = self.compile_one(text)
                self.assertEqual(res.errors, [])
                self.assertEqual(res.warnings, [])
                ops = json.loads(res.outputs["game/data/dialogue/compiled/t_corpus.json"])["nodes"]["t_corpus"]["ops"]
                self.assertEqual((ops[0]["op"], ops[0]["speaker"]), ("line", ""))
                self.assertNotIn("tags", ops[0])
                self.assertEqual(res.loc_rows, [("DLG_T_CORPUS_001", text)])

    def test_captions_warn_but_compile_as_narration(self) -> None:
        self.assertTrue(set(CAPTIONS).isdisjoint(CORPUS))
        for text in CAPTIONS:
            with self.subTest(text=text):
                res = self.compile_one(text)
                self.assertEqual(res.errors, [])
                self.assertEqual(len(res.warnings), 1, res.warnings)
                self.assertIn("looks like a speaker", res.warnings[0])
                self.assertIn("write '\\:' for a colon in narration", res.warnings[0])
                self.assertEqual(res.loc_rows, [("DLG_T_CORPUS_001", text)])
                ops = json.loads(res.outputs["game/data/dialogue/compiled/t_corpus.json"])["nodes"]["t_corpus"]["ops"]
                self.assertEqual(ops[0]["speaker"], "")


if __name__ == "__main__":
    unittest.main()
